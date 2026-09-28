import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from danzariel_quero.services import files


class TestFileResolution(unittest.TestCase):
    def test_resolves_unicode_audio_filename(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir)
            music_dir = data_dir / "musica"
            music_dir.mkdir()
            filename = 'El Libro de Enoc (Audiolibro Completo) ＂Voz Real Humana＂.mp3'
            audio_file = music_dir / filename
            audio_file.touch()
            test_settings = SimpleNamespace(data_dir=data_dir, areas=["musica"])

            with patch.object(files, "settings", test_settings):
                resolved = files.resolve_existing_file("musica", filename)

        self.assertEqual(resolved, audio_file.resolve())

    def test_does_not_resolve_file_outside_area(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir)
            music_dir = data_dir / "musica"
            music_dir.mkdir()
            (data_dir / "outside.mp3").touch()
            test_settings = SimpleNamespace(data_dir=data_dir, areas=["musica"])

            with patch.object(files, "settings", test_settings):
                with self.assertRaises(HTTPException):
                    files.resolve_existing_file("musica", "../outside.mp3")


if __name__ == "__main__":
    unittest.main()