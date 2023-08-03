import shutil
import xml.dom.minidom
import os
import copy
from bs4 import BeautifulSoup

# package of utility helpers that are not specific to the task of LegacyMan


def ditaToHTML(path, soup):
    # 1. if outer element is a div, replace with a span element
    if soup.name == "div":
        soup.name = "span"
        del soup["id"]

    # 2. Replace child divs with a span element
    for div in soup.find_all("div"):
        div.name = "p"
        del div["name"]

    # 3. For img elements, rename it to image, and rename the src attribute to href
    for img in soup.find_all("img"):
        img.name = "image"
        img["href"] = img["src"].lower()
        del img["src"]

    # 4a. replace h1 with paragraph with correct outputClass
    for h1 in soup.find_all("h1"):
        h1.name = "p"
        h1.outputClass = "h1"

    # 4b. replace h1 with paragraph with correct outputClass
    for h2 in soup.find_all("h2"):
        h2.name = "p"
        h2.outputClass = "h2"

    # 4c. replace h1 with paragraph with correct outputClass
    for h3 in soup.find_all("h3"):
        h3.name = "p"
        h3.outputClass = "h3"

    # 5. Fix hyperlinks
    for a in soup.find_all("a"):
        a.name = "xref"
        a["href"] = "#"

    # 6. Fix unordered lists
    for ul in soup.find_all("ul"):
        ul.name = "ol"

    # 7. Fix tables
    # for ul in soup.find_all('ul'):
    #     ul.name = 'ol'

    return soup


def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("Target directory deleted:" + path)
    else:
        print("Target directory does not exist")


def create_directory(name):
    try:
        os.makedirs(name)
        print(f"{name} directory created")
    except FileExistsError:
        print(f"The directory {name} already exists")


def copy_directory(src_folder, dst_folder):
    shutil.copytree(src_folder, dst_folder)


def copy_files(source_dir, target_dir, file_names=[]):
    # create the target dir if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # copy files
    if not file_names:
        # if file_names is empty, copy all files from source_dir
        for file_name in os.listdir(source_dir):
            source_file = os.path.join(source_dir, file_name)
            target_file = os.path.join(target_dir, file_name)
            shutil.copy(source_file, target_file)
    else:
        # copy only the files specified in file_names
        for file_name in file_names:
            source_file = os.path.join(source_dir, file_name)
            target_file = os.path.join(target_dir, file_name)
            shutil.copy(source_file, target_file)


def prettify_xml(xml_code):
    dom = xml.dom.minidom.parseString(xml_code)
    return dom.toprettyxml()


def get_files_in_path(path, make_lowercase=False):
    entries = os.listdir(path)

    # If make_lowercase is True, convert directory names to lowercase
    if make_lowercase:
        entries = [
            entry.lower() if os.path.isfile(os.path.join(path, entry)) else entry
            for entry in entries
        ]

    # Get a list of all files in the path
    files = [f for f in entries if os.path.isfile(os.path.join(path, f))]
    return files


__all__ = [
    "delete_directory",
    "create_directory",
    "copy_directory",
    "copy_files",
    "prettify_xml",
    "get_files_in_path",
]
