from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement

from crawler.simple_crawler import SimpleCrawler
from legacyman_parser.utils.class_html_template import ClassU


class ClassParser:

    def __init__(self):
        self.CLASS_COLLECTION = []
        self.SUBTYPE_COLLECTION = {}
        self.NON_STANDARD_COUNTRY = []
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
        class_h1 = soup.find_all('h1')
        assert len(class_h1) == 1, "InvalidAssumption: Each ns country page contains only 1 h1 header"
        class_subtypes_list = class_h1[0].find_next_siblings('div')
        assert len(class_subtypes_list) >= 1, "InvalidAssumption: Each ns class listing has one or more entries"
        for ns_sub_type in class_subtypes_list:
            sub_type_url = urljoin(parsed_url, ns_sub_type.find('a')['href'])
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
        class_list_all = soup.find_all('div', {"id": "PageLayer"})
        assert len(class_list_all) == 1, "InvalidAssumption: Each country page contains only 1 PageLayer div" \
                                         " that lists classes."
        class_list = class_list_all[0]
        if class_list:
            table_list = class_list.find_all('table')
            assert len(table_list) == 1, "InvalidAssumption: PageLayer div contains only 1 table of classes"
            rows = table_list[0].find_all('tr')
            self._current_subtype_id = self.create_sub_type_id_of_ns_class(rows[0],
                                                                           userland_dict.get('country').country)
            for row in rows[1:]:
                self.process_class_row(row, userland_dict['country'], parsed_url)
        else:
            self.NON_STANDARD_COUNTRY.append(parsed_url)
        assert self._class_table_header_is_identified, "InvalidAssumption: Class Table will mandatorily have table header with " \
                                                       "its first column header as text Class (case sensitive)"
        assert self.CLASS_FOUND_FOR_COUNTRY.get(userland_dict['country'],
                                                False), "InvalidAssumption: Country ({}) page will " \
                                                        "have at least one class." \
            .format(userland_dict['country'])

    def extract_classes_of_country(self, soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                                   userland_dict: dict = None) -> []:
        self._class_table_header_is_identified = False
        self._current_subtype_id = None
        self.classRowExtractor = userland_dict.get('class_extractor')
        class_list_all = soup.find_all('div', {"id": "PageLayer"})
        assert len(class_list_all) == 1, "InvalidAssumption: Each country page contains only 1 PageLayer div" \
                                         " that lists classes."
        class_list = class_list_all[0]
        if class_list:
            table_list = class_list.find_all('table')
            assert len(table_list) == 1, "InvalidAssumption: PageLayer div contains only 1 table of classes"
            for row in table_list[0].find_all('tr'):
                self.process_class_row(row, userland_dict['country'], parsed_url)
        else:
            self.NON_STANDARD_COUNTRY.append(parsed_url)
        assert self._class_table_header_is_identified, "InvalidAssumption: Class Table will mandatorily have " \
                                                       "table header with its first column header as text " \
                                                       "Class (case sensitive)"
        assert self.CLASS_FOUND_FOR_COUNTRY.get(userland_dict['country'],
                                                False), "InvalidAssumption: Country ({}) page will " \
                                                        "have at least one class." \
            .format(userland_dict['country'])

    def process_class_row(self, row: PageElement, country: dict, parsed_url: str):
        """Check if not _class_table_header_is_identified"""
        if not self._class_table_header_is_identified:
            """See if this is the header, and set 
            _class_table_header_is_identified accordingly 
            and return"""
            self._class_table_header_is_identified = self.is_this_class_header(row)
            return

        # Check if record is a subtype, as at this point table header is identified
        if self.is_this_subcategory_data(row):
            # Add to set and set _current_subtype_id flag and return
            self._current_subtype_id = self.identify_or_create_sub_type_id(self.extract_subcategory(row))
            return

        # Normal record
        if not self.is_this_class_record(row):
            self.log_row_as_containing_too_few_class_properties(parsed_url)
            return
        # Extract information and map against _current_subtype_id
        self.create_new_class_with_extracted_subcategory(row, country, self._current_subtype_id, parsed_url)

    def identify_or_create_sub_type_id(self, sub_type: str):
        if sub_type in self.SUBTYPE_COLLECTION:
            return sub_type, self.SUBTYPE_COLLECTION[sub_type]
        new_id = len(self.SUBTYPE_COLLECTION) + 1
        self.SUBTYPE_COLLECTION[sub_type] = new_id
        return sub_type, new_id

    def create_sub_type_id_of_ns_class(self, sub_type_str: str, country):
        beginswith = "Overview of "
        endswith = " in " + country
        assert sub_type_str.text.strip().startswith(beginswith), "InvalidAssumption: Subtype identification " \
                                                                 "of classes of non-standard countries does not" \
                                                                 "begin with 'Overview of'"
        assert sub_type_str.text.strip().endswith(endswith), "InvalidAssumption: Subtype identification " \
                                                             "of classes of non-standard countries does not" \
                                                             "end with ' in Country'"
        sub_type = sub_type_str.text.strip().replace(beginswith, "").replace(endswith, "")
        if sub_type in self.SUBTYPE_COLLECTION:
            return sub_type, self.SUBTYPE_COLLECTION[sub_type]
        new_id = len(self.SUBTYPE_COLLECTION) + 1
        self.SUBTYPE_COLLECTION[sub_type] = new_id
        return sub_type, new_id

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
                                                    parsed_url: str):
        columns = row.find_all('td')
        tonal_href = None
        has_tonal = self.does_class_contain_tonal(columns[0])
        if has_tonal:
            tonal_href = urljoin(parsed_url, self.extract_tonal_href(columns[0]))
        # Declare contents of a class
        class_name, designator, power, shaft, bhp, temp, rr = self.classRowExtractor.retrieve_row(columns)

        seq = len(self.CLASS_COLLECTION) + 1
        self.CLASS_COLLECTION.append(ClassU(seq,
                                            class_name,
                                            current_subtype,
                                            country,
                                            designator,
                                            power,
                                            shaft,
                                            bhp,
                                            temp,
                                            rr,
                                            has_tonal,
                                            tonal_href))
        self.CLASS_FOUND_FOR_COUNTRY[country] = True

    @staticmethod
    def does_class_contain_tonal(table_data: PageElement):
        if table_data.find('a') is not None:
            return True
        return False

    @staticmethod
    def extract_tonal_href(table_data: PageElement):
        return table_data.find('a').get('href')

    def log_row_as_containing_too_few_class_properties(self, parsed_url: str):
        self.TOO_FEW_PROPERTIES.append(parsed_url)