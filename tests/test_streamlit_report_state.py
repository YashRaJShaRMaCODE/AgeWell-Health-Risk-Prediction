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
        disclosures = [element.value for element in app.get("markdown")]
        estimate_note = next(value for value in disclosures if "The classifier uses age" in value)
        self.assertIn("not a probability", estimate_note)
        self.assertIn("separate rule-based outputs", estimate_note)
        privacy_notice = next(
            element.value
            for element in app.get("markdown")
            if "The hosted demo processes values" in element.value
        )
        self.assertIn("temporary file is deleted", privacy_notice)
        self.assertIn("this session's memory", privacy_notice)
        self.assertNotIn("held temporarily on the host", privacy_notice)
        self.assertEqual(len(app.get("download_button")), 1)
        app.button(key="clear-agewell-report").click().run()

        self.assertFalse(app.exception)
        self.assertNotIn("last_pdf_data", app.session_state)

    def test_reset_clears_inputs_confirmation_and_report_bytes(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=30)
        app.session_state["synthetic_data_confirmed"] = True
        app.session_state["age"] = 88
        app.session_state["last_pdf_data"] = b"sample report"
        app.run()

        self.assertFalse(app.exception)
        app.button(key="reset-agewell-sample").click().run()

        self.assertFalse(app.exception)
        self.assertFalse(app.session_state["synthetic_data_confirmed"])
        self.assertEqual(app.session_state["age"], 70)
        self.assertNotIn("last_pdf_data", app.session_state)

    def test_fictional_example_requires_fresh_confirmation_and_clears_outputs(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=30)
        app.session_state["synthetic_data_confirmed"] = True
        app.session_state["create_pdf"] = True
        app.session_state["send_alert"] = True
        app.session_state["last_pdf_data"] = b"previous report"
        app.run()

        self.assertFalse(app.exception)
        app.button(key="load-example-sample-b").click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["age"], 78)
        self.assertEqual(app.session_state["heart_rate"], 88)
        self.assertFalse(app.session_state["synthetic_data_confirmed"])
        self.assertFalse(app.session_state["create_pdf"])
        self.assertFalse(app.session_state["send_alert"])
        self.assertNotIn("last_pdf_data", app.session_state)


if __name__ == "__main__":
    unittest.main()
