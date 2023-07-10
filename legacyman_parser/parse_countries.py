import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup

"""Independent unit testable parse_countries module 
to process country data
"""
COUNTRY_COLLECTION = []
COUNTRY_TABLE_NOT_FOUND = []
COUNTRY_TABLE_FOUND = []


class CountryMap:
    def __init__(self, id, country, region, url):
        self.id = id
        self.country = country
        self.region = region
        self.url = url

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.id, self.country, self.region.region, self.url)

class RichCollection:
    def __init__(self, title, body, related_pages, url, cols, rows):
        self.url = url
        self.title = title
        self.body = body
        self.cols = cols
        self.rows = rows
        self.related_pages = related_pages

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.title, self.body, self.related_pages, self.url, self.cols, self.rows)


class TableLink:
    def __init__(self, text, href, src, style):
        self.text = text
        self.href = href
        self.src = src
        self.style = style

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.text, self.href, self.src, self.style)

def extract_countries_in_region(soup: BeautifulSoup = None,
                                parsed_url: str = None,
                                parent_url: str = None,
                                userland_dict: dict = None) -> []:
    seq = userland_dict['seq']
    # get the heading
    heading = soup.find('h1')
    # get the first table after the heading
    country_table = heading.find_next('table') if heading is not None else None
    # Log discrepancy if no table found.
    if country_table is None:
        COUNTRY_TABLE_NOT_FOUND.append(parsed_url)
        return
    # loop through URLs in the table
    for country in country_table.find_all('td'):
        COUNTRY_COLLECTION.append(create_country(seq.next_value(), country, userland_dict['region'], parsed_url))

def extract_nst_countries_in_region(soup: BeautifulSoup = None,
                                parsed_url: str = None,
                                parent_url: str = None,
                                userland_dict: dict = None) -> []:
    url = userland_dict['url']
    title = soup.find('h2')
    div_element = soup.find('div', id='ImageLinksTable')
    if div_element is None:
        sys.exit(f"Exiting: ImageLinksTable not found in {parsed_url}")

    body = div_element.find('table')



    first_row = body.find('tr')
    columns = first_row.find_all('td')
    cols = len(columns)
    
    rows = []
    for row in body.find_all('tr'):
        tr = []
        for td in row.find_all('td'):
            try:
                td = td
            except IndexError:
                continue
            href = None
            src = None
            style = None

            for link in td.find_all('a'):
                href = link.get('href')

            for image in td.find_all('img'):
                src = image.get('src')
                style = image.get('style')

            tr.append(TableLink(td.text, href, src, style))
        
        rows.append(tr)
        
    COUNTRY_TABLE_FOUND.append(RichCollection(title.text, body, None, url, cols, rows))


def create_country(seq, country, region, url):
    url_tag = country.find('a')
    url_str = None
    parsed_url = None
    if url_tag is not None:
        url_str = url_tag.get('href')
        parsed_url = urljoin(url, url_str)
    return CountryMap(seq, country.getText(), region, parsed_url)
