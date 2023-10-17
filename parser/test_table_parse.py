from parser import Parser
from pathlib import Path
from bs4 import BeautifulSoup
from html_to_dita import htmlToDITA
from parser_utils import write_prettified_xml

with open("/home/LegacyMan/test/test_content/table4.html") as f:
    contents = f.read()

html_soup = BeautifulSoup(contents, "html.parser")

dita_doctype = '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
dita_soup = BeautifulSoup(dita_doctype, "lxml-xml")

ref_tag = dita_soup.new_tag("reference")
ref_tag["id"] = "test-id"
dita_soup.append(ref_tag)
title_tag = dita_soup.new_tag("title")
title_tag.string = "Test Title"
refbody_tag = dita_soup.new_tag("refbody")
section_tag = dita_soup.new_tag("section")
refbody_tag.append(section_tag)
ref_tag.extend([title_tag, refbody_tag])


dita_output = htmlToDITA(html_soup, dita_soup, "test-topic")
section_tag.append(dita_output)
write_prettified_xml(dita_soup, "/home/LegacyMan/test/test_content/table4_converted.xml")
