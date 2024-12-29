import csv
import os


class CSVLogger:
    def __init__(self, output_file):
        self.output_file = output_file
        self.headers = [
            "Timestamp",
            "Session ID",
            "Tested Note",
            "Guessed Note",
            "Time Taken (s)",
        ]
        self.setup_csv()

    def setup_csv(self):
        if (
            not os.path.isfile(self.output_file)
            or os.path.getsize(self.output_file) == 0
        ):
            self._write_headers()

    def _write_headers(self):
        with open(self.output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)

    def log_result(self, session_id, tested_note, guessed_note, time_taken, timestamp):
        if (
            not os.path.isfile(self.output_file)
            or os.path.getsize(self.output_file) == 0
        ):
            self._write_headers()
        try:
            with open(self.output_file, mode="a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        timestamp,
                        session_id,
                        tested_note,
                        guessed_note,
                        f"{time_taken:.3f}",
                    ]
                )
        except Exception as e:
            raise RuntimeError(f"Failed to log result to {self.output_file}") from e
