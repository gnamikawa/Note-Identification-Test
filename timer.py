import time


class Timer:
    def __init__(self):
        """Initialize the Timer with no start time."""
        self.start_time: float | None = None

    def start(self) -> None:
        """Start the timer by recording the current time."""
        self.start_time = time.time()

    def stop(self) -> float:
        """Stop the timer and return the elapsed time.

        Returns:
            float: The elapsed time in seconds since the timer started.
        """
        return 0.0 if self.start_time is None else time.time() - self.start_time
