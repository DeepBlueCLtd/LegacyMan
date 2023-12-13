from collections import defaultdict
from pathlib import Path
import platform
import shutil
import sys
import time
import re
import os
import subprocess
from urllib.parse import urlparse
import bs4
from bs4 import BeautifulSoup
from pprint import pprint, pformat
from html_to_dita import htmlToDITA
import time
import logging
import json
import argparse
from html_to_dita import convert_html_table_to_dita_table


from parser_utils import (
    delete_directory,
    copy_files,
    remove_leading_slashes,
    write_prettified_xml,
    convert_html_href_to_dita_href,
    get_top_value,
    generate_top_to_div_mapping,
    add_if_not_a_child_or_parent_of_existing,
    sanitise_filename,
    is_button_id,
    is_skippable_div_id,
    does_image_links_table_exist,
)

FIRST_PAGE_LAYER_MARKER = "##### First Page Layer"


class Parser:
    def __init__(self, root_path, target_path_base):
        self.root_path = root_path
        self.target_path_base = target_path_base
        self.link_tracker = defaultdict(set)
        self.files_already_processed = set()
        self.only_process_single_file = False
        self.warn_on_blank_runs = False

    def process_regions(self):
        # copy the world-map.gif file
        source_dir = f"{self.root_path}/PlatformData/Content/Images/"
        target_dir = "target/dita/regions/PlatformData/Content/Images"
        worldMapFile = "WorldMap.jpg"
        copy_files(source_dir, target_dir, [worldMapFile])

        # read the PD_1.html file
        with open(f"{self.root_path}/PlatformData/PD_1.html", "r") as f:
            html_string = f.read()

        # set Beautifulsoup objects to parse HTML and DITA files
        soup = BeautifulSoup(html_string, "html.parser")

        dita_doctype = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">'
        dita_soup = BeautifulSoup(dita_doctype, "lxml-xml")

        # Parse the HTML string, parser the <map> and the <img> elements
        img_element = soup.find("img", {"usemap": "#image3Map"})
        map_element = soup.find("map", {"name": "image3Map"})

        # Create the html <image> element in the DITA file
        dita_image = dita_soup.new_tag("image")
        dita_image["href"] = sanitise_filename(img_element["src"])

        dita_image_alt = dita_soup.new_tag("alt")
        dita_image_alt.string = "World Map"
        dita_image.append(dita_image_alt)

        # Create the DITA document type declaration string

        # Create a body,title and imagemap elements
        dita_body = dita_soup.new_tag("body")
        dita_imagemap = dita_soup.new_tag("imagemap")
        dita_title = dita_soup.new_tag("title")
        dita_title.string = "Regions"

        # Append the image and the map in the imagemap
        dita_imagemap.append(dita_image)
        for area in map_element.find_all("area"):
            dita_shape = dita_soup.new_tag("shape")
            dita_shape.string = area["shape"]

            dita_coords = dita_soup.new_tag("coords")
            dita_coords.string = area["coords"]

            dita_xref = dita_soup.new_tag("xref")
            dita_xref["format"] = "dita"
            dita_xref["href"] = "./regions.dita"

            # if link starts with ../ create a dita file for the country => example ../Britain/Britain1.html
            link = area["href"]
            country = area["alt"]

            if link.startswith("../"):
                country_name = sanitise_filename(
                    os.path.dirname(remove_leading_slashes(link)), directory=True
                )
                country_path = self.process_ns_countries(
                    country, country_name, remove_leading_slashes(link)
                )
                dita_xref["href"] = f"../{country_path}"
            else:
                sub_region_path = self.process_sub_region(self.root_path / "PlatformData" / link)
                dita_xref["href"] = sub_region_path

            dita_area = dita_soup.new_tag("area")
            dita_area.append(dita_shape)
            dita_area.append(dita_coords)
            dita_area.append(dita_xref)
            dita_imagemap.append(dita_area)

        dita_body.append(dita_imagemap)

        # Create a <topic> element in the DITA file and append the <map> and the <image> elements
        dita_topic = dita_soup.new_tag("topic")
        dita_topic["id"] = "PD_1"

        dita_topic.append(dita_title)

        dita_shortdesc = dita_soup.new_tag("shortdesc")
        shortdesc = soup.find(id="short-description")
        if shortdesc:
            dita_shortdesc.string = shortdesc.text.strip()

        dita_topic.append(dita_shortdesc)
        dita_topic.append(dita_body)

        # Find all the QuickLinks tables and extract their link text and href
        # We find them by finding all divs with an id that includes the text QuickLinksTable (gets QLT, QLT1, QLT2 etc)
        # and get all their links
        ql_divs = soup.findAll("div", id=re.compile("QuickLinksTable"))
        links = []

        for ql_div in ql_divs:
            links.extend(ql_div.findAll("a"))

        quicklinks = {l.text: l["href"] for l in links}

        related_links = self.process_quicklinks_table(dita_soup, quicklinks, dita_topic["id"])
        if related_links:
            dita_topic.append(related_links)

        bodylink_hrefs = []
        a_tags = soup.find_all("a")
        for a_tag in a_tags:
            parent_pagelayer = a_tag.find_parent("div", id=re.compile("PageLayer"))
            parent_layer = a_tag.find_parent("div", id=re.compile("^layer"))
            if parent_pagelayer or parent_layer:
                if a_tag.get("href"):
                    bodylink_hrefs.append(a_tag["href"])

        all_links = list(quicklinks.values()) + bodylink_hrefs
        self.track_all_links(all_links, Path(f"{self.root_path}/PlatformData/PD_1.html"))

        # Append the <topic> element to the BeautifulSoup object
        dita_soup.append(dita_topic)

        # create /target/dita/regions dir
        regions_path = "target/dita/regions"
        os.makedirs(regions_path, exist_ok=True)

        write_prettified_xml(dita_soup, f"{regions_path}/PlatformData/PD_1.dita")
        self.files_already_processed.add(f"{regions_path}/PlatformData/PD_1.dita")

    def process_sub_region(self, link):
        with open(link, "r") as f:
            html_string = f.read()

        # set Beautifulsoup objects to parse the HTML file
        html_soup = BeautifulSoup(html_string, "html.parser")

        dita_doctype = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">'
        dita_soup = BeautifulSoup(dita_doctype, "xml")

        divs_with_no_id = html_soup.find_all("div", id="")
        table = None
        for div in divs_with_no_id:
            table = div.find("table")
            if table:
                break
        if table:
            a_tags = table.find_all("a")
            for a_tag in a_tags:
                href = a_tag["href"]
                if href == "#":
                    # Empty link
                    continue
                path = href.replace("../", "")
                country_name = sanitise_filename(
                    os.path.dirname(remove_leading_slashes(str(href))), directory=True
                )
                # Work out whether it's a Non-Standard country or a Standard Country
                # by looking for the Image Links Table
                if does_image_links_table_exist(self.root_path / path):
                    self.process_ns_countries(country_name, country_name, href.replace("../", ""))
                else:
                    country_flag_link = ""
                    self.process_category_pages(
                        href,
                        remove_leading_slashes(os.path.dirname(href)),
                        country_name,
                        country_flag_link,
                    )

        dita_topic = dita_soup.new_tag("topic")
        dita_topic["id"] = Path(sanitise_filename(Path(link).name, remove_extension=True))

        dita_title = dita_soup.new_tag("title")
        dita_title.string = "Regions"

        dita_body = dita_soup.new_tag("body")

        for div in divs_with_no_id:
            converted_content = htmlToDITA(div, dita_soup, "test", "div")
            dita_body.append(converted_content)

        dita_topic.append(dita_title)
        dita_topic.append(dita_body)
        dita_soup.append(dita_topic)

        output_path = Path(self.make_relative_to_data_dir(Path(link))).with_suffix(".dita")
        write_prettified_xml(dita_soup, self.target_path_base / output_path)
        self.files_already_processed.add(self.target_path_base / output_path)

        # note: on MS-Win, the path generator produces windows slashes, but
        # DITA expects URL-style slashes

        return_value = str(output_path).replace("\\", "/").replace("PlatformData/", "")
        return return_value

    def process_ns_countries(self, country, country_name, link):
        """Processes a non-standard country - ie. one that has an extra page at the start with links to various categories,
        and then those category pages have the actual information"""
        logging.debug(f"Called process_ns_countries with args {country}, {country_name}, {link}")
        # read the html file
        with open(f"{self.root_path}/{link}", "r") as f:
            html_string = f.read()

        # set Beautifulsoup objects to parse the HTML file
        soup = BeautifulSoup(html_string, "html.parser")

        # Parse the HTML string, parser the <map> and the <img> elements
        img_links_table = soup.find("div", {"id": "ImageLinksTable"})
        title = soup.find("h2")
        country_flag = title.find_next("img")["src"]

        if img_links_table is None:
            # terminate early. Our high level processing has gone wrong
            # if we encounter a NS Country page without an ImageLinksTable
            raise ValueError("ImageLinksTable not found in the HTML file")

        # Create the DITA document type declaration string
        dita_doctype = (
            '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
        )
        dita_soup = BeautifulSoup(dita_doctype, "xml")

        # Create dita elements: <reference>,<title>,<table>,<tbody>,<tgroup>...
        dita_reference = dita_soup.new_tag("reference")
        dita_reference["id"] = country

        dita_title = dita_soup.new_tag("title")
        dita_title.string = country
        dita_reference.append(dita_title)

        # Create DITA elements tbody,row,xref,b,table
        dita_tbody = dita_soup.new_tag("tbody")
        dita_tgroup = dita_soup.new_tag("tgroup")
        dita_tgroup["cols"] = "2"

        dita_table = dita_soup.new_tag("table")
        dita_body = dita_soup.new_tag("refbody")

        # Create the dir to store the content and the dita files for countries
        regions_path = f"target/dita/regions"
        country_path = f"{regions_path}/{country_name}"
        os.makedirs(country_path, exist_ok=True)

        for index, tr in enumerate(img_links_table.find_all("tr")):
            dita_row = dita_soup.new_tag("row")

            for a in tr.find_all("a"):
                category_href = a["href"].replace(".html", ".dita")

                dita_xref = dita_soup.new_tag("xref")
                dita_xref["href"] = category_href
                dita_xref["format"] = "dita"

                dita_bold = dita_soup.new_tag("b")
                dita_bold.string = a.text.strip()

                dita_img = dita_soup.new_tag("image")

                # if we're in second row, put text label after image
                if index == 0:
                    dita_xref.append(dita_bold)

                dita_entry = dita_soup.new_tag("entry")
                dita_entry.append(dita_xref)

                dita_row.append(dita_entry)

                # Process category pages from this file
                category_page_link = a["href"]
                category = remove_leading_slashes(os.path.dirname(category_href))

                self.process_category_pages(
                    category_page_link,
                    category,
                    country_name,
                    country_flag,
                )

                # Copy each category images to /dita/regions/$Category_Name/Content/Images dir
                if a.find("img") is not None:
                    src_img_file = os.path.basename(a.find("img")["src"])
                    img_src_dir = f"{self.root_path}/{os.path.dirname(category_page_link.replace('../', ''))}/Content/Images"
                    img_target_dir = f"{regions_path}/{category}/Content/Images"
                    copy_files(img_src_dir, img_target_dir, [src_img_file])

                    dita_img["href"] = sanitise_filename(
                        f'../{category}/Content/Images/{os.path.basename(a.img["src"])}'
                    )
                    if a.img.has_attr("height"):
                        dita_img["height"] = a.img["height"]
                    if a.img.has_attr("width"):
                        dita_img["width"] = a.img["width"]
                    dita_xref.append(dita_img)

                    # if we're in second row, put text label after image
                    if index == 1:
                        dita_xref.append(dita_bold)

            dita_tbody.append(dita_row)

        dita_tgroup.append(dita_tbody)
        dita_table.append(dita_tgroup)
        dita_body.append(dita_table)
        dita_reference.append(dita_body)

        # Find all the QuickLinks tables and extract their link text and href
        # We find them by finding all divs with an id that includes the text QuickLinksTable (gets QLT, QLT1, QLT2 etc)
        # and get all their links
        ql_divs = soup.findAll("div", id=re.compile("QuickLinksTable"))
        links = []

        for ql_div in ql_divs:
            links.extend(ql_div.findAll("a"))

        quicklinks = {l.text: l["href"] for l in links}

        related_links = self.process_quicklinks_table(dita_soup, quicklinks, dita_reference["id"])
        if related_links:
            dita_reference.append(related_links)

        # Append the reference element to the dita_soup object
        dita_soup.append(dita_reference)

        # Copy each country images to /dita/regions/$Country_name/Content/Images dir
        source_dir = f"{self.root_path}/{country_name}/Content/Images"
        copy_files(source_dir, f"{country_path}/Content/Images")

        output_path = str(Path(link).with_suffix(".dita"))
        write_prettified_xml(dita_soup, self.target_path_base / output_path)
        self.files_already_processed.add(self.target_path_base / output_path)

        # note: on MS-Windows a MS-Win slash is generated, but DITA requires URL-style slashes
        return output_path.replace("\\", "/")

    def process_category_pages(
        self,
        category_page_link,
        category,
        country_name,
        country_flag_link,
    ):
        logging.debug(
            f"Called process_category_pages with category_page_link = {category_page_link}, country_flag_link = {country_flag_link}"
        )
        # read the category page
        with open(f"{self.root_path}/{remove_leading_slashes(category_page_link)}", "r") as f:
            category_page_html = f.read()

        soup = BeautifulSoup(category_page_html, "html.parser")

        # If there is an empty div with an ID of "handle_as_generic" then this should be handled as a generic
        # page, not as a category page.
        # Note we need to add the FIRST_PAGE_LAYER_MARKER for this page to the list of pages to extract
        # before we call process_generic_file, or nothing will be extracted
        handle_as_generic_div = soup.find_all("div", id="handle_as_generic")
        if len(handle_as_generic_div) == 1:
            path = f"{self.root_path}/{remove_leading_slashes(category_page_link)}"
            filepath = self.make_relative_to_data_dir(Path(path)).resolve()
            self.link_tracker[str(filepath)].add(FIRST_PAGE_LAYER_MARKER)
            self.process_generic_file(path)
            return

        if country_flag_link == "" or country_flag_link is None:
            title = soup.find("h2")
            country_flag_link = title.find_next("img")["src"]

        # Find a <td> with colspan=7, this indicates that the page is a category page
        td = soup.find("td", {"colspan": "7"})
        title = soup.find("h2")
        topic_id = sanitise_filename(title.text)

        if td is None:
            # This used to be a workaround for not dealing with a page without a <td> with colspan 7,
            # it shouldn't be needed now, but is kept as a fallback error in case we find something
            # we can't handle
            print(f"<td> element with colspan 7 not found in the {category_page_link} file")
            return

        # Create the DITA document type declaration string
        dita_doctype = (
            '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
        )
        dita_soup = BeautifulSoup(dita_doctype, "xml")
        dita_refbody = dita_soup.new_tag("refbody")
        dita_reference = dita_soup.new_tag("reference")
        dita_section = dita_soup.new_tag("section")
        dita_flagsection = dita_soup.new_tag("section")
        dita_emptytitle = dita_soup.new_tag("title")
        dita_emptytitle2 = dita_soup.new_tag("title")

        dita_shortdesc = dita_soup.new_tag("shortdesc")

        # Create dita elements for <tgroup>,<table>, <tbody> ...
        dita_tbody = dita_soup.new_tag("tbody")
        dita_tgroup = dita_soup.new_tag("tgroup")
        dita_table = dita_soup.new_tag("table")
        # format attributes to show table borders
        dita_table["colsep"] = "1"
        dita_table["rowsep"] = "1"
        dita_table["frame"] = "all"
        dita_table["outputclass"] = "category"

        dita_title = dita_soup.new_tag("title")
        dita_image = dita_soup.new_tag("image")
        dita_fig = dita_soup.new_tag("fig")

        shortdesc = soup.find(id="short-description")
        if shortdesc:
            dita_shortdesc.string = shortdesc.text.strip()

        # Get table columns <td> from the second row <tr> (the first <tr> is used for title so we can't get the column count from it)
        parent_table = td.find_parent("table")
        tr_list = parent_table.find_all("tr")
        second_tr_element = tr_list[1]
        table_columns = second_tr_element.find_all("td")
        dita_tgroup["cols"] = len(table_columns)

        # TODO: change the href of the image
        dita_image["href"] = sanitise_filename(
            f"../{country_name}/{remove_leading_slashes(country_flag_link)}"
        )
        dita_image["id"] = "flag"

        # create folder for category pages
        category_path = f"target/dita/regions/{sanitise_filename(category, directory=True)}"
        os.makedirs(category_path, exist_ok=True)

        dita_table = convert_html_table_to_dita_table(parent_table, dita_soup, topic_id)

        # Go through the original HTML table and process all the links
        # by calling process_generic_file on them
        # Note: This is what was done by the original manual table parsing code here
        # We have replaced that with the convert_html_table_to_dita_table as it deals with all the edge cases
        # and then taken this part out and run it separately
        for a in parent_table.find_all("a"):
            if a.has_attr("href"):
                href = a.get("href")
                href = href.split(".html")[0] + ".html"
                class_file_src_path = f"{self.root_path}/{os.path.dirname(remove_leading_slashes(category_page_link))}/{href}"

                if not self.only_process_single_file:
                    self.process_generic_file(class_file_src_path)

        dita_section.append(dita_emptytitle)
        dita_section.append(dita_table)
        dita_refbody.append(dita_section)

        # Append the <title>,<flag> and <refbody> elements in the <reference>
        dita_title.string = title.text.strip()

        dita_fig.append(dita_image)
        dita_flagsection["id"] = "flag-section"
        dita_flagsection.append(dita_emptytitle2)
        dita_flagsection.append(dita_fig)
        dita_refbody.insert(0, dita_flagsection)

        dita_reference["id"] = topic_id
        dita_reference.append(dita_title)
        dita_reference.append(dita_shortdesc)
        dita_reference.append(dita_refbody)

        # Find all the QuickLinks tables and extract their link text and href
        # We find them by finding all divs with an id that includes the text QuickLinksTable (gets QLT, QLT1, QLT2 etc)
        # and get all their links
        ql_divs = soup.findAll("div", id=re.compile("QuickLinksTable"))
        links = []

        for ql_div in ql_divs:
            links.extend(ql_div.findAll("a"))

        quicklinks = {l.text: l["href"] for l in links}

        related_links = self.process_quicklinks_table(dita_soup, quicklinks, dita_reference["id"])
        if related_links:
            dita_reference.append(related_links)

        bodylink_hrefs = []
        a_tags = soup.find_all("a")
        for a_tag in a_tags:
            parent_pagelayer = a_tag.find_parent("div", id=re.compile("PageLayer"))
            parent_layer = a_tag.find_parent("div", id=re.compile("^layer"))
            if parent_pagelayer or parent_layer:
                if a_tag.get("href"):
                    bodylink_hrefs.append(a_tag["href"])

        all_links = list(quicklinks.values()) + bodylink_hrefs
        self.track_all_links(
            all_links, Path(f"{self.root_path}/{remove_leading_slashes(category_page_link)}")
        )

        # Append the whole page to the dita soup
        dita_soup.append(dita_reference)

        # Copy the category images to /dita/regions/$category_name/Content/Images folder
        category_page_link = remove_leading_slashes(category_page_link.replace(".html", ".dita"))
        source_img_dir = f"{self.root_path}/{os.path.dirname(category_page_link)}/Content/Images"
        target_img_dir = f"{category_path}/Content/Images"
        copy_files(source_img_dir, target_img_dir)

        category_file_path = f"{category_path}/{os.path.basename(category_page_link)}"
        write_prettified_xml(dita_soup, category_file_path)
        self.files_already_processed.add(category_file_path)

        input_file_path = Path(f"{self.root_path}/{remove_leading_slashes(category_page_link)}")
        input_file_directory = input_file_path.parent

        for _, href in quicklinks.items():
            clean_href = href.split("#")[0]
            link_path = (input_file_directory / clean_href).resolve()
            if link_path.exists():
                self.process_generic_file(link_path)
            else:
                logging.error(
                    f"File {link_path} doesn't exist, linked in the QuickLinks table from {input_file_path}"
                )

    def process_generic_file_pagelayer(self, dita_soup, page, topic_id, filename=""):
        # Exclude links that are in divs just for buttons, as they're not proper links they're just things that go
        # back to the map etc
        if page.name == "div":
            div_id = page.get("id")
            if div_id is not None and is_button_id(div_id):
                return None

        dita_section_title = dita_soup.new_tag("title")

        # find the first heading
        headers = ["h1", "h2", "h3", "h4", "h5"]
        for element in page.children:
            if element.name in headers:
                dita_section_title.string = element.text
                break

        top_to_div_mapping = generate_top_to_div_mapping(page, recursive=False, filename=filename)
        converted_bits = []
        for _, sub_div in top_to_div_mapping:
            # process the content in html to dita. Note: since this is a non-class
            # file, we instruct `div` elements to remain as `div`
            converted_soup = htmlToDITA(sub_div, dita_soup, topic_id, "div")
            if converted_soup:
                converted_bits.append(converted_soup)

        # create the new `section`
        dita_section = dita_soup.new_tag("section")

        # insert title
        dita_section.append(dita_section_title)

        # insert rest of converted content
        dita_section.extend(converted_bits)

        def is_empty_p_element(el):
            if el is None:
                return False
            elif el.name == "p" and el.text.strip() == "" and len(el.find_all()) == 0:
                return True
            else:
                return False

        def next_sibling_tag(el):
            next_sib = el.next_sibling
            while type(next_sib) is bs4.element.NavigableString:
                next_sib = next_sib.next_sibling

            return next_sib

        # Check for repeated <p>&nbsp;</p> elements
        p_elements = page.find_all("p")
        empty_p_elements = list(filter(is_empty_p_element, p_elements))

        found = False
        for el in empty_p_elements:
            count = 0
            while is_empty_p_element(next_sibling_tag(el)):
                count += 1
                if count >= 4:
                    found = True
                    break
            if found and self.warn_on_blank_runs:
                logging.warning(
                    f"Found string of repeated <p>&nbsp;</p> elements in div with ID {page.get('id')} in file {filename}"
                )
                break

        return dita_section

    def find_first_page_layer(self, top_to_div_mapping, html_soup):
        page = None
        if len(top_to_div_mapping) > 0:
            logging.debug({el[0]: el[1].get("id") for el in top_to_div_mapping})
            for top_value, div in top_to_div_mapping:
                # Don't look at any divs that are within a BottomLayer or PageLayer div
                bl_parents = div.find_parents(id=re.compile("BottomLayer|PageLayer"))
                if len(bl_parents) > 0:
                    continue
                div_id = div.get("id")
                # Don't look at any divs without an ID
                if div_id is None:
                    continue
                # Ignore divs with an id of btN (where N is a number) as they're just buttons
                if is_button_id(div_id):
                    continue
                if is_skippable_div_id(div_id):
                    continue
                if div.has_attr("style") and "hidden" in div["style"]:
                    continue

                image_tags = div.find_all("img")
                div_text = div.get_text().strip()
                if div_id is not None and "PicLayer" in div_id:
                    continue
                # Skip any divs that just have an image020 image in them - that's just the corporate logo
                if len(image_tags) == 1 and "image020" in image_tags[0]["src"] and div_text == "":
                    continue
                logging.debug(
                    f"top_value = {top_value}, div_id = {div_id}, n_image_tags = {len(image_tags)}"
                )
                text = div.get_text().strip()
                if len(image_tags) > 0:
                    page = div
                    break
                elif text != "" and text != "Return to map":
                    page = div
                    break
                elif div_id is not None and "PageLayer" in div_id:
                    page = div
                    break

        if page is None:
            page = html_soup.find("div", id=re.compile("PageLayer"))

        return page

    def process_generic_file_content(self, html_soup, input_file_path, quicklinks):
        # Create the DITA document type declaration string
        dita_doctype = (
            '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
        )
        dita_soup = BeautifulSoup(dita_doctype, "xml")

        # create document level elements
        dita_reference = dita_soup.new_tag("reference")
        topic_id = Path(
            sanitise_filename(input_file_path.name, remove_extension=True)
        )  # remove spaces, to make legal ID value
        dita_reference["id"] = topic_id
        dita_title = dita_soup.new_tag("title")

        # Try and extract the title from a div with an id of Title*
        title_tags = html_soup.find_all(id=re.compile("Title"))
        title_tags = sorted(title_tags, key=lambda tag: tag.get("id"))
        try:
            dita_title.string = title_tags[0].get_text()
        except Exception:
            # If we fail then take the first div we can find that just has one h2 child
            h2s = html_soup.select("div > h2")
            for h2 in h2s:
                children_of_parent = h2.parent.find_all()
                if len(children_of_parent) == 1:
                    dita_title.string = h2.get_text()
                    break
            else:
                # If that also fails, then take the first h1 and use that, giving an error if there aren't any
                h1s = html_soup.find_all("h1")
                if len(h1s) >= 1:
                    dita_title.string = h1s[0].get_text()
                else:
                    logging.warning(f"Could not extract title from {input_file_path}")

        dita_reference.append(dita_title)

        dita_shortdesc = dita_soup.new_tag("shortdesc")
        shortdesc = html_soup.find(id="short-description")
        if shortdesc:
            dita_shortdesc.string = shortdesc.text.strip()

        dita_reference.append(dita_shortdesc)
        dita_ref_body = dita_soup.new_tag("refbody")

        if self.write_generic_files:
            sections = []
            key = str(Path(input_file_path).resolve().relative_to(self.root_path))
            anchors_to_export = self.link_tracker[key]
            pages_to_process = set()
            top_to_div_mapping = generate_top_to_div_mapping(
                html_soup, recursive=True, filename=input_file_path
            )
            for anchor in anchors_to_export:
                if anchor == FIRST_PAGE_LAYER_MARKER:
                    page = self.find_first_page_layer(top_to_div_mapping, html_soup)
                    if page:
                        logging.debug(
                            f"Selected page for First Page Layer with id {page.get('id')}"
                        )
                        pages_to_process = add_if_not_a_child_or_parent_of_existing(
                            pages_to_process, page
                        )
                    continue

                a_elements = html_soup.find_all("a", attrs={"name": anchor})
                div_elements = html_soup.find_all(["div", "h3"], id=anchor)
                all_elements = a_elements + div_elements

                if len(all_elements) == 0:
                    logging.warning(f"Cannot find anchor {anchor} in page {input_file_path}")
                    continue
                elif len(all_elements) == 1:
                    if all_elements[0].name == "div":
                        # Deal with the case where the ID given is for the div itself
                        if "PageLayer" in all_elements[0]["id"]:
                            page = all_elements[0]
                    else:
                        # Otherwise it's an <a> anchor, so we need to:
                        # 1. Get the CSS top value for the enclosing div
                        # 2. Get all top values for all BottomLayer divs
                        # 3. Find the closest higher top value in the document
                        # print(f"Dealing with anchor {anchor} in page {input_file_path}")
                        anchor = all_elements[0]
                        enclosing_div = anchor.find_parent("div")
                        if not enclosing_div:
                            logging.warning(
                                f"Could not find enclosing div for anchor {anchor} in file {input_file_path}"
                            )
                            continue
                        style_attrib = enclosing_div.get("style")
                        if not style_attrib:
                            logging.warning(
                                f"Could not find style attrib on enclosing div for anchor {anchor} in file {input_file_path}"
                            )
                            continue
                        enclosing_div_top_value = get_top_value(style_attrib)
                        if not enclosing_div_top_value:
                            logging.warning(
                                f"Enclosing div for anchor {anchor} has no top value in file {input_file_path}"
                            )
                            continue
                        # print(f"Enclosing div top value = {enclosing_div_top_value}")
                        page = None
                        # print(f"Enclosing div ID = {enclosing_div.get('id')}")
                        # print(f"Enclosing div top value = {enclosing_div_top_value}")
                        for top_value, bottom_layer_div in top_to_div_mapping:
                            div_id = bottom_layer_div.get("id")
                            if div_id:
                                # print(f"div id = {div_id}")
                                if (
                                    "BottomLayer" not in div_id
                                    and "PageLayer" not in div_id
                                    and "image" not in div_id
                                    and "layer" not in div_id
                                ):
                                    continue
                            # print(f"top_value = {top_value}")
                            # Skip any divs whose content is just a single img tag with the corporate logo in it
                            img_tags = bottom_layer_div.find_all("img")
                            if (
                                img_tags is not None
                                and len(img_tags) == 1
                                and "image020" in img_tags[0]["src"]
                            ):
                                continue
                            if top_value > enclosing_div_top_value:
                                # Check that the difference isn't too big
                                if top_value - enclosing_div_top_value < 800:
                                    page = bottom_layer_div
                                    # print(f"Found div top value = {top_value}")
                                    break
                        if not page:
                            top_to_div_mapping_with_graylayers = generate_top_to_div_mapping(
                                html_soup,
                                recursive=True,
                                ignore_graylayer=False,
                                filename=input_file_path,
                            )
                            for top_value, bottom_layer_div in top_to_div_mapping_with_graylayers:
                                div_id = bottom_layer_div.get("id")
                                # print(f"{top_value}: {div_id}")
                                if div_id:
                                    # print(f"div id = {div_id}")
                                    if "GrayLayer" not in div_id:
                                        continue
                                # print(f"top_value = {top_value}")
                                if top_value > enclosing_div_top_value:
                                    # Check that the difference isn't too big
                                    if top_value - enclosing_div_top_value < 500:
                                        page = bottom_layer_div
                                        page = page.find(id=re.compile("BottomLayer"))
                                        # print(f"Found div top value = {top_value}")
                                        break
                            if not page:
                                logging.warning(
                                    f"Couldn't find BottomLayer with appropriate top value - where top value is {enclosing_div_top_value}, in file {input_file_path}"
                                )
                                continue
                    if page is None:
                        logging.warning(
                            f"Couldn't find PageLayer parent of anchor {anchor} in page {input_file_path}"
                        )
                        continue

                    # See if there is already an element in the page that has a name containing the anchor value that we're
                    # processing (eg. "number2")
                    # If there isn't, then add an empty div at the top of this page with that anchor value in it
                    elements_with_id_of_anchor = page.find_all(attrs={"name": anchor["name"]})
                    if len(elements_with_id_of_anchor) == 0:
                        anchor_div = dita_soup.new_tag("div")
                        anchor_div["id"] = anchor["name"]
                        logging.debug(f"Inserting {anchor_div}")
                        page.insert(0, anchor_div)
                    pages_to_process = add_if_not_a_child_or_parent_of_existing(
                        pages_to_process, page
                    )
                else:
                    logging.warning(f"Multiple matches for anchor {anchor} in {input_file_path}")

            def get_top_value_for_page(page):
                style = page.get("style")
                if style:
                    top = get_top_value(style)

                if top:
                    return top
                else:
                    return 0

            pages_to_process = sorted(
                list(pages_to_process), key=lambda x: get_top_value_for_page(x)
            )

            for page in pages_to_process:
                try:
                    logging.debug(f"Processing sub-page {page['id']}")
                except Exception:
                    pass
                processed_page = self.process_generic_file_pagelayer(
                    dita_soup, page, topic_id, filename=input_file_path
                )
                if processed_page:
                    sections.append(processed_page)
        else:
            sections = []
            for page in html_soup.find_all("div"):
                if page.has_attr("id") and "PageLayer" in page["id"]:
                    processed_page = self.process_generic_file_pagelayer(
                        dita_soup, page, topic_id, filename=input_file_path
                    )
                    if processed_page:
                        sections.append(processed_page)

        dita_ref_body.extend(sections)

        dita_reference.append(dita_ref_body)

        related_links = self.process_quicklinks_table(dita_soup, quicklinks, topic_id)

        if related_links:
            dita_reference.append(related_links)
        dita_soup.append(dita_reference)

        return dita_soup

    def process_quicklinks_table(self, dita_soup, quicklinks, topic_id, name="related-links"):
        # Generate related-links for quicklinks table
        related_links = dita_soup.new_tag(name, id="related-pages")

        if len(quicklinks) == 0:
            return None

        for link_text, link_href in quicklinks.items():
            link = dita_soup.new_tag("link")
            link["href"], extension = convert_html_href_to_dita_href(link_href)
            if link["href"].startswith("#"):
                # It's an internal link to somewhere else on the page
                link["href"] = f"#{topic_id}/{link['href'][1:]}"
                link["format"] = "dita"
            else:
                if extension != "dita":
                    link["format"] = extension
            linktext = dita_soup.new_tag("linktext")
            linktext.string = link_text
            link.append(linktext)
            related_links.append(link)

        return related_links

    def make_relative_to_data_dir(self, filepath):
        try:
            filepath = filepath.relative_to(self.root_path)
        except ValueError:
            filepath = filepath.relative_to(self.root_path.name)

        return filepath

    def track_all_links(self, all_links, input_file_path):
        for value in all_links:
            if value == "history.go(-1)":
                continue
            parsed = urlparse(value)

            if parsed.path:
                filepath = (input_file_path.parent / Path(parsed.path)).resolve()
                if filepath.suffix != ".html":
                    continue
            else:
                filepath = input_file_path.resolve()

            filepath = self.make_relative_to_data_dir(filepath)

            if parsed.fragment:
                self.link_tracker[str(filepath)].add(parsed.fragment)
            else:
                self.link_tracker[str(filepath)].add(FIRST_PAGE_LAYER_MARKER)

    def process_generic_file(self, input_file_path):
        if "PD_1" in str(input_file_path):
            return

        input_file_path = Path(input_file_path)
        input_file_directory = input_file_path.parent

        relative_input_file_directory = self.make_relative_to_data_dir(input_file_directory)
        target_path = self.target_path_base / sanitise_filename(
            relative_input_file_directory, directory=True
        )

        output_dita_path = (
            target_path / sanitise_filename(input_file_path.with_suffix(".dita").name)
        ).resolve()

        # Check to see if we have the relevant Content/Images folder for this file
        # and if not, then copy it over
        # (It may have been copied already by one of the category page processors but may not have been if
        # we haven't gone via a category page)
        if not (target_path / "Content").exists() and (input_file_directory / "Content").exists():
            copy_files(input_file_directory / "Content", target_path / "Content")

        if output_dita_path in self.files_already_processed:
            return output_dita_path

        # Parse the HTML
        html = input_file_path.read_text()
        html_soup = BeautifulSoup(html, "html.parser")

        # Find all the QuickLinks tables and extract their link text and href
        # We find them by finding all divs with an id that includes the text QuickLinksTable (gets QLT, QLT1, QLT2 etc)
        # and get all their links
        ql_divs = html_soup.findAll("div", id=re.compile("QuickLinksTable"))
        links = []

        for ql_div in ql_divs:
            links.extend(ql_div.findAll("a"))

        quicklinks = {l.text: l["href"] for l in links}

        # Find all the links in the body of the page - that is, links that are inside a <div> with an id containing PageLayer
        # or an id starting with layer
        bodylink_hrefs = []
        a_tags = html_soup.find_all("a")
        for a_tag in a_tags:
            parent_pagelayer = a_tag.find_parent("div", id=re.compile("PageLayer"))
            parent_layer = a_tag.find_parent("div", id=re.compile("^layer"))
            if parent_pagelayer or parent_layer:
                if a_tag.get("href"):
                    bodylink_hrefs.append(a_tag["href"])

        # If we're actually writing the files then do the conversion and write the file
        if self.write_generic_files:
            logging.debug(
                f"Processing generic file {input_file_path} to output at {output_dita_path}"
            )
            dita_soup = self.process_generic_file_content(html_soup, input_file_path, quicklinks)
            write_prettified_xml(dita_soup, output_dita_path)
        else:
            logging.debug(f"Processing generic file {input_file_path} to store link information")

        # Keep track of which files we've processed
        # (we can't just use the existence of the file to keep track, as if we run with self.write_generic_files
        # set to false then there will no files written)
        self.files_already_processed.add(output_dita_path)

        # Track all the links on this page and where they point to, so that we know which parts of pages
        # are used, so we know which to export when we run with self.write_generic_files as True
        all_links = list(quicklinks.values()) + bodylink_hrefs
        self.track_all_links(all_links, input_file_path)

        # Process all the pages that are linked from this page
        # We get a list of unique HTML pages that are linked to from this page
        # This removes any duplicates, removes links to labels within a page etc
        unique_page_links = set(
            [urlparse(l).path for l in list(quicklinks.values()) + bodylink_hrefs]
        )
        unique_page_links.discard("")

        # Go through each of the unique links and either call this function
        # again to process the HTML file, or copy the file across (if it's not a HTML file)
        for link in unique_page_links:
            if link.split(".")[-1] == "html":
                link_path = (input_file_directory / link).resolve()
                if self.only_process_single_file:
                    continue
                if link_path.exists():
                    self.process_generic_file(link_path)
                else:
                    logging.warning(
                        f"{link_path} found from file {input_file_path} does not exist!"
                    )
            else:
                # Non HTML pages, so just copy the file over
                logging.debug(f"Copying non-HTML file {link}")
                link = Path(link.replace("\\", "/"))
                if "(-1)" in str(link):
                    continue
                elif (input_file_path.parent / link).exists():
                    (target_path / link.parent).mkdir(parents=True, exist_ok=True)

                    source_filename = input_file_path.parent / link
                    target_filename = target_path / link.parent / sanitise_filename(link.name)
                    logging.debug(f"Copying from {source_filename} to {target_filename}")
                    shutil.copy(source_filename, target_filename)
                else:
                    logging.warning(f"Link {link} does not exist, from page {input_file_path}")

        return output_dita_path

    def run_dita_command(self, input_path="target/dita/index.ditamap", run_validator=True):
        if "Windows" in platform.system():
            dita_executable = "dita.bat"
        else:
            dita_executable = "dita"

        validator_time = 0
        if run_validator:
            time1 = time.time()
            logging.info(
                "Running dita validation command - output below is errors/warnings directly from the dita command"
            )
            validate_command = [
                dita_executable,
                "--format",
                "svrl",
                "--input",
                str(input_path),
                "--args.validate.ignore.rules=href-not-lower-case,running-text-lorem-ipsum,id-not-lower-case,section-id-missing,fig-title-missing,file-not-lower-case",
            ]
            subprocess.run(validate_command)
            time2 = time.time()
            validator_time = time2 - time1
            logging.info(f"DITA validator took {validator_time:.1f} seconds")

        logging.info(
            "Running dita publish command - output below is errors/warnings directly from the dita command"
        )
        time1 = time.time()
        # Run DITA-OT command to transform the index.ditamap file to html
        publish_command = [
            dita_executable,
            "-i",
            str(input_path),
            "-f",
            "html5",
            "-o",
            "./target/html",
            "-Dargs.cssroot=$(pwd)/template/F13ldMan",  # absolute path to CSS file
            # note: the above attribute won't work from props file, since it requires
            # absolute path, which doesn't allow for portable repo.
            "--propertyfile=html5.properties",  # properties file
        ]
        subprocess.run(publish_command)
        time2 = time.time()
        publish_time = time2 - time1
        logging.info(f"DITA publish took {publish_time:.1f} seconds")

        return validator_time, publish_time

    def process_contents_page(self):
        self.process_generic_file(self.root_path / "Introduction" / "ContentsPage.html")

    def store_link_tracker(self):
        links_without_sets = {key: list(value) for key, value in self.link_tracker.items()}
        with open("link_tracker.json", "w") as f:
            json.dump(links_without_sets, f)

    def load_link_tracker(self):
        if not os.path.exists("link_tracker.json"):
            print("Error: link_tracker.json does not exist. Run a full parse first.")
            return False

        with open("link_tracker.json") as f:
            links_without_sets = json.load(f)

        self.link_tracker = defaultdict(set)
        for key, value in links_without_sets.items():
            self.link_tracker[key] = set(value)

        return True

    def run(self, skip_first_run=False, run_validation=False):
        time1 = time.time()
        self.write_generic_files = True
        self.process_contents_page()

        if not skip_first_run:
            self.write_generic_files = False
            self.process_regions()
            self.store_link_tracker()
            logging.info("Done run 1")
        else:
            result = self.load_link_tracker()
            if not result:
                sys.exit()

        time2 = time.time()
        if not skip_first_run:
            logging.info(f"Run 1 took {time2-time1:.1f} seconds")
        else:
            logging.info("Starting run 2")
        self.write_generic_files = True
        self.files_already_processed = set()
        self.process_regions()
        time3 = time.time()
        logging.info("Done run 2")
        logging.info(f"Run 2 took {time3-time2:.1f} seconds")
        logging.debug("Dictionary of links:")
        logging.debug(pformat(self.link_tracker))
        validator_time, publish_time = self.run_dita_command(run_validator=run_validation)
        time4 = time.time()
        logging.info("Timings:")
        if not skip_first_run:
            logging.info(f"Run 1: {time2-time1:.1f} seconds")
        logging.info(f"Run 2: {time3-time2:.1f} seconds")
        if run_validation:
            logging.info(f"DITA validator: {validator_time:.1f} seconds")
        logging.info(f"DITA publish: {publish_time:.1f} seconds")
        logging.info(f"Total: {time4-time1:.1f} seconds")


