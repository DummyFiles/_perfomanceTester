import subprocess
import json
import re
import os

from shutil import rmtree

from typing import Dict, Tuple, Sequence, Optional

from console_helper import ConsoleHelper
from hardware_test import HardwareReport


float_pattern = r"[0-9]\.[0-9]*"
size_pattern  = r"([0-9]+)-(b|kb|mb|gb)(,?)"


class MdTable:
    def __init__(self) -> None:
        self.header = ""
        self.columns_type = ""
        self.body = ""

    def set_header(self, name: str, array: Sequence[Tuple[int, str]], last: str) -> None:

        data = (name, *(f"{size} {units}" for size, units in array), last)
        self.header = f'| {" | ".join(data)} |'
        self.columns_type = f'| --- |{" | ".join([":---:" for _ in array])} | ---: |'

    def add_row(self, name: str, array: Sequence[float], last: str) -> None:
        data = (name, *(f"{n:.4}" for n in array), last)
        self.body += f'| {" | ".join(data)} |\n'

    def get_content(self) -> str:
        return "\n".join((self.header, self.columns_type, self.body))


class TestRecord:
    def __init__(self, func_name: str, size: int, units: str, cpu_time: float, total_time: float) -> None:
        self.func_name  = func_name
        self.container = {
            (size, units): {
                "cpu_time": [cpu_time],
                "total_time": [total_time]
            }
        }

    def update_record(self, size: int, units: str, cpu_time: float, total_time: float) -> None:
        key = (size, units)
        if key in self.container:
            self.container[key]["cpu_time"].append(cpu_time)
            self.container[key]["total_time"].append(total_time)
        else:
            self.container[key] = {
                "cpu_time": [cpu_time],
                "total_time": [total_time]
            }

    def get_entity_avg_by_key(self, key: Tuple[int, str]) -> Dict[str, float]:
        entity = self.container.get(key)
        return {
            "cpu_time": sum(entity["cpu_time"])/len(entity["cpu_time"]),
            "total_time": sum(entity["total_time"])/len(entity["total_time"])
        }

    def get_avg_cpu_time_ordered_by_list(self, order_list: Sequence[Tuple[int, str]]) -> Sequence[float]:
        return [self.get_entity_avg_by_key(key)["cpu_time"] for key in order_list]


