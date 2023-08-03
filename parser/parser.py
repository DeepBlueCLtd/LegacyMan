import sys
import time
import os
import subprocess
from bs4 import BeautifulSoup


from parser.parser_utils import (
    create_directory,
    get_files_in_path,
    delete_directory,
    copy_directory,
    copy_files,
    prettify_xml,
    htmlToDITA,
)


def process_regions():
    # copy the world-map.gif file
    source_dir = "data/PlatformData/Content/images/"
    target_dir = "target/dita/regions/content/images"
    worldMapFile = "WorldMap.jpg".lower()
    copy_files(source_dir, target_dir, [worldMapFile])

    # read the PD_1.html file
    with open("data/PlatformData/PD_1.html", "r") as f:
        html_string = f.read()

    # set Beautifulsoup objects to parse HTML and DITA files
    soup = BeautifulSoup(html_string, "html.parser")
    dita_soup = BeautifulSoup("", "lxml-xml")

    # Parse the HTML string, parser the <map> and the <img> elements
    img_element = soup.find("img", {"usemap": "#image3Map"})
    map_element = soup.find("map", {"name": "image3Map"})

    # Create the html <image> element in the DITA file
    dita_image = dita_soup.new_tag("image")
    dita_image["href"] = img_element["src"].lower()

    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, "xml")

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
        country_name = area["alt"]

        if link.startswith("../"):
            country_path = process_ns_countries(country_name.lower(), link[3:])
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

    # Write the DITA file
    dita_output = "target/dita/regions"
    create_directory(dita_output)

    # Prettify the code
    prettified_code = prettify_xml(str(dita_soup))

    with open(f"{dita_output}/regions.dita", "wb") as f:
        f.write(prettified_code.encode("utf-8"))


def process_ns_countries(country_name, link):
    # read the html file
    with open(f"data/{link}", "r") as f:
        html_string = f.read()

    # set Beautifulsoup objects to parse HTML and DITA files
    soup = BeautifulSoup(html_string, "html.parser")

    # Parse the HTML string, parser the <map> and the <img> elements
    img_links_table = soup.find("div", {"id": "ImageLinksTable"})
    title = soup.find("h2")
    country_flag = title.find_next("img")["src"]

    if img_links_table is None:
        raise ValueError("ImageLinksTable not found in the HTML file")

    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE rich-collection SYSTEM "../../../../dtd/rich-collection.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, "xml")

    # Create dita elements: <rich-collection>,<title>,<table>,<tbody>,<tgroup>...
    dita_rich_collection = dita_soup.new_tag("rich-collection")
    dita_rich_collection["id"] = country_name

    dita_title = dita_soup.new_tag("title")
    dita_title.string = country_name
    dita_rich_collection.append(dita_title)

    # Create DITA elements tbody,row,xref,b,table
    dita_tbody = dita_soup.new_tag("tbody")
    dita_tgroup = dita_soup.new_tag("tgroup")
    dita_tgroup["cols"] = "2"

    dita_table = dita_soup.new_tag("table")
    dita_body = dita_soup.new_tag("body")

    for tr in img_links_table.find_all("tr"):
        dita_row = dita_soup.new_tag("row")

        for a in tr.find_all("a"):
            dita_xref = dita_soup.new_tag("xref")
            dita_xref["href"] = a["href"][1:].replace(".html", ".dita").lower()
            dita_xref["format"] = "dita"

            dita_bold = dita_soup.new_tag("b")
            dita_bold.string = a.text.strip()

            dita_img = dita_soup.new_tag("image")
            dita_img["width"] = "400px"

            dita_xref.append(dita_bold)
            dita_xref.append(dita_img)

            dita_entry = dita_soup.new_tag("entry")
            dita_entry.append(dita_xref)

            dita_row.append(dita_entry)

            # Process category pages from this file
            category_page_link = a["href"]
            process_category_pages(category_page_link, country_name, country_flag)
            dita_img["href"] = a.img["src"][1:].lower()

        dita_tbody.append(dita_row)

    dita_tgroup.append(dita_tbody)
    dita_table.append(dita_tgroup)
    dita_body.append(dita_table)
    dita_rich_collection.append(dita_body)

    # Append the rich-collection element to the dita_soup object
    dita_soup.append(dita_rich_collection)

    # Write the DITA file
    country_path = f"target/dita/regions/{country_name}"
    create_directory(country_path)

    # Copy the images to /dita/regions/$Country_name/content/images dir
    source_dir = f"data/{country_name}/content/images"
    file_names = get_files_in_path(source_dir, make_lowercase=True)
    copy_files(source_dir, f"{country_path}/content/images", file_names)

    # Prettify the code
    prettified_code = prettify_xml(str(dita_soup))

    with open(f"{country_path}/{country_name}.dita", "wb") as f:
        f.write(prettified_code.encode("utf-8"))

    return f"{country_name}/{country_name}.dita"


