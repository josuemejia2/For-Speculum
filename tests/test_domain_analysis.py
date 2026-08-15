from __future__ import annotations

import csv
import tempfile
from pathlib import Path
from unittest import TestCase

from domain.analysis import ResultadoAnalisis, analizar_mercado, calcular_indicadores, cargar_velas


class TestDomainAnalysis(TestCase):
    def test_cargar_velas_and_calcular_indicadores(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "sample.csv"
            rows = [
                {"timestamp": "2026-01-01 00:00:00", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0},
                {"timestamp": "2026-01-01 00:05:00", "open": 105.0, "high": 115.0, "low": 100.0, "close": 110.0},
                {"timestamp": "2026-01-01 00:10:00", "open": 110.0, "high": 120.0, "low": 105.0, "close": 118.0},
            ]
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerows(rows)

            df = cargar_velas(csv_path)
            self.assertEqual(len(df), 3)
            self.assertIn("timestamp", df.columns)

            indicators = calcular_indicadores(df)
            self.assertIn("EMA_3", indicators.columns)
            self.assertIn("PSAR", indicators.columns)
            self.assertIn("MACD_HIST", indicators.columns)

    def test_analizar_mercado_returns_resultado(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "sample.csv"
            rows = [
                {"timestamp": "2026-01-01 00:00:00", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0},
                {"timestamp": "2026-01-01 00:05:00", "open": 105.0, "high": 115.0, "low": 100.0, "close": 110.0},
                {"timestamp": "2026-01-01 00:10:00", "open": 110.0, "high": 120.0, "low": 105.0, "close": 118.0},
            ]
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerows(rows)

            resultado = analizar_mercado(csv_path=csv_path)
            self.assertIsInstance(resultado, ResultadoAnalisis)
            self.assertIn(resultado.signal, {"LONG", "SHORT", "NO_TRADE"})
            self.assertIsInstance(resultado.confidence, int)
