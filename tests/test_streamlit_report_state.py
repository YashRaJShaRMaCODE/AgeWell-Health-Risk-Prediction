import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitReportStateTests(unittest.TestCase):
    def test_report_bytes_are_cleared_from_the_session_on_request(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=30)
        app.session_state["last_pdf_data"] = b"sample report"
        app.run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("download_button")), 1)
        app.button(key="clear-agewell-report").click().run()

        self.assertFalse(app.exception)
        self.assertNotIn("last_pdf_data", app.session_state)


if __name__ == "__main__":
    unittest.main()
