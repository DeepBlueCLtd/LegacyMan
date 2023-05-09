import os.path
import shutil
import time
from os.path import basename
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from legacyman_parser.utils.constants import COPY_CLASS_IMAGES_TO_DIRECTORY
from legacyman_parser.utils.stateful_suffix_generator import StatefulSuffixGenerator

"""
Independent testable parse class image module
"""

CLASS_IMAGES_COLLECTION = []
already_processed_html_img_sources = {}
folder_specific_suffix_generator = {}


class ClassImages:
    def __init__(self,
                 class_u,
                 class_images):
        self.class_u = class_u
        self.class_images = class_images

    def __str__(self):
        return "{} has the following images: {}.".format(self.class_u.id, self.class_images)


def instantiate_or_retrieve_cached_generator(file_name):
    dir_name = os.path.dirname(file_name).upper()
    if dir_name not in folder_specific_suffix_generator:
        suffix_gen = StatefulSuffixGenerator()
        folder_specific_suffix_generator[dir_name] = suffix_gen
    return folder_specific_suffix_generator[dir_name]


def extract_class_images(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                         userland_dict: dict = None) -> []:
    # This parser will handle class image extraction for only non-Britain like countries.
    all_class_images = soup.find_all('img')

    def not_blacklisted_filter(tag):
        # filter for images that aren't in black-listed images
        black_list = ['image020.jpg', 'check_db.gif', 'prev_db.gif', 'rtn2map_db.gif']
        in_black_list = filter(
            lambda item: item in tag.get('src').lower(), black_list)
        in_black_list_item = list(in_black_list)
        return len(list(in_black_list_item)) == 0

    # only include images that have not been blacklisted
    class_images = list(filter(not_blacklisted_filter, all_class_images))

    class_images_obj = ClassImages(userland_dict['class'], [])
    already_referenced_image_in_class = set()
    for class_image_attr in class_images:
        class_image = urljoin(parsed_url, class_image_attr['src'])
        assert Path(class_image).is_file(), "InvalidAssumption: Class image file exists if provided in " \
                                            "img attribute. {} not found as specified " \
                                            "in {}.".format(
                                                class_image, parsed_url)
        # Track already processed images in source, don't copy duplicate images
        if class_image.upper() in already_referenced_image_in_class:
            continue
        already_referenced_image_in_class.add(class_image.upper())

        # Track already parsed images in destination, instead of copying again.
        new_destination_of_img_src = os.path.join(COPY_CLASS_IMAGES_TO_DIRECTORY,
                                                  userland_dict['class'].country.country.lower(),
                                                  'Generic'.lower(),
                                                  userland_dict['class'].sub_category[0].lower(),
                                                  basename(class_image).lower())

        if new_destination_of_img_src not in already_processed_html_img_sources:
            already_processed_html_img_sources[new_destination_of_img_src] = [
                class_image.upper()]
            if not os.path.exists(os.path.dirname(new_destination_of_img_src)):
                os.makedirs(os.path.dirname(new_destination_of_img_src))
            shutil.copy2(class_image, new_destination_of_img_src)
        else:
            if class_image.upper() not in already_processed_html_img_sources[new_destination_of_img_src]:
                already_processed_html_img_sources[new_destination_of_img_src].append(
                    class_image.upper())
                if os.path.exists(new_destination_of_img_src):
                    suffix_gen = instantiate_or_retrieve_cached_generator(
                        new_destination_of_img_src)
                    new_destination_of_img_src = os.path.splitext(new_destination_of_img_src)[0] \
                        + "_" \
                        + suffix_gen.next_value() \
                        + os.path.splitext(new_destination_of_img_src)[1]
                shutil.copy2(class_image, new_destination_of_img_src)
        class_images_obj.class_images.append(new_destination_of_img_src)
    CLASS_IMAGES_COLLECTION.append(class_images_obj)
