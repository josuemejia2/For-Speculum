from unittest import TestCase

from quero.brain.classifier import RuleBasedClassifier


class QueroBrainClassifierTests(TestCase):
    def setUp(self):
        self.classifier = RuleBasedClassifier()

    def test_image_file_goes_to_images(self):
        result = self.classifier.predict("foto_familia.png", "image/png")

        self.assertEqual(result.category, "imagenes")
        self.assertEqual(result.folder, "/imagenes")
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 100)
        self.assertIn("type:image", result.signals)

    def test_markdown_quero_file_goes_to_knowledge(self):
        result = self.classifier.predict(
            "manual_quero.md",
            "text/markdown",
            "Manual del protocolo DANZARIEL QUERO y paradigma central.",
        )

        self.assertEqual(result.category, "knowledge")
        self.assertEqual(result.folder, "/knowledge")
        self.assertTrue(any(signal.startswith("keyword:") for signal in result.signals))

    def test_trading_image_goes_to_trading_images(self):
        result = self.classifier.predict("grafico_bitcoin.png", "image/png")

        self.assertEqual(result.category, "trading")
        self.assertEqual(result.folder, "/trading/imagenes")
        self.assertIn("combined:image+trading", result.signals)

    def test_unknown_file_gets_neutral_document_suggestion(self):
        result = self.classifier.predict("archivo_sin_contexto.bin", "application/octet-stream")

        self.assertEqual(result.category, "documentos")
        self.assertEqual(result.folder, "/documentos")
        self.assertIn("fallback:neutral", result.signals)
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 100)
