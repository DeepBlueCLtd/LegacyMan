# LegacyMan

Legacy content for Field Service Manual, a digital twin that we are going to develop against.

See the original mock data [here](https://deepbluecltd.github.io/LegacyMan/data/PlatformData/PD_1.html).

## Technologies

- python >= 3.9
- beautifulsoup4
- simplejson

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

Execute the following command from the project root directory to run program.

```
python -m legacyman_parser.parser data/PlatformData/PD_1.html
```

This will
* generate the json file to be imported into the Data Browser application
* generate a discrepancy report of inaccessible urls

### Generate DITA content

This is still under development.
