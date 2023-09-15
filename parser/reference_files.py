import os
from bs4 import BeautifulSoup
from parser_utils import write_prettified_xml

from html_to_dita import htmlToDITA


def parse_non_class_file(file_path, title, options):
    """
    this function will convert a non-class HTML file to a DITA file.
    :param file_path: full path to the target file
    :param title: the title to be used (typically the text from the link)
    :param options: file paths & supporting content
    :return: file_path of dita_file
    """
    # generate DITA version of file_path
    file_name = os.path.basename(file_path)
    file_name = file_name.replace(".html", ".dita")

    # check if DITA file already present (only progress if not already present)
    if not os.path.exists(f"{options['target_path']}/{file_name}"):
        # read the target file
        with open(file_path, "r") as f:
            file = f.read()
        html_soup = BeautifulSoup(file, "html.parser")

        # Create the DITA document type declaration string
        dita_doctype = (
            '<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">'
        )
        dita_soup = BeautifulSoup(dita_doctype, "xml")

        # create document level elements
        dita_reference = dita_soup.new_tag("reference")
        topic_id = file_name.replace(" ", "-")  # remove spaces, to make legal ID value
        dita_reference["id"] = topic_id
        dita_title = dita_soup.new_tag("title")
        dita_title.string = title
        dita_reference.append(dita_title)
        dita_ref_body = dita_soup.new_tag("refbody")

        for page in html_soup.find_all("div"):
            if page.has_attr("id") and "PageLayer" in page["id"]:
                print(f"Processing {file_path}")

                dita_section_title = dita_soup.new_tag("title")

                # find the first heading
                headers = ["h1", "h2", "h3", "h4", "h5"]
                for element in page.children:
                    if element.name in headers:
                        dita_section_title.string = element.text
                        break

                # process the content in html to dita. Note: since this is a non-class
                # file, we instruct `div` elements to remain as `div`
                soup = htmlToDITA(options["file_name"], page, dita_soup, "div")

                # create the new `section`
                dita_section = dita_soup.new_tag("section")

                # insert title
                dita_section.append(dita_section_title)

                # insert rest of converted content
                dita_section.append(soup)

                # append to dita_ref_body
                dita_ref_body.append(dita_section)

        # write files
        target_file_path = f"{options['target_path']}/{file_name}"

        dita_reference.append(dita_ref_body)
        dita_soup.append(dita_reference)

        write_prettified_xml(dita_soup, target_file_path)

    return file_name
