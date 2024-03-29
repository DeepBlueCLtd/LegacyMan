import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement

from legacyman_parser.utils.text_cleanser import cleanse

"""Independent testable parse_tonals module
to process tonals data
"""
TONAL_COLLECTION = []
TONAL_TYPE_COLLECTION = {}
TONAL_SOURCE_COLLECTION = {}

TONAL_TABLE_NOT_FOUND = []
TONAL_HEADER_NOT_FOUND = []
TONAL_FOUND_FOR_CLASS = {}
DIAGNOSTICS_FOR_SPLIT_TONALS = {}

_tonal_table_header_is_identified = False
_current_tonal_type = None

tonalRowExtractor = None


class Tonal:
    def __init__(self, class_u, source, ratio_freq, harmonics, remarks, tonal_type):
        self.class_u = class_u
        self.source = source
        self.ratio_freq = ratio_freq
        self.harmonics = harmonics
        self.remarks = remarks
        self.tonal_type = tonal_type

    def __str__(self):
        return "    {} => [{}], [{}], [{}], [{}]".format(self.tonal_type,
                                                         self.source,
                                                         self.ratio_freq,
                                                         self.harmonics,
                                                         self.remarks)


def find_propulsion_tag(tag):
    # note: in at least one class the QuickLinksTable includes a `propulsion calculator` link.
    # we need to avoid returning cells like that.  But, we cannot check for
    # precisely `propulsion` since valid instances do include other text
    return tag.name == 'td' and "propulsion" in tag.text.lower() and not "calculator" in tag.text.lower()


def select_tables_with_valid_propulsion_data(table_tag):
    table_data = table_tag.find_all('td')
    if len(table_data) == 0:
        return False
    # Filter td with propulsion
    propulsion_tds = list(filter(lambda a: "propulsion" in a.text.lower() and not "calculator" in a.text.lower(),
                                 table_data))
    if len(propulsion_tds) == 0:
        return False
    propulsion_tds_with_anchor = list(
        filter(lambda a: a.find('a') is not None, propulsion_tds))
    if len(propulsion_tds_with_anchor) == 0:
        return False
    propulsion_td_anchors_with_href = list(
        filter(lambda a: a.find('a')['href'] is not None, propulsion_tds_with_anchor))
    if len(propulsion_td_anchors_with_href) == 0:
        return False
    return True


def identify_propulsion_href_if_applicable(soup, parsed_url):
    propulsion_href = parsed_url
    quicklink_divs = soup.find_all('div', id=re.compile("QuickLinksTable*"))
    if len(quicklink_divs) == 0:
        return propulsion_href
    # Filter out divs without table
    quicklink_tables = list(
        map(lambda a: a.find('table'), list(filter(lambda a: a.find('table') is not None, quicklink_divs))))
    # Filter out tables without "propulsion" td
    propulsion_tables = list(
        filter(select_tables_with_valid_propulsion_data, quicklink_tables))
    if propulsion_tables:
        propulsion_rows = propulsion_tables[0].find_all(find_propulsion_tag)
        propulsion_href = urljoin(parsed_url, propulsion_rows[0].find('a')[
            'href']).split("#")[0]
    return propulsion_href


def extract_tonals_of_class(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                            userland_dict: dict = None) -> []:
    userland_dict['class'].propulsion_href = parsed_url
    propulsion_href = identify_propulsion_href_if_applicable(soup, parsed_url)
    # Extract and set the propulsion href from the table
    if propulsion_href != parsed_url:
        userland_dict['class'].propulsion_href = propulsion_href
        DIAGNOSTICS_FOR_SPLIT_TONALS[parsed_url] = propulsion_href

    global _tonal_table_header_is_identified, _current_tonal_type, tonalRowExtractor
    _tonal_table_header_is_identified = False
    _current_tonal_type = None
    tonalRowExtractor = userland_dict.get('tonal_extractor')
    # issue here.  Sometimes the Commonly Detected Sources includes a <span>*</span> marker.
    # so, start by finding all `strong` blocks, then find one that contains our selected
    # text, but without looking inside child blocks (recursive=False)
    strong_blocks = soup.find_all("strong")

    def common_block(tag):
        return tag.find(string="Commonly Detected Sources", recursive=False)

    tonal_texts = list(filter(common_block, strong_blocks))
    if len(tonal_texts) == 1:
        tonal_text = tonal_texts[0]
        tonal_table = tonal_text.find_parent("table")
        if tonal_table:
            for row in tonal_table.find_all('tr'):
                process_tonal_row(row, userland_dict['class'])
        else:
            TONAL_TABLE_NOT_FOUND.append(parsed_url)
    else:
        TONAL_HEADER_NOT_FOUND.append(parsed_url)
    if not TONAL_FOUND_FOR_CLASS.get(userland_dict['class'], False):
        print("Extract tonals. No tonals found for {}".format(parsed_url))
        # assert TONAL_FOUND_FOR_CLASS.get(userland_dict['class'], False), "InvalidAssumption: Class ({}) page will " \
        #                                                                  "have at least one tonal in page {}."\
        #     .format(userland_dict['class'], parsed_url)


