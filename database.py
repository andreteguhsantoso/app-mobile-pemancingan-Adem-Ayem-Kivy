import sqlite3
import os
import hashlib
import hmac
import secrets
from contextlib import contextmanager
from datetime import datetime


class BookingConflictError(Exception):
    """Raised when a requested spot is no longer available."""


class BookingStateError(Exception):
    """Raised when a booking cannot transition to the requested state."""


class AccountExistsError(Exception):
    """Raised when a username is already registered."""


class PasswordError(Exception):
    """Raised when a password operation is rejected."""


class BookingDatabase:
    def __init__(self, path):
        self.path = path

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self, events, base_occupied, gallery_items=None, news_items=None):
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    avatar_path TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    event_time TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK(price >= 0),
                    quota INTEGER NOT NULL CHECK(quota > 0),
                    release_info TEXT NOT NULL,
                    image TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_code TEXT UNIQUE NOT NULL,
                    event_id TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    ticket_count INTEGER NOT NULL DEFAULT 1,
                    payment_method TEXT NOT NULL,
                    total_amount INTEGER NOT NULL,
                    payment_status TEXT NOT NULL,
                    bait_rule_accepted INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    spot_number INTEGER,
                    customer_notes TEXT NOT NULL DEFAULT '',
                    payment_reference TEXT,
                    updated_at TEXT,
                    user_id INTEGER,
                    FOREIGN KEY(event_id) REFERENCES events(event_id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS event_spots (
                    event_id TEXT NOT NULL,
                    spot_number INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('available', 'occupied')),
                    source TEXT NOT NULL DEFAULT 'inventory',
                    booking_id INTEGER,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(event_id, spot_number),
                    FOREIGN KEY(event_id) REFERENCES events(event_id),
                    FOREIGN KEY(booking_id) REFERENCES bookings(id)
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    details TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS login_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username_attempt TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    source TEXT NOT NULL DEFAULT 'local_app',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS gallery_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seed_key TEXT UNIQUE,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS news_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seed_key TEXT UNIQUE,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    publish_date TEXT NOT NULL,
                    badge TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    event_id TEXT,
                    body_text TEXT NOT NULL,
                    facts TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(event_id) REFERENCES events(event_id)
                );

                CREATE INDEX IF NOT EXISTS idx_bookings_created_at
                    ON bookings(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_event_spots_status
                    ON event_spots(event_id, status);
                CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
                    ON audit_logs(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_login_logs_user
                    ON login_logs(user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_gallery_active
                    ON gallery_items(is_active, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_news_active
                    ON news_items(is_active, created_at DESC);
                """
            )
            self._migrate_booking_columns(connection)
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_bookings_user
                ON bookings(user_id, created_at DESC)
                """
            )

            timestamp = datetime.now().isoformat(timespec="seconds")
            for event_id, event in events.items():
                connection.execute(
                    """
                    INSERT OR IGNORE INTO events (
                        event_id, title, event_date, event_time, price, quota,
                        release_info, image, is_active, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        event_id,
                        event["title"],
                        event["date"],
                        event["time"],
                        event["price"],
                        event["quota"],
                        event["release"],
                        event["image"],
                        timestamp,
                    ),
                )
                for spot_number in range(1, event["quota"] + 1):
                    occupied = spot_number in base_occupied.get(event_id, set())
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO event_spots (
                            event_id, spot_number, status, source, updated_at
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            event_id,
                            spot_number,
                            "occupied" if occupied else "available",
                            "initial_event_data" if occupied else "inventory",
                            timestamp,
                        ),
                    )

            for filename, title, category in gallery_items or ():
                connection.execute(
                    """
                    INSERT OR IGNORE INTO gallery_items (
                        seed_key, title, category, image_path, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 1, ?, ?)
                    """,
                    (f"seed:{filename}", title, category, filename, timestamp, timestamp),
                )

            for index, item in enumerate(news_items or ()):
                connection.execute(
                    """
                    INSERT OR IGNORE INTO news_items (
                        seed_key, category, title, summary, publish_date, badge,
                        image_path, event_id, body_text, facts, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    (
                        f"seed:news:{index}", item["category"], item["title"],
                        item["summary"], item["date"], item["badge"],
                        item["image"], item.get("event_id"),
                        "\n\n".join(item["body"]), item["facts"], timestamp, timestamp,
                    ),
                )

            self._link_existing_bookings(connection, timestamp)
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_active_spot
                ON bookings(event_id, spot_number)
                WHERE spot_number IS NOT NULL AND payment_status != 'cancelled'
                """
            )
            connection.commit()

    @staticmethod
    def _migrate_booking_columns(connection):
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(bookings)")
        }
        additions = {
            "spot_number": "INTEGER",
            "customer_notes": "TEXT NOT NULL DEFAULT ''",
            "payment_reference": "TEXT",
            "updated_at": "TEXT",
            "user_id": "INTEGER",
        }
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(
                    f"ALTER TABLE bookings ADD COLUMN {name} {definition}"
                )
        connection.execute(
            "UPDATE bookings SET updated_at = created_at WHERE updated_at IS NULL"
        )

    @staticmethod
    def _link_existing_bookings(connection, timestamp):
        rows = connection.execute(
            """
            SELECT id, event_id, spot_number
            FROM bookings
            WHERE spot_number IS NOT NULL AND payment_status != 'cancelled'
            ORDER BY id
            """
        ).fetchall()
        for row in rows:
            connection.execute(
                """
                UPDATE event_spots
                SET status = 'occupied', source = 'booking', booking_id = ?, updated_at = ?
                WHERE event_id = ? AND spot_number = ?
                  AND source != 'initial_event_data'
                """,
                (
                    row["id"],
                    timestamp,
                    row["event_id"],
                    row["spot_number"],
                ),
            )

    def list_events(self, active_only=True):
        where = "WHERE e.is_active = 1" if active_only else ""
        with self.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT e.event_id, e.title, e.event_date, e.event_time, e.price,
                       e.quota, e.release_info, e.image, e.is_active, e.updated_at,
                       SUM(CASE WHEN s.status = 'available' THEN 1 ELSE 0 END) AS available
                FROM events e
                LEFT JOIN event_spots s ON s.event_id = e.event_id
                {where}
                GROUP BY e.event_id
                ORDER BY e.rowid ASC
                """
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "title": row["title"],
                "date": row["event_date"],
                "time": row["event_time"],
                "price": row["price"],
                "quota": row["quota"],
                "available": row["available"] or 0,
                "release": row["release_info"],
                "image": row["image"],
                "is_active": bool(row["is_active"]),
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def create_event(self, event, initial_available=None, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        quota = int(event.get("quota", 82))
        available = quota if initial_available is None else int(initial_available)
        if quota < 1 or available < 0 or available > quota:
            raise ValueError("Jumlah lapak tersedia harus berada antara 0 dan kuota.")
        with self.connect() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO events (
                        event_id, title, event_date, event_time, price, quota,
                        release_info, image, is_active, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        event["event_id"], event["title"], event["date"],
                        event["time"], int(event["price"]), quota,
                        event["release"], event["image"], timestamp,
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError("Kode event sudah digunakan.") from error
            occupied_count = quota - available
            occupied_numbers = set(
                sorted(range(1, quota + 1), key=lambda number: ((number * 29 + 17) % (quota + 1), number))[:occupied_count]
            )
            connection.executemany(
                """
                INSERT INTO event_spots (
                    event_id, spot_number, status, source, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        event["event_id"], number,
                        "occupied" if number in occupied_numbers else "available",
                        "initial_event_data" if number in occupied_numbers else "inventory",
                        timestamp,
                    )
                    for number in range(1, quota + 1)
                ],
            )
            self._write_audit(
                connection, actor, "create", "event", event["event_id"],
                f'{event["title"]}; {available}/{quota} tersedia', timestamp,
            )
            connection.commit()
        return event["event_id"]

    def update_event(self, event_id, event, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE events
                SET title = ?, event_date = ?, event_time = ?, price = ?,
                    release_info = ?, image = ?, updated_at = ?
                WHERE event_id = ?
                """,
                (
                    event["title"], event["date"], event["time"],
                    int(event["price"]), event["release"], event["image"],
                    timestamp, event_id,
                ),
            )
            if not cursor.rowcount:
                raise ValueError("Event tidak ditemukan.")
            self._write_audit(
                connection, actor, "update", "event", event_id,
                event["title"], timestamp,
            )
            connection.commit()

    def set_event_active(self, event_id, active, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                "UPDATE events SET is_active = ?, updated_at = ? WHERE event_id = ?",
                (1 if active else 0, timestamp, event_id),
            )
            self._write_audit(
                connection, actor, "activate" if active else "archive", "event",
                event_id, None, timestamp,
            )
            connection.commit()

    def list_gallery_items(self, active_only=True):
        where = "WHERE is_active = 1" if active_only else ""
        with self.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, title, category, image_path, is_active, created_at
                FROM gallery_items {where}
                ORDER BY id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def create_gallery_item(self, title, category, image_path, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO gallery_items (
                    title, category, image_path, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, 1, ?, ?)
                """,
                (title, category, image_path, timestamp, timestamp),
            )
            self._write_audit(
                connection, actor, "create", "gallery", str(cursor.lastrowid),
                title, timestamp,
            )
            connection.commit()
            return cursor.lastrowid

    def set_gallery_active(self, item_id, active, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                "UPDATE gallery_items SET is_active = ?, updated_at = ? WHERE id = ?",
                (1 if active else 0, timestamp, item_id),
            )
            self._write_audit(
                connection, actor, "activate" if active else "archive", "gallery",
                str(item_id), None, timestamp,
            )
            connection.commit()

    def list_news_items(self, active_only=True):
        where = "WHERE is_active = 1" if active_only else ""
        with self.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, category, title, summary, publish_date, badge,
                       image_path, event_id, body_text, facts, is_active, created_at
                FROM news_items {where}
                ORDER BY id DESC
                """
            ).fetchall()
        return [
            {
                "id": row["id"], "category": row["category"],
                "title": row["title"], "summary": row["summary"],
                "date": row["publish_date"], "badge": row["badge"],
                "image": row["image_path"], "event_id": row["event_id"],
                "body": tuple(part for part in row["body_text"].split("\n\n") if part),
                "facts": row["facts"], "is_active": bool(row["is_active"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def create_news_item(self, item, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        body = item["body"]
        body_text = "\n\n".join(body) if not isinstance(body, str) else body
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO news_items (
                    category, title, summary, publish_date, badge, image_path,
                    event_id, body_text, facts, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    item["category"], item["title"], item["summary"], item["date"],
                    item["badge"], item["image"], item.get("event_id") or None,
                    body_text, item["facts"], timestamp, timestamp,
                ),
            )
            self._write_audit(
                connection, actor, "create", "news", str(cursor.lastrowid),
                item["title"], timestamp,
            )
            connection.commit()
            return cursor.lastrowid

    def set_news_active(self, item_id, active, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                "UPDATE news_items SET is_active = ?, updated_at = ? WHERE id = ?",
                (1 if active else 0, timestamp, item_id),
            )
            self._write_audit(
                connection, actor, "activate" if active else "archive", "news",
                str(item_id), None, timestamp,
            )
            connection.commit()

    def list_bookings(self, limit=100, user_id=None):
        with self.connect() as connection:
            where_clause = "WHERE user_id = ?" if user_id is not None else ""
            parameters = (user_id, limit) if user_id is not None else (limit,)
            rows = connection.execute(
                f"""
                SELECT booking_code, event_id, customer_name, customer_phone,
                       customer_notes, ticket_count, payment_method, total_amount,
                       payment_status, spot_number, bait_rule_accepted, created_at,
                       payment_reference, user_id
                FROM bookings
                {where_clause}
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                parameters,
            ).fetchall()
        return [self._booking_dict(row) for row in reversed(rows)]

    def occupied_spots(self, event_id):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT spot_number FROM event_spots
                WHERE event_id = ? AND status = 'occupied'
                """,
                (event_id,),
            ).fetchall()
        return {row["spot_number"] for row in rows}

    def remaining_spots(self, event_id):
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total FROM event_spots
                WHERE event_id = ? AND status = 'available'
                """,
                (event_id,),
            ).fetchone()
        return row["total"] if row else 0

    def create_booking(self, booking):
        timestamp = booking["created_at"]
        with self.connect() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                spot_update = connection.execute(
                    """
                    UPDATE event_spots
                    SET status = 'occupied', source = 'booking', updated_at = ?
                    WHERE event_id = ? AND spot_number = ? AND status = 'available'
                    """,
                    (
                        timestamp,
                        booking["event_id"],
                        booking["spot_number"],
                    ),
                )
                if spot_update.rowcount != 1:
                    raise BookingConflictError(
                        "Lapak baru saja dipesan atau tidak tersedia."
                    )
                cursor = connection.execute(
                    """
                    INSERT INTO bookings (
                        booking_code, event_id, customer_name, customer_phone,
                        customer_notes, ticket_count, payment_method, total_amount,
                        payment_status, spot_number, bait_rule_accepted, created_at,
                        payment_reference, updated_at, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        booking["booking_code"],
                        booking["event_id"],
                        booking["customer_name"],
                        booking["customer_phone"],
                        booking.get("customer_notes", ""),
                        booking["ticket_count"],
                        booking["payment_method"],
                        booking["total_amount"],
                        booking["payment_status"],
                        booking["spot_number"],
                        int(booking["bait_rule_accepted"]),
                        booking["created_at"],
                        booking.get("payment_reference"),
                        timestamp,
                        booking.get("user_id"),
                    ),
                )
                connection.execute(
                    """
                    UPDATE event_spots SET booking_id = ?
                    WHERE event_id = ? AND spot_number = ?
                    """,
                    (
                        cursor.lastrowid,
                        booking["event_id"],
                        booking["spot_number"],
                    ),
                )
                self._write_audit(
                    connection,
                    f'user:{booking.get("user_id") or "legacy"}',
                    "booking_created",
                    "booking",
                    booking["booking_code"],
                    f'{booking["event_id"]}:spot-{booking["spot_number"]}',
                    timestamp,
                )
                connection.commit()
            except BookingConflictError:
                connection.rollback()
                raise
            except sqlite3.IntegrityError as error:
                connection.rollback()
                raise BookingConflictError(
                    "Lapak atau kode booking sudah digunakan."
                ) from error
        return dict(booking)

    def create_user(self, username, password, full_name, phone):
        username = username.strip().lower()
        timestamp = datetime.now().isoformat(timespec="seconds")
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        with self.connect() as connection:
            try:
                cursor = connection.execute(
                    """
                    INSERT INTO users(
                        username, full_name, phone, password_hash, password_salt,
                        avatar_path, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, NULL, 'active', ?, ?)
                    """,
                    (
                        username,
                        full_name.strip(),
                        phone.strip(),
                        password_hash,
                        salt,
                        timestamp,
                        timestamp,
                    ),
                )
                self._write_audit(
                    connection,
                    f"user:{cursor.lastrowid}",
                    "account_created",
                    "user",
                    str(cursor.lastrowid),
                    username,
                    timestamp,
                )
                connection.commit()
            except sqlite3.IntegrityError as error:
                raise AccountExistsError("Username sudah digunakan.") from error
        return self.get_user(cursor.lastrowid)

    def authenticate_user(self, username, password):
        timestamp = datetime.now().isoformat(timespec="seconds")
        normalized_username = username.strip().lower()
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM users
                WHERE username = ? COLLATE NOCASE
                """,
                (normalized_username,),
            ).fetchone()
            success = False
            if row and row["status"] == "active":
                expected = self._hash_password(password, row["password_salt"])
                success = hmac.compare_digest(expected, row["password_hash"])
            connection.execute(
                """
                INSERT INTO login_logs(
                    user_id, username_attempt, success, source, created_at
                ) VALUES (?, ?, ?, 'local_app', ?)
                """,
                (row["id"] if row else None, normalized_username, int(success), timestamp),
            )
            connection.commit()
        return self._user_dict(row) if success else None

    def get_user(self, user_id):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE id = ? AND status = 'active'",
                (user_id,),
            ).fetchone()
        return self._user_dict(row) if row else None

    def list_users(self):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT u.id, u.username, u.full_name, u.phone, u.avatar_path,
                       u.status, u.created_at, u.updated_at,
                       COUNT(DISTINCT b.id) AS booking_count,
                       MAX(CASE WHEN l.success = 1 THEN l.created_at END) AS last_login
                FROM users u
                LEFT JOIN bookings b ON b.user_id = u.id
                LEFT JOIN login_logs l ON l.user_id = u.id
                GROUP BY u.id
                ORDER BY u.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def login_history(self, user_id=None, limit=50):
        with self.connect() as connection:
            if user_id is None:
                rows = connection.execute(
                    """
                    SELECT user_id, username_attempt, success, source, created_at
                    FROM login_logs ORDER BY created_at DESC, id DESC LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT user_id, username_attempt, success, source, created_at
                    FROM login_logs WHERE user_id = ?
                    ORDER BY created_at DESC, id DESC LIMIT ?
                    """,
                    (user_id, limit),
                ).fetchall()
        return [dict(row) for row in rows]

    def update_user(self, user_id, username, full_name, phone, avatar_path=None):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            try:
                connection.execute(
                    """
                    UPDATE users
                    SET username = ?, full_name = ?, phone = ?, avatar_path = ?,
                        updated_at = ?
                    WHERE id = ? AND status = 'active'
                    """,
                    (
                        username.strip().lower(),
                        full_name.strip(),
                        phone.strip(),
                        avatar_path,
                        timestamp,
                        user_id,
                    ),
                )
                self._write_audit(
                    connection,
                    f"user:{user_id}",
                    "profile_updated",
                    "user",
                    str(user_id),
                    username.strip().lower(),
                    timestamp,
                )
                connection.commit()
            except sqlite3.IntegrityError as error:
                raise AccountExistsError("Username sudah digunakan.") from error
        return self.get_user(user_id)

    def change_password(self, user_id, current_password, new_password):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            row = connection.execute(
                "SELECT password_hash, password_salt FROM users WHERE id = ? AND status = 'active'",
                (user_id,),
            ).fetchone()
            if not row:
                raise PasswordError("Akun tidak ditemukan atau tidak aktif.")
            current_hash = self._hash_password(
                current_password, row["password_salt"]
            )
            if not hmac.compare_digest(current_hash, row["password_hash"]):
                raise PasswordError("Password saat ini tidak sesuai.")
            self._set_password(connection, user_id, new_password, timestamp)
            self._write_audit(
                connection,
                f"user:{user_id}",
                "password_changed",
                "user",
                str(user_id),
                "self_service",
                timestamp,
            )
            connection.commit()

    def reset_user_password(self, user_id, new_password):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if not exists:
                raise PasswordError("Akun tidak ditemukan.")
            self._set_password(connection, user_id, new_password, timestamp)
            self._write_audit(
                connection,
                "admin",
                "password_reset",
                "user",
                str(user_id),
                "admin_reset",
                timestamp,
            )
            connection.commit()

    def set_user_status(self, user_id, status):
        if status not in ("active", "inactive"):
            raise ValueError("Status akun tidak valid.")
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                "UPDATE users SET status = ?, updated_at = ? WHERE id = ?",
                (status, timestamp, user_id),
            )
            self._write_audit(
                connection,
                "admin",
                "account_status_changed",
                "user",
                str(user_id),
                status,
                timestamp,
            )
            connection.commit()

    def _set_password(self, connection, user_id, password, timestamp):
        if len(password) < 8:
            raise PasswordError("Password baru minimal 8 karakter.")
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        connection.execute(
            """
            UPDATE users SET password_hash = ?, password_salt = ?, updated_at = ?
            WHERE id = ?
            """,
            (password_hash, salt, timestamp, user_id),
        )

    @staticmethod
    def _hash_password(password, salt):
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), 260_000
        ).hex()

    @staticmethod
    def _user_dict(row):
        return {
            "id": row["id"],
            "username": row["username"],
            "full_name": row["full_name"],
            "phone": row["phone"],
            "avatar_path": row["avatar_path"],
            "status": row["status"],
            "created_at": row["created_at"],
        }

    def cancel_booking(self, booking_code):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            booking = connection.execute(
                """
                SELECT id, event_id, spot_number, payment_status
                FROM bookings WHERE booking_code = ?
                """,
                (booking_code,),
            ).fetchone()
            if not booking:
                connection.rollback()
                raise BookingStateError("Pesanan tidak ditemukan.")
            if booking["payment_status"] == "cancelled":
                connection.rollback()
                raise BookingStateError("Pesanan sudah dibatalkan.")
            if booking["payment_status"] == "paid":
                connection.rollback()
                raise BookingStateError(
                    "Pesanan yang sudah dibayar harus dibatalkan oleh admin."
                )

            connection.execute(
                """
                UPDATE bookings
                SET payment_status = 'cancelled', updated_at = ?
                WHERE id = ?
                """,
                (timestamp, booking["id"]),
            )
            connection.execute(
                """
                UPDATE event_spots
                SET status = 'available', source = 'inventory',
                    booking_id = NULL, updated_at = ?
                WHERE booking_id = ? AND source = 'booking'
                """,
                (timestamp, booking["id"]),
            )
            self._write_audit(
                connection,
                "customer",
                "booking_cancelled",
                "booking",
                booking_code,
                f'{booking["event_id"]}:spot-{booking["spot_number"]}',
                timestamp,
            )
            connection.commit()

    def get_setting(self, key, default=None):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT setting_value FROM app_settings WHERE setting_key = ?",
                (key,),
            ).fetchone()
        return row["setting_value"] if row else default

    def set_settings(self, values, actor="admin"):
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.connect() as connection:
            for key, value in values.items():
                connection.execute(
                    """
                    INSERT INTO app_settings(setting_key, setting_value, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(setting_key) DO UPDATE SET
                        setting_value = excluded.setting_value,
                        updated_at = excluded.updated_at
                    """,
                    (key, str(value), timestamp),
                )
            self._write_audit(
                connection,
                actor,
                "settings_updated",
                "app_settings",
                None,
                ",".join(sorted(values)),
                timestamp,
            )
            connection.commit()

    def operational_status(self):
        defaults = {
            "venue_status": "Buka",
            "fish_mood": "Aktif / nafsu makan",
            "daily_release_kg": "225",
            "operator_note": "Ikan aktif di sisi timur sejak pagi.",
            "opening_hours": "06.00 - 22.00",
        }
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT setting_key, setting_value FROM app_settings
                WHERE setting_key IN (?, ?, ?, ?, ?)
                """,
                tuple(defaults),
            ).fetchall()
        defaults.update({row["setting_key"]: row["setting_value"] for row in rows})
        return defaults

    def backup(self, destination_directory):
        os.makedirs(destination_directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        destination = os.path.join(
            destination_directory, f"adem-ayem-backup-{timestamp}.db"
        )
        with self.connect() as source:
            target = sqlite3.connect(destination)
            try:
                source.backup(target)
                target.commit()
            finally:
                target.close()
        return destination

    @staticmethod
    def _write_audit(
        connection, actor, action, entity_type, entity_id, details, timestamp
    ):
        connection.execute(
            """
            INSERT INTO audit_logs(
                actor, action, entity_type, entity_id, details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (actor, action, entity_type, entity_id, details, timestamp),
        )

    @staticmethod
    def _booking_dict(row):
        booking = dict(row)
        booking["bait_rule_accepted"] = bool(booking["bait_rule_accepted"])
        return booking
