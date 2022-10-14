# _perfomanceTester

This script was created to test (and compare) the performance of `DummyImage` implementations. Mainly for internal use.<br>
`DummyImage` is a tool for generating images of a specific file size. Created for testing needs (for example, uploader apps)

**Available Implementations**:
 - [`hsDummyImage`](https://github.com/DummyFiles/hsDummyImage)
 
\[[Search more](https://github.com/orgs/DummyFiles/repositories?q=topic%3Adummyimage&type=all)]

## Reports examples:

<details> <summary> 
  <h3>Markdown</h3> 
  </summary>
  
  > ##### Runner hardware:
  > * 🏿 8-x CPU cores
  > * 💾 Disk drive write speed: 332.725MiB/s

  | Names | 1 kb | 128 kb | 512 kb | 1 mb | 16 mb | 128 mb | Total |
  | --- |:---: | :---: | :---: | :---: | :---: | :---: | ---: |
  | `fastest_mono` | 0.00147 | 0.003712 | 0.007038 | 0.01023 | 0.1398 | 1.241 | 1.403 |
  | `high_crosswalk` | 0.00146 | 0.003754 | 0.00755 | 0.01173 | 0.1615 | 1.4 | 1.586 |
  | `hypnotoad` | 0.001478 | 0.003614 | 0.007582 | 0.01197 | 0.1666 | 1.463 | 1.654 |
  | `matrix` | 0.001474 | 0.003746 | 0.008026 | 0.01258 | 0.1718 | 1.477 | 1.674 |
  | `stains` | 0.001504 | 0.003642 | 0.007912 | 0.01247 | 0.175 | 1.525 | 1.726 |
  | `alt_stains` | 0.00146 | 0.00476 | 0.008646 | 0.01415 | 0.1981 | 1.7 | 1.927 |
  | `cold_grid` | 0.001446 | 0.006434 | 0.01618 | 0.03039 | 0.4541 | 3.693 | 4.202 |
</details>
  
<details> <summary> 
  <h3>JSON</h3> 
  </summary>
  
  ```json
    {
     "order_list":[
        [ 1,   "kb" ],
        [ 128, "kb" ],
        [ 512, "kb" ],
        [ 1,   "mb" ],
        [ 16,  "mb" ],
        [ 128, "mb" ]
     ],
     "functions":{
        "stains":[
           0.0015039999999999997,
           0.003641999999999999,
           0.007911999999999999,
           0.012468,
           0.17498200000000005,
           1.5254980000000007
        ],
        "hypnotoad":[
           0.0014780000000000001,
           0.0036139999999999987,
           0.007582,
           0.011968000000000001,
           0.166592,
           1.463032
        ],
        "fastest_mono":[
           0.0014700000000000002,
           0.0037120000000000013,
           0.007038,
           0.010233999999999998,
           0.139816,
           1.2409919999999999
        ],
        "alt_stains":[
           0.0014599999999999997,
           0.004759999999999999,
           0.008646000000000003,
           0.014153999999999998,
           0.19806999999999994,
           1.6998259999999994
        ],
        "matrix":[
           0.0014740000000000003,
           0.0037459999999999993,
           0.008026,
           0.012581999999999992,
           0.17179999999999995,
           1.4765080000000004
        ],
        "cold_grid":[
           0.0014459999999999998,
           0.006434,
           0.016176000000000006,
           0.030388000000000005,
           0.4540780000000001,
           3.693310000000002
        ],
        "high_crosswalk":[
           0.0014599999999999993,
           0.0037539999999999995,
           0.007549999999999998,
           0.011725999999999993,
           0.16147200000000006,
           1.400354
        ]
     },
     "hardware_report":{
        "cpu":{
           "cores":8
        },
        "drive":{
           "skipped":false,
           "write_speed":{
              "value":332.72530485461925,
              "units":"MiB"
           }
        }
     }
  }
  ```
  
</details>
  

## Usage:

```
usage: main.py [-h] [--binary-command BINARY_COMMAND] [--additional-args ADDITIONAL_ARGS] [--temp-dir TEMP_DIR] [--delete-after-each] [--keep-all] [--repeats-count REPEATS_COUNT] [--generate-md-report] [--md-output MD_OUTPUT]
               [--generate-json-report] [--json-output JSON_OUTPUT] [--std-report-delimiter STD_REPORT_DELIMITER] [--disable-log-output] [--disable-console-spinner] [--skip-drive-benchmark] [--test-sizes-list TEST_SIZES_LIST]

Tool for testing DummyImage realisation

optional arguments:
  -h, --help            show this help message and exit
  --binary-command BINARY_COMMAND, -b BINARY_COMMAND
                        The command(path) to run the binary
  --additional-args ADDITIONAL_ARGS, -a ADDITIONAL_ARGS
                        Additional arguments when running the binary
  --temp-dir TEMP_DIR   Folder for temporary storage of dummies
  --delete-after-each, -d
                        Delete dummies immediately after generation
  --keep-all, -k        Keep all dummies. Overrides the --delete-after-each flag
  --repeats-count REPEATS_COUNT, -r REPEATS_COUNT
                        Number of test repetitions for each combination of (function, size)
  --generate-md-report, --md
                        Generate Markdown report
  --md-output MD_OUTPUT
                        The file for writing the MD report. If the value is empty, it will be redirected to stdout
  --generate-json-report, --json
                        Generate JSON report
  --json-output JSON_OUTPUT
                        The file for writing the JSON report. If the value is empty, it will be redirected to stdout
  --std-report-delimiter STD_REPORT_DELIMITER
                        This line will be inserted before and after each print(stdout) of report
  --disable-log-output  Disable output of all information except reports
  --disable-console-spinner
                        Disable wait spinner
  --skip-drive-benchmark
                        Skip disk check. Speed ​​data will not be displayed in the report
  --test-sizes-list TEST_SIZES_LIST, -t TEST_SIZES_LIST
                        The list of sizes on which the test will be carried out. In the format: size1-units1,size2-units2,...

```
