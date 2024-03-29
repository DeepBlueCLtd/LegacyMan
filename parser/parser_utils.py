from collections import namedtuple
import shutil
from urllib.parse import urlparse
import xml.dom.minidom
import os
import copy
from bs4 import BeautifulSoup, NavigableString
from pathlib import Path
import cssutils
import logging
import re
import bs4

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
    # prettified_code = prettify_xml(str(dita_soup))
    prettified_code = str(dita_soup)

    target_file_path = Path(sanitise_filename(target_file_path))
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
    if css_string is None:
        return None

    css = cssutils.css.CSSStyleDeclaration(css_string, validating=False)
    top = css.top

    if top == "":
        return None

    return int(top.replace("px", ""))


def generate_top_to_div_mapping(
    html_soup, include_anchors=False, recursive=True, ignore_graylayer=True, filename=""
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
        if "hidden" in style_attrib:
            continue

        top_value = get_top_value(bottom_layer_div["style"])

        if top_value is not None:
            while top_value in top_to_div_mapping.keys():
                top_value += 1
            top_to_div_mapping[top_value] = bottom_layer_div

    top_to_div_mapping = sorted(top_to_div_mapping.items())

    # If there are no top values at all then just return the whole lot with a fake
    # top value of 0
    if len(top_to_div_mapping) == 0:
        return [(0, html_soup)]

    # Otherwise, look for all elements that don't have a top value
    # and also aren't just a <p> or a <h1> containing spaces (including nbsps)
    all_elements = html_soup.find_all(recursive=False)
    elements_without_top_value = []
    for el in all_elements:
        if el.name in ("p", "h1") and el.text.strip() == "":
            continue
        top_value = get_top_value(el.get("style"))
        if top_value is None:
            elements_without_top_value.append(el)

    # If we get here then there are definitely some elements with top values (because otherwise we'd have
    # exited in an earlier if statement), so we check if there are some elements without top values
    # and raise a warning if so
    if len(elements_without_top_value) > 0 and len(html_soup.find_all(recursive=False)) > 1:
        # logging.warning(
        #     f"Elements with no top value found inside element with ID {html_soup.get('id')} in file {filename}"
        # )
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

    if img_links_table is None:
        return False
    else:
        return True


def sanitise_filename(filename, remove_extension=False, directory=False):
    filename = str(filename).replace(" ", "_").replace("&", "and").replace("(", "").replace(")", "")
    p = Path(filename)
    basename = str(p.name)

    if basename == "":
        return str(p).replace("\\", "/")

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
    SKIPPABLE_DIV_IDS = [
        "submitButtons",
        "templateDetails",
        "pageDetails",
        "Layer",
        "GrayLayer",
        "header",
        "ClickOnThePic",
    ]
    for skip_id in SKIPPABLE_DIV_IDS:
        if div_id.startswith(skip_id):
            return True

    return False


def get_top_value_for_page(page):
    style = page.get("style")
    if style:
        top = get_top_value(style)

    if top:
        return top
    else:
        return 0


def append_caption_if_needed(page, top_to_div_mapping):
    if page is None:
        return

    CLICK_PICTURE_TEXT = "Click the picture to return to previous page."
    if page.name == "div" and page.has_attr("id") and page["id"].startswith("image"):
        # If it's just an image div then look for an associated caption div and add it
        page_top_value = get_top_value_for_page(page)
        # Get a mapping just for potential caption divs
        caption_top_to_div_mapping = {
            int(key): value
            for key, value in top_to_div_mapping
            if value.has_attr("id") and "ClickOnThePic" in value.get("id")
        }
        selected_caption = None
        # Loop through until we find a relative top value (relative to the page top value)
        # that is greater than -100 (ie. shortly before it, or after it on the page)
        # and not more than 1000 pixels below it
        # print(f"items:{caption_top_to_div_mapping}")
        caption_before = False
        for key, value in caption_top_to_div_mapping.items():
            rel_top_value = key - page_top_value
            # print(f"key:{key} {page_top_value} {rel_top_value}")
            if rel_top_value < -100:
                # caption too far above
                # print("too far above")
                continue
            elif rel_top_value < 0:
                # caption could be above image
                # print("immediately above")
                selected_caption = value
                caption_before = True
                break
            elif rel_top_value < 700:
                # print("below")
                # caption not too far below image
                selected_caption = value
                break

        # Replace the "Click the picture..." text if it exists in the caption
        if selected_caption is not None and CLICK_PICTURE_TEXT in selected_caption.get_text():
            for el in selected_caption.find_all():
                if el.string is not None:
                    if CLICK_PICTURE_TEXT in el.string:
                        el.string = el.string.replace(CLICK_PICTURE_TEXT, "")
                else:
                    for c in el.contents:
                        if type(c) is NavigableString:
                            if CLICK_PICTURE_TEXT in c.string:
                                c.string.replace_with(c.string.replace(CLICK_PICTURE_TEXT, ""))

        if selected_caption is not None:
            if caption_before:
                page.insert(0, selected_caption)
            else:
                page.append(selected_caption)


def is_empty_p_element(el):
    if el is None:
        return False
    elif el.name == "p" and el.text.strip() == "" and len(el.find_all()) == 0:
        return True
    elif el.name == "br":
        return True
    else:
        return False


def next_sibling_tag(el):
    next_sib = el.next_sibling
    while type(next_sib) is bs4.element.NavigableString:
        next_sib = next_sib.next_sibling

    return next_sib


def is_floating_div_or_span(el):
    if el.name in ("div", "span") and el.has_attr("style"):
        bl_parents = el.find_parents(id=re.compile("BottomLayer"))
        if len(bl_parents) > 0:
            if el.has_attr("id") and "PageLayer" in el["id"]:
                return False
            css = el.get("style")
            top_value = get_top_value(css)
            if top_value is not None:
                return True
    return False


def remove_style_recursively(el):
    del el["style"]
    for child_el in el.find_all(recursive=False):
        del child_el["style"]


def get_whole_page_top_value(el):
    running_top_value = 0

    while el.name != "body":
        if el.has_attr("style"):
            top_value = get_top_value(el["style"])
            if top_value is not None:
                running_top_value += top_value
        el = el.parent
        if el is None:
            break

    return running_top_value


FloatingElement = namedtuple("FloatingElement", ["element", "top"])
BlankSpaceElements = namedtuple("BlankSpaceElements", ["elements", "top"])


def get_floating_elements(html):
    floating_elements = html.find_all(is_floating_div_or_span)

    floating_elements = [
        FloatingElement(element=el, top=get_whole_page_top_value(el)) for el in floating_elements
    ]

    floating_elements = sorted(floating_elements, key=lambda el: el.top)

    return floating_elements


def get_blank_spaces(html):
    p_elements = html.find_all("p")

    blank_elements = []
    i = 0
    while i < len(p_elements):
        el = p_elements[i]
        count = 0
        # If it's not an empty p element then skip to next one in the list
        if not is_empty_p_element(el):
            i += 1
            continue
        # If we've got here then it is an empty p element
        while is_empty_p_element(next_sibling_tag(el)):
            count += 1
            el = next_sibling_tag(el)
        if count > 0:
            i += count
        if count >= 3:
            # print(f"i = {i}, count = {count}, start = {i - (count)}, end = {i + 1}")
            chosen_elements = p_elements[i - (count) : i]
            top_value = get_whole_page_top_value(chosen_elements[0])
            if top_value != 0:
                bse = BlankSpaceElements(elements=chosen_elements, top=top_value)

                blank_elements.append(bse)
        else:
            i += 1
    return blank_elements


CountryFlag = namedtuple("CountryFlag", ["path", "width", "height"])
