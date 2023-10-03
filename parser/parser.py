from collections import defaultdict
from pathlib import Path
import shutil
import sys
import time
import re
import os
import subprocess
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pprint import pprint
from html_to_dita import htmlToDITA
import cssutils

from parser_utils import (
    delete_directory,
    copy_files,
    remove_leading_slashes,
    write_prettified_xml,
    convert_html_href_to_dita_href,
    get_top_value,
    generate_top_to_div_mapping,
)

FIRST_PAGE_LAYER_MARKER = "##### First Page Layer"


class Parser:
    def __init__(self, root_path, target_path_base):
        self.root_path = root_path
        self.target_path_base = target_path_base
        self.link_tracker = defaultdict(set)
        self.generic_files_already_processed = set()

    def process_regions(self):
        # copy the world-map.gif file
        source_dir = f"{self.root_path}/PlatformData/Content/images/"
        target_dir = "target/dita/regions/Content/Images"
        worldMapFile = "WorldMap.jpg"
        copy_files(source_dir, target_dir, [worldMapFile])

        # read the PD_1.html file
        with open(f"{root_path}/PlatformData/PD_1.html", "r") as f:
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
        dita_image["href"] = img_element["src"].replace(" ", "%20")

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
                country_name = os.path.dirname(remove_leading_slashes(link))
                country_path = self.process_ns_countries(
                    country, country_name, remove_leading_slashes(link)
                )
                dita_xref["href"] = f"./{country_path}"

            dita_area = dita_soup.new_tag("area")
            dita_area.append(dita_shape)
            dita_area.append(dita_coords)
            dita_area.append(dita_xref)
            dita_imagemap.append(dita_area)

        dita_body.append(dita_imagemap)

        # Create a <topic> element in the DITA file and append the <map> and the <image> elements
        dita_topic = dita_soup.new_tag("topic")
        dita_topic["id"] = "links_1"

        dita_topic.append(dita_title)
        dita_topic.append(dita_body)

        # Append the <topic> element to the BeautifulSoup object
        dita_soup.append(dita_topic)

        # create /target/dita/regions dir
        regions_path = "target/dita/regions"
        os.makedirs(regions_path, exist_ok=True)

        write_prettified_xml(dita_soup, f"{regions_path}/regions.dita")

    def process_ns_countries(self, country, country_name, link):
        """Processes a non-standard country - ie. one that has an extra page at the start with links to various categories,
        and then those category pages have the actual information"""
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
        dita_doctype = '<!DOCTYPE rich-collection SYSTEM "../../../../dtd/rich-collection.dtd">'
        dita_soup = BeautifulSoup(dita_doctype, "xml")

        # Create dita elements: <rich-collection>,<title>,<table>,<tbody>,<tgroup>...
        dita_rich_collection = dita_soup.new_tag("rich-collection")
        dita_rich_collection["id"] = country

        dita_title = dita_soup.new_tag("title")
        dita_title.string = country
        dita_rich_collection.append(dita_title)

        # Create DITA elements tbody,row,xref,b,table
        dita_tbody = dita_soup.new_tag("tbody")
        dita_tgroup = dita_soup.new_tag("tgroup")
        dita_tgroup["cols"] = "2"

        dita_table = dita_soup.new_tag("table")
        dita_body = dita_soup.new_tag("body")

        # Create the dir to store the content and the dita files for countries
        regions_path = f"target/dita/regions"
        country_path = f"{regions_path}/{country_name}"
        os.makedirs(country_path, exist_ok=True)

        for tr in img_links_table.find_all("tr"):
            dita_row = dita_soup.new_tag("row")

            for a in tr.find_all("a"):
                category_href = a["href"].replace(".html", ".dita")

                dita_xref = dita_soup.new_tag("xref")
                dita_xref["href"] = category_href
                dita_xref["format"] = "dita"

                dita_bold = dita_soup.new_tag("b")
                dita_bold.string = a.text.strip()

                dita_img = dita_soup.new_tag("image")
                dita_img["width"] = "400px"

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

                    dita_img[
                        "href"
                    ] = f'../{category}/Content/Images/{os.path.basename(a.img["src"])}'.replace(
                        " ", "%20"
                    )
                    dita_xref.append(dita_img)

            dita_tbody.append(dita_row)

        dita_tgroup.append(dita_tbody)
        dita_table.append(dita_tgroup)
        dita_body.append(dita_table)
        dita_rich_collection.append(dita_body)

        # Append the rich-collection element to the dita_soup object
        dita_soup.append(dita_rich_collection)

        # Copy each country images to /dita/regions/$Country_name/Content/Images dir
        source_dir = f"{self.root_path}/{country_name}/Content/Images"
        copy_files(source_dir, f"{country_path}/Content/Images")

        write_prettified_xml(dita_soup, f"{country_path}/{country_name}.dita")

        return f"{country_name}/{country_name}.dita"

    def process_category_pages(
        self,
        category_page_link,
        category,
        country_name,
        country_flag_link,
    ):
        # read the category page
        with open(f"{self.root_path}/{remove_leading_slashes(category_page_link)}", "r") as f:
            category_page_html = f.read()

        soup = BeautifulSoup(category_page_html, "html.parser")

        # Find a <td> with colspan=7, this indicates that the page is a category page
        td = soup.find("td", {"colspan": "7"})
        title = soup.find("h2")

        if td is None:
            raise ValueError(
                f"<td> element with colspan 7 not found in the {category_page_link} file"
            )

        # Create the DITA document type declaration string
        dita_doctype = '<!DOCTYPE classlist SYSTEM "../../../../dtd/classlist.dtd">'
        dita_soup = BeautifulSoup(dita_doctype, "xml")

        # Create dita elements for <tgroup>,<table>, <tbody> ...
        dita_tbody = dita_soup.new_tag("tbody")
        dita_tgroup = dita_soup.new_tag("tgroup")
        dita_table = dita_soup.new_tag("table")
        dita_classlistbody = dita_soup.new_tag("classlistbody")
        dita_classlist = dita_soup.new_tag("classlist")
        dita_flag = dita_soup.new_tag("flag")
        dita_title = dita_soup.new_tag("title")
        dita_image = dita_soup.new_tag("image")
        dita_fig = dita_soup.new_tag("fig")

        # Get table columns <td> from the second row <tr> (the first <tr> is used for title so we can't get the column count from it)
        parent_table = td.find_parent("table")
        tr_list = parent_table.find_all("tr")
        second_tr_element = tr_list[1]
        table_columns = second_tr_element.find_all("td")
        dita_tgroup["cols"] = len(table_columns)

        # TODO: change the href of the image
        dita_image[
            "href"
        ] = f"../{country_name}/{remove_leading_slashes(country_flag_link)}".replace(" ", "%20")
        dita_image["alt"] = "flag"

        # create folder for category pages
        category_path = f"target/dita/regions/{category}"
        os.makedirs(category_path, exist_ok=True)

        # Read the parent <table> element
        for tr in parent_table.find_all("tr"):
            dita_row = dita_soup.new_tag("row")

            for td_count, td in enumerate(tr.find_all("td")):
                dita_entry = dita_soup.new_tag("entry")
                dita_entry.string = td.text.strip()

                # Add "namest" and "nameend" attributes to rows with a colspan of 7,
                # (which includes the first row)
                if td.get("colspan") == "7":
                    dita_entry["namest"] = "col1"
                    dita_entry["nameend"] = f"col{len(table_columns)}"
                    dita_entry["align"] = "center"
                    dita_entry["outputclass"] = "table-separator"

                # If there is a link element in the <tr> append it to <entry>
                for a in td.find_all("a"):
                    # Process links to class files (not anchors)
                    href = a.get("href")
                    if href is not None:
                        dita_xref = dita_soup.new_tag("xref")

                        # Remove any #anchor_id value after the href
                        href = href.split(".html")[0] + ".html"
                        file_name = os.path.basename(href.replace(".html", ""))
                        class_name = a.text
                        class_file_src_path = f"{self.root_path}/{os.path.dirname(remove_leading_slashes(category_page_link))}/{href}"

                        if not href.startswith("../"):
                            # process_class_files(
                            #     class_file_src_path, category_path, class_name, file_name
                            # )
                            self.process_generic_file(class_file_src_path)

                        file_link = href.replace(".html", ".dita")
                        dita_xref["href"] = file_link

                        dita_xref.string = a.text.strip()
                        dita_entry.string = ""
                        dita_entry.append(dita_xref)

                dita_row.append(dita_entry)

            dita_tbody.append(dita_row)

        # Generate <colspec> elements based on the <td> elements count
        for count, td in enumerate(table_columns):
            dita_colspec = dita_soup.new_tag("colspec")
            dita_colspec["colnum"] = count + 1
            dita_colspec["colname"] = f"col{count + 1}"
            dita_tgroup.append(dita_colspec)

        dita_tgroup.append(dita_tbody)
        dita_table.append(dita_tgroup)
        dita_classlistbody.append(dita_table)

        # Append the <title>,<flag> and <classlistbody> elements in the <classlist>
        dita_title.string = title.text.strip()

        dita_fig.append(dita_image)
        dita_flag.append(dita_fig)

        dita_classlist["id"] = title.text.replace(" ", "")
        dita_classlist.append(dita_title)
        dita_classlist.append(dita_flag)
        dita_classlist.append(dita_classlistbody)

        # Append the whole page to the dita soup
        dita_soup.append(dita_classlist)

        # Copy the category images to /dita/regions/$category_name/Content/Images folder
        category_page_link = remove_leading_slashes(category_page_link.replace(".html", ".dita"))
        source_img_dir = f"{root_path}/{os.path.dirname(category_page_link)}/Content/Images"
        target_img_dir = f"{category_path}/Content/Images"
        copy_files(source_img_dir, target_img_dir)

        category_file_path = f"{category_path}/{os.path.basename(category_page_link)}"
        write_prettified_xml(dita_soup, category_file_path)

    def process_generic_file_pagelayer(self, dita_soup, page):
        # Exclude links that are in divs just for buttons, as they're not proper links they're just things that go
        # back to the map etc
        if page.name == "div":
            div_id = page.get("id")
            if div_id is not None and (div_id.startswith("btn") or div_id.startswith("bt")):
                return None

        dita_section_title = dita_soup.new_tag("title")

        # find the first heading
        headers = ["h1", "h2", "h3", "h4", "h5"]
        for element in page.children:
            if element.name in headers:
                dita_section_title.string = element.text
                break

        # TODO: Do a better recursive=False which gets down to the PageLayer
        top_to_div_mapping = generate_top_to_div_mapping(page, recursive=False)
        # print(f"Top to div mapping for div with id = {page['id']}")
        # print([el[0] for el in top_to_div_mapping])
        converted_bits = []
        for _, sub_div in top_to_div_mapping:
            # process the content in html to dita. Note: since this is a non-class
            # file, we instruct `div` elements to remain as `div`
            # try:
            #     print(f"Div id = {sub_div['id']}")
            # except Exception:
            #     print("Div has no id")
            converted_soup = htmlToDITA(sub_div, dita_soup, "div")
            converted_bits.append(converted_soup)

        # create the new `section`
        dita_section = dita_soup.new_tag("section")

        # insert title
        dita_section.append(dita_section_title)

        # insert rest of converted content
        dita_section.extend(converted_bits)

        return dita_section

    def process_generic_file_content(self, html_soup, input_file_path, quicklinks):
        # Create the DITA document type declaration string
        dita_doctype = (
            '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
        )
        dita_soup = BeautifulSoup(dita_doctype, "xml")

        # create document level elements
        dita_reference = dita_soup.new_tag("reference")
        topic_id = Path(
            str(input_file_path.name).replace(" ", "-")
        )  # remove spaces, to make legal ID value
        dita_reference["id"] = topic_id
        dita_title = dita_soup.new_tag("title")
        dita_title.string = "Test Title"
        dita_reference.append(dita_title)
        dita_ref_body = dita_soup.new_tag("refbody")

        if self.write_generic_files:
            sections = []
            anchors_to_export = self.link_tracker[
                str(Path(input_file_path).relative_to(self.root_path))
            ]
            pages_to_process = set()
            top_to_div_mapping = generate_top_to_div_mapping(html_soup, recursive=True)
            # print([el[0] for el in top_to_div_mapping])
            # breakpoint()
            for anchor in anchors_to_export:
                if anchor == FIRST_PAGE_LAYER_MARKER:
                    # We need to select the PageLayer with the lowest top value
                    # or if none of them have top values, then just the first one
                    # TODO: Ask Ian - currently fails for banjo_pics.html
                    page = None
                    if len(top_to_div_mapping) > 0:
                        for top_value, div in top_to_div_mapping:
                            div_id = div.get("id")
                            # print(f"top_value = {top_value}, div_id = {div_id}")
                            if div_id is not None and "PageLayer" in div_id:
                                page = div
                                break

                    if page is None:
                        page = html_soup.find("div", id=re.compile("PageLayer"))
                    if page:
                        pages_to_process.add(page)
                    continue

                a_elements = html_soup.find_all("a", attrs={"name": anchor})
                div_elements = html_soup.find_all(["div", "h3"], id=anchor)
                all_elements = a_elements + div_elements

                if len(all_elements) == 0:
                    print(f"### Warning: Cannot find anchor {anchor} in page {input_file_path}")
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
                            print(f"### Warning, could not find enclosing div")
                            continue
                        style_attrib = enclosing_div.get("style")
                        if not style_attrib:
                            print(f"### Warning, could not find style attrib on enclosing div")
                            continue
                        enclosing_div_top_value = get_top_value(style_attrib)
                        if not enclosing_div_top_value:
                            print(f"### Warning, enclosing div has no top value")
                            continue
                        # print(f"Enclosing div top value = {enclosing_div_top_value}")
                        page = None
                        for top_value, bottom_layer_div in top_to_div_mapping:
                            # print(f"top_value = {top_value}")
                            if top_value > enclosing_div_top_value:
                                # Check that the difference isn't too big
                                if top_value - enclosing_div_top_value < 500:
                                    page = bottom_layer_div
                                    # print(f"Found div top value = {top_value}")
                                    break
                        if not page:
                            print(
                                f"### Warning, couldn't find value BottomLayer with appropriate top value - where top value is {enclosing_div_top_value}"
                            )
                            continue
                    if page is None:
                        print(
                            f"### Warning, couldn't find PageLayer parent of anchor {anchor} in page {input_file_path}"
                        )
                        continue
                    pages_to_process.add(page)
                else:
                    print(f"### Warning: Multiple matches for anchor {anchor} in {input_file_path}")

            def get_top_value_for_page(page):
                style = page.get("style")
                if style:
                    top = get_top_value(style)

                if top:
                    return top
                else:
                    return 0

            # pages_to_process = sorted(list(pages_to_process), key=lambda x: x.sourceline)
            pages_to_process = sorted(
                list(pages_to_process), key=lambda x: get_top_value_for_page(x)
            )

            for page in pages_to_process:
                # try:
                #     print(f"Processing page {page['id']}")
                # except Exception:
                #     pass
                processed_page = self.process_generic_file_pagelayer(dita_soup, page)
                if processed_page:
                    sections.append(processed_page)
        else:
            sections = []
            for page in html_soup.find_all("div"):
                if page.has_attr("id") and "PageLayer" in page["id"]:
                    processed_page = self.process_generic_file_pagelayer(dita_soup, page)
                    if processed_page:
                        sections.append(processed_page)

        dita_ref_body.extend(sections)

        dita_reference.append(dita_ref_body)

        # Generate related-links for quicklinks table
        related_links = dita_soup.new_tag("related-links", id="related-pages")
        for link_text, link_href in quicklinks.items():
            link = dita_soup.new_tag("link")
            new_href, extension = convert_html_href_to_dita_href(link_href)
            link["href"] = new_href
            if extension != "dita":
                link["format"] = extension
            linktext = dita_soup.new_tag("linktext")
            linktext.string = link_text
            link.append(linktext)
            related_links.append(link)

        dita_reference.append(related_links)
        dita_soup.append(dita_reference)

        return dita_soup

    def make_relative_to_data_dir(self, filepath):
        try:
            filepath = filepath.relative_to(self.root_path)
        except ValueError:
            filepath = filepath.relative_to(self.root_path.name)

        return filepath

    def track_all_links(self, all_links, input_file_path):
        for value in all_links:
            parsed = urlparse(value)
            if parsed.path:
                filepath = (input_file_path.parent / Path(parsed.path)).resolve()
            else:
                filepath = input_file_path

            filepath = self.make_relative_to_data_dir(filepath)

            if parsed.fragment:
                self.link_tracker[str(filepath)].add(parsed.fragment)
            else:
                self.link_tracker[str(filepath)].add(FIRST_PAGE_LAYER_MARKER)

    def process_generic_file(self, input_file_path):
        input_file_path = Path(input_file_path)
        input_file_directory = input_file_path.parent

        # if str(input_file_directory).startswith("/"):
        #     target_path = self.target_path_base / input_file_directory.relative_to(self.root_path)
        # else:
        #     # target_path = target_path_base / input_file_directory.relative_to("data")
        #     target_path = self.target_path_base / input_file_directory.relative_to(
        #         self.root_path.name
        #     )

        relative_input_file_directory = self.make_relative_to_data_dir(input_file_directory)
        target_path = self.target_path_base / relative_input_file_directory

        output_dita_path = target_path / input_file_path.with_suffix(".dita").name

        if output_dita_path in self.generic_files_already_processed:
            return

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
        bodylink_hrefs = []
        a_tags = html_soup.find_all("a")
        for a_tag in a_tags:
            parent_pagelayer = a_tag.find_parent("div", id=re.compile("PageLayer"))
            if parent_pagelayer:
                if a_tag.get("href"):
                    bodylink_hrefs.append(a_tag["href"])

        # If we're actually writing the files then do the conversion and write the file
        if self.write_generic_files:
            print(f"Processing generic file {input_file_path} to output at {output_dita_path}")
            dita_soup = self.process_generic_file_content(html_soup, input_file_path, quicklinks)
            write_prettified_xml(dita_soup, output_dita_path)
        else:
            print(f"Processing generic file {input_file_path} to store link information")

        # Keep track of which files we've processed
        # (we can't just use the existence of the file to keep track, as if we run with self.write_generic_files
        # set to false then there will no files written)
        self.generic_files_already_processed.add(output_dita_path)

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
                if link_path.exists():
                    self.process_generic_file(link_path)
                else:
                    print(f"### Warning: {link_path} does not exist!")
            else:
                # Non HTML pages, so just copy the file over
                link = Path(link)
                (target_path / link.parent).mkdir(parents=True, exist_ok=True)
                shutil.copy(
                    input_file_path.parent / link,
                    target_path / link.parent / link.name.replace(" ", "_"),
                )

    def run_dita_command(self):
        print("-" * 40)
        print("Running dita publish command")
        print("-" * 40)
        # Run DITA-OT command to transform the index.ditamap file to html
        dita_command = [
            "dita",
            "-i",
            "./target/dita/index.ditamap",
            "-f",
            "html5",
            "-o",
            "./target/html",
        ]
        subprocess.run(dita_command)

    def run(self):
        self.write_generic_files = False
        self.process_regions()
        print("Done run 1")
        self.write_generic_files = True
        self.generic_files_already_processed = set()
        self.process_regions()
        print("Done run 2")
        self.run_dita_command()


def parse_from_root(root_path, target_path):
    """
    this function will parse a body of HTML, writing to DITA format
    :param root_path: the location of the source data
    :param target_path: where to write the results
    """
    print(f"LegacyMan parser running, with these arguments: {root_path} {target_path}")
    start_time = time.time()

    # remove existing target directory and recreate it
    delete_directory(os.path.join(os.getcwd(), "target/dita"))
    delete_directory(os.path.join(os.getcwd(), "target/html"))
    os.makedirs("target", exist_ok=True)

    # copy index.dita and welcome.dita from data dir to target/dita
    source_dir = root_path
    target_dir = os.path.join("target", "dita")
    copy_files(source_dir, target_dir, ["index.ditamap", "welcome.dita"])

    parser = Parser(Path(root_path).resolve(), Path(target_dir) / "regions")

    parser.run()

    end_time = time.time()
    parse_time = end_time - start_time
    print(f"Publish complete after {parse_time} seconds. Root file at /target/dita/index.ditamap")

    pprint(parser.link_tracker)


if __name__ == "__main__":
    root_path = sys.argv[1]
    if len(sys.argv) == 3:
        target_path = sys.argv[2]
    else:
        target_path = "./target/html"
    print(target_path)
    parse_from_root(root_path, target_path)
