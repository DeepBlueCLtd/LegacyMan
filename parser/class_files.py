import os
from bs4 import BeautifulSoup

from parser_utils import prettify_xml
from html_to_dita import htmlToDITA

from parser_utils import replace_characters

# lower case version of images we ignore. Note `prev_db.jpg` added for testing
black_list = [
    "image020.jpg",
    "check_db.gif",
    "prev_db.gif",
    "rtn2map_db.gif",
    "prev_db.jpg",
    "flags.jpg",
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
    parse_images(html_soup, dita_body, dita_soup)

    # Parse the summary and the signatures block
    if html_soup.find("td", {"colspan": "6"}) is None:
        print(f">>> Failed to find colspan:6 for {class_file_src_path}")
    else:
        # Parse the summary and the signature blocks from the html and build a dita <signagures> and <summary> blocks
        parse_summary_and_signatures(html_soup, dita_body, dita_soup)

    options = {"file_name": file_name, "file_path": class_file_src_path}
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


def parse_images(tag, target, dita_soup):
    # create dita elements
    dita_images = dita_soup.new_tag("images")

    # loop through the HTML images and change them to dita
    images = tag.find_all("img")
    for img in images:
        img_link = img["src"]
        image_filename = os.path.basename(img_link)

        # check it's not blacklisted
        if not image_filename in black_list:
            dita_image = dita_soup.new_tag("image")
            dita_image["href"] = replace_characters(img_link, " ", "%20")
            dita_image["scale"] = 33
            dita_image["align"] = "left"
            dita_images.append(dita_image)

    # Append the dita <images> to the dita <body>
    target.append(dita_images)


def parse_summary_and_signatures(
    tag,
    target,
    dita_soup,
):
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

    dita_colspec = dita_soup.new_tag("colspec")
    dita_signatures = dita_soup.new_tag("signatures")
    dita_signatures["id"] = "sigantures"

    for tr_count, tr in enumerate(table.find_all("tr")):
        dita_row = dita_soup.new_tag("row")
        cells = tr.find_all("td")
        for idx, td in enumerate(cells):
            # Append the first and second <tr> elements to the <summary> element
            dita_entry = dita_soup.new_tag("entry")
            dita_entry.string = td.text.strip()
            # if only one cell, do colspan
            if len(cells) == 1:
                dita_entry["nameend"] = "col4"
                dita_entry["namest"] = "col1"
                dita_entry["align"] = "center"
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
        propulsion_soup = htmlToDITA(options["file_name"], propulsion_div, dita_soup)
        dita_propulsion.append(propulsion_soup)

        target.append(dita_propulsion)

    else:
        print(f"{options['file_path']} does not have a div element with h1 named PROPULSION")


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


__all__ = ["process_class_files"]
