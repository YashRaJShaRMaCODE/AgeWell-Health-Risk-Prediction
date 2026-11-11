from pathlib import Path


def read_and_remove_report(path):
    report_path = Path(path)
    try:
        return report_path.read_bytes()
    finally:
        try:
            report_path.unlink()
        except FileNotFoundError:
            pass
