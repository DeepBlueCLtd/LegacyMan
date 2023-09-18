import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from parser_utils import write_prettified_xml

from html_to_dita import htmlToDITA


def process_generic_file_content(html_soup, input_file_path):
    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, "xml")

    # create document level elements
    dita_reference = dita_soup.new_tag("reference")
    topic_id = Path(str(input_file_path).replace(" ", "-"))  # remove spaces, to make legal ID value
    dita_reference["id"] = topic_id
    dita_title = dita_soup.new_tag("title")
    dita_title.string = "Test Title"
    dita_reference.append(dita_title)
    dita_ref_body = dita_soup.new_tag("refbody")

    for page in html_soup.find_all("div"):
        if page.has_attr("id") and "PageLayer" in page["id"]:
            print(f"Processing generic file {input_file_path}")

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
    dita_soup.append(dita_reference)

    return dita_soup


def process_generic_file(input_file_path, target_path):
    input_file_path = Path(input_file_path)
    input_file_directory = input_file_path.parent
    target_path = Path(target_path)
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

    dita_soup = process_generic_file_content(html_soup, input_file_path)

    write_prettified_xml(dita_soup, output_dita_path)

    # Get a list of unique HTML pages that are linked to from this page
    # This removes any duplicates, removes links to labels within a page etc
    unique_page_links = set([urlparse(l).path for l in quicklinks.values()])
    for link in unique_page_links:
        if link.split(".")[-1] == "html":
            link_path = (input_file_directory / link).resolve()
            if link_path.exists():
                process_generic_file(link_path, target_path)
            else:
                print(f"### Warning: {link_path} does not exist!")


if __name__ == "__main__":
    process_generic_file(sys.argv[1], sys.argv[2])
