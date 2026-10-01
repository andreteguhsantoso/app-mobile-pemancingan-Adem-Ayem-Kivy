import json
import os
import sys
import tempfile


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault("KIVY_HOME", os.path.join(PROJECT_DIR, ".kivy"))

from media_picker import ImageSelectionError, copy_local_image, detect_image_type
from supabase_client import SupabaseClient, SupabaseSettings


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.content = json.dumps(payload).encode("utf-8") if payload is not None else b""
        self.text = self.content.decode("utf-8")

    def json(self):
        return self._payload


class FakeHTTP:
    def __init__(self):
        self.calls = []

    def request(self, method, url, headers=None, **kwargs):
        self.calls.append((method, url, headers or {}, kwargs))
        if "/auth/v1/token" in url:
            return FakeResponse(
                200,
                {
                    "access_token": "access-test",
                    "refresh_token": "refresh-test",
                    "expires_in": 3600,
                    "user": {"id": "user-1", "email": "budi@example.com"},
                },
            )
        if "/rest/v1/profiles" in url:
            return FakeResponse(
                200,
                [
                    {
                        "id": "user-1",
                        "username": "budi_nila",
                        "full_name": "Budi Nila",
                        "phone": "081234567890",
                        "role": "customer",
                        "status": "active",
                    }
                ],
            )
        return FakeResponse(200, {})


def run_test():
    assert detect_image_type(b"\xff\xd8\xff\xe0") == "jpeg"
    assert detect_image_type(b"\x89PNG\r\n\x1a\nrest") == "png"
    assert detect_image_type(b"RIFF1234WEBPrest") == "webp"
    assert detect_image_type(b"not-an-image") is None

    with tempfile.TemporaryDirectory() as temporary:
        source = os.path.join(temporary, "camera-photo.bin")
        with open(source, "wb") as image_file:
            image_file.write(b"\xff\xd8\xff" + b"photo" * 100)
        copied = copy_local_image(
            source, os.path.join(temporary, "private"), "gallery", 1024 * 1024
        )
        assert copied.endswith(".jpg")
        assert os.path.isfile(copied)

        try:
            copy_local_image(source, temporary, "too-small", 8)
        except ImageSelectionError:
            pass
        else:
            raise AssertionError("Oversized images must be rejected")

        settings = SupabaseSettings(
            url="https://kivy-test.supabase.co",
            publishable_key="sb_publishable_test",
        )
        fake_http = FakeHTTP()
        client = SupabaseClient(settings, temporary, http=fake_http)
        client.sign_in("budi@example.com", "password-kuat")
        assert client.signed_in
        assert client.user_id == "user-1"
        assert client.current_profile()["username"] == "budi_nila"
        assert os.path.isfile(client.session_path)
        assert all(
            call[2]["apikey"] == "sb_publishable_test" for call in fake_http.calls
        )
        assert any(
            call[2]["Authorization"] == "Bearer access-test"
            for call in fake_http.calls
            if "/rest/v1/" in call[1]
        )

    print("ONLINE_FOUNDATION_OK")


if __name__ == "__main__":
    run_test()
