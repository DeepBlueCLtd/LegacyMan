from random import random
from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement

from crawler.simple_crawler import SimpleCrawler
from legacyman_parser.utils.class_html_template import ClassU


class ClassParser:
    """A generic parser class that contains methods and state attributes to handle parsing of classes for
    Standard and non-Standard countries.

    Here non-Standard countries are the ones which have a welcome page that breaks the platforms down by type,
    each referencing to its own HTML page.
    They are mostly found at the same level as "Region", and some instances of also occur within "Region"

    Standard countries are the ones which list all the sub-categories and corresponding  classes in the
    same HTML page. They are always found only within a "Region"




    Attributes:

    CLASS_COLLECTION                     An array that captures all the classes parsed by this instance of ClassParser
                                         Used to generate publication data
    SUBTYPE_COLLECTION                   Contains a global collection of SubCategory type id and names.
                                         Passed as constructor argument, and used to generate publication data
    COUNTRIES_WITHOUT_CLASS_TABLE        List of HTML pages parsed by this instance of ClassParser where no table rows
                                         were found but were expected. The "NON_STANDARD" in this attribute does not
                                         have anything to do with the non-Standard countries described earlier in the
                                         doc string. Used for discrepancy reporting.
    TOO_FEW_PROPERTIES                   List of HTML pages parsed by this instance of ClassParser where one or more
                                         class row has fewer property columns than expected. Used for discrepancy reporting.
    CLASS_FOUND_FOR_COUNTRY              Used for assert operations, this dict marks a country immediately once it's
                                         able to parse one class for this country. The assumption is that countries
                                         have at least one class.
    _class_table_header_is_identified    A state variable which marks the current header in the table being processed
                                         currently by this instance of ClassParser
    _current_subtype_id                  A state variable which marks the current sub category in the table being processed
                                         currently by this instance of ClassParser
    classRowExtractor                    Instance of MergedRowsExtractor to process merged rows
    """

    def __init__(self, sub_type_maps):
        self.CLASS_COLLECTION = []
        self.SUBTYPE_COLLECTION = sub_type_maps
        self.COUNTRIES_WITHOUT_CLASS_TABLE = []
        self.TOO_FEW_PROPERTIES = []
        self.CLASS_FOUND_FOR_COUNTRY = {}
        self._class_table_header_is_identified = False
        self._current_subtype_id = None
        self.classRowExtractor = None

    def extract_classes_of_ns_country(self, soup: BeautifulSoup = None, parsed_url: str = None,
                                      parent_url: str = None,
                                      userland_dict: dict = None) -> []:
        self._class_table_header_is_identified = False
        self._current_subtype_id = None
        self.classRowExtractor = userland_dict.get('class_extractor')

        links = soup.find_all('a')

        def has_img_child_filter(tag):
            # filter for links that have image child
            return tag.find('img')

        def src_is_parent_folder_filter(tag):
            # filter for links that start with parent folder
            href = tag.get('href')
            return href.startswith('../')

        def src_is_correct_folder_type_filter(tag):
            # filter for links with relevant folder
            href = tag.get('href')
            bad_titles = ['quicklinksdata', 'platformdata', '_noise']
            return not any([x in href.lower() for x in bad_titles])

        has_img_child = list(filter(has_img_child_filter, links))
        src_is_parent_folder = list(
            filter(src_is_parent_folder_filter, has_img_child))
        class_subtypes_list = list(
            filter(src_is_correct_folder_type_filter, src_is_parent_folder))

        assert len(class_subtypes_list) >= 1, "InvalidAssumption: Each ns class listing has one or more entries => {} Found {}".format(
            parsed_url, len(class_subtypes_list))
        for ns_sub_type in class_subtypes_list:
            sub_type_url = urljoin(parsed_url, ns_sub_type.get('href'))
            ns_country_spidey_to_extract_classes = SimpleCrawler(url=sub_type_url,
                                                                 disable_crawler_log=False,
                                                                 userland_dict=userland_dict)
            ns_country_spidey_to_extract_classes.crawl(
                resource_processor_callback=self.extract_classes_of_subtype_of_ns_country,
                crawl_recursively=False,
                parent_url=parsed_url)

    def extract_classes_of_subtype_of_ns_country(self, soup: BeautifulSoup = None, parsed_url: str = None,
                                                 parent_url: str = None,
                                                 userland_dict: dict = None) -> []:
        self._class_table_header_is_identified = False
        self._current_subtype_id = None

        headings = soup.find_all('h2')
        assert len(headings) == 1, "InvalidAssumption: Each country page contains only one h2. => {} Found {}".format(
            parsed_url, len(headings))

        self._current_subtype_id = self.create_sub_type_id_of_ns_class(headings[0].contents[0],
                                                                       userland_dict.get('country').country, parsed_url)

        # now find the table of classes
        tables = soup.find_all('table')

        def has_correct_first_row_filter(tag):
            # filter for tables with more than one row, that is a colspan 7
            rows = tag.find_all('tr')
            assert len(rows) > 0, "InvalidAssumption: Table has more than one row => {}".format(
                parsed_url)
            first_row = rows[0]
            cells = first_row.find_all('td')
            if len(cells) == 1:
                colspan = cells[0].get('colspan')
                return colspan and colspan == "7"
            else:
                return False

        class_tables = list(filter(has_correct_first_row_filter, tables))

        # note: it is acceptable for zero class tables to be found, since one legitimate class table has 8 cols.  We
        # don't (yet) support it, but the code shouldn't fail.
        assert len(class_tables) <= 1, "InvalidAssumption: Should just have found one table of classes => {} Found: {}".format(
            parsed_url, len(class_tables))

        if len(class_tables) == 1:
            rows = class_tables[0].find_all('tr')

            for row in rows[1:]:
                self.process_class_row(
                    row, userland_dict['country'], parsed_url, userland_dict)
            else:
                self.COUNTRIES_WITHOUT_CLASS_TABLE.append(parsed_url)
            assert self._class_table_header_is_identified, "InvalidAssumption: Class Table will mandatorily have table header with its first column header as text Class (case sensitive) => {}".format(
                parsed_url)
            assert self.CLASS_FOUND_FOR_COUNTRY.get(userland_dict['country'],
                                                    False), "InvalidAssumption: Country ({}) page will have at least one class. => {}".format(userland_dict['country'], parsed_url)

    def extract_classes_of_country(self, soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                                   userland_dict: dict = None) -> []:
        self._class_table_header_is_identified = False
        self._current_subtype_id = None
        self.classRowExtractor = userland_dict.get('class_extractor')
        class_list_all = soup.find_all('div', {"id": "PageLayer"})
        assert len(
            class_list_all) == 1, "InvalidAssumption: Each country page contains only 1 PageLayer div that lists classes. => {}. Found {}".format(
            parsed_url, len(class_list_all))
        class_list = class_list_all[0]
        if class_list:
            table_list = class_list.find_all('table')
            assert len(table_list) == 1, "InvalidAssumption: PageLayer div contains only 1 table of classes => {}. Found {}".format(
                parsed_url, len(table_list))
            for row in table_list[0].find_all('tr'):
                self.process_class_row(
                    row, userland_dict['country'], parsed_url, userland_dict)
        else:
            self.COUNTRIES_WITHOUT_CLASS_TABLE.append(parsed_url)
        assert self._class_table_header_is_identified, "InvalidAssumption: Class Table will mandatorily have " \
                                                       "table header with its first column header as text " \
                                                       "Class (case sensitive) => {}".format(
                                                           parsed_url)
        assert self.CLASS_FOUND_FOR_COUNTRY.get(userland_dict['country'],
                                                False), "InvalidAssumption: Country ({}) page will " \
                                                        "have at least one class. => {}" \
            .format(userland_dict['country'], parsed_url)

    def process_class_row(self, row: PageElement, country: dict, parsed_url: str, userland_dict: dict):
        """Check if not _class_table_header_is_identified"""
        if not self._class_table_header_is_identified:
            """See if this is the header, and set
            _class_table_header_is_identified accordingly
            and return"""
            self._class_table_header_is_identified = self.is_this_class_header(
                row)
            return

        # Check if record is a subtype, as at this point table header is identified
        if self.is_this_subcategory_data(row):
            # Add to set and set _current_subtype_id flag and return
            self._current_subtype_id = self.identify_or_create_sub_type_id(
                self.extract_subcategory(row))
            return

        # Normal record
        if not self.is_this_class_record(row):
            self.log_row_as_containing_too_few_class_properties(parsed_url)
            return
        # Extract information and map against _current_subtype_id
        self.create_new_class_with_extracted_subcategory(
            row, country, self._current_subtype_id, parsed_url, userland_dict)

    def identify_or_create_sub_type_id(self, sub_type_str: str):
        sub_type = sub_type_str.replace('/', '-')
        if sub_type in self.SUBTYPE_COLLECTION:
            return sub_type, self.SUBTYPE_COLLECTION[sub_type]
        new_id = len(self.SUBTYPE_COLLECTION) + 1
        self.SUBTYPE_COLLECTION[sub_type] = new_id
        return sub_type, new_id

    def create_sub_type_id_of_ns_class(self, sub_type_str: str, country, parsed_url):
        # note: the sub_type_str is expected to look like `Britain - Composites`
        parts = sub_type_str.replace('/', '-').split(' - ')
        assert len(
            parts) == 2, "InvalidAssumption: h2 contains two elements, separated by '-' => {}. Found {}".format(parsed_url, parts)
        sub_type = parts[1].strip()
        if sub_type in self.SUBTYPE_COLLECTION:
            return sub_type, self.SUBTYPE_COLLECTION[sub_type]
        new_id = len(self.SUBTYPE_COLLECTION) + 1
        self.SUBTYPE_COLLECTION[sub_type] = new_id
        return sub_type, new_id

    @ staticmethod
    def is_this_class_header(row: PageElement):
        """Identify the table header:
        first < tr > which contains < td > element with innerHTML
        as string literal "Class" as its first child/column heading."""
        header = row.find_all('td')
        # For fields that don't have table data, like sub-categories, descriptions etc
        if len(header) <= 0:
            return False
        if header[0].text == "Class":
            return True
        return False

    @ staticmethod
    def is_this_subcategory_data(row: PageElement):
        """Identify the `Sub-Category` header:
        first < tr > following table header will be the
        first `Sub-Category` < tr > which will have an optional
        < td > indicating the sub-category,
        say `SC1` or `Composite` or `Legacy`"""
        columns = row.find_all('td')
        if len(columns) != 1:
            return False
        colspan_val = columns[0].get('colspan', 0)
        if int(colspan_val) != 7:
            return False
        bgcolor_val = columns[0].get('bgcolor', "")
        if bgcolor_val != "#CCCCCC":
            return False
        return True

    @ staticmethod
    def extract_subcategory(row: PageElement):
        """It might also have < strong > attribute"""
        columns = row.find_all('td')
        if len(columns) == 0:
            return row.text
        return columns[0].find('strong').text if columns[0].find('strong') is not None else columns[0].text

    def is_this_class_record(self, row: PageElement):
        """ This should have more than one < td >"""
        columns = row.find_all('td')
        if len(columns) == 7:
            return True
        if self.classRowExtractor.effective_length_of(columns) == 7:
            return True
        return False

    def create_new_class_with_extracted_subcategory(self, row: PageElement, country: dict, current_subtype: str,
                                                    parsed_url: str, userland_dict: dict):
        columns = row.find_all('td')
        tonal_href = None
        has_link = self.does_have_a_link(columns[0])
        if has_link:
            tonal_href = urljoin(
                parsed_url, self.extract_tonal_href(columns[0]))
            # strip fragment id from URL (when present), since when present we try to extract
            # data from the URL, and it breaks if its just an anchor. Note: this code still
            # works if a fragment id isn't present in the URL
            tonal_href = tonal_href.split('#')[0]
        # Declare contents of a class
        class_name, designator, power, shaft, bhp, temp, rr = self.classRowExtractor.retrieve_row(
            columns)

        self.CLASS_COLLECTION.append(ClassU(class_name + current_subtype[0] + country.country,
                                            class_name,
                                            current_subtype,
                                            country,
                                            designator,
                                            power,
                                            shaft,
                                            bhp,
                                            temp,
                                            rr,
                                            has_link,
                                            tonal_href))
        self.CLASS_FOUND_FOR_COUNTRY[country] = True
        combination_key = country.country.lower(
        )+"|"+current_subtype[0].lower()+"|"+class_name.lower()
        if combination_key in userland_dict["ucc_comb_discrepancy_collection"]:
            userland_dict["ucc_comb_discrepancy_collection"][combination_key].append(
                parsed_url)
        else:
            userland_dict["ucc_comb_discrepancy_collection"][combination_key] = [
                parsed_url]

    @ staticmethod
    def does_have_a_link(table_data: PageElement):
        link = table_data.find('a')
        if link is not None:
            href = link.get('href')
            if href is not None:
                return True
        return False

    @ staticmethod
    def extract_tonal_href(table_data: PageElement):
        return table_data.find('a').get('href')

    def log_row_as_containing_too_few_class_properties(self, parsed_url: str):
        self.TOO_FEW_PROPERTIES.append(parsed_url)
