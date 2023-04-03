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

######################################################
# filter functions, to help with filtering flag images
######################################################


def in_content_images_filter(tag):
    # filter for images where src is in images sub-folder
    src = tag.get('src')
    return src.lower().startswith('./content/images')


def not_blacklisted_filter(tag):
    # filter for images that aren't in black-listed images
    black_list = ['image020.jpg', 'yellow3.jpg', 'yellow4.jpg']
    in_black_list = filter(
        lambda item: item in tag.get('src').lower(), black_list)
    in_black_list_item = list(in_black_list)
    return len(list(in_black_list_item)) == 0


def extract_flag_of_country(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                            userland_dict: dict = None) -> []:
    # This parser will handle flag extraction for only non-Britain like countries.
    images = soup.find_all('img')

    # apply our filters
    in_content_images = list(filter(in_content_images_filter, images))
    non_blacklisted = list(filter(not_blacklisted_filter, in_content_images))
    flag_images = non_blacklisted

    assert len(flag_images) == 1 or len(flag_images) == 2, "InvalidAssumption: Only 1 or 2 flags " \
                                                           "are there for any given country." \
                                                           " Failed for {}. Found {}".format(
                                                               parsed_url, len(flag_images))
    # Always take the last flag
    flag_image = urljoin(parsed_url, flag_images[len(flag_images) - 1]['src'])
    assert Path(flag_image).is_file(), "InvalidAssumption: Flag file exists if provided in img attribute. " \
                                       "{} not found as specified in {}.".format(
                                           flag_image, parsed_url)

    # Copy to target directory
    destination_file = COPY_FLAGS_TO_DIRECTORY + \
        userland_dict['country'].country + os.path.splitext(flag_image)[1]
    shutil.copy2(flag_image, destination_file)

    COUNTRY_FLAG_COLLECTION.append(CountryFlag(
        userland_dict['country'], destination_file))


def extract_flag_of_ns_country(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                               userland_dict: dict = None) -> []:
    # This parser will handle flag extraction for only non-standard countries.
    graylayer = soup.find_all('div', {'id': 'GrayLayer'})
    assert len(graylayer) >= 1, "InvalidAssumption: There should at least one Graylayer div in the landing" \
                                "page of a non-standard country: " + parsed_url
    images = graylayer[0].find_all('img')

    # apply our filters
    in_content_images = list(filter(in_content_images_filter, images))
    non_blacklisted = list(filter(not_blacklisted_filter, in_content_images))
    flag_images = non_blacklisted

    assert len(flag_images) == 1 or len(flag_images) == 2, "InvalidAssumption: There should one or two images in this Graylayer, " \
        "that of the flag: {}. Found {}".format(
        parsed_url, flag_images)
    flag_images = soup.find_all('img')
    # Always take the first flag
    flag_image = urljoin(parsed_url, flag_images[0]['src'])
    assert Path(flag_image).is_file(), "InvalidAssumption: Flag file exists if provided in img attribute. " \
                                       "{} not found as specified in {}.".format(
                                           flag_image, parsed_url)

    # Copy to target directory
    destination_file = COPY_FLAGS_TO_DIRECTORY + \
        userland_dict['country'].country + os.path.splitext(flag_image)[1]
    shutil.copy2(flag_image, destination_file)

    COUNTRY_FLAG_COLLECTION.append(CountryFlag(
        userland_dict['country'], destination_file))
