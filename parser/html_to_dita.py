import copy
import os
from bs4 import BeautifulSoup
import bs4
from pathlib import Path

from parser_utils import convert_html_href_to_dita_href, sanitise_filename


def testParse():
    """
    utility to allow quick high level testing of `htmlToDITA`, so a dev can extend it without having
    to understand the rest of LegacyMan
    """
    # read the PD_1.html file
    with open("input.html", "r") as f:
        html_string = f.read()

    # set Beautifulsoup objects to parse HTML and DITA files
    soup = BeautifulSoup(html_string, "html.parser")
    xml_soup = BeautifulSoup("", "lxml-xml")

    remarks_h1 = soup.find("h1", string="REMARKS")

    if remarks_h1 is not None:
        # Get the parent div of the <h1>
        remarks_div = remarks_h1.find_parent("div")

        # convert to DITA
        remarks_soup = htmlToDITA("input", remarks_div)

        xml_soup.append(remarks_soup)

        # output to file
        with open("output.html", "wb") as f:
            f.write(str(xml_soup).encode("utf-8"))

    else:
        print("FAILED TO FIND H1")


def htmlToDITA(soup_in, dita_soup, div_replacement="span", wrap_strings=False):
    """
    this function will convert a block of html to a block of DITA xml
    :param file_name: current filename, used to generate local click target until valid targets present
    :param soup_in: BS4 tag to be converted
    :param dita_soup: BS4 soup XML element, used for generating new elements
    :param div_replacement: the tag to replace `div` elements with
    :param wrap_strings: flag to indicate that bare strings should be wrapped in a paragraph
    :return: converted block of dita

    General strategy: the HTML content isn't all that far from DITA format. So, we clone the content, then transform it
    steadily into DITA format. Where the HTML element is already quite similar to the DITA one, we update it in place.
    But where the DITA is quite different to the HTML (esp where the HTML may have lots of irrelevant attributes), we
    replace the HTML element with a fresh one - only bringing over the relevant fields.

    """

    # TODO: take clone of soup before we process it, since other high-level processing may be applied to the original
    # HTML content, which could rely on it not being transformed.
    # It remains a `TODO:` - since in the last time I checked, I don't think we're doing an actual clone,
    # I think we're still manipulating the original soup
    soup = copy.copy(soup_in)

    # 1. if outer element is a div, replace with whatever div_replacement is (by default a span)
    if soup.name == "div":
        soup.name = div_replacement
        if soup.has_attr("name"):
            soup.id = soup["name"]
            del soup["name"]
        del soup["style"]

    # 1a. swap spans inside td's for a p tag
    if soup.name == "td":
        # swap spans for p's
        for span in soup.find_all("span"):
            span.name = "p"
            if span.has_attr("style"):
                del span["style"]

    # 2. Replace child divs with a paragraph element
    for div in soup.find_all("div"):
        # see if this is an image placeholder
        if div.has_attr("align") and div["align"] == "center" and div.find("img"):
            div.name = "fig"
            div["outputclass"] = "center"
            del div["align"]
            # get the text content
            content = div.text
            # get the images
            child_images = div.find_all("img", recursive=False)
            # clear the element
            div.clear()
            # reinstate the child images
            for img in child_images:
                div.append(img)
            # put any child text into a `p`
            newPara = dita_soup.new_tag("p")
            newPara["outputclass"] = "figtitle"
            newPara.string = content
            div.append(newPara)
        else:
            # A9 has the content within a parent div
            if div.has_attr("id") and div["id"].startswith("layer"):
                # just drop it, and keep the children
                div.unwrap()
            else:
                div.name = "p"
                # TODO: verify if real HTML has divs with names
                del div["name"]
                # TODO: examine use of centre-aligned DIVs. Do we need to reproduce that formatting?
                del div["align"]
                del div["style"]
        if div.get("id") == "":
            del div["id"]

    # 3. For img elements, rename it to image, and rename the src attribute to href
    for img in soup.find_all("img"):
        img.name = "image"
        img["href"] = img["src"]
        # swap spaces out of src
        if " " in img["href"]:
            img["href"] = sanitise_filename(img["href"])
        del img["src"]
        del img["border"]
        # name not allowed in DITA image, put value into ID, if present
        if img.has_attr("name"):
            img.id = img["name"]
            del img["name"]

    # 4. We can't handle headings in paragraphs. So, first search for, and fix
    # headings in paragraphs
    for p in soup.find_all("p"):
        # replace h1, h2 and h3 with paragraph with correct outputClasses
        for tag in ["h1", "h2", "h3"]:
            for h_tag in p.find_all(tag):
                h_tag.name = "b"
                h_tag["outputclass"] = tag

        # 4a4. Handle embedded paragraphs, by swapping for bold.
        # NOTE: in the future, we may need to check the para is just one line long, or
        # use some other test to establish that it's just providing a title
        for pp in p.find_all("p"):
            # check it doesn't contain an image
            if pp.find("image"):
                pp.unwrap()
            else:
                # check it's not a p that we have generated earlier
                if not pp.has_attr("outputclass"):
                    pp.name = "b"

    # 4b. replace h1, h2, h3 with paragraph with correct outputClasses
    for tag in ["h1", "h2", "h3"]:
        for h_tag in soup.find_all(tag):
            h_tag.name = "p"
            h_tag["outputclass"] = tag

    # 5a. Fix hyperlinks (a with href attribute)
    for a in soup.find_all("a", {"href": True}):
        a.name = "xref"
        a["href"], file_format = convert_html_href_to_dita_href(a["href"])
        if file_format != "html":
            a["format"] = file_format
        del a["target"]

    # 5b. Fix anchors (a without href attribute)
    # TODO: handle this instance in Issue #288
    # We actually convert them to <div> elements now, in case they have something inside them
    # (which they do in Phase_F_Size.html - where a heading and more is inside)
    for a in soup.find_all("a", {"href": False}):
        a.name = "div"
        a["id"] = a["name"]
        del a["name"]

    # 6. Remove <br> newlines
    for br in soup.find_all("br"):
        br.decompose()

    # 7. Replace the tables with a placeholder tag like "<p> There is a table here </p>""
    for tb in soup.find_all("table"):
        first_cell = tb.find("td")
        para = dita_soup.new_tag("b")
        para.string = f"[TABLE PLACEHOLDER] - {first_cell.text} - with links from the table: "
        para["outputclass"] = "placeholder"
        # Include the links from the table, as if this is the only link to a page then the
        # page won't be included in the HTML output from DITA as it won't find any way to get
        # to the page
        links_in_table = tb.find_all("xref", recursive=True)
        if len(links_in_table) > 0:
            for link in links_in_table:
                xref = dita_soup.new_tag("xref")
                xref["href"], file_format = convert_html_href_to_dita_href(link["href"])
                if file_format != "html":
                    xref["format"] = file_format
                para.append(xref)

        tb.replace_with(para)
    if soup.name == "table":
        # whole element is a table. Replace it with a placeholder
        first_cell = soup.find("td")
        soup.clear
        soup.name = "p"
        soup["outputclass"] = "placeholder"
        soup.string = f"[TABLE PLACEHOLDER] - {first_cell.text}"
        if soup.has_attr("border"):
            del soup["border"]

    # 8. Replace <strong> with <bold>
    for strong in soup.find_all("strong"):
        if strong.find_all("image"):
            strong.name = "p"
            strong["outputclass"] = "bold"
        else:
            strong.name = "b"
    if soup.name == "strong":
        if soup.find_all("image"):
            soup.name = "p"
            soup["outputclass"] = "bold"
        else:
            soup.name = "b"

    # 9a. For top-level block-quotes that contain child block-quotes
    for bq in soup.find_all("blockquote", recursive=False):
        if bq.find("blockquote"):
            # blockquotes used for padding. replace with placeholder
            para = dita_soup.new_tag("p")
            para.string = "[WHITESPACE FOR TABLE]"
            para["outputclass"] = "placeholder"
            bq.replace_with(para)

    # 9b. For remaining block-quotes check for lists
    for bq in soup.find_all("blockquote", recursive=True):
        # note: we aren't doing this recursively, we're just looking at the top level
        # in other scenarios there are nested blockquotes, culminating in a heading in a p
        # we need to handle them separately.
        if bq.find("p", recursive=False):
            # it's an indented list.
            bq.name = "ul"
            for p in bq.find_all("p", recursive=False):
                p.name = "li"
        # note: we aren't doing this recursively, we're just looking at the top level
        # in other scenarios there are nested blockquotes, culminating in a heading in a p
        # we need to handle them separately.
        if bq.find("b", recursive=False):
            # it's an indented list.
            bq.name = "ul"
            for p in bq.find_all("b", recursive=False):
                p.name = "li"

    # 10a. Replace `span` or `strong` used for red-formatting with a <ph> equivalent
    for span in soup.find_all("span", recursive=True):
        if span.has_attr("style"):
            if "color:" in span["style"]:
                span.name = "ph"
                if "#F00" in span["style"]:
                    span["outputclass"] = "red"
                elif "#00F" in span["style"]:
                    span["outputclass"] = "blue"
                del span["style"]
            elif "font-style: italic" in span["style"]:
                span.name = "i"
                del span["style"]

    for strong in soup.find_all(
        "b", recursive=True
    ):  # note: strong has already been converted to `b`
        if strong.has_attr("style"):
            if "color:" in strong["style"]:
                if "#F00" in strong["style"]:
                    strong["outputclass"] = "red"
                elif "#00F" in strong["style"]:
                    strong["outputclass"] = "blue"
                del strong["style"]

    # 11. Put loose text into a paragraph
    if wrap_strings:
        for child in soup.children:
            if type(child) is bs4.element.NavigableString:
                # check it's not just single char (eg. a newline or a space)
                if len(child.string) > 1:
                    para = dita_soup.new_tag("p")
                    para.string = child.string
                    child.replace_with(para)

    # 12. remove "align" attribute for paragraphs
    for p in soup.find_all("p", recursive=True):
        if p.has_attr("align"):
            del p["align"]
    if soup.name == "p" and soup.has_attr("align"):
        del soup["align"]

    # 13. remove "style" attribute for unordered lists
    for ul in soup.find_all("ul", recursive=True):
        if ul.has_attr("style"):
            del ul["style"]
    if soup.name == "ul" and soup.has_attr("style"):
        del soup["style"]

    return soup


def processLinkedPage(href):
    print(f"%% TODO: Process linked page: {href}")


if __name__ == "__main__":
    testParse()
