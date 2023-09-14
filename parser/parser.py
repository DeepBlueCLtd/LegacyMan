import sys
import time
import os
import subprocess
from bs4 import BeautifulSoup


from parser_utils import (
    get_files_in_path,
    delete_directory,
    copy_files,
    prettify_xml,
    remove_leading_slashes,
)

from class_files import process_class_files


def process_regions(root_path):
    # copy the world-map.gif file
    source_dir = f"{root_path}/PlatformData/Content/images/"
    target_dir = "target/dita/regions/Content/Images"
    worldMapFile = "WorldMap.jpg"
    copy_files(source_dir, target_dir, [worldMapFile])

    # read the PD_1.html file
    with open(f"{root_path}/PlatformData/PD_1.html", "r") as f:
        html_string = f.read()

    # set Beautifulsoup objects to parse HTML and DITA files
    soup = BeautifulSoup(html_string, "html.parser")

    dita_doctype = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, "lxml-xml")

    # Parse the HTML string, parser the <map> and the <img> elements
    img_element = soup.find("img", {"usemap": "#image3Map"})
    map_element = soup.find("map", {"name": "image3Map"})

    # Create the html <image> element in the DITA file
    dita_image = dita_soup.new_tag("image")
    dita_image["href"] = img_element["src"].replace(" ", "%20")

    dita_image_alt = dita_soup.new_tag("alt")
    dita_image_alt.string = "World Map"
    dita_image.append(dita_image_alt)

    # Create the DITA document type declaration string

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
        country = area["alt"]

        if link.startswith("../"):
            country_name = os.path.dirname(remove_leading_slashes(link))
            country_path = process_ns_countries(
                country, country_name, remove_leading_slashes(link), root_path
            )
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

    # create /target/dita/regions dir
    regions_path = "target/dita/regions"
    os.makedirs(regions_path, exist_ok=True)

    # Prettify the code
    prettified_code = prettify_xml(str(dita_soup))

    # Write the DITA file
    with open(f"{regions_path}/regions.dita", "wb") as f:
        f.write(prettified_code.encode("utf-8"))


def process_ns_countries(country, country_name, link, root_path):
    """Processes a non-standard country - ie. one that has an extra page at the start with links to various categories,
    and then those category pages have the actual information"""
    # read the html file
    with open(f"{root_path}/{link}", "r") as f:
        html_string = f.read()

    # set Beautifulsoup objects to parse the HTML file
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
    dita_rich_collection["id"] = country

    dita_title = dita_soup.new_tag("title")
    dita_title.string = country
    dita_rich_collection.append(dita_title)

    # Create DITA elements tbody,row,xref,b,table
    dita_tbody = dita_soup.new_tag("tbody")
    dita_tgroup = dita_soup.new_tag("tgroup")
    dita_tgroup["cols"] = "2"

    dita_table = dita_soup.new_tag("table")
    dita_body = dita_soup.new_tag("body")

    # Create the dir to store the content and the dita files for countries
    regions_path = f"target/dita/regions"
    country_path = f"{regions_path}/{country_name}"
    os.makedirs(country_path, exist_ok=True)

    for tr in img_links_table.find_all("tr"):
        dita_row = dita_soup.new_tag("row")

        for a in tr.find_all("a"):
            category_href = a["href"].replace(".html", ".dita")

            dita_xref = dita_soup.new_tag("xref")
            dita_xref["href"] = category_href
            dita_xref["format"] = "dita"

            dita_bold = dita_soup.new_tag("b")
            dita_bold.string = a.text.strip()

            dita_img = dita_soup.new_tag("image")
            dita_img["width"] = "400px"

            dita_xref.append(dita_bold)

            dita_entry = dita_soup.new_tag("entry")
            dita_entry.append(dita_xref)

            dita_row.append(dita_entry)

            # Process category pages from this file
            category_page_link = a["href"]
            category = remove_leading_slashes(os.path.dirname(category_href))

            process_category_pages(
                country, category_page_link, category, country_name, country_flag, root_path
            )

            # Copy each category images to /dita/regions/$Category_Name/Content/Images dir
            if a.find("img") is not None:
                src_img_file = os.path.basename(a.find("img")["src"])
                img_src_dir = f"{root_path}/{os.path.dirname(category_page_link.replace('../', ''))}/Content/Images"
                img_target_dir = f"{regions_path}/{category}/Content/Images"
                copy_files(img_src_dir, img_target_dir, [src_img_file])

                dita_img[
                    "href"
                ] = f'../{category}/Content/Images/{os.path.basename(a.img["src"])}'.replace(
                    " ", "%20"
                )
                dita_xref.append(dita_img)

        dita_tbody.append(dita_row)

    dita_tgroup.append(dita_tbody)
    dita_table.append(dita_tgroup)
    dita_body.append(dita_table)
    dita_rich_collection.append(dita_body)

    # Append the rich-collection element to the dita_soup object
    dita_soup.append(dita_rich_collection)

    # Copy each country images to /dita/regions/$Country_name/Content/Images dir
    source_dir = f"{root_path}/{country_name}/Content/Images"
    file_names = get_files_in_path(source_dir, make_lowercase=False)
    copy_files(source_dir, f"{country_path}/Content/Images", file_names)

    # Prettify the code
    prettified_code = prettify_xml(str(dita_soup))
    with open(f"{country_path}/{country_name}.dita", "wb") as f:
        f.write(prettified_code.encode("utf-8"))

    return f"{country_name}/{country_name}.dita"


