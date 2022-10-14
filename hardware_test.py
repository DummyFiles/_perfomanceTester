import os
import time

from multiprocessing import cpu_count
from console_helper import ConsoleHelper


class HardwareReport:
    drive_test_file = "DriveBenchmarkBuffer"
    drive_test_block_count = 128
    drive_test_block_size = 1048576 # 2^20

    def __init__(self, console: ConsoleHelper, target_dir: str, skip_drive_test: bool = False, auto_start_tests: bool = True) -> None:
        self.console        = console
        self.target_dir     = target_dir
        self.skip_drive_test = skip_drive_test

        self.container = {
            "cpu": {
                "cores": None
            },
            "drive": {
                "skipped": skip_drive_test,
                "write_speed": {
                    "value": None,
                    "units": None
                }
            }
        }
        if auto_start_tests:
            self.run_tests()

    def run_tests(self) -> None:
        self.console.set_status("Collecting hardware report")
        for test_name in (name for name in dir(self) if name.startswith("_test_")):
            getattr(self, test_name)()

    @staticmethod
    def get_max_units_for_bytes_size(bytes_size: int) -> str:
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(bytes_size) < 1024.0:
                return f"{unit}B"
            bytes_size /= 1024.0
        raise ValueError("'bytes_size' value is too big")

    def _test_cpu_info(self) -> None:
        self.container["cpu"]["cores"] = cpu_count()

    def _test_disk_benchmark(self) -> None:
        if self.skip_drive_test:
            return

        benchmark_file_path = os.path.join(os.path.splitdrive(self.target_dir)[0], self.drive_test_file)
        benchmark_file = os.open(benchmark_file_path, os.O_CREAT | os.O_WRONLY, 0o666)
        recorded_time = []
        for i in range(self.drive_test_block_count):
            self.console.set_status(
                f"Drive testing... {str(i).rjust(5)}/{self.drive_test_block_count} blocks"
            )
            buff = os.urandom(self.drive_test_block_size)

            write_start = time.time()
            os.write(benchmark_file, buff)
            os.fsync(benchmark_file)
            recorded_time.append(time.time() - write_start)

        self.console.clear_status()
        os.close(benchmark_file)
        os.remove(benchmark_file_path)

        write_speed = self.drive_test_block_count / sum(recorded_time)
        write_speed_units = self.get_max_units_for_bytes_size(self.drive_test_block_size)
        self.console.log(f"Drive speed => {write_speed} {write_speed_units}/s")
        self.container["drive"]["write_speed"]["value"] = write_speed
        self.container["drive"]["write_speed"]["units"] = write_speed_units

    @property
    def dict_like(self) -> dict:
        return self.container


if __name__ == '__main__':
    from console_helper import ConsoleHelper

    with ConsoleHelper() as console:
        report = HardwareReport(console, os.getcwd())
        console.log(str(report.dict_like))
