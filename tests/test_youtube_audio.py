import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from youtube_audio import _download_error_message, audio_output_dir, build_download_options, is_youtube_url


class TestYoutubeAudio(unittest.TestCase):
    def test_defaults_output_to_icloud_sonido_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            with patch.dict(os.environ, {"DQ_AUDIO_OUTPUT_DIR": ""}):
                with patch("youtube_audio.Path.home", return_value=home):
                    target = audio_output_dir()
                    self.assertTrue(target.is_dir())

        self.assertEqual(target, home / "iCloudDrive" / "sonidos")

    def test_uses_configured_audio_output_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            configured_dir = Path(tmp_dir) / "custom-audio"
            with patch.dict(os.environ, {"DQ_AUDIO_OUTPUT_DIR": str(configured_dir)}):
                target = audio_output_dir()

        self.assertEqual(target, configured_dir)

    def test_accepts_youtube_urls_only(self):
        self.assertTrue(is_youtube_url("https://www.youtube.com/watch?v=abc"))
        self.assertTrue(is_youtube_url("https://youtu.be/abc"))
        self.assertFalse(is_youtube_url("https://example.com/video"))
        self.assertFalse(is_youtube_url("youtube.com/watch?v=abc"))

    def test_builds_mp3_options_for_output_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(
                os.environ,
                {
                    "YOUTUBE_COOKIES_FROM_BROWSER": "",
                    "YOUTUBE_COOKIES_BROWSER_PROFILE": "",
                    "YOUTUBE_COOKIES_FILE": "",
                },
            ):
                options = build_download_options(Path(tmp_dir), "192")

        self.assertEqual(options["format"], "bestaudio/best")
        self.assertTrue(options["noplaylist"])
        processor = options["postprocessors"][0]
        self.assertEqual(processor["preferredcodec"], "mp3")
        self.assertEqual(processor["preferredquality"], "192")

    def test_uses_browser_cookies_when_configured(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(
                os.environ,
                {
                    "YOUTUBE_COOKIES_FROM_BROWSER": "chrome",
                    "YOUTUBE_COOKIES_BROWSER_PROFILE": "",
                    "YOUTUBE_COOKIES_FILE": "",
                },
            ):
                options = build_download_options(Path(tmp_dir), "128")

        self.assertEqual(options["cookiesfrombrowser"], ("chrome", None))

    def test_uses_cookie_file_when_configured(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = Path(tmp_dir) / "cookies.txt"
            with patch.dict(
                os.environ,
                {
                    "YOUTUBE_COOKIES_FROM_BROWSER": "",
                    "YOUTUBE_COOKIES_BROWSER_PROFILE": "",
                    "YOUTUBE_COOKIES_FILE": str(cookie_file),
                },
            ):
                options = build_download_options(Path(tmp_dir), "128")

        self.assertEqual(options["cookiefile"], str(cookie_file))

    def test_translates_youtube_bot_check_error_without_ansi_codes(self):
        message = _download_error_message(
            RuntimeError("\x1b[0;31mERROR:\x1b[0m Sign in to confirm you’re not a bot")
        )

        self.assertIn("YOUTUBE_COOKIES_FROM_BROWSER=chrome", message)
        self.assertNotIn("\x1b[", message)

    def test_explains_chrome_cookie_database_lock(self):
        message = _download_error_message(
            RuntimeError("ERROR: Could not copy Chrome cookie database. See issue #7271")
        )

        self.assertIn("Cierra Chrome por completo", message)
        self.assertIn("chrome.exe", message)
        self.assertIn("YOUTUBE_COOKIES_FILE=", message)
        self.assertIn("formato Netscape", message)


if __name__ == "__main__":
    unittest.main()