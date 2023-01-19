import os.path
import shutil
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from legacyman_parser.utils.constants import COPY_FLAGS_TO_DIRECTORY

"""
Independent testable parse flag module
"""

COUNTRY_FLAG_COLLECTION = []


class CountryFlag:
    def __init__(self,
                 country,
                 file_location):
        self.country = country
        self.file_location = file_location

    def __str__(self):
        return "{}'s flag is located at {}.".format(self.country.country, self.file_location)


def extract_flag_of_country(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                            userland_dict: dict = None) -> []:
    # This parser will handle flag extraction for only non-Britain like countries.
    flag_images = soup.find_all('img')
    assert len(flag_images) == 1 or len(flag_images) == 2, "InvalidAssumption: Only 1 or 2 flags " \
                                                           "are there for any given country." \
                                                           " Failed for {}".format(parsed_url)
    # Always take the last flag
    flag_image = urljoin(parsed_url, flag_images[len(flag_images) - 1]['src'])
    assert Path(flag_image).is_file(), "InvalidAssumption: Flag file exists if provided in img attribute. " \
                                       "{} not found as specified in {}.".format(flag_image, parsed_url)

    # Copy to target directory
    destination_file = COPY_FLAGS_TO_DIRECTORY + userland_dict['country'].country + os.path.splitext(flag_image)[1]
    shutil.copy2(flag_image, destination_file)

    COUNTRY_FLAG_COLLECTION.append(CountryFlag(userland_dict['country'], destination_file))
