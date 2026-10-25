import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from app.services.health_service import PredictionResult, process_patient
    from app.utils.pdf_report import generate_health_report
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f"Install repository requirements first ({exc.name} is missing)") from exc


class PrivacyDefaultTests(unittest.TestCase):
    @patch("app.services.health_service.generate_health_report")
    @patch("app.services.health_service.db.insert_record")
    @patch("app.services.health_service.evaluate_patient")
    def test_prediction_does_not_persist_or_generate_a_report_by_default(
        self, evaluate_patient, insert_record, generate_report
    ):
        evaluate_patient.return_value = PredictionResult(
            risk=0,
            risk_label="Low",
            bmi=22.4,
            health_score=100,
            food_plan="Balanced diet",
            exercise_plan="Walk regularly",
        )

        result = process_patient(65, 80, 120, 180, 65, 1.7, send_alert=False)

        self.assertIsNone(result.patient_id)
        self.assertIsNone(result.pdf_file)
        insert_record.assert_not_called()
        generate_report.assert_not_called()

    def test_same_patient_reports_use_distinct_files(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = [
                generate_health_report(
                    7, 65, 80, 120, 180, 22.4, 100, "Low",
                    "Balanced diet", "Walk regularly", output_dir=folder,
                )
                for _ in range(2)
            ]

            self.assertNotEqual(paths[0], paths[1])
            self.assertTrue(all(Path(path).is_file() for path in paths))


if __name__ == "__main__":
    unittest.main()
