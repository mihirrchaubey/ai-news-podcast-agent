import tempfile
import unittest
import wave
from pathlib import Path

from ai_news_podcast import config
from ai_news_podcast.tools.audio import wave_file
from ai_news_podcast.tools.financial import get_financial_context
from ai_news_podcast.tools.storage import save_news_to_markdown


class TestFinancial(unittest.TestCase):
    def test_all_placeholder_tickers(self):
        out = get_financial_context(["N/A", "na", ""])
        self.assertTrue(all(v == "No financial data" for v in out.values()))

    def test_empty_list(self):
        self.assertEqual(get_financial_context([]), {})


class TestStorage(unittest.TestCase):
    def setUp(self):
        self._orig = config.OUTPUT_DIR
        self._tmp = tempfile.TemporaryDirectory()
        config.OUTPUT_DIR = Path(self._tmp.name)

    def tearDown(self):
        config.OUTPUT_DIR = self._orig
        self._tmp.cleanup()

    def test_saves_and_adds_extension(self):
        res = save_news_to_markdown("report", "# hi")
        self.assertEqual(res["status"], "success")
        self.assertEqual((config.OUTPUT_DIR / "report.md").read_text(), "# hi")

    def test_blocks_path_traversal(self):
        save_news_to_markdown("../../evil.md", "x")
        self.assertTrue((config.OUTPUT_DIR / "evil.md").exists())


class TestAudio(unittest.TestCase):
    def test_wave_file_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "t.wav"
            wave_file(path, b"\x00\x00" * 24000)  # 1 second of silence
            with wave.open(str(path)) as wf:
                self.assertEqual(wf.getframerate(), 24000)
                self.assertEqual(wf.getnchannels(), 1)
                self.assertAlmostEqual(wf.getnframes() / wf.getframerate(), 1.0, places=2)


if __name__ == "__main__":
    unittest.main()
