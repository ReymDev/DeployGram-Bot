from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.utils.callbacks import decode_path, encode_path
from services.archive import ArchiveError, safe_extract_zip
from services.project import ProjectService


class PathValidationTests(unittest.TestCase):
    def test_valid_container_paths(self):
        self.assertEqual(ProjectService._validate_path(None, "/app/main.py"), "/app/main.py")
        self.assertEqual(ProjectService._validate_path(None, "main.py"), "/app/main.py")
        self.assertEqual(ProjectService._validate_path(None, "/app", allow_root=True), "/app")

    def test_path_traversal_is_rejected(self):
        for bad in ("/app/../etc/passwd", "../x", "/etc/passwd", "C:/x"):
            with self.subTest(path=bad):
                with self.assertRaises(ValueError):
                    ProjectService._validate_path(None, bad)


class ArchiveTests(unittest.TestCase):
    def test_safe_archive_is_extracted(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("app/main.py", "print('ok')")
            safe_extract_zip(archive.getvalue(), tmp)
            self.assertTrue((Path(tmp) / "app" / "main.py").is_file())

    def test_traversal_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("../evil.py", "bad")
            with self.assertRaises(ArchiveError):
                safe_extract_zip(archive.getvalue(), tmp)

    def test_symlink_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w") as zf:
                info = zipfile.ZipInfo("link")
                info.external_attr = 0o120777 << 16
                zf.writestr(info, "/etc/passwd")
            with self.assertRaises(ArchiveError):
                safe_extract_zip(archive.getvalue(), tmp)


class CallbackTokenTests(unittest.TestCase):
    def test_path_tokens_roundtrip(self):
        paths = [
            "/app/main.py",
            "/app/very/long/" + "nested/" * 30 + "file.py",
        ]
        for path in paths:
            token = encode_path(path)
            self.assertLessEqual(len(token), 30)
            self.assertEqual(decode_path(token), path)
            self.assertLessEqual(
                len(f"file_del_confirm_1234567890_{token}"), 64
            )


if __name__ == "__main__":
    unittest.main()
