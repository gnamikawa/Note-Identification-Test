import time


class Timer:
    def __init__(self):
        self.start_time: float | None = None

    def start(self) -> None:
        self.start_time = time.time()

    def stop(self) -> float:
        return 0.0 if self.start_time is None else time.time() - self.start_time
