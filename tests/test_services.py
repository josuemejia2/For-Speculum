import json
import tempfile
import unittest
from pathlib import Path

from services import (
    add_candle,
    append_json_entry,
    backup_document,
    document_stats,
    layer_text,
    load_market_df,
    read_document,
    replace_document_layer,
    split_document_sections,
    split_document_layers,
    write_document,
)


class TestServices(unittest.TestCase):
    def test_document_service_wrappers(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            path = tmp_path / "doc.md"
            write_document(path, "# Hola\nMundo\n")
            self.assertEqual(read_document(path), "# Hola\nMundo\n")
            stats = document_stats(path)
            self.assertTrue(stats["exists"])

            sections = split_document_sections(read_document(path))
            self.assertEqual(sections[0][0], "Hola")

            layers = split_document_layers(read_document(path))
            self.assertEqual(layers[0].title, "Hola")
            self.assertTrue(layer_text(read_document(path), layers[0]))

            backup_dir = tmp_path / "backups"
            backup_path = backup_document(path, backup_dir)
            self.assertTrue(backup_path.exists())

    def test_market_service_wrappers(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "candles.csv"
            add_candle(1.0, 2.0, 0.5, 1.5, csv_path)
            df = load_market_df(csv_path)
            self.assertFalse(df.empty)
            self.assertEqual(list(df.columns)[0], "timestamp")

    def test_append_json_entry_service_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_path = Path(tmp_dir) / "log.json"
            append_json_entry(json_path, {"x": 1})
            append_json_entry(json_path, {"y": 2})
            self.assertTrue(json_path.exists())
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), [{"x": 1}, {"y": 2}])
