"""Small Supabase HTTP client for the Kivy/Android application.

The mobile app intentionally uses only a Supabase publishable key.  Database
authorization is enforced by the RLS policies in ``supabase_kivy/migrations``;
secret and service-role keys must never be bundled into the APK.
"""

from __future__ import annotations

import json
import mimetypes
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:  # Keeps local UI usable before optional deps are installed.
    requests = None


class SupabaseError(RuntimeError):
    """A safe, user-displayable error returned by Supabase."""

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


@dataclass(frozen=True)
class SupabaseSettings:
    url: str = ""
    publishable_key: str = field(default="", repr=False)

    @property
    def configured(self):
        return bool(self.url and self.publishable_key)

    @classmethod
    def load(cls, *config_paths):
        """Load runtime config, with environment variables taking precedence."""

        payload = {}
        for path in config_paths:
            if path and os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as config_file:
                        candidate = json.load(config_file)
                    if isinstance(candidate, dict):
                        payload = candidate
                        break
                except (OSError, ValueError):
                    continue

        url = os.environ.get("ADEM_AYEM_SUPABASE_URL", payload.get("url", ""))
        key = os.environ.get(
            "ADEM_AYEM_SUPABASE_PUBLISHABLE_KEY",
            payload.get("publishable_key", ""),
        )
        url = str(url).strip().rstrip("/")
        key = str(key).strip()
        if url and not url.startswith("https://"):
            return cls()
        if key and not (key.startswith("sb_publishable_") or key.startswith("eyJ")):
            return cls()
        return cls(url=url, publishable_key=key)


