import os
from bs4 import BeautifulSoup

from parser_utils import prettify_xml
from html_to_dita import htmlToDITA

# lower case version of images we ignore. Note `prev_db.jpg` added for testing
black_list = [
    "image020.jpg",
    "check_db.gif",
    "prev_db.gif",
    "rtn2map_db.gif",
    "prev_db.jpg",
    "flags.jpg",
]


def process_c_file(class_file_src_path, class_file_target_path, class_name, file_name):
    # read the class file
    with open(class_file_src_path, "r") as f:
        class_file = f.read()

    html_soup = BeautifulSoup(class_file, "html.parser")

    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE class SYSTEM "../../../../../dtd/class.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, "xml")

    dita_body = dita_soup.new_tag("body")

    # Parse the images
    parse_images(html_soup, dita_body, dita_soup)


def parse_images(tag, target, dita_soup):
    # create dita elements
    dita_images = dita_soup.new_tag("images")

    # loop through the HTML images and change them to dita
    images = tag.find_all("img")
    for img in images:
        img_link = img["src"].lower()
        image_filename = os.path.basename(img_link)

        # check it's not blacklisted
        if not image_filename in black_list:
            dita_image = dita_soup.new_tag("image")
            dita_image["href"] = img_link
            dita_image["scale"] = 33
            dita_image["align"] = "left"
            dita_images.append(dita_image)

    # Append the dita <images> to the dita <body>
    target.append(dita_images)


__all__ = ["process_class_files", "process_c_file"]