def process_tonal_row(row: PageElement, class_u: any):
    """Check if not _tonal_table_header_is_identified"""
    global _tonal_table_header_is_identified, _current_tonal_type
    if not _tonal_table_header_is_identified:
        """See if this is the header, and set 
        _tonal_table_header_is_identified accordingly 
        and return"""
        _tonal_table_header_is_identified = is_this_tonal_header(row)
        return

    # Check if record is a tonal type, as at this point table header is identified
    if is_this_tonal_type_data(row):
        # Add to set and set _current_tonal_type flag and return
        _current_tonal_type = identify_or_create_tonal_type_id(
            extract_tonal_type(row))
        return

    # Normal record
    if not is_this_tonal_record(row):
        return
    # Extract information and map against _current_tonal_type
    create_new_tonal_with_extracted_tonal_type(
        row, class_u, _current_tonal_type)


def identify_or_create_tonal_type_id(tonal_type: str):
    if tonal_type in TONAL_TYPE_COLLECTION:
        return tonal_type, TONAL_TYPE_COLLECTION[tonal_type]
    new_id = len(TONAL_TYPE_COLLECTION) + 1
    TONAL_TYPE_COLLECTION[tonal_type] = new_id
    return tonal_type, new_id


def is_this_tonal_header(row: PageElement):
    """Identify the tonal header:
    first < tr > which contains < td > elements
    with innerHTML as string literals
    "Source", "Ratio/Freq",  "Harmonics", and
    "Remarks" in the same order."""
    header = row.find_all('td')
    # For fields that don't have tonal headers
    if len(header) != 4:
        return False
    if (header[0].text, header[3].text) == (
            "Source", "Remarks"):
        return True
    return False


def is_this_tonal_type_data(row: PageElement):
    """Identify the `Tonal-Type` header:
    first < tr > following tonal header will be the first `Tonal-Type` < tr >
    which might have optional < td > indicating the tonal-type,
    say `Propulsion Related` or `Auxiliary Machinery` or `Transient Sources`.
    It MAY also have < strong > attribute"""
    columns = row.find_all('td')
    if len(columns) <= 1:
        return True
    return False


def extract_tonal_type(row: PageElement):
    """It might also have < strong > attribute"""
    columns = row.find_all('td')
    if len(columns) == 0:
        return row.text
    return columns[0].find('strong').text if columns[0].find('strong') is not None else columns[0].text


def is_this_tonal_record(row: PageElement):
    """ This should have exactly 4 < td >"""
    columns = row.find_all('td')
    if len(columns) == 4:
        return True

    # Some tonals have merged remarks
    if tonalRowExtractor.effective_length_of(columns) == 4:
        return True

    return False


def create_new_tonal_with_extracted_tonal_type(row: PageElement, class_u: any, current_tonal_type: str):
    columns = row.find_all('td')
    tonal_source_text, ratio_freq, harmonics, current_remarks = tonalRowExtractor.retrieve_row(
        columns)
    tonal_source = identify_or_create_tonal_source_id(tonal_source_text)
    TONAL_COLLECTION.append(
        Tonal(class_u, tonal_source, ratio_freq, cleanse(harmonics), cleanse(current_remarks), current_tonal_type))
    TONAL_FOUND_FOR_CLASS[class_u] = True


def identify_or_create_tonal_source_id(tonal_source: str):
    if tonal_source in TONAL_SOURCE_COLLECTION:
        return tonal_source, TONAL_SOURCE_COLLECTION[tonal_source]
    new_id = len(TONAL_SOURCE_COLLECTION) + 1
    TONAL_SOURCE_COLLECTION[tonal_source] = new_id
    return tonal_source, new_id
