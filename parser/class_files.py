import os
from bs4 import BeautifulSoup
import bs4

from parser_utils import prettify_xml
from html_to_dita import htmlToDITA

from parser_utils import replace_characters
from reference_files import parse_non_class_file

# lower case version of images we ignore. Note `prev_db.jpg` added for testing
black_list = [
    "image020.jpg",
    "check_db.gif",
    "prev_db.gif",
    "rtn2map_db.gif",
    "prev_db.jpg",
    "flags.jpg",
    "return_db.gif",
    "prev_db.gif",
]


def process_class_files(class_file_src_path, class_file_target_path, class_name, file_name):
    # read the class file
    with open(class_file_src_path, "r") as f:
        class_file = f.read()

    html_soup = BeautifulSoup(class_file, "html.parser")

    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE class SYSTEM "../../../../../dtd/class.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, "xml")

    dita_body = dita_soup.new_tag("body")

    # Parse the images
    parse_images(html_soup, dita_body, dita_soup, file_name)

    options = {
        "file_name": file_name,
        "file_path": class_file_src_path,
        "target_path": class_file_target_path,
    }

    # Parse the summary and the signatures block
    if html_soup.find("td", {"colspan": "6"}) is None:
        print(f">>> Failed to find colspan:6 for {class_file_src_path}")
    else:
        # Parse the summary and the signature blocks from the html and build a dita <signagures> and <summary> blocks
        parse_summary_and_signatures(html_soup, dita_body, dita_soup, options)

    # Parse the propulsion block and build a dita <propulsion>
    parse_propulsion(html_soup, dita_body, dita_soup, options)

    # Parse the remarks block and build a dita <remarks> element
    parse_remarks(html_soup, dita_body, dita_soup, options)

    # Append the dita <body> to the <class> element
    dita_class = dita_soup.new_tag("class")
    dita_class["id"] = file_name

    dita_main_title = dita_soup.new_tag("title")
    dita_main_title.string = class_name

    dita_class.append(dita_main_title)
    dita_class.append(dita_body)
    dita_soup.append(dita_class)

    file_name = os.path.basename(class_file_src_path.replace(".html", ".dita"))
    file_path = f"{class_file_target_path}/{file_name}"

    # Prettify the code
    prettified_code = prettify_xml(str(dita_soup))
    with open(file_path, "wb") as f:
        f.write(prettified_code.encode("utf-8"))


def parse_images(tag, target, dita_soup, file_name):
    # create dita elements
    dita_images = dita_soup.new_tag("images")
    dita_images_title = dita_soup.new_tag("title")
    dita_images_title.string = "Images"
    dita_images.append(dita_images_title)

    # Find the colspan:6 table
    td = tag.find("td", {"colspan": "6"})

    if td:
        # Find the parent table (div id="Table")
        parent_table = td.find_parent("div", id="Table")

        # Find the parent element of the table
        parent_div = parent_table.parent

        # loop through children
        for div in parent_div.children:
            if type(div) is bs4.element.Tag:
                # check if it's not the colspan, since we handle that separately
                if div.find("td", {"colspan": "6"}) is None:
                    # check our understanding of the data
                    if len(div.find_all("img")) > 1:
                        print(
                            f"%% WARNING: Higher than expected number of images in div: {file_name} ({len(img)})"
                        )
                    img = div.find("img")
                    if img is not None:
                        img_link = img["src"]
                        img_filename = os.path.basename(img_link)

                        # check it's not blacklisted
                        if not img_filename.lower() in black_list:
                            dita_image = dita_soup.new_tag("image")
                            dita_image["href"] = replace_characters(img_link, " ", "%20")
                            dita_image["scale"] = 33
                            dita_image["align"] = "left"
                            dita_images.append(dita_image)
                            # TODO: transfer the height and width too?
                            # NOTE: If we transfer them we may as well just rename the object,
                            # rather than copy attributes to a new object

    # Append the dita <images> to the dita <body>
    target.append(dita_images)