def process_category_pages(
    country, category_page_link, category, country_name, country_flag_link, root_path
):
    # read the category page
    with open(f"{root_path}/{remove_leading_slashes(category_page_link)}", "r") as f:
        category_page_html = f.read()

    soup = BeautifulSoup(category_page_html, "html.parser")

    # Find a <td> with colspan=7, this indicates that the page is a category page
    td = soup.find("td", {"colspan": "7"})
    title = soup.find("h2")

    if td is None:
        raise ValueError(f"<td> element with colspan 7 not found in the {category_page_link} file")

    # Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE classlist SYSTEM "../../../../dtd/classlist.dtd">'
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
    dita_image["href"] = f"../{country_name}/{remove_leading_slashes(country_flag_link)}".replace(
        " ", "%20"
    )
    dita_image["alt"] = "flag"

    # create folder for category pages
    category_path = f"target/dita/regions/{category}"
    os.makedirs(category_path, exist_ok=True)

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
                # Process links to class files (not anchors)
                href = a.get("href")
                if href is not None:
                    dita_xref = dita_soup.new_tag("xref")

                    # Remove any #anchor_id value after the href
                    href = href.split(".html")[0] + ".html"
                    file_name = os.path.basename(href.replace(".html", ""))
                    class_name = a.text
                    class_file_src_path = f"{root_path}/{os.path.dirname(remove_leading_slashes(category_page_link))}/{href}"

                    if not href.startswith("../"):
                        process_class_files(
                            class_file_src_path, category_path, class_name, file_name
                        )

                    file_link = href.replace(".html", ".dita")
                    dita_xref["href"] = file_link

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

    dita_classlist["id"] = title.text.replace(" ", "")
    dita_classlist.append(dita_title)
    dita_classlist.append(dita_flag)
    dita_classlist.append(dita_classlistbody)

    # Append the whole page to the dita soup
    dita_soup.append(dita_classlist)

    # Copy the category images to /dita/regions/$category_name/Content/Images folder
    category_page_link = remove_leading_slashes(category_page_link.replace(".html", ".dita"))
    source_img_dir = f"{root_path}/{os.path.dirname(category_page_link)}/Content/Images"
    target_img_dir = f"{category_path}/Content/Images"
    file_names = get_files_in_path(source_img_dir, make_lowercase=False)
    copy_files(source_img_dir, target_img_dir, file_names)

    # Prettify the code
    prettified_code = prettify_xml(str(dita_soup))

    # Write the category file to target/dita/regions/$category_name folder
    category_file_path = f"{category_path}/{os.path.basename(category_page_link)}"
    with open(category_file_path, "wb") as f:
        f.write(prettified_code.encode("utf-8"))


def parse_from_root(root_path, target_path):
    """
    this function will parse a body of HTML, writing to DITA format
    :param root_path: the location of the source data
    :param target_path: where to write the results
    """

    print(f"LegacyMan parser running, with these arguments: {root_path} {target_path}")
    start_time = time.time()

    # remove existing target directory and recreate it
    delete_directory(os.path.join(os.getcwd(), "target/dita"))
    delete_directory(os.path.join(os.getcwd(), "target/html"))
    os.makedirs("target", exist_ok=True)

    # copy index.dita and welcome.dita from data dir to target/dita
    source_dir = root_path
    target_dir = os.path.join("target", "dita")
    copy_files(source_dir, target_dir, ["index.ditamap", "welcome.dita"])

    # Process the regions, which will call functions to process the countries, and then each class within the country etc
    # This is the entry point to the whole parsing process
    process_regions(root_path)

    # Run DITA-OT command to transform the index.ditamap file to html
    dita_command = [
        "dita",
        "-i",
        "./target/dita/index.ditamap",
        "-f",
        "html5",
        "-o",
        target_path,
    ]
    subprocess.run(dita_command)

    end_time = time.time()
    parse_time = end_time - start_time
    print(f"Publish complete after {parse_time} seconds. Root file at /target/dita/index.ditamap")


if __name__ == "__main__":
    root_path = sys.argv[1]
    if len(sys.argv) == 3:
        target_path = sys.argv[2]
    else:
        target_path = "./target/html"
    print(target_path)
    parse_from_root(root_path, target_path)
