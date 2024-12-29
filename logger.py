import csv
import os


class CSVLogger:
    def __init__(self, output_file: str):
        """Initialize the CSV logger with the specified output file.

        Args:
            output_file (str): The path to the output CSV file.
        """
        self.output_file: str = output_file
        self.headers: list[str] = [
            "Timestamp",
            "Session ID",
            "Tested Note",
            "Guessed Note",
            "Time Taken (s)",
        ]
        self.setup_csv()

    def setup_csv(self) -> None:
        """Set up the CSV file by writing headers if the file is empty or doesn't exist."""
        if (
            not os.path.isfile(self.output_file)
            or os.path.getsize(self.output_file) == 0
        ):
            self._write_headers()

    def _write_headers(self) -> None:
        """Write the headers to the CSV file."""
        with open(self.output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)

    def log_result(
        self,
        session_id: str,
        tested_note: str,
        guessed_note: str,
        time_taken: float,
        timestamp: str,
    ) -> None:
        """Log the result of a note test to the CSV file.

        Args:
            session_id (str): The session ID.
            tested_note (str): The tested note.
            guessed_note (str): The guessed note.
            time_taken (float): The time taken to guess the note.
            timestamp (str): The timestamp of the result.
        """
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