class TestsContainer:
    def __init__(self, console: ConsoleHelper, hardware_report_dict: Optional[Dict] = None) -> None:
        self.records: Dict[str, TestRecord] = {}
        self.console = console
        self.hardware_report_dict = hardware_report_dict

    def add_record(self, func_name: str, *args, **kwargs) -> None:
        if func_name not in self.records:
            self.records[func_name] = TestRecord(func_name, *args, **kwargs)
        else:
            self.records[func_name].update_record(*args, **kwargs)

    def build_md_content(self, order_list: Sequence[Tuple[int, str]]) -> str:

        table = MdTable()
        table.set_header("Names", order_list, last="Total")

        records_dump = []

        for func_name, entity_container in self.records.items():
            values = entity_container.get_avg_cpu_time_ordered_by_list(order_list)
            records_dump.append((f"`{func_name}`", values, f"{sum(values):.4}",))

        for rc in sorted(records_dump, key=lambda x: x[-1]):
            table.add_row(*rc)

        md_content: str = ""

        if self.hardware_report_dict is not None:
            disk_drive_info = (
                f"{self.hardware_report_dict['drive']['write_speed']['value']:.3f}"
                f"{self.hardware_report_dict['drive']['write_speed']['units']}/s"
            ) if not self.hardware_report_dict['drive']['skipped'] else "SKIPPED"
            md_content = (
                "> ##### Runner hardware:\n"
                f"> * 🏿 {self.hardware_report_dict['cpu']['cores']}-x CPU cores\n"
                f"> * 💾 Disk drive write speed: {disk_drive_info}\n\n"
            )
        return f"{md_content}{table.get_content()}"

    def build_json_content(self, order_list: Sequence[Tuple[int, str]]) -> str:

        records_dump = {
            "order_list": order_list,
            "functions": {},
            "hardware_report": self.hardware_report_dict
        }

        for func_name, entity_container in self.records.items():
            records_dump["functions"][func_name] = entity_container.get_avg_cpu_time_ordered_by_list(order_list)

        return json.dumps(records_dump)

    def build_report(self, order_list: Sequence[Tuple[int, str]], r_type: str, r_output: str, *, hardware_report_dict: Optional[Dict] = None) -> None:
        report_content: str

        if r_type == "json":
            report_content = self.build_json_content(order_list)
        elif r_type == "md":
            report_content = self.build_md_content(order_list)
        else:
            raise ValueError(f"'{r_type}' is unknown report type")

        if r_output:
            with open(r_output, 'w', encoding="utf-8") as f:
                f.write(report_content)
            console.log(f"[{r_type.upper()}] report saved in ({r_output})")
        else:
            self.console.print_report(report_content)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Tool for testing DummyImage realisation")
    parser.add_argument("--binary-command", "-b", help="The command(path) to run the binary", default="binary-exe.exe")
    parser.add_argument("--additional-args", "-a", help="Additional arguments when running the binary", default="")
    parser.add_argument("--temp-dir", help="Folder for temporary storage of dummies", default="./temp_bin")
    parser.add_argument("--delete-after-each", "-d", help="Delete dummies immediately after generation", action="store_true", default=False)
    parser.add_argument("--keep-all", "-k", help="Keep all dummies. Overrides the --delete-after-each flag", action="store_true", default=False)
    parser.add_argument("--repeats-count", "-r", help="Number of test repetitions for each combination of (function, size)", type=int, default=1)

    parser.add_argument("--generate-md-report", "--md", help="Generate Markdown report", action="store_true", default=False)
    parser.add_argument("--md-output", help="The file for writing the MD report. If the value is empty, it will be redirected to stdout", default="")
    parser.add_argument("--generate-json-report", "--json", help="Generate JSON report", action="store_true", default=False)
    parser.add_argument("--json-output", help="The file for writing the JSON report. If the value is empty, it will be redirected to stdout", default="")

    parser.add_argument("--std-report-delimiter", help="This line will be inserted before and after each print(stdout) of report", default=">--------#REPORT#--<")
    parser.add_argument("--disable-log-output", help="Disable output of all information except reports", action="store_true", default=False)
    parser.add_argument("--disable-console-spinner", help="Disable wait spinner", action="store_true", default=False)

    parser.add_argument("--skip-drive-benchmark", help="Skip disk check. Speed ​​data will not be displayed in the report", action="store_true", default=False)

    parser.add_argument(
        "--test-sizes-list",
        "-t",
        help="The list of sizes on which the test will be carried out. In the format: size1-units1,size2-units2,...",
        default="1-kb,128-kb,512-kb,1-mb,16-mb"
    )

    args = parser.parse_args()

    temp_bin_path = args.temp_dir
    os.makedirs(temp_bin_path, exist_ok=True)

    delete_flag = args.delete_after_each and not args.keep_all

    repeats_count = args.repeats_count
    reports_request = (
        rep[1:] for rep in
        (
            (args.generate_json_report or args.json_output, "json", args.json_output),
            (args.generate_md_report or args.md_output, "md", args.md_output),
        )
        if rep[0]
    )

    disable_log = args.disable_log_output
    with ConsoleHelper(
            disable_log=disable_log,
            disable_spinner=disable_log or args.disable_console_spinner,
            report_delimiter=args.std_report_delimiter
         ) as console:

        console.log("Script started")

        call_res = subprocess.run([args.binary_command, "-h"], stdout=subprocess.PIPE)
        stdout_res = call_res.stdout.decode()

        if "--dump-func-list" not in stdout_res:
            raise OSError(f"Command \"--dump-func-list\" not supported by {''}")

        call_res = subprocess.run([args.binary_command, "--dump-func-list"], stdout=subprocess.PIPE)
        stdout_res = call_res.stdout.decode()

        available_funcs = stdout_res[1:-1].split(" | ")
        console.log(f"Functions supported by the binary -> {available_funcs}")

        found_sizes = re.findall(size_pattern, args.test_sizes_list)
        if not len(found_sizes):
            raise ValueError(f"Sizes for testing are either empty or written in the wrong format. Received: {args.test_sizes_list}")

        target_sizes = [(int(s[0]), s[1]) for s in found_sizes]
        console.log(f"Target sizes: {target_sizes}")

        hardware_report = HardwareReport(console, temp_bin_path, args.skip_drive_benchmark)
        tests_cont = TestsContainer(console, hardware_report_dict=hardware_report.dict_like)

        total_combinations = repeats_count * len(available_funcs) * len(target_sizes)
        current_stage = 0

        for _ in range(repeats_count):
            for func_name in available_funcs:
                for size, units in target_sizes:
                    output_file_name = f"{func_name}_{size}_{units}.png"
                    console.set_status(f"Progress {current_stage*100/total_combinations:>5.1f}% | Current -> {output_file_name}")
                    res = subprocess.run(
                        " ".join([args.binary_command, args.additional_args, f"-o{output_file_name}", f"-f{func_name}", f"-s{size}", f"-u{units}", f"-d{temp_bin_path}"]),
                        stdout=subprocess.PIPE, shell=True
                    )
                    rs = res.stdout.decode()
                    cpu_time, total_time = map(lambda s: float(s), re.findall(float_pattern, rs))
                    tests_cont.add_record(func_name, size, units, cpu_time, total_time)
                    if delete_flag:
                        os.remove(os.path.join(temp_bin_path, output_file_name))
                    current_stage += 1

        if not args.keep_all:
            rmtree(temp_bin_path)

        for req in reports_request:
            console.set_status(f"Generating [{req[0].upper()}] report...")
            tests_cont.build_report(
                target_sizes,
                *req,
                hardware_report_dict=hardware_report.dict_like
            )