def init_argparse():
    parser = argparse.ArgumentParser(usage="%(prog)s [OPTION] DATA_PATH [LOGGING_LEVEL]")
    parser.add_argument("DATA_PATH", help="Path to the source data")
    parser.add_argument(
        "LOGGING_LEVEL",
        default="info",
        nargs="?",
        help="Debug level - must be one of debug, warning or info",
    )
    parser.add_argument(
        "--skip-first-run",
        action=argparse.BooleanOptionalAction,
        help="Skip Run 1, loading the shopping list from the link_tracker.json file",
    )
    parser.add_argument(
        "--warn-on-blank-runs",
        action=argparse.BooleanOptionalAction,
        help="Print warning messages whenever runs of blank paragraphs are found",
    )
    parser.add_argument(
        "--run-validation",
        action=argparse.BooleanOptionalAction,
        help="Run the DITA validation step",
    )
    return parser


if __name__ == "__main__":
    parser = init_argparse()

    args = parser.parse_args()

    root_path = args.DATA_PATH
    logging_format = "%(levelname)s:  %(message)s"
    logging_level = args.LOGGING_LEVEL.lower()
    if logging_level == "debug":
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
        logging.info("Logging level set to DEBUG")
    elif logging_level == "info":
        logging.basicConfig(level=logging.INFO, format=logging_format)
        logging.info("Logging level set to INFO")
    elif logging_level == "warning":
        logging.basicConfig(level=logging.WARNING, format=logging_format)
        logging.info("Logging level set to WARNING")

    target_path = "./target/html"
    logging.info(f"LegacyMan parser running, with these arguments: {root_path} {target_path}")

    # remove existing target directory and recreate it
    delete_directory(os.path.join(os.getcwd(), "target/dita"))
    delete_directory(os.path.join(os.getcwd(), "target/html"))
    os.makedirs("target", exist_ok=True)

    # copy index.dita and welcome.dita from data dir to target/dita
    source_dir = root_path
    target_dir = os.path.join("target", "dita")
    copy_files(source_dir, target_dir, ["index.ditamap"])

    parser = Parser(Path(root_path).resolve(), Path(target_dir) / "regions")
    parser.warn_on_blank_runs = args.warn_on_blank_runs

    parser.run(args.skip_first_run, args.run_validation)
