import os.path
import shutil
import time
from os.path import basename
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from legacyman_parser.utils.constants import COPY_CLASS_IMAGES_TO_DIRECTORY

"""
Independent testable parse class image module
"""

CLASS_IMAGES_COLLECTION = []
already_processed_html_img_sources = {}


class ClassImages:
    def __init__(self,
                 class_u,
                 class_images):
        self.class_u = class_u
        self.class_images = class_images

    def __str__(self):
        return "{} has the following images: {}.".format(self.class_u.id, self.class_images)


def extract_class_images(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                         userland_dict: dict = None) -> []:
    # This parser will handle class image extraction for only non-Britain like countries.
    class_images = soup.find_all('img')
    class_images_obj = ClassImages(userland_dict['class'], [])
    for class_image_attr in class_images:
        class_image = urljoin(parsed_url, class_image_attr['src'])
        assert Path(class_image).is_file(), "InvalidAssumption: Class image file exists if provided in " \
                                            "img attribute. {} not found as specified " \
                                            "in {}.".format(class_image, parsed_url)

        # Track already parsed images in destination, instead of copying again.
        new_destination_of_img_src = os.path.join(COPY_CLASS_IMAGES_TO_DIRECTORY,
                                                  userland_dict['class'].country.country,
                                                  'Generic',
                                                  userland_dict['class'].sub_category[0],
                                                  basename(class_image))

        if new_destination_of_img_src.upper() not in already_processed_html_img_sources:
            already_processed_html_img_sources[new_destination_of_img_src.upper()] = [class_image.upper()]
            if not os.path.exists(os.path.dirname(new_destination_of_img_src)):
                os.makedirs(os.path.dirname(new_destination_of_img_src))
            shutil.copy2(class_image, new_destination_of_img_src)
        else:
            if class_image.upper() not in already_processed_html_img_sources[new_destination_of_img_src.upper()]:
                already_processed_html_img_sources[new_destination_of_img_src.upper()].append(class_image.upper())
                if os.path.exists(new_destination_of_img_src):
                    new_destination_of_img_src = os.path.splitext(new_destination_of_img_src)[0] \
                                                 + "_" \
                                                 + str(round(time.time() * 1000)) \
                                                 + os.path.splitext(new_destination_of_img_src)[1]
                shutil.copy2(class_image, new_destination_of_img_src)
        class_images_obj.class_images.append(new_destination_of_img_src)
    CLASS_IMAGES_COLLECTION.append(class_images_obj)