def process_class_file(class_file_src_path, class_file_target_path, class_name, file_name):
    # read the class file
    with open(class_file_src_path, "r") as f:
        class_file = f.read()

    soup = BeautifulSoup(class_file, "html.parser")

    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE class SYSTEM "../../../../../dtd/class.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, "xml")

    dita_body = dita_soup.new_tag("body")

    dita_summary_table = dita_soup.new_tag("table")
    dita_signatures_table = dita_soup.new_tag("table")

    dita_images = dita_soup.new_tag("images")
    dita_summary = dita_soup.new_tag("summary")
    dita_summary["id"] = "summary"

    dita_summary_tgroup = dita_soup.new_tag("tgroup")
    dita_summary_tgroup["cols"] = "6"
    dita_signatures_tgroup = dita_soup.new_tag("tgroup")
    dita_signatures_tgroup["cols"] = "4"

    dita_colspec = dita_soup.new_tag("colspec")
    dita_signatures = dita_soup.new_tag("signatures")
    dita_signatures["id"] = "sigantures"
    dita_propulsion = dita_soup.new_tag("propulsion")
    dita_propulsion["id"] = "propulsion"

    dita_remarks = dita_soup.new_tag("remarks")
    dita_remarks["id"] = "remarks"

    dita_span = dita_soup.new_tag("span")
    dita_class = dita_soup.new_tag("class")
    dita_class["id"] = file_name.lower()

    dita_main_title = dita_soup.new_tag("title")
    dita_main_title.string = class_name

    dita_related_pages = dita_soup.new_tag("related-pages")

    # Parse all of the <img> elements
    img = soup.find("img")
    if img is not None:
        img_link = img["src"].lower()
        dita_image = dita_soup.new_tag("image")
        dita_image["href"] = img_link
        dita_image["scale"] = 33
        dita_image["align"] = "left"
        dita_images.append(dita_image)

    # Find the <td> element with colspan 6 and find its parent table
    td = soup.find("td", {"colspan": "6"})
    if td is None:
        print(f">>> Failed to find colspan:6 for {class_file_src_path}")
    else:
        table = td.find_parent("table")
        dita_summary_thead = dita_soup.new_tag("thead")
        dita_summary_tbody = dita_soup.new_tag("tbody")
        dita_signatures_thead = dita_soup.new_tag("thead")
        dita_signatures_tbody = dita_soup.new_tag("tbody")

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

        # Parse the propulsion block from the html
        propulsion_h1 = soup.find("h1", string="PROPULSION")

        # Add title for the propulsion block
        dita_propulsion_title = dita_soup.new_tag("title")
        dita_propulsion_title.string = "Propulsion"
        dita_propulsion.append(dita_propulsion_title)

        if propulsion_h1 is not None:
            propulsion_div = propulsion_h1.find_parent("div")

            # TODO: in the forloop below we are only getting the <p> elements but there are <ul> elements in some of the parent containers, so need to parse the <ul> elements as well
            for p in propulsion_div.find_all("p"):
                dita_propulsion_p = dita_soup.new_tag("p")
                dita_propulsion_p.string = p.text.strip()
                dita_propulsion.append(dita_propulsion_p)
        else:
            print(f"{class_file_src_path} does not have a div element with h1 named PROPOULSION")

        # Parse the remark block from the HTML
        remarks_h1 = soup.find("h1", string="REMARKS")

        if remarks_h1 is not None:
            # Add title for the remark block
            dita_remarks_title = dita_soup.new_tag("title")
            dita_remarks_title.string = "Remarks"
            dita_remarks.append(dita_remarks_title)

            # Get the parent div of the <h1>
            remarks_div = remarks_h1.find_parent("div")
            remarks_soup = htmlToDITA(file_name, remarks_div)
            dita_remarks.append(remarks_soup)
        else:
            print(f"{class_file_src_path} does not have a div element with h1 named REMARKS")

        # Append all of the elements to the dita_soup object
        dita_body.append(dita_images)
        dita_body.append(dita_summary)
        dita_body.append(dita_signatures)
        dita_body.append(dita_propulsion)
        dita_body.append(dita_remarks)

        dita_class.append(dita_main_title)
        dita_class.append(dita_body)
        dita_soup.append(dita_class)

        file_name = os.path.basename(class_file_src_path.replace(".html", ".dita"))
        file_path = f"{class_file_target_path}/{file_name}"

        # Prettify the code
        prettified_code = prettify_xml(str(dita_soup))
        with open(file_path, "wb") as f:
            f.write(prettified_code.encode("utf-8"))


