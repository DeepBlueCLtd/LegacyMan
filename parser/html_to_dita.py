import copy
import logging
import os
from bs4 import BeautifulSoup
import bs4
from pathlib import Path, PurePath
import cssutils
import re
from parser_utils import convert_html_href_to_dita_href, sanitise_filename, is_button_id


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


def htmlToDITA(soup_in, dita_soup, topic_id, div_replacement="span", wrap_strings=False):
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
    # It is ESSENTIAL that this is the first line of code in this function.
    # DO NOT move it down or put anything above it
    # It needs to do the copy straight away, so that nothing it does affects the original
    soup = copy.copy(soup_in)

    # If this is just a string of content (ie. not a set of tags) then just pass the text through
    # unchanged
    if type(soup) is bs4.NavigableString:
        return soup
    elif type(soup) is bs4.Comment:
        return None

    # TODO: take clone of soup before we process it, since other high-level processing may be applied to the original
    # HTML content, which could rely on it not being transformed.
    # It remains a `TODO:` - since in the last time I checked, I don't think we're doing an actual clone,
    # I think we're still manipulating the original soup

    # 0. Parse the tables
    for tb in soup.find_all("table"):
        converted_table = convert_html_table_to_dita_table(tb, dita_soup, topic_id)
        tb.replace_with(converted_table)
    if soup.name == "table":
        converted_table = convert_html_table_to_dita_table(soup, dita_soup, topic_id)
        soup.replace_with(converted_table)

    # 1. if outer element is a div, replace with whatever div_replacement is (by default a span)
    if soup.name == "div":
        soup.name = div_replacement
        if soup.has_attr("name"):
            soup.id = soup["name"]
            del soup["name"]
        del soup["style"]
        div_id = soup.get("id")
        # Remove btn divs as they just contain buttons
        if div_id is not None and is_button_id(div_id):
            soup.decompose()
            return None
        style_string = soup.get("style")
        if style_string and "hidden" in style_string:
            soup.decompose()
            return None

    # 1a. swap spans inside td's for a p tag
    if soup.name == "td":
        # swap spans for p's
        for span in soup.find_all("span"):
            span.name = "p"
            if span.has_attr("style"):
                del span["style"]

    # 2. Replace child divs with a paragraph element
    for div in soup.find_all("div"):
        style_string = div.get("style")
        if style_string and "hidden" in style_string:
            div.decompose()
            continue
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
                # we don't need the `PageLayer` divs
                # NOTE: sometimes the div inside the `BottomLayer` is missing an id, as
                # in `unit_charlie.html`
                isPageLayer = div.has_attr("id") and "PageLayer" in div["id"]
                isAbsolute = False
                if not isPageLayer and div.has_attr("style"):
                    css_string = div["style"]
                    css = cssutils.css.CSSStyleDeclaration(css_string, validating=False)
                    position = css.position
                    isAbsolute = position == "absolute"

                if isPageLayer or isAbsolute:
                    div.unwrap()
                else:
                    div.name = "p"
                    # TODO: verify if real HTML has divs with names
                    del div["name"]
                    # TODO: examine use of centre-aligned DIVs. Do we need to reproduce that formatting?
                    del div["align"]
                    del div["style"]
        div_id = div.get("id")
        if div_id == "":
            del div["id"]
        # Remove btn divs as they just contain buttons
        if div_id is not None and is_button_id(div_id):
            div.decompose()

    # 3. For img elements, rename it to image, and rename the src attribute to href
    imgItems = soup.find_all("img")
    if soup.name.lower() == "img":
        imgItems.append(soup)
    for img in imgItems:
        img.name = "image"
        img["href"] = img["src"]
        if "image020." in img["href"]:
            # Ignore this image
            img.decompose()
            continue
        img["href"] = sanitise_filename(img["href"])
        del img["src"]
        del img["border"]
        # name not allowed in DITA image, put value into ID, if present
        if img.has_attr("name"):
            img.id = img["name"]
            del img["name"]
        # Make sure the image tag has no contents within it, as that isn't allowed in DITA
        # If there are contents, put them after the image tag
        if len(list(img.children)) > 0:
            for child in img.children:
                img.insert_after(child)

    # 3a. Replace font elements with p elements
    for font_el in soup.find_all("font"):
        font_el.name = "p"
        del font_el["size"]

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
            if pp.find("table"):
                pp.unwrap()
            else:
                # check it's not a p that we have generated earlier
                if not pp.has_attr("outputclass"):
                    # don't need to rename if parent is a div
                    if pp.parent.name != "div":
                        pp.name = "b"

    # 4b. replace h1, h2, h3 with paragraph with correct outputClasses
    for tag in ["h1", "h2", "h3"]:
        for h_tag in soup.find_all(tag):
            h_tag.name = "p"
            h_tag["outputclass"] = tag

    # 5a. Fix hyperlinks (a with href attribute)

    # First deal with the fact that the whole thing passed to this function
    # might just be an a tag
    if soup.name == "a":
        if soup.has_attr("href"):
            all_a_tags = [soup]
        else:
            all_a_tags = []
    else:
        all_a_tags = soup.find_all("a", {"href": True})
    # Then go through all the a tags we've got from the above
    for a in all_a_tags:
        a.name = "xref"
        if "(-1)" in a["href"]:
            a.decompose()
            continue
        a["href"], file_format = convert_html_href_to_dita_href(a["href"])
        if a["href"].startswith("#"):
            if a["href"] != "#":
                # It's an internal link to somewhere else on the page
                a["href"] = f"#{topic_id}/{a['href'][1:]}"
                a["format"] = "dita"
        else:
            if file_format != "html":
                a["format"] = file_format
            else:
                a["format"] = "dita"
        del a["target"]
        if a.has_attr("style") and "font-weight: bold" in a["style"]:
            bold = dita_soup.new_tag("b")
            a.wrap(bold)
            del a["style"]

    # 5b. Fix anchors (a without href attribute)
    # TODO: handle this instance in Issue #288
    # We actually convert them to <b> elements now, in case they have something inside them
    # (which they do in Phase_F_Size.html (ref a3b) - where a heading and more is inside)
    for a in soup.find_all("a", {"href": False}):
        # move name to id, if present - that's the modern structure of an href
        if a.has_attr("name"):
            a["id"] = a["name"]
            del a["name"]
        a.name = "b"

    # 6. Replace <br> newlines with the linebreak processing instruction
    # todo: this converts the brackets to &lt; and &gt;.
    # we need to find a way to make BS4 generate the processing instruction
    for br in soup.find_all("br"):
        br.decompose()
    if soup.name.lower() == "br":
        return "<?linebreak?>"

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
    spanItems = soup.find_all("span", recursive=True)
    if soup.name.lower() == "span":
        # append the soup to the list of spans
        spanItems.append(soup)

    for span in spanItems:
        if span.has_attr("style"):
            style = span["style"].lower()
            if "color:" in style:
                span.name = "ph"
                if "#f00" in style:
                    span["outputclass"] = "colorRed"
                elif "#00f" in style:
                    span["outputclass"] = "colorBlue"
                elif "#777" in style:
                    span["outputclass"] = "colorGray"
                elif "#000066" in style:
                    span["outputclass"] = "colorDarkBlue"
                elif "#663300" in style:
                    span["outputclass"] = "colorDarkBrown"
                del span["style"]
            elif "font-style: italic" in style:
                span.name = "i"
                del span["style"]
        # handle use of class for italic formatting
        if span.has_attr("class"):
            if "italic" in span["class"]:
                span.name = "i"
                del span["class"]
        if span.name == "span":
            # If it's still a span element by the time we get here
            # then just change it to a ph element with no output class
            span.name = "ph"
            del span["align"]
            # span may be used to position image. remove style
            if span.has_attr("style"):
                del span["style"]

    for strong in soup.find_all(
        "b", recursive=True
    ):  # note: strong has already been converted to `b`
        if strong.has_attr("style"):
            if "color:" in strong["style"]:
                if "#f00" in strong["style"].lower():
                    strong["outputclass"] = "colorRed"
                elif "#00f" in strong["style"].lower():
                    strong["outputclass"] = "colorBlue"
            del strong["style"]

    if soup.name == "b":
        if soup.has_attr("style"):
            if "color:" in soup["style"]:
                if "#F00" in soup["style"]:
                    soup["outputclass"] = "colorRed"
                elif "#00F" in soup["style"]:
                    soup["outputclass"] = "colorBlue"
            del soup["style"]

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

    # 14. Swap "em" for "i"
    for a in soup.find_all("em"):
        a.name = "i"

    # 15. Process imagemaps
    for mmap in soup.find_all("map"):
        # Find associated image
        image_tag = soup.find_all(
            "image",
            usemap=re.compile(f'#{mmap["name"]}', re.IGNORECASE),
        )
        if len(image_tag) != 1:
            logging.warning(f"Cannot find image tag to match map element with ID {mmap['name']}")
            continue
        image_filename = image_tag[0]["href"]
        image_tag[0].decompose()

        dita_imagemap = dita_soup.new_tag("imagemap")
        dita_image = dita_soup.new_tag("image")
        dita_image["href"] = sanitise_filename(image_filename)
        dita_imagemap.append(dita_image)
        for area in mmap.find_all("area"):
            dita_shape = dita_soup.new_tag("shape")
            dita_shape.string = area["shape"]

            dita_coords = dita_soup.new_tag("coords")
            dita_coords.string = area["coords"]

            dita_xref = dita_soup.new_tag("xref")
            dita_xref["href"], dita_xref["format"] = convert_html_href_to_dita_href(area["href"])
            if area.has_attr("alt"):
                dita_xref.string = area["alt"]

            dita_area = dita_soup.new_tag("area")
            dita_area.append(dita_shape)
            dita_area.append(dita_coords)
            dita_area.append(dita_xref)
            dita_imagemap.append(dita_area)

        mmap.replace_with(dita_imagemap)
    return soup


