import tempfile
import unittest
from pathlib import Path

from app.utils.temporary_report import read_and_remove_report


class TemporaryReportTests(unittest.TestCase):
    def test_reading_a_report_returns_bytes_and_removes_the_host_file(self):
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "report.pdf"
            report.write_bytes(b"sample pdf")

            self.assertEqual(read_and_remove_report(report), b"sample pdf")
            self.assertFalse(report.exists())


if __name__ == "__main__":
    unittest.main()
