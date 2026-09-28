import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from infra import repositories


class TestInfraRepositories(unittest.TestCase):
    def test_read_write_text_and_stats(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "doc.md"
            repositories.write_text(path, "# Hola\nContenido\n")
            self.assertEqual(repositories.read_text(path), "# Hola\nContenido\n")

            stats = repositories.doc_stats(path)
            self.assertTrue(stats["exists"])
            self.assertEqual(stats["lines"], 2)
            self.assertEqual(stats["headings"], 1)

    def test_split_sections_and_layers(self):
        text = "# Titulo\nLinea 1\n## Subtitulo\nLinea 2\n---\nFinal"
        sections = repositories.split_sections(text)
        self.assertEqual(sections[0][0], "Titulo")
        self.assertIn("Linea 1", sections[0][1])

        layers = repositories.split_layers(text)
        self.assertGreaterEqual(len(layers), 1)
        self.assertEqual(layers[0].title, "Titulo")

        layer_text = repositories.layer_text(text, layers[0])
        self.assertIn("# Titulo", layer_text)

        replaced = repositories.replace_layer(text, layers[0], "# Nuevo\nTexto")
        self.assertIn("# Nuevo", replaced)

    def test_backup_document(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.txt"
            repositories.write_text(path, "contenido\n")
            target_dir = Path(tmp_dir) / "backups"
            backup_path = repositories.backup_document(path, target_dir)
            self.assertTrue(backup_path.exists())
            self.assertEqual(repositories.read_text(backup_path), "contenido\n")

    def test_load_and_append_candle(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "candles.csv"
            repositories.append_candle(1.0, 2.0, 0.5, 1.5, csv_path)
            df = repositories.load_raw_df(csv_path)
            self.assertFalse(df.empty)
            self.assertEqual(list(df.columns), ["timestamp", "open", "high", "low", "close"])
            self.assertEqual(float(df.iloc[0]["open"]), 1.0)

    def test_append_json_entry_creates_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_path = Path(tmp_dir) / "log.json"
            repositories.append_json_entry(json_path, {"a": 1})
            repositories.append_json_entry(json_path, {"b": 2})
            self.assertTrue(json_path.exists())
            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(data, [{"a": 1}, {"b": 2}])

    def test_prepare_df_for_table_with_invalid_columns(self):
        df = pd.DataFrame({
            "Open": ["1.0", "2.5"],
            "High": ["1.2", "2.7"],
            "Low": ["0.8", "2.4"],
            "Close": ["1.5", "2.7"],
            "other": ["x", "y"],
        })
        prepared = repositories.prepare_df_for_table(df)
        self.assertIn("tipo_vela", prepared.columns)
        self.assertEqual(prepared.iloc[0]["tipo_vela"], "Entrada")
