# LegacyMan

Legacy content for Field Service Manual, a digital twin that we are going to develop against.

See the original mock data [here](https://deepbluecltd.github.io/LegacyMan/data/PlatformData/PD_1.html).

## Burndown
![burndown chart](https://docs.google.com/spreadsheets/d/e/2PACX-1vS4RYYUIkU93MCcW95v64qu00MSFEgq7RXvMgtL21ad0uHNW2gTnS7HBzYS7AZsZ8ladWYJ8VZ1WV_w/pubchart?oid=1341797319&format=image)

## Technologies

- python >= 3.9
- beautifulsoup4

## Initial Setup

### Install dependencies

Python dependencies are specified in `requirements.txt` in the project root directory.

Install these automatically using the below `pip` command from the same directory.

```
pip install -r requirements.txt
```

## Running tests

Execute the following command from the project root directory to run the tests.

```
python -m unittest discover
```

## Running LegacyMan parser program (against mock data)

Execute the following command from the project root directory to run program. The test_payload_for_parsed_json is optional parameter.

### Install DITA-OT

1. Check if `DITA-OT` is already installed by running the command below
   ```
     dita --version
   ```
2. If the `dita` command is not found, then you need to download and install the latest version of `DITA-OT` from the official [website](https://www.dita-ot.org/download).

3. Once you have downloaded and extracted the package to a directory on your system, you can add the `DITA-OT/bin` directory to your `PATH` variable by adding the following line to your `.bash_profile` file:

   ```
    export PATH=$PATH:/path/to/DITA-OT/bin
   ```

   Replace `/path/to/DITA-OT` with the actual path to your DITA-OT installation directory. After saving the file, you'll need to reload your `.bash_profile` file by running the following command:

   ```
    source ~/.bash_profile
   ```

4. Test that `DITA-OT` is installed correctly by running the `dita --version` command in your terminal. If the command returns a version number, then `DITA-OT` is installed and configured correctly. You can now use the `dita` command in your terminal to perform various DITA-related tasks.

### Run the parser

```
python parser/lman_parser.py data

```

There are a number of arguments that can be passed to the parser script. Run with `--help` to see them:

```
python parser/lman_parser.py --help
usage: lman_parser.py [OPTION] DATA_PATH [LOGGING_LEVEL]

positional arguments:
  DATA_PATH             Path to the source data
  LOGGING_LEVEL         Debug level - must be one of debug, warning or info

options:
  -h, --help            show this help message and exit
  --skip-first-run, --no-skip-first-run
                        Skip Run 1, loading the shopping list from the link_tracker.json file
  --warn-on-blank-runs, --no-warn-on-blank-runs
                        Print warning messages whenever runs of blank paragraphs are found
  --run-validation, --no-run-validation
                        Run the DITA validation step
```

These allow you to skip the first run, warn about sequences of blank paragraphs or run the DITA validation. 

There is a separate script to run the parser for a single file. Run:

```
python parser/parse_single_file.py INPUT_FOLDER SINGLE_FILE LOGGING_LEVEL
```

The only extra parameter is the `SINGLE_FILE` which should be the path to the individual file you want to process. For example:

```
python parser/parse_single_file.py data /home/LegacyMan/data/Britain_Cmplx/Phase_F.html debug
```

will process `Phase_F.html`, with debug logging

## Running LegacyMan parser program (against REAL data)

Apply the version controlled (checked into Git) **HTML discrepancy corrections** available at client site.
Checking out the applicable branch and replacing the files in the project location should do.

Execute the following command from the project root directory to run program.
The test_payload_for_parsed_json is optional parameter.

The < data directory > placeholder is to be replaced by a valid path containing the following directories:

- PlatformData (as in < data directory >/PlatformData/PD_1.html)
- QuickLinksData (as in < data directory >/QuickLinksData/Abbreviations.html)

From tests, an absolute path `c:\real_data` works more reliably than using a relative path `..\..\real_data`.

```

python parser./parser.py < data directory > < target directory >

```

## Running the file checker

We have also developed a checking script that will search for content in files in the source directory and check that it appears in content in the target directory. Each 'chunk' of content is a bit of plain text (ie. no tags in the middle of it) that is at least 40 characters long.

To run the file checker run:

```
python parser/check_files.py --help
```

This will show this help text:

```
usage: check_files.py [OPTION] SOURCE_PATH TARGET_PATH

positional arguments:
  SOURCE_PATH    Path to the source data
  TARGET_PATH    Path to the target (converted) data

options:
  -h, --help     show this help message and exit
  --files FILES  Either an integer, to process that number of random files, or 'all' to process all files (default: 5)
  --text TEXT    Either an integer, to read that number of random text strings from each file or 'all' to read all valid text strings from the file (default: 10)
  ```

  Running with just the path to the source and target files will check 10 chunks of text each from 5 files. These numbers can be adjusted by setting the `--files` and `--text` parameters, and the checking can be run on all chunks of text in all files by passing `--files all --text all`.