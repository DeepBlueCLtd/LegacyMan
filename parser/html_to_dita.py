import os
from bs4 import BeautifulSoup


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


def htmlToDITA(file_name, soup, dita_soup):
    """
    this function will convert a block of html to DITA
    :param file_name: any number
    :param soup: BS4 tag to be converted
    :param dita_soup: BS4 soup XML element, used for generating new elements
    :return: converted block of dita
    """

    # TODO: take clone of soup before we process it

    # 1. if outer element is a div, replace with a span element
    if soup.name == "div":
        soup.name = "span"
        del soup["id"]
        del soup["style"]

    # 2. Replace child divs with a paragraph element
    for div in soup.find_all("div"):
        div.name = "p"
        # TODO: verify if real HTML has divs with names
        del div["name"]
        # TODO: examine use of centre-aligned DIVs. Do we need to reproduce that formatting?
        del div["align"]
        del div["style"]

    # 3. For img elements, rename it to image, and rename the src attribute to href
    for img in soup.find_all("img"):
        img.name = "image"
        img["href"] = img["src"].lower()
        del img["src"]
        del img["border"]
        # name not allowed in DITA image, put value into ID
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

    # 5. Fix hyperlinks
    for a in soup.find_all("a"):
        a.name = "xref"
        processLinkedPage(a["href"])
        a["href"] = os.path.join(".", file_name + ".dita")

    # 6. Remove <br> newlines
    for br in soup.find_all("br"):
        br.decompose()

    # 7. TODO: Replace the tables with a placeholder tag like "<p> There is a table here </p>""
    for tb in soup.find_all("table"):
        tb.replace_with("[TABLE PLACEHOLDER]")

    # for ul in soup.find_all('ul'):
    #     ul.name = 'ol'

    return soup


def processLinkedPage(href):
    print(f"%% TODO: Process linked page: {href}")


__all__ = ["htmlToDITA"]

if __name__ == "__main__":
    testParse()
