def htmlToDITA(path, soup):
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
        h1.outputClass = "h1"

    # 4b. replace h1 with paragraph with correct outputClass
    for h2 in soup.find_all("h2"):
        h2.name = "p"
        h2.outputClass = "h2"

    # 4c. replace h1 with paragraph with correct outputClass
    for h3 in soup.find_all("h3"):
        h3.name = "p"
        h3.outputClass = "h3"

    # 5. Fix hyperlinks
    for a in soup.find_all("a"):
        a.name = "xref"
        a["href"] = "#"

    # 6. Fix unordered lists
    for ul in soup.find_all("ul"):
        ul.name = "ol"

    # 7. Remove <br> newlines
    for br in soup.find_all("br"):
        br.decompose()

    # 7. TODO: Repalce the tables with a placeholder tag like "<p> There is a table here </p>""
    # for ul in soup.find_all('ul'):
    #     ul.name = 'ol'

    return soup


__all__ = ["htmlToDITA"]
