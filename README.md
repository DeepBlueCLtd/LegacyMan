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

```
python -m legacyman_parser.parser data test_payload_for_parsed_json=legacy_tester/test_payload/mock_data_test_payload.json
```

To disable the *assert* statements, the above command can be executed with -O flag (hyphen capital o)

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
```
python -m legacyman_parser.parser < data directory >
```

To disable the *assert* statements, the above command can be executed with -O flag (hyphen capital o)

```
python -O -m legacyman_parser.parser < data directory >
```

## Parser outcomes

This will
* generate the json file to be imported into the Data Browser application
* validate assumptions about the html structure with *assert*
* generate a discrepancy report

### Generate DITA content

This is still under development.
