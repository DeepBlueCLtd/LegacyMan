import copy
import os
from bs4 import BeautifulSoup
import bs4


def testParse():
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


def htmlToDITA(file_name, soup_in, dita_soup, div_replacement="span", wrap_strings=False):
    """
    this function will convert a block of html to DITA
    :param file_name: any number
    :param soup_in: BS4 tag to be converted
    :param dita_soup: BS4 soup XML element, used for generating new elements
    :param div_replacement: the tag to replace `div` elements with
    :param wrap_strings: flag to indicate that bare strings should be wrapped in a paragraph
    :return: converted block of dita
    """

    # TODO: take clone of soup before we process it
    soup = copy.copy(soup_in)

    # 1. if outer element is a div, replace with a span element
    if soup.name == "div":
        soup.name = div_replacement
        # del soup["id"]
        if soup.has_attr("name"):
            soup.id = soup["name"]
            del soup["name"]
        del soup["style"]

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
            # check it's not a formatting placeholder for an image
            for img in child_images:
                div.append(img)
            # put any child text into a `p`
            newPara = dita_soup.new_tag("p")
            newPara["outputclass"] = "figtitle"
            newPara.string = content
            div.append(newPara)
        else:
            div.name = "p"
            # TODO: verify if real HTML has divs with names
            del div["name"]
            # TODO: examine use of centre-aligned DIVs. Do we need to reproduce that formatting?
            del div["align"]
            del div["style"]

    # 3. For img elements, rename it to image, and rename the src attribute to href
    for img in soup.find_all("img"):
        img.name = "image"
        img["href"] = img["src"]
        # swap spaces out of src
        if " " in img["href"]:
            img["href"] = img["href"].replace(" ", "%20")
        del img["src"]
        del img["border"]
        # name not allowed in DITA image, put value into ID, if present
        if img.has_attr("name"):
            img.id = img["name"]
            del img["name"]

    # 4. We can't handle headings in paragraphs. So, first search for, and fix
    # headings in paragraphs
    for p in soup.find_all("p"):
        # 4a1. replace h1 with paragraph with correct outputClass
        for h1 in p.find_all("h1"):
            h1.name = "b"
            h1["outputclass"] = "h1"

        # 4a2. replace h1 with paragraph with correct outputClass
        for h2 in p.find_all("h2"):
            h2.name = "b"
            h2["outputclass"] = "h2"

        # 4a3. replace h1 with paragraph with correct outputClass
        for h3 in p.find_all("h3"):
            h3.name = "b"
            h3["outputclass"] = "h3"

        # 4a4. Handle embedded paragraphs, by swapping for bold.
        # NOTE: in the future, we may need to check the para is just one line long, or
        # use some other test to establish that it's just providing a title
        for pp in p.find_all("p"):
            # check it's not a p that we have generated earlier
            if not pp.has_attr("outputclass"):
                pp.name = "b"

    # 4b. replace h1 with paragraph with correct outputClass
    for h1 in soup.find_all("h1"):
        h1.name = "p"
        h1["outputclass"] = "h1"

    # 4c. replace h2 with paragraph with correct outputClass
    for h2 in soup.find_all("h2"):
        h2.name = "p"
        h2["outputclass"] = "h2"

    # 4d. replace h3 with paragraph with correct outputClass
    for h3 in soup.find_all("h3"):
        h3.name = "p"
        h3["outputclass"] = "h3"

    # 5a. Fix hyperlinks (a with href attribute)
    for a in soup.find_all("a", {"href": True}):
        a.name = "xref"
        processLinkedPage(a["href"])
        a["href"] = "/".join([".", file_name + ".dita"])
        # insert marker to show not implemented, if it's a string link
        a["outputclass"] = "placeholder"

    # 5b. Fix anchors (a without href attribute)
    # TODO: handle this instance in Issue #288
    for a in soup.find_all("a", {"href": False}):
        a.decompose()

    # 6. Remove <br> newlines
    for br in soup.find_all("br"):
        br.decompose()

    # 7. TODO: Replace the tables with a placeholder tag like "<p> There is a table here </p>""
    for tb in soup.find_all("table"):
        para = dita_soup.new_tag("b")
        para.string = "[TABLE PLACEHOLDER]"
        para["outputclass"] = "placeholder"
        tb.replace_with(para)
    if soup.name == "table":
        # whole element is a table. Replace it with a placeholder
        soup.clear
        soup.name = "p"
        soup["outputclass"] = "placeholder"
        soup.string = "[TABLE PLACEHOLDER]"
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

    # 9. For top-level block-quotes that contain `p` elements, switch to UL lists
    for bq in soup.find_all("blockquote", recursive=False):
        if bq.find("blockquote"):
            # blockquotes used for padding. replace with placeholder
            para = dita_soup.new_tag("p")
            para.string = "[WHITESPACE FOR TABLE]"
            para["outputclass"] = "placeholder"
            bq.replace_with(para)
        else:
            # note: we aren't doing this recursively, we're just looking at the top level
            # in other scenarios there are nested blockquotes, culminating in a heading in a p
            # we need to handle them separately.
            if bq.find("p", recursive=False):
                # it's an indented list.
                bq.name = "ul"
                for p in bq.find_all("p", recursive=False):
                    p.name = "li"

    # 10a. Replace `span` or `strong` used for red-formatting with a <ph> equivalent
    for span in soup.find_all("span", recursive=True):
        if span.has_attr("style"):
            if "color: #F00" in span["style"]:
                span.name = "ph"
                span["outputclass"] = "red"
                del span["style"]

    for strong in soup.find_all(
        "b", recursive=True
    ):  # note: strong has already been converted to `b`
        if strong.has_attr("style"):
            if "color: #F00" in strong["style"]:
                strong["outputclass"] = "red"
                del strong["style"]

    # 11. Put loose text into a paragraph
    if wrap_strings:
        for child in soup.children:
            if type(child) is bs4.element.NavigableString:
                # check it's not just newline char
                if len(child.text) > 1:
                    para = dita_soup.new_tag("p")
                    para.string = child.text
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


__all__ = ["htmlToDITA"]

if __name__ == "__main__":
    testParse()
