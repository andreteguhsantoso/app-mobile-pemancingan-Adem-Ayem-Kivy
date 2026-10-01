"""Read-only public Supabase synchronization for the Kivy presentation layer."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime

from media_picker import detect_image_type
from supabase_client import SupabaseError


EVENT_KEY_BY_REMOTE_ID = {
    "00000000-0000-4000-8000-000000000225": "NILA-GP",
    "00000000-0000-4000-8000-000000000200": "NILA-200",
    "00000000-0000-4000-8000-000000000150": "NILA-150",
    "00000000-0000-4000-8000-000000000100": "NILA-100",
}


class PublicBackendSync:
    def __init__(self, client, cache_directory):
        self.client = client
        self.cache_directory = os.fspath(cache_directory)

    def fetch(self):
        events = self.client.public_events()
        gallery = self.client.select(
            "gallery_items",
            {
                "status": "eq.approved",
                "is_active": "eq.true",
                "order": "created_at.desc",
                "limit": "30",
            },
            auth=False,
        )
        news = self.client.select(
            "news_items",
            {"is_active": "eq.true", "order": "published_at.desc", "limit": "20"},
            auth=False,
        )
        leaders = self.client.select(
            "leaderboard_entries",
            {"is_active": "eq.true", "order": "fish_weight_kg.desc", "limit": "30"},
            auth=False,
        )
        venue_rows = self.client.select("venue_settings", {"limit": "1"}, auth=False)

        for item in events:
            item["cached_image"] = self._cache_public_media(
                "content", item.get("image_path")
            )
            try:
                item["occupied_spots"] = self.client.occupied_spots(item["id"])
            except SupabaseError:
                item["occupied_spots"] = set()
        for item in gallery:
            item["cached_image"] = self._cache_private_media(
                "gallery", item.get("image_path")
            )
        for item in news:
            item["cached_image"] = self._cache_public_media(
                "content", item.get("image_path")
            )
        for item in leaders:
            item["cached_image"] = self._cache_public_media(
                "content", item.get("image_path")
            )
        return {
            "events": events,
            "gallery": gallery,
            "news": news,
            "leaders": leaders,
            "venue": venue_rows[0] if venue_rows else None,
        }

    def _cache_public_media(self, bucket, object_path):
        if not object_path:
            return None
        url = self.client.public_media_url(bucket, object_path)
        return self._download(url, f"{bucket}/{object_path}")

    def _cache_private_media(self, bucket, object_path):
        if not object_path:
            return None
        try:
            url = self.client.signed_media_url(bucket, object_path, 900)
        except SupabaseError:
            return None
        return self._download(url, f"{bucket}/{object_path}")

    def _download(self, url, cache_key):
        digest = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        os.makedirs(self.cache_directory, exist_ok=True)
        for extension in (".jpg", ".png", ".webp"):
            existing = os.path.join(self.cache_directory, digest + extension)
            if os.path.isfile(existing) and os.path.getsize(existing) > 0:
                return existing
        try:
            response = self.client.http.request("GET", url, timeout=45)
        except Exception:
            return None
        if response.status_code >= 400 or not response.content:
            return None
        if len(response.content) > 5 * 1024 * 1024:
            return None
        image_type = detect_image_type(response.content[:16])
        extension = {"jpeg": ".jpg", "png": ".png", "webp": ".webp"}.get(
            image_type
        )
        if not extension:
            return None
        destination = os.path.join(self.cache_directory, digest + extension)
        temporary = destination + ".part"
        try:
            with open(temporary, "wb") as media_file:
                media_file.write(response.content)
            os.replace(temporary, destination)
            return destination
        except OSError:
            try:
                os.remove(temporary)
            except OSError:
                pass
            return None


def parse_timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
