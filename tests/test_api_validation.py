import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.routes.api import app


class ApiValidationTests(unittest.TestCase):
    def setUp(self):
        self.auth_token = "t" * 32
        self.auth_patch = patch("app.routes.api.API_AUTH_TOKEN", self.auth_token)
        self.auth_patch.start()
        self.client = app.test_client()

    def tearDown(self):
        self.auth_patch.stop()

    def post_json(self, data):
        return self.client.post(
            "/predict",
            json=data,
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

    def test_non_object_json_returns_a_json_client_error(self):
        response = self.client.post(
            "/predict",
            data="not-json",
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Request body must be a JSON object"})

    def test_non_boolean_privacy_flags_return_a_client_error(self):
        response = self.post_json({
            "age": 65,
            "heart_rate": 80,
            "systolic_bp": 120,
            "cholesterol": 180,
            "weight": 65,
            "height": 1.7,
            "save_to_db": "false",
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "save_to_db must be a boolean"})

    def test_requested_pdf_is_returned_and_temporary_file_is_removed(self):
        payload = {
            "age": 65, "heart_rate": 80, "systolic_bp": 120,
            "cholesterol": 180, "weight": 65, "height": 1.7,
            "generate_pdf": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.pdf"
            report.write_bytes(b"%PDF-test")
            result = SimpleNamespace(
                patient_id=None, risk_label="Low", bmi=22.49, health_score=100,
                food_plan="Example", exercise_plan="Example", pdf_file=str(report),
                email_sent=False,
            )
            with patch("app.routes.api.process_patient", return_value=result):
                response = self.post_json(payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        self.assertEqual(response.data, b"%PDF-test")
        self.assertEqual(response.headers["X-AgeWell-Risk"], "Low")
        self.assertFalse(report.exists())


if __name__ == "__main__":
    unittest.main()
