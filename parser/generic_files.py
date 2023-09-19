from collections import defaultdict
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from parser_utils import write_prettified_xml, convert_html_href_to_dita_href

from html_to_dita import htmlToDITA

big_dict = defaultdict(set)


def process_generic_file_content(html_soup, input_file_path, quicklinks):
    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
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

    for page in html_soup.find_all("div"):
        if page.has_attr("id") and "PageLayer" in page["id"]:
            dita_section_title = dita_soup.new_tag("title")

            # find the first heading
            headers = ["h1", "h2", "h3", "h4", "h5"]
            for element in page.children:
                if element.name in headers:
                    dita_section_title.string = element.text
                    break

            # process the content in html to dita. Note: since this is a non-class
            # file, we instruct `div` elements to remain as `div`
            soup = htmlToDITA(str(input_file_path), page, dita_soup, "div")

            # create the new `section`
            dita_section = dita_soup.new_tag("section")

            # insert title
            dita_section.append(dita_section_title)

            # insert rest of converted content
            dita_section.append(soup)

            # append to dita_ref_body
            dita_ref_body.append(dita_section)

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


def process_generic_file(input_file_path, target_path_base, data_path):
    global big_dict

    input_file_path = Path(input_file_path)
    input_file_directory = input_file_path.parent

    if str(input_file_directory).startswith("/"):
        target_path = target_path_base / input_file_directory.relative_to(data_path)
    else:
        # target_path = target_path_base / input_file_directory.relative_to("data")
        target_path = target_path_base / input_file_directory.relative_to(data_path.name)

    output_dita_path = target_path / input_file_path.with_suffix(".dita").name

    if output_dita_path.exists():
        return

    html = input_file_path.read_text()

    html_soup = BeautifulSoup(html, "html.parser")

    # Find all divs with an id that includes the text QuickLinksTable (gets QLT, QLT1, QLT2 etc)
    # and get all their links
    ql_divs = html_soup.findAll("div", id=re.compile("QuickLinksTable"))
    links = []

    for ql_div in ql_divs:
        links.extend(ql_div.findAll("a"))

    quicklinks = {l.text: l["href"] for l in links}

    print(f"Processing generic file {input_file_path} to output at {output_dita_path}")
    dita_soup = process_generic_file_content(html_soup, input_file_path, quicklinks)

    bodylink_xrefs = dita_soup.find_all("xref")
    bodylink_hrefs = []
    for el in bodylink_xrefs:
        bodylink_hrefs.append(el["href"])
        el["href"], format = convert_html_href_to_dita_href(el["href"])

    write_prettified_xml(dita_soup, output_dita_path)

    # Get a list of unique HTML pages that are linked to from this page
    # This removes any duplicates, removes links to labels within a page etc
    unique_page_links = set([urlparse(l).path for l in list(quicklinks.values()) + bodylink_hrefs])
    unique_page_links.discard("")

    # big_dict[str(input_file_path)] = list(quicklinks.values())

    for value in quicklinks.values():
        parsed = urlparse(value)
        if parsed.path:
            filepath = (input_file_directory / Path(parsed.path)).resolve()
        try:
            filepath = input_file_path.relative_to(data_path)
        except ValueError:
            filepath = input_file_path.relative_to(data_path.name)
        if parsed.fragment:
            big_dict[str(filepath)].add(parsed.fragment)

    for link in unique_page_links:
        if link.split(".")[-1] == "html":
            link_path = (input_file_directory / link).resolve()
            if link_path.exists():
                if link.startswith(".."):
                    p = Path(link).parent
                    target_path = (target_path / p).resolve()
                process_generic_file(link_path, target_path_base, data_path)
            else:
                print(f"### Warning: {link_path} does not exist!")
        else:
            # Non HTML pages
            link = Path(link)
            (target_path / link.parent).mkdir(parents=True, exist_ok=True)
            shutil.copy(
                input_file_path.parent / link,
                target_path / link.parent / link.name.replace(" ", "_"),
            )


if __name__ == "__main__":
    process_generic_file(sys.argv[1], sys.argv[2])
