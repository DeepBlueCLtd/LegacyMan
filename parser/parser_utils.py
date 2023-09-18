import shutil
from urllib.parse import urlparse
import xml.dom.minidom
import os
import copy
from bs4 import BeautifulSoup
from pathlib import Path

# package of utility helpers that are not specific to the task of LegacyMan


def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        print("Target directory deleted:" + path)
    else:
        print("Target directory does not exist")


def copy_directory(src_folder, dst_folder):
    shutil.copytree(src_folder, dst_folder)


def copy_files(source_dir, target_dir, file_names=[]):
    # create the target dir if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # If no names passed, then copy all the files in the folder
    if not file_names:
        file_names = os.listdir(source_dir)

    for file_name in file_names:
        source_file = os.path.join(source_dir, file_name)
        target_file = os.path.join(target_dir, file_name)
        shutil.copy(source_file, target_file)


def prettify_xml(xml_code):
    dom = xml.dom.minidom.parseString(xml_code)
    pretty_dom = dom.toprettyxml()
    # remove duplicate newlines
    clean_dom = os.linesep.join([s for s in pretty_dom.splitlines() if s.strip()])
    return clean_dom


def remove_leading_slashes(path):
    while path.startswith("../") or path.startswith("./"):
        path = path.lstrip("../").lstrip("./")
    return path


def write_prettified_xml(dita_soup, target_file_path):
    prettified_code = prettify_xml(str(dita_soup))

    target_file_path = Path(target_file_path)
    target_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_file_path, "wb") as f:
        f.write(prettified_code.encode("utf-8"))


def convert_html_href_to_dita_href(href):
    parsed = urlparse(href)

    parsed = parsed._replace(path=parsed.path.replace(".html", ".dita").replace(" ", "_"))
    p = Path(parsed.path)

    if parsed.fragment:
        id_str = p.name.split(".")[0]
        parsed = parsed._replace(fragment=f"{id_str}/{parsed.fragment}")

    print(f"Converted URL = {parsed.geturl()}")
    return parsed.geturl(), parsed.path.split(".")[-1]
