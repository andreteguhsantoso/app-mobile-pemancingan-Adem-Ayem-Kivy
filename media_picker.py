"""Cross-platform image selection helpers.

Android does not expose gallery images as ordinary filesystem paths.  The
``AndroidImagePicker`` below opens Android's Storage Access Framework and
copies the selected ``content://`` URI into the application's private storage.
Desktop callers keep using Kivy's file chooser and share the same validation
code.
"""

from __future__ import annotations

import os
import shutil
import threading
from pathlib import Path
from uuid import uuid4

from kivy.clock import Clock


SUPPORTED_IMAGE_TYPES = {
    "jpeg": ".jpg",
    "png": ".png",
    "webp": ".webp",
}


class ImageSelectionError(ValueError):
    """Raised when a selected file cannot be used as an application image."""


def detect_image_type(header: bytes) -> str | None:
    """Return a supported image type from its binary signature."""

    if header.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "webp"
    return None


def _copy_validated_stream(source, destination_directory, prefix, max_bytes):
    """Copy an image stream safely and return its private local path."""

    destination_directory = os.fspath(destination_directory)
    os.makedirs(destination_directory, exist_ok=True)
    temporary_path = os.path.join(destination_directory, f".{prefix}-{uuid4().hex}.part")
    total = 0
    header = b""
    try:
        with open(temporary_path, "wb") as output:
            while True:
                chunk = source.read(128 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ImageSelectionError(
                        f"Ukuran foto melebihi batas {max_bytes // (1024 * 1024)} MB."
                    )
                if len(header) < 16:
                    header = (header + chunk)[:16]
                output.write(chunk)
        image_type = detect_image_type(header)
        if image_type is None:
            raise ImageSelectionError(
                "Format foto tidak didukung. Gunakan JPG, PNG, atau WEBP."
            )
        destination = os.path.join(
            destination_directory,
            f"{prefix}-{uuid4().hex}{SUPPORTED_IMAGE_TYPES[image_type]}",
        )
        os.replace(temporary_path, destination)
        return destination
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def copy_local_image(source_path, destination_directory, prefix, max_bytes):
    """Validate and copy a desktop-selected image into private app storage."""

    source_path = os.fspath(source_path)
    if not os.path.isfile(source_path):
        raise ImageSelectionError("File foto tidak ditemukan.")
    with open(source_path, "rb") as source:
        return _copy_validated_stream(
            source, destination_directory, prefix, max_bytes
        )


class AndroidImagePicker:
    """Open Android's system image picker and copy the selected content URI."""

    REQUEST_CODE = 4317

    def __init__(self):
        self._activity_api = None
        self._success_callback = None
        self._error_callback = None
        self._destination_directory = None
        self._prefix = "image"
        self._max_bytes = 10 * 1024 * 1024
        self._active = False

    def pick(
        self,
        destination_directory,
        prefix,
        max_bytes,
        on_success,
        on_error,
    ):
        """Launch the Android picker. Returns ``True`` when it was opened."""

        if self._active:
            on_error("Pemilih foto masih terbuka.")
            return False
        try:
            from android import activity
            from jnius import autoclass

            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("image/*")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

            self._activity_api = activity
            self._destination_directory = os.fspath(destination_directory)
            self._prefix = prefix
            self._max_bytes = int(max_bytes)
            self._success_callback = on_success
            self._error_callback = on_error
            self._active = True
            activity.bind(on_activity_result=self._on_activity_result)
            PythonActivity.mActivity.startActivityForResult(
                intent, self.REQUEST_CODE
            )
            return True
        except Exception as exc:
            self._finish()
            on_error(f"Galeri Android tidak dapat dibuka: {exc}")
            return False

    def _on_activity_result(self, request_code, result_code, intent):
        if request_code != self.REQUEST_CODE:
            return
        success_callback = self._success_callback
        error_callback = self._error_callback
        destination_directory = self._destination_directory
        prefix = self._prefix
        max_bytes = self._max_bytes
        self._finish()

        # RESULT_CANCELED is a normal user action; there is nothing to report.
        if result_code != -1 or intent is None:
            return
        uri = intent.getData()
        if uri is None:
            if error_callback:
                error_callback("Foto tidak dapat dibaca dari galeri.")
            return

        threading.Thread(
            target=self._copy_uri,
            args=(
                uri,
                destination_directory,
                prefix,
                max_bytes,
                success_callback,
                error_callback,
            ),
            daemon=True,
        ).start()

    @staticmethod
    def _copy_uri(
        uri,
        destination_directory,
        prefix,
        max_bytes,
        success_callback,
        error_callback,
    ):
        descriptor = None
        stream = None
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            resolver = PythonActivity.mActivity.getContentResolver()
            descriptor = resolver.openFileDescriptor(uri, "r")
            if descriptor is None:
                raise ImageSelectionError("Android tidak dapat membuka foto tersebut.")
            file_descriptor = descriptor.detachFd()
            descriptor = None
            stream = os.fdopen(file_descriptor, "rb")
            local_path = _copy_validated_stream(
                stream, destination_directory, prefix, max_bytes
            )
            Clock.schedule_once(
                lambda _dt, path=local_path: success_callback(path), 0
            )
        except Exception as exc:
            message = str(exc) or "Foto gagal disalin dari galeri."
            if error_callback:
                Clock.schedule_once(
                    lambda _dt, error=message: error_callback(error), 0
                )
        finally:
            if stream is not None:
                stream.close()
            if descriptor is not None:
                descriptor.close()

    def _finish(self):
        if self._activity_api is not None:
            try:
                self._activity_api.unbind(on_activity_result=self._on_activity_result)
            except Exception:
                pass
        self._activity_api = None
        self._success_callback = None
        self._error_callback = None
        self._destination_directory = None
        self._active = False


def image_display_name(path):
    """Return a short label suitable for Kivy status text."""

    return Path(path).name