def parse_summary_and_signatures(tag, target, dita_soup, options):
    td = tag.find("td", {"colspan": "6"})
    table = td.find_parent("table")

    # Create Dita elements
    dita_summary_thead = dita_soup.new_tag("thead")
    dita_summary_tbody = dita_soup.new_tag("tbody")

    dita_signatures_thead = dita_soup.new_tag("thead")
    dita_signatures_tbody = dita_soup.new_tag("tbody")

    dita_summary_tgroup = dita_soup.new_tag("tgroup")
    dita_summary_tgroup["cols"] = "6"

    dita_signatures_tgroup = dita_soup.new_tag("tgroup")
    dita_signatures_tgroup["cols"] = "4"

    dita_summary_table = dita_soup.new_tag("table")
    dita_signatures_table = dita_soup.new_tag("table")

    dita_summary = dita_soup.new_tag("summary")
    dita_summary["id"] = "summary"
    dita_summary_title = dita_soup.new_tag("title")
    dita_summary_title.string = "Summary"
    dita_summary.append(dita_summary_title)

    dita_colspec = dita_soup.new_tag("colspec")
    dita_signatures = dita_soup.new_tag("signatures")
    dita_signatures["id"] = "signatures"
    dita_signatures_title = dita_soup.new_tag("title")
    dita_signatures_title.string = "Signatures"
    dita_signatures.append(dita_signatures_title)

    for tr_count, tr in enumerate(table.find_all("tr")):
        dita_row = dita_soup.new_tag("row")
        cells = tr.find_all("td")
        for idx, td in enumerate(cells):
            # Append the first and second <tr> elements to the <summary> element
            # dita_entry = dita_soup.new_tag("entry")
            # dita_entry.string = td.text.strip()

            dita_entry = htmlToDITA(options["file_name"], td, dita_soup)
            dita_entry.name = "entry"

            # handle the cell width & height
            if dita_entry.has_attr("width"):
                del dita_entry["width"]
            if dita_entry.has_attr("height"):
                del dita_entry["height"]

            if dita_entry.has_attr("style"):
                if "F00" in dita_entry["style"]:
                    dita_entry["outputclass"] = "red"
                if "00F" in dita_entry["style"]:
                    dita_entry["outputclass"] = "blue"
                del dita_entry["style"]

            # support cell shading
            if dita_entry.has_attr("bgcolor"):
                if dita_entry["bgcolor"] == "#CCCCCC":
                    dita_entry["outputclass"] = "lightGray"
                elif dita_entry["bgcolor"] == "#999999":
                    dita_entry["outputclass"] = "darkGray"
                else:
                    print(f"Failed to handle this background color:{dita_entry['bgcolor']}")
                del dita_entry["bgcolor"]

            # remove colspans and rowspans.
            # In the future we will have to reflect
            # colspan/rowspan using CALS terms.
            # To be tidily handled in #324
            if dita_entry.has_attr("colspan"):
                del dita_entry["colspan"]
            if dita_entry.has_attr("rowspan"):
                del dita_entry["rowspan"]

            # if only one cell, do colspan
            if len(cells) == 1:
                dita_entry["nameend"] = "col4"
                dita_entry["namest"] = "col1"
                dita_entry["align"] = "center"
                if dita_entry.has_attr("outputclass"):
                    dita_entry["outputclass"] = dita_entry["outputclass"] + " table-separator"
                else:
                    dita_entry["outputclass"] = "table-separator"

            # if two cells, make the second one wider
            if len(cells) == 2:
                if idx == 1:
                    dita_entry["nameend"] = "col4"
                    dita_entry["namest"] = "col2"

            dita_row.append(dita_entry)

        if tr_count == 0:
            dita_summary_thead.append(dita_row)
        elif tr_count == 1:
            dita_summary_tbody.append(dita_row)
        elif tr_count == 2:
            dita_signatures_thead.append(dita_row)
        else:
            dita_signatures_tbody.append(dita_row)

    dita_summary_tgroup.append(dita_summary_thead)
    dita_summary_tgroup.append(dita_summary_tbody)
    dita_summary_table.append(dita_summary_tgroup)
    dita_summary.append(dita_summary_table)

    for count in range(4):
        dita_colspec = dita_soup.new_tag("colspec")
        dita_colspec["colnum"] = count + 1
        dita_colspec["colname"] = f"col{count + 1}"
        dita_signatures_tgroup.append(dita_colspec)

    dita_signatures_tgroup.append(dita_signatures_thead)
    dita_signatures_tgroup.append(dita_signatures_tbody)
    dita_signatures_table.append(dita_signatures_tgroup)
    dita_signatures.append(dita_signatures_table)

    # lastly, parse any content in signatures that isn't the colspan:6
    parent = table.parent
    for element in parent.children:
        if type(element) is bs4.element.Comment:
            # html comments are valid in DITA
            dita_signatures.append(element)
        elif type(element) is bs4.element.NavigableString:
            # check it's not a line-break
            if len(element) != 1:
                dita_signatures.append(element)
        elif type(element) is bs4.element.Tag:
            if not element.find("td", {"colspan": "6"}):
                dita = htmlToDITA(options["file_name"], element, dita_soup, "p")
                dita_signatures.append(dita)

    # Append the summary and the signatures in the dita <body>
    target.append(dita_summary)
    target.append(dita_signatures)