class SupabaseClient:
    """Supabase Auth, PostgREST, RPC, and Storage over HTTPS."""

    def __init__(self, settings, state_directory, http=None, timeout=25):
        self.settings = settings
        self.state_directory = os.fspath(state_directory)
        self.session_path = os.path.join(
            self.state_directory, "supabase-session.json"
        )
        self.http = http or (requests.Session() if requests else None)
        self.timeout = timeout
        self._lock = threading.RLock()
        self.session = self._load_session()

    @property
    def configured(self):
        return self.settings.configured and self.http is not None

    @property
    def signed_in(self):
        return bool(self.session.get("access_token"))

    @property
    def user(self):
        return self.session.get("user")

    @property
    def user_id(self):
        return (self.user or {}).get("id")

    def _require_config(self):
        if not self.configured:
            raise SupabaseError("Backend online belum dikonfigurasi pada aplikasi.")

    def _load_session(self):
        try:
            with open(self.session_path, "r", encoding="utf-8") as session_file:
                payload = json.load(session_file)
            return payload if isinstance(payload, dict) else {}
        except (OSError, ValueError):
            return {}

    def _save_session(self):
        os.makedirs(self.state_directory, exist_ok=True)
        temporary = f"{self.session_path}.tmp"
        with open(temporary, "w", encoding="utf-8") as session_file:
            json.dump(self.session, session_file, separators=(",", ":"))
        os.replace(temporary, self.session_path)

    def _clear_session(self):
        self.session = {}
        try:
            os.remove(self.session_path)
        except FileNotFoundError:
            pass

    def _headers(self, authenticated=True, extra=None):
        token = self.session.get("access_token") if authenticated else None
        headers = {
            "apikey": self.settings.publishable_key,
            "Authorization": f"Bearer {token or self.settings.publishable_key}",
            "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    @staticmethod
    def _decode_response(response):
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def _error_message(payload, fallback):
        if isinstance(payload, dict):
            return str(
                payload.get("msg")
                or payload.get("message")
                or payload.get("error_description")
                or payload.get("error")
                or fallback
            )
        return fallback

    def _perform(self, method, url, headers, **kwargs):
        try:
            response = self.http.request(
                method, url, headers=headers, timeout=self.timeout, **kwargs
            )
        except Exception as exc:
            raise SupabaseError(
                "Tidak dapat terhubung ke database online. Periksa internet lalu coba lagi."
            ) from exc
        payload = self._decode_response(response)
        if response.status_code >= 400:
            raise SupabaseError(
                self._error_message(payload, "Permintaan ke backend ditolak."),
                response.status_code,
                payload,
            )
        return payload

    def _capture_auth_payload(self, payload):
        if not isinstance(payload, dict):
            return payload
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")
        if not access_token:
            return payload
        expires_at = payload.get("expires_at")
        if not expires_at:
            expires_at = int(time.time()) + int(payload.get("expires_in", 3600))
        self.session = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(expires_at),
            "user": payload.get("user") or self.session.get("user"),
        }
        self._save_session()
        return payload

    def sign_up(self, email, password, username, full_name, phone):
        self._require_config()
        payload = self._perform(
            "POST",
            f"{self.settings.url}/auth/v1/signup",
            self._headers(authenticated=False, extra={"Content-Type": "application/json"}),
            json={
                "email": email.strip().lower(),
                "password": password,
                "data": {
                    "username": username.strip(),
                    "full_name": full_name.strip(),
                    "phone": phone.strip(),
                },
            },
        )
        return self._capture_auth_payload(payload)

    def sign_in(self, email, password):
        self._require_config()
        payload = self._perform(
            "POST",
            f"{self.settings.url}/auth/v1/token?grant_type=password",
            self._headers(authenticated=False, extra={"Content-Type": "application/json"}),
            json={"email": email.strip().lower(), "password": password},
        )
        return self._capture_auth_payload(payload)

    def refresh_session(self):
        self._require_config()
        refresh_token = self.session.get("refresh_token")
        if not refresh_token:
            self._clear_session()
            raise SupabaseError("Sesi telah berakhir. Silakan masuk kembali.")
        payload = self._perform(
            "POST",
            f"{self.settings.url}/auth/v1/token?grant_type=refresh_token",
            self._headers(authenticated=False, extra={"Content-Type": "application/json"}),
            json={"refresh_token": refresh_token},
        )
        return self._capture_auth_payload(payload)

    def sign_out(self):
        if self.configured and self.signed_in:
            try:
                self._perform(
                    "POST",
                    f"{self.settings.url}/auth/v1/logout",
                    self._headers(),
                )
            finally:
                self._clear_session()
        else:
            self._clear_session()

    def _ensure_fresh_session(self):
        expires_at = int(self.session.get("expires_at") or 0)
        if self.signed_in and expires_at and expires_at <= int(time.time()) + 30:
            self.refresh_session()

    def request(self, method, path, params=None, body=None, headers=None, auth=True):
        self._require_config()
        with self._lock:
            if auth:
                self._ensure_fresh_session()
            return self._perform(
                method,
                f"{self.settings.url}{path}",
                self._headers(
                    authenticated=auth,
                    extra={"Content-Type": "application/json", **(headers or {})},
                ),
                params=params,
                json=body,
            )

    def select(self, table, params=None, auth=False):
        query = {"select": "*", **(params or {})}
        return self.request("GET", f"/rest/v1/{quote(table)}", query, auth=auth)

    def current_profile(self):
        if not self.user_id:
            raise SupabaseError("Silakan masuk untuk membuka profil online.")
        rows = self.select(
            "profiles", {"id": f"eq.{self.user_id}", "limit": "1"}, auth=True
        )
        if not rows:
            raise SupabaseError("Profil online belum tersedia.")
        return rows[0]

    def public_events(self):
        return self.select(
            "events",
            {"status": "eq.published", "order": "starts_at.asc"},
            auth=False,
        )

    def occupied_spots(self, event_id):
        rows = self.rpc(
            "get_occupied_spots", {"p_event_id": event_id}, auth=False
        )
        return {
            int(row["spot_number"])
            for row in (rows or [])
            if isinstance(row, dict) and row.get("spot_number") is not None
        }

    def occupied_spots(self, event_id):
        rows = self.rpc(
            "get_occupied_spots", {"p_event_id": event_id}, auth=False
        )
        return {
            int(row["spot_number"])
            for row in (rows or [])
            if isinstance(row, dict) and row.get("spot_number") is not None
        }

    def reserve_ticket(
        self, event_id, spot_number, participant_name, participant_phone, notes=""
    ):
        from uuid import uuid4

        payload = self.rpc(
            "reserve_ticket",
            {
                "p_event_id": event_id,
                "p_spot_number": int(spot_number),
                "p_participant_name": participant_name.strip(),
                "p_participant_phone": participant_phone.strip(),
                "p_notes": notes.strip() or None,
                "p_request_id": str(uuid4()),
            },
        )
        if isinstance(payload, list) and payload:
            return payload[0]
        return payload

    def insert(self, table, values):
        return self.request(
            "POST",
            f"/rest/v1/{quote(table)}",
            body=values,
            headers={"Prefer": "return=representation"},
        )

    def update(self, table, values, params):
        return self.request(
            "PATCH",
            f"/rest/v1/{quote(table)}",
            params=params,
            body=values,
            headers={"Prefer": "return=representation"},
        )

    def rpc(self, function_name, arguments=None, auth=True):
        return self.request(
            "POST",
            f"/rest/v1/rpc/{quote(function_name)}",
            body=arguments or {},
            auth=auth,
        )

    def upload_file(self, bucket, object_path, local_path, upsert=False):
        self._require_config()
        self._ensure_fresh_session()
        object_path = "/".join(quote(part, safe="") for part in object_path.split("/"))
        mime_type = mimetypes.guess_type(local_path)[0] or "application/octet-stream"
        with open(local_path, "rb") as media_file:
            try:
                response = self.http.request(
                    "POST",
                    f"{self.settings.url}/storage/v1/object/{quote(bucket)}/{object_path}",
                    headers=self._headers(
                        extra={
                            "Content-Type": mime_type,
                            "x-upsert": "true" if upsert else "false",
                        }
                    ),
                    data=media_file,
                    timeout=max(self.timeout, 60),
                )
            except Exception as exc:
                raise SupabaseError("Unggah foto gagal. Periksa koneksi internet.") from exc
        payload = self._decode_response(response)
        if response.status_code >= 400:
            raise SupabaseError(
                self._error_message(payload, "Foto ditolak oleh penyimpanan online."),
                response.status_code,
                payload,
            )
        return payload

    def signed_media_url(self, bucket, object_path, expires_in=3600):
        object_path = "/".join(quote(part, safe="") for part in object_path.split("/"))
        payload = self.request(
            "POST",
            f"/storage/v1/object/sign/{quote(bucket)}/{object_path}",
            body={"expiresIn": int(expires_in)},
        )
        signed = payload.get("signedURL") or payload.get("signedUrl")
        if not signed:
            raise SupabaseError("URL foto tidak diterima dari penyimpanan online.")
        return signed if signed.startswith("http") else f"{self.settings.url}/storage/v1{signed}"

    def public_media_url(self, bucket, object_path):
        encoded_path = "/".join(
            quote(part, safe="") for part in object_path.split("/")
        )
        return (
            f"{self.settings.url}/storage/v1/object/public/"
            f"{quote(bucket, safe='')}/{encoded_path}"
        )


def run_async(operation, on_success=None, on_error=None, dispatch=None):
    """Run a blocking backend operation away from the Kivy UI thread."""

    dispatch = dispatch or (lambda callback: callback())

    def worker():
        try:
            result = operation()
        except Exception as exc:
            if on_error:
                dispatch(lambda error=exc: on_error(error))
        else:
            if on_success:
                dispatch(lambda value=result: on_success(value))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return thread
