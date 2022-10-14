from threading import Thread
from typing import Generator
import time
import os


class ConsoleHelper(Thread):
    """Helper class for drawing spinner in console"""
    def __init__(self, disable_log: bool = False, disable_spinner: bool = False, report_delimiter: str = "", spinner_style: int = 1) -> None:
        super().__init__()
        self.disable_log = disable_log
        self.disable_spinner = disable_spinner
        self.report_delimiter = report_delimiter
        self.style = spinner_style
        self._status = ""
        self.running = False
        self.output_queue = []

    def start(self) -> None:
        self.running = True
        super().start()
        
    def stop(self) -> None:
        while len(self.output_queue)>0:
            time.sleep(0.05)
        self.running = False
        super().join()
        self.clear()

    def set_status(self, status: str) -> None:
        self._status = status

    def clear_status(self) -> None:
        self._status = ""
        
    def clear(self) -> None:
        max_columns: int
        try:
            max_columns = os.get_terminal_size().columns - 1
        except OSError:
            max_columns = 80

        print(f"\r{' ' * max_columns}\r", end="")
        
    def print(self, msg: str) -> None:
        if self.disable_spinner:
            print(msg)
        else:
            self.output_queue.append(msg)

    def print_report(self, msg: str) -> None:
        self.print(f"\n{self.report_delimiter}\n{msg}\n{self.report_delimiter}")

    def log(self, msg: str) -> None:
        if not self.disable_log:
            self.print(f"| LOG> {msg}")
        
    def run(self) -> None:
        def spinner_generator(style: int = 0) -> Generator[str, None, None]:
            sp_styles = [
                ["◌","○","●","○",],
                [" █ "," ▓ "," ▒ "," ░ "," ▒ "," ▓ ",],
                ["/","|","\\",]
            ]
            sp_list = sp_styles[style % len(sp_styles)]
            last_sp_index = 0
            while True:
                yield sp_list[last_sp_index]
                last_sp_index = (last_sp_index+1) % len(sp_list)
                
        sp_gen = spinner_generator(self.style)
        
        while self.running:
            self.clear()
            if len(self.output_queue) > 0:
                print(self.output_queue.pop(0))
            print(f"\r{next(sp_gen)} {self._status}", end="")
            time.sleep(0.1)
        
    def __enter__(self) -> 'ConsoleHelper':
        if not self.disable_spinner:
            self.start()
        return self
        
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if not self.disable_spinner:
            self.stop()


if __name__ == "__main__":
    with ConsoleHelper() as spinner:
        spinner.print("Some text")    
        time.sleep(3)