def parse_propulsion(tag, target, dita_soup, options):
    dita_propulsion = dita_soup.new_tag("propulsion")
    dita_propulsion["id"] = "propulsion"

    propulsion_h1 = tag.find("h1", string="PROPULSION")
    if propulsion_h1 is not None:
        # Add title for the propulsion block
        dita_propulsion_title = dita_soup.new_tag("title")
        dita_propulsion_title.string = "Propulsion"
        dita_propulsion.append(dita_propulsion_title)

        propulsion_div = propulsion_h1.find_parent("div")
        propulsion_soup = htmlToDITA(options["file_name"], propulsion_div, dita_soup, "span", True)
        dita_propulsion.append(propulsion_soup)

        target.append(dita_propulsion)

    else:
        # Check if there is an html <div id="QuickLinksTable"> </div>
        quick_links_table = tag.find("div", {"id": "QuickLinksTable"})
        propulsion = quick_links_table.find("td", text="Propulsion")

        if quick_links_table and propulsion:
            related_page_link = propulsion.find("a")["href"]
            current_page_link = os.path.basename(options["file_path"])

            # Remove any #anchor_id from the file link
            related_page_link = related_page_link.split(".html")[0] + ".html"

            if related_page_link == current_page_link:
                print(
                    f"Faild to parse linked file {related_page_link}, The link found in the QuickLinksTable is the same as the current page link"
                )
            else:
                source_file_path = f"{os.path.dirname(options['file_path'])}/{related_page_link}"
                linked_file_path = parse_non_class_file(source_file_path, "Propulsion", options)

                # Add a <propulsionRef> element in the current file so it can point to the linked file
                propulsion_ref = dita_soup.new_tag("propulsionRef")
                propulsion_ref["id"] = "propulsion"

                ref_title = dita_soup.new_tag("title")
                ref_title.string = "Propulsion"

                ref_xref = dita_soup.new_tag("xref")
                ref_xref["href"] = linked_file_path
                ref_xref["format"] = "dita"

                propulsion_ref.append(ref_title)
                propulsion_ref.append(ref_xref)

                # Append the propulsionRef link to the current dita file
                target.append(propulsion_ref)


def parse_remarks(tag, target, dita_soup, options):
    dita_remarks = dita_soup.new_tag("remarks")
    dita_remarks["id"] = "remarks"

    remarks_h1 = tag.find("h1", string="REMARKS")
    if remarks_h1 is not None:
        # Add title for the remark block
        dita_remarks_title = dita_soup.new_tag("title")
        dita_remarks_title.string = "Remarks"
        dita_remarks.append(dita_remarks_title)

        # Get the parent div of the <h1>
        remarks_div = remarks_h1.find_parent("div")
        remarks_soup = htmlToDITA(options["file_name"], remarks_div, dita_soup)
        dita_remarks.append(remarks_soup)

        target.append(dita_remarks)

    else:
        print(f"{options['file_path']} does not have a div element with h1 named REMARKS")

        # Check if there is an html <div id="QuickLinksTable"> </div>
        quick_links_table = tag.find("div", {"id": "QuickLinksTable"})
        remark = quick_links_table.find("td", text="Remarks")

        if quick_links_table and remark:
            related_page_link = remark.find("a")["href"]
            current_page_link = os.path.basename(options["file_path"])

            # Remove any #anchor_id from the file link
            related_page_link = related_page_link.split(".html")[0] + ".html"

            if related_page_link == current_page_link:
                print(
                    f"Faild to parse linked file {related_page_link}, The link found in the QuickLinksTable is the same as the current page link"
                )
            else:
                source_file_path = f"{os.path.dirname(options['file_path'])}/{related_page_link}"
                linked_file_path = parse_non_class_file(source_file_path, "Remarks", options)

                # Add a <propulsionRef> element in the current file so it can point to the linked file
                remarks_ref = dita_soup.new_tag("remarks")
                remarks_ref["id"] = "remarks"

                ref_title = dita_soup.new_tag("title")
                ref_title.string = "Remarks"

                ref_span = dita_soup.new_tag("span")

                ref_xref = dita_soup.new_tag("xref")
                ref_xref["href"] = linked_file_path
                ref_xref["format"] = "dita"

                ref_para = dita_soup.new_tag("p")
                ref_para.append(ref_xref)

                ref_span.append(ref_para)

                remarks_ref.append(ref_title)
                remarks_ref.append(ref_span)

                # Append the remarksRef link to the current dita file
                target.append(remarks_ref)


__all__ = ["process_class_files"]
