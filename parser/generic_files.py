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
