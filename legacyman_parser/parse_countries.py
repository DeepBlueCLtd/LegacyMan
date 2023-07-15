import sys
import os
from urllib.parse import urljoin
from os.path import dirname, abspath


from bs4 import BeautifulSoup

"""Independent unit testable parse_countries module 
to process country data
"""
COUNTRY_COLLECTION = []
COUNTRY_TABLE_NOT_FOUND = []
COUNTRY_TABLE_FOUND = []
COUNTRY_TABLE_COLLECTION_LINKS = []
COUNTRY_TABLE_COLLECTION = []
COUNTRY_TABLE_CLASS = []
COUNTRY_TABLE_CLASS_DATA = []

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

class ClassList:
    def __init__(self, title, related_pages, url, cols, rows, flag):
        self.url = url
        self.title = title
        self.cols = cols
        self.rows = rows
        self.related_pages = related_pages
        self.flag = flag

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.title, self.related_pages, self.url, self.cols, self.rows, self.flag)

class ClassData:
    def __init__(self, url, title, images, summary, signatures, propulsion, remarks,related_pages, parent, colspan):
        self.url = url
        self.title = title
        self.images = images
        self.summary = summary
        self.signatures = signatures
        self.propulsion = propulsion
        self.remarks = remarks
        self.related_pages = related_pages
        self.parent = parent
        self.colspan = colspan

     
    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.url, self.title, self.images, self.summary, self.signatures, self.propulsion, self.remarks, self.related_pages, self.parent, self.colspan)

class TableLink:
    def __init__(self, text, href, src, style):
        self.text = text
        self.href = href
        self.src = src
        self.style = style

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.text, self.href, self.src, self.style)

class CollectionLink:
    def __init__(self, href, flag, flag_dest, parent):
        self.href = href
        self.flag = flag
        self.flag_dest = flag_dest
        self.parent = parent

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.href, self.flag, self.flag_dest, self.parent)

class Section:
    def __init__(self, title, table):
        self.title = title
        self.table = table

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.title, self.table)

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

    image_flag = title.find_next('img')
    
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

            link_href = dirname(dirname(url))+str(href).replace("../", "/")
            flag = dirname(url)+str(image_flag.get('src')).replace("./", "/")
            flag_dest = os.path.basename(dirname(url))+str(image_flag.get('src')).replace("./", "/")
            COUNTRY_TABLE_COLLECTION_LINKS.append(CollectionLink(link_href, flag, flag_dest, url))

            tr.append(TableLink(td.text, href, src, style))
        
        rows.append(tr)
        
    COUNTRY_TABLE_FOUND.append(RichCollection(title.text, body, None, url, cols, rows))

def extract_collections_non_standard_country(soup: BeautifulSoup = None,
                                parsed_url: str = None,
                                parent_url: str = None,
                                userland_dict: dict = None) -> []:

    url = userland_dict['url']
    flag = userland_dict['flag']
    flag_dest = userland_dict['flag_dest']
    parent = userland_dict['parent']
    
    
    title = soup.find('h2')   
    wide_col = soup.find("td", {"colspan" : "7"})

    if wide_col is None:
        sys.exit(f"Exiting: table not found in {parsed_url}")

    body = wide_col.find_parent("table")
    first_row = body.find('tr')
    columns = first_row.find('td')
    cols = columns.get('colspan')

    rows = []
    for row in body.find_all('tr'):
        tr = []
        for td in row.find_all('td'):
            href = None
            for link in td.find_all('a'):
                href = link.get('href')
            tr.append([td.text, href])

            link_href = dirname(url)+"/"+str(href).replace("./", "/")
            link_href_dest = os.path.basename(dirname(url))+"/"+str(href).replace("./", "/")

            if href != None:
                COUNTRY_TABLE_CLASS.append([parent, link_href, link_href_dest])
        rows.append(tr)

    flagdata = CollectionLink(None, flag, flag_dest, parent)

    COUNTRY_TABLE_COLLECTION.append(ClassList(title.text,None, url, cols, rows, flagdata))


def extract_collections_non_standard_class(soup: BeautifulSoup = None,
                                parsed_url: str = None,
                                parent_url: str = None,
                                userland_dict: dict = None) -> []:
    parent = userland_dict['parent']
    url = userland_dict['url']
    link_dest = userland_dict['link_dest']

    # Propulsion
    heading = soup.find("h1")
    # prop = heading.find_next('table') if heading is not None else None
    # heading =  heading.text if heading is not None else "Propulsion"
    # rows_propulson = Section(heading, process_table(table=prop,colspan=4))

    propulsion_str = heading.text if heading != None else None

    bullets_propulson = []
    if heading != None:
        all_elements_after_h1 = heading.find_next_siblings()
        for element in all_elements_after_h1:
            bullets_propulson.append(element)

    rows_propulson = Section(propulsion_str, bullets_propulson)

    # Remarks
    headings = soup.find_all('h1')
    # last h1
    remarks =  headings[-1] if headings else None
    remarks_str = remarks.text if remarks != None else None

    bullets = []
    if remarks != None:
        all_elements_after_h1 = remarks.find_next_siblings()
        for element in all_elements_after_h1:
            bullets.append(element)

    rows_remarks = Section(remarks_str, bullets)

    wide_col = soup.find("td", {"colspan" : "6"})
    if wide_col is None:
        sys.exit(f"Exiting: table not found in {parsed_url}")


    body = wide_col.find_parent("table")
    first_row = body.find('tr')
    columns = first_row.find('td')
    colspan = 6

    rows_summary = []
    rows_signatures = []
    i = 1
    for row in body.find_all('tr'):
        tr = []
        for td in row.find_all('td'):
            href = None
            for link in td.find_all('a'):
                href = link.get('href')
            trcolspan = None
            if td.get('colspan') != None:
                trcolspan = td.get('colspan')

            tr.append([td.text, href, trcolspan])

        if i <= 2:    
            rows_summary.append(tr)
        
        if i >= 3:    
            rows_signatures.append(tr)

        i += 1

    rows_summary = Section("Summary", rows_summary)
    rows_signatures = Section("Signatures", rows_signatures)

    title = soup.find('h1')  
    if title == None:
        title_text = "PROPULSION_EMPTY"  
        COUNTRY_TABLE_CLASS_DATA.append(ClassData(url, title_text, None, rows_summary, rows_signatures, rows_propulson, rows_remarks, None, parent, colspan))

    if title != None:
        title_text = title.text
        COUNTRY_TABLE_CLASS_DATA.append(ClassData(url, title_text, None, rows_summary, rows_signatures, rows_propulson, rows_remarks, None, parent, colspan))
    

def create_country(seq, country, region, url):
    url_tag = country.find('a')
    url_str = None
    parsed_url = None
    if url_tag is not None:
        url_str = url_tag.get('href')
        parsed_url = urljoin(url, url_str)
    return CountryMap(seq, country.getText(), region, parsed_url)


def process_table(table=None, colspan=None):
    rows_propulson = []
    if table != None:
        first_row = table.find('tr')
        columns = first_row.find('td')
        
        i = 1
        for row in table.find_all('tr'):
            tr = []
            for td in row.find_all('td'):
                href = None
                for link in td.find_all('a'):
                    href = link.get('href')
                trcolspan = None
                if td.get('colspan') != None:
                    trcolspan = td.get('colspan')

                trrowsspan = None
                if td.get('rowspan') != None:
                    trrowsspan = td.get('rowspan')


                tr.append([td.text, href, trcolspan, trrowsspan])

            rows_propulson.append(tr)
            i += 1

    return rows_propulson
