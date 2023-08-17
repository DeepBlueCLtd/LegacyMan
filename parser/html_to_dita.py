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


def htmlToDITA(file_name, soup):
    # 1. if outer element is a div, replace with a span element
    if soup.name == "div":
        soup.name = "span"
        del soup["id"]

    # 2. Replace child divs with a span element
    for div in soup.find_all("div"):
        div.name = "p"
        # TODO: verify if real HTML has divs with names
        del div["name"]
        # TODO: examine use of centre-aligned DIVs. Do we need to reproduce that formatting?
        del div["align"]

    # 3. For img elements, rename it to image, and rename the src attribute to href
    for img in soup.find_all("img"):
        img.name = "image"
        img["href"] = img["src"].lower()
        del img["src"]

    # 4a. replace h1 with paragraph with correct outputClass
    for h1 in soup.find_all("h1"):
        h1.name = "p"
        h1["outputclass"] = "h1"

    # 4b. replace h1 with paragraph with correct outputClass
    for h2 in soup.find_all("h2"):
        h2.name = "p"
        h2["outputclass"] = "h2"

    # 4c. replace h1 with paragraph with correct outputClass
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
    # for ul in soup.find_all('ul'):
    #     ul.name = 'ol'

    return soup


def processLinkedPage(href):
    print(f"%% TODO: Process linked page: {href}")


__all__ = ["htmlToDITA"]

if __name__ == "__main__":
    testParse()