def convert_html_table_to_dita_table(source_html, target_soup, topic_id):
    # Create a new DITA table element.
    dita_table_element = target_soup.new_tag("table")
    dita_table_element["colsep"] = "1"
    dita_table_element["rowsep"] = "1"

    if source_html.has_attr("border") and source_html["border"] == "1":
        dita_table_element["frame"] = "all"

    if source_html.has_attr("outputclass"):
        dita_table_element["outputclass"] = source_html["outputclass"]

    # Get max number of columns in all rows
    max_num_columns = 0
    for tr in source_html.find_all("tr"):
        num_columns = len(tr.find_all(["th", "td"]))
        if num_columns > max_num_columns:
            max_num_columns = num_columns

    # Get the highest colspan value in any row
    max_colspan = 0
    for td in source_html.find_all("td"):
        if td.has_attr("colspan"):
            colspan = int(td["colspan"])
            if colspan > max_colspan:
                max_colspan = colspan

    # If the max colspan value is bigger than the number of columns
    # then we've got a table whose structure makes no sense
    # and it has a colspan across the whole table (eg. colspan=8)
    # when there are only actually a max of 6 columns
    # This *should* sort it out, but there are no guarantees
    if max_colspan > max_num_columns:
        max_num_columns = max_colspan

    # Create a new DITA tgroup element.
    dita_tgroup_element = target_soup.new_tag("tgroup")
    dita_tgroup_element["cols"] = max_num_columns

    # Create colspec elements to represent columns.
    for col_number in range(max_num_columns):
        colspec_element = target_soup.new_tag("colspec")
        colspec_element["colname"] = f"c{col_number + 1}"
        dita_tgroup_element.append(colspec_element)

    # Wrap the entire table with tbody tags.
    dita_tbody_element = target_soup.new_tag("tbody")

    # Iterate over the rows of the HTML table and add them to the DITA table.
    for html_row_element in source_html.find_all("tr"):
        dita_row_element = target_soup.new_tag("row")

        # Iterate over the cells of the HTML row and add them to the DITA row.
        count_of_cols_seen_so_far = 0
        for col_index, html_cell_element in enumerate(html_row_element.find_all(["th", "td"])):
            dita_cell_element = target_soup.new_tag("entry")
            # Deal with rowspans by converting them to the morerows attribute
            if html_cell_element.has_attr("rowspan"):
                dita_cell_element["morerows"] = int(html_cell_element["rowspan"]) - 1

            # Deal with colspan by giving the column names to span over
            if html_cell_element.has_attr("colspan"):
                colspan = int(html_cell_element["colspan"])
                # If this colspan itself is longer than the number of cols in the table
                # then it is obviously wrong - set it to the number of cols in the table
                # (this could apply for a column that is merged across the whole width of the table,
                # but the original HTML had a higher colspan number than makes sense)
                if colspan > max_num_columns:
                    colspan = max_num_columns
                # If the length of this colspan plus the number of cols seen so far exceeds
                # the number of cols in the table then reduce this colspan to the maximum it is allowed to be
                elif (colspan + count_of_cols_seen_so_far) > max_num_columns:
                    colspan = max_num_columns - count_of_cols_seen_so_far
                # Otherwise just use the colspan as-is
                else:
                    colspan = int(html_cell_element["colspan"])
                dita_cell_element["namest"] = f"c{count_of_cols_seen_so_far+1}"
                dita_cell_element["nameend"] = f"c{count_of_cols_seen_so_far + colspan}"
                count_of_cols_seen_so_far += colspan
            else:
                count_of_cols_seen_so_far += 1

            # Deal with aligning by finding any alignment specifiers in any children of the cell and applying that to
            # the whole cell
            if html_cell_element.has_attr("align"):
                dita_cell_element["align"] = html_cell_element["align"]
            else:
                align = None
                for el in html_cell_element.find_all():
                    if el.has_attr("align"):
                        align = el["align"]

                if align:
                    dita_cell_element["align"] = align

            # Set the outputClass attribute of the DITA cell element based on the background color of the HTML cell element.
            bgcolor = html_cell_element.get("bgcolor", "").lower()
            if bgcolor == "#cccccc":
                dita_cell_element["outputclass"] = "bkLightGray"
            elif bgcolor == "#999999":
                dita_cell_element["outputclass"] = "bkDarkGray"
            elif bgcolor == "#ffff00":
                dita_cell_element["outputclass"] = "bkYellow"
            elif bgcolor == "#0000ff":
                dita_cell_element["outputclass"] = "bkBlue"
            elif bgcolor == "#ff0000":
                dita_cell_element["outputclass"] = "bkRed"
            elif bgcolor == "#00ff00":
                dita_cell_element["outputclass"] = "bkGreen"

            style = html_cell_element.get("style", "").lower()
            if style == "color: #f00":
                dita_cell_element["outputclass"] = "colorRed"

            # dita_cell_element = htmlToDITA(html_cell_element, target_soup, "topic")
            # Convert all the children of the <td> element to DITA, one at a time
            for child in html_cell_element.contents:
                converted_child = htmlToDITA(child, target_soup, topic_id)
                if converted_child is not None:
                    dita_cell_element.append(converted_child)
            # Add the DITA cell element to the DITA row element.
            dita_row_element.append(dita_cell_element)

        # Add the DITA row element to the DITA tbody.
        dita_tbody_element.append(dita_row_element)

    # Add the DITA tbody to the DITA tgroup.
    dita_tgroup_element.append(dita_tbody_element)

    # Add the DITA tgroup to the DITA table.
    dita_table_element.append(dita_tgroup_element)

    return dita_table_element


if __name__ == "__main__":
    testParse()
