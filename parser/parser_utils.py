import shutil
from urllib.parse import urlparse
import xml.dom.minidom
import os
import copy
from bs4 import BeautifulSoup
from pathlib import Path
import cssutils
import logging

# package of utility helpers that are not specific to the task of LegacyMan


def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        logging.debug("Target directory deleted:" + path)
    else:
        logging.debug("Target directory does not exist")


def copy_files(source_dir, target_dir, file_names=None, recursive=True):
    if file_names:
        recursive = False

    target_dir = sanitise_filename(target_dir, directory=True)

    # create the target dir if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # If no names passed, then copy all the files in the folder
    if not file_names:
        file_names = os.listdir(source_dir)

    for file_name in file_names:
        if not "_notes" in file_name:
            source_file = os.path.join(source_dir, file_name)
            target_file = os.path.join(target_dir, sanitise_filename(file_name))
            if recursive and os.path.isdir(source_file):
                copy_files(source_file, target_file)
            else:
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
    # prettified_code = str(dita_soup)

    target_file_path = Path(target_file_path)
    target_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_file_path, "wb") as f:
        f.write(prettified_code.encode("utf-8"))


def convert_html_href_to_dita_href(href):
    if ".dita" in href:
        return href, "dita"
    if ".html" in href:
        parsed = urlparse(href)

        parsed = parsed._replace(path=sanitise_filename(parsed.path.replace(".html", ".dita")))
        p = Path(parsed.path)

        if parsed.fragment:
            id_str = p.name.split(".")[0]
            if "/" in id_str:
                id_str = id_str.split("/")[-1]
            new_fragment = f"{sanitise_filename(id_str, remove_extension=True)}/{parsed.fragment}"
            parsed = parsed._replace(fragment=new_fragment)

        url = parsed.geturl()

        # Prepend ./ to the URL if it's a URL in the same directory, so that
        # we don't get errors from Oxygen (without ./ is valid DITA but Oxygen complains)
        if not url.startswith("."):
            url = "./" + url

        return url, parsed.path.split(".")[-1]
    else:
        parsed = urlparse(href)
        return sanitise_filename(href), parsed.path.split(".")[-1]


def get_top_value(css_string):
    css = cssutils.css.CSSStyleDeclaration(css_string, validating=False)
    top = css.top

    if top == "":
        return None

    return int(top.replace("px", ""))


def generate_top_to_div_mapping(
    html_soup, include_anchors=False, recursive=True, ignore_graylayer=True
):
    top_to_div_mapping = {}

    if not recursive:
        # If this div only has one child, and that child is a PageLayer div
        # then process that div instead (ie. run the rest of the function on
        # that div, and get top values of divs inside that one instead)
        id_value = html_soup.get("id")
        direct_div_children = html_soup.find_all("div", recursive=False)
        if len(direct_div_children) == 1:
            id_value = direct_div_children[0].get("id")
            if id_value is not None and "PageLayer" in id_value:
                html_soup = direct_div_children[0]

    if include_anchors:
        all_bottom_layer_divs = html_soup.find_all(["div", "a"], recursive=recursive)
    else:
        all_bottom_layer_divs = html_soup.find_all("div", recursive=recursive)

    for bottom_layer_div in all_bottom_layer_divs:
        div_id = bottom_layer_div.get("id")
        # print(f"Processing div id = {div_id}")
        # Exclude GrayLayer divs and QuickLinksTable divs
        if ignore_graylayer and div_id and "GrayLayer" in div_id:
            continue
        elif div_id and "QuickLinksTable" in div_id:
            continue
        elif div_id and div_id.startswith("btnHist"):
            continue

        if ignore_graylayer:
            # Ignore anything that is inside a GrayLayer div (ie. has one as a parent)
            gray_layer = False
            parent_divs = bottom_layer_div.find_parents("div")
            if parent_divs:
                for parent_div in parent_divs:
                    parent_div_id = parent_div.get("id")
                    if parent_div_id and "GrayLayer" in parent_div_id:
                        gray_layer = True

            # print(f"Gray layer = {gray_layer}")
            if gray_layer:
                continue

        # Ignore ones without a style attribute as they can't have a top value
        style_attrib = bottom_layer_div.get("style")
        if style_attrib is None:
            continue

        top_value = get_top_value(bottom_layer_div["style"])

        if top_value:
            while top_value in top_to_div_mapping.keys():
                top_value += 1
            top_to_div_mapping[top_value] = bottom_layer_div

    top_to_div_mapping = sorted(top_to_div_mapping.items())

    if len(top_to_div_mapping) == 0:
        return [(0, html_soup)]

    return top_to_div_mapping


def add_if_not_a_child_or_parent_of_existing(pages_to_process, new_page):
    is_child = False
    for existing_page in pages_to_process:
        if existing_page is None:
            continue

        children = existing_page.find_all()
        if new_page in children:
            logging.debug("Found in children")
            is_child = True
            break

    for existing_page in pages_to_process:
        if existing_page is None:
            continue
        parents = existing_page.find_parents()
        if new_page in parents:
            logging.debug("Found in parents")
            pages_to_process.remove(existing_page)
            pages_to_process.add(new_page)
            return pages_to_process

    if not is_child:
        pages_to_process.add(new_page)

    # This is weird - the set doesn't seem to be keeping things unique properly, so we get around it
    # by converting to a list and then back to a set. This shouldn't be needed, but seems to fix the problem
    return set(list(pages_to_process))


def does_image_links_table_exist(path):
    with open(path, "r") as f:
        html_string = f.read()

    # set Beautifulsoup objects to parse the HTML file
    soup = BeautifulSoup(html_string, "html.parser")

    # Parse the HTML string, parser the <map> and the <img> elements
    img_links_table = soup.find("div", {"id": "ImageLinksTable"})
    title = soup.find("h2")
    country_flag = title.find_next("img")["src"]

    if img_links_table is None:
        return False
    else:
        return True


def sanitise_filename(filename, remove_extension=False, directory=False):
    filename = str(filename).replace(" ", "_").replace("&", "and").replace("(", "").replace(")", "")
    p = Path(filename)
    basename = str(p.name)

    # print(f"Sanitising filename {basename}")

    if basename[0].isdigit():
        basename = "_" + basename

    if not directory:
        if remove_extension:
            basename = basename.split(".")[0]
        else:
            # Make the extension lower case
            path_obj = Path(basename)
            basename = str(path_obj.with_suffix(path_obj.suffix.lower()))

    new_full_path = str(p.with_name(basename))
    new_full_path = new_full_path.replace("\\", "/")

    return new_full_path


def is_button_id(div_id):
    if div_id == "btn":
        return True
    elif div_id == "btnHist":
        return True
    elif div_id.startswith("btn") and len(div_id) == 4:
        return True
    elif div_id.startswith("btnHist") and len(div_id) == 8:
        return True
    elif div_id.startswith("bt") and len(div_id) == 3:
        return True
    else:
        return False


def is_skippable_div_id(div_id):
    SKIPPABLE_DIV_IDS = ["submitButtons", "templateDetails", "pageDetails", "Layer", "GrayLayer"]
    for skip_id in SKIPPABLE_DIV_IDS:
        if div_id.startswith(skip_id):
            return True

    return False
