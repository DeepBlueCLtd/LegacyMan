# LegacyMan

Legacy content for Field Service Manual, a digital twin that we are going to develop against.

See the original mock data [here](https://deepbluecltd.github.io/LegacyMan/data/PlatformData/PD_1.html).

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
python -m legacyman_parser.parser data test_payload_for_parsed_json=legacy_tester/test_payload/mock_data_test_payload.json

```

To disable the _assert_ statements, the above command can be executed with -O flag (hyphen capital o)

```

python -O -m legacyman_parser.parser data test_payload_for_parsed_json=legacy_tester/test_payload/mock_data_test_payload.json

```

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

python -m legacyman_parser.parser < data directory >

```

To disable the _assert_ statements, the above command can be executed with -O flag (hyphen capital o)

```

python -O -m legacyman_parser.parser < data directory >

```

## Parser outcomes

This will

- generate the json file to be imported into the Data Browser application
- validate assumptions about the html structure with _assert_
- generate a discrepancy report

### Generate DITA content

This is still under development.

```

```