def process_category_pages(category_page_link, country_name, country_flag_link):
    # read the category page
    with open(f"data/{category_page_link[3:]}", "r") as f:
        category_page_html = f.read()

    soup = BeautifulSoup(category_page_html, "html.parser")

    # Find a <td> with colspan=7, this indicates that the page is a category page
    td = soup.find("td", {"colspan": "7"})
    title = soup.find("h2")

    if td is None:
        raise ValueError(f"<td> element with colspan 7 not found in the {category_page_link} file")

    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE classlist SYSTEM "../../../../../dtd/classlist.dtd">'
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
    dita_image["href"] = f"../{country_flag_link[2:].lower()}"
    dita_image["alt"] = "flag"

    country_path = f"target/dita/regions/{country_name}"
    file_path = f"{country_path}/{os.path.dirname(category_page_link[3:].lower())}"
    create_directory(file_path)

    # Read the parent <table> element
    for tr_count, tr in enumerate(parent_table.find_all("tr")):
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
                dita_xref = dita_soup.new_tag("xref")

                # Process class files
                href = a.get("href")
                if href is not None:
                    file_name = os.path.basename(a["href"].replace(".html", ""))
                    class_name = a.text
                    class_file_src_path = f"data/{os.path.dirname(category_page_link[3:])}/{href}"
                    class_file_target_path = f"target/dita/regions/{country_name}/{os.path.dirname(category_page_link[3:].lower())}"
                    process_class_file(
                        class_file_src_path, class_file_target_path, class_name, file_name
                    )

                    file_link = a["href"].replace(".html", ".dita")
                    dita_xref["href"] = f"./{file_link}"

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

    dita_classlist["id"] = title.text.replace(" ", "").lower()
    dita_classlist.append(dita_title)
    dita_classlist.append(dita_flag)
    dita_classlist.append(dita_classlistbody)

    # Append the whole page to the dita soup
    dita_soup.append(dita_classlist)

    # Copy all images to /dita/regions/$Country_name/$Category_page/content/images dir
    category_page_link = category_page_link.lower().replace(".html", ".dita")[3:]
    source_img_dir = f"data/{os.path.dirname(category_page_link)}/content/images"
    target_img_dir = f"{country_path}/{os.path.dirname(category_page_link)}/content/images"
    file_names = get_files_in_path(source_img_dir, make_lowercase=True)
    copy_files(source_img_dir, target_img_dir, file_names)

    # Prettify the code
    prettified_code = prettify_xml(str(dita_soup))
    with open(f"{country_path}/{category_page_link}", "wb") as f:
        f.write(prettified_code.encode("utf-8"))


def parse_from_root(args):
    print(f"LegacyMan parser running, with these arguments: {args}")
    start_time = time.time()

    # remove existing target directory and recreate it
    delete_directory(os.path.join(os.getcwd(), "target/dita"))
    delete_directory(os.path.join(os.getcwd(), "target/html"))
    create_directory("target")

    # copy index.dita and welcome.dita from data dir to target/dita
    source_dir = "data"
    target_dir = os.path.join("target", "dita")
    copy_files(source_dir, target_dir, ["index.ditamap", "welcome.dita"])

    # Produce the world map
    process_regions()

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

    end_time = time.time()
    parse_time = end_time - start_time
    print(f"Publish complete after {parse_time} seconds. Root file at /target/dita/index.ditamap")


if __name__ == "__main__":
    args = sys.argv[1:]
    parse_from_root(args)
