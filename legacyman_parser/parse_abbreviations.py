from bs4 import BeautifulSoup

"""Independent unit testable parse_abbreviations module 
to process abbreviations
"""
ABBREVIATIONS = []


class AbbreviationMap:
    def __init__(self, id, abbreviation, full_form):
        self.id = id
        self.abbreviation = abbreviation
        self.full_form = full_form

    def __str__(self):
        return "{}. {} ==> {}".format(self.id, self.abbreviation, self.full_form)


def parse_abbreviations(soup: BeautifulSoup = None,
                    parsed_url: str = None,
                    parent_url: str = None,
                    userland_dict: dict = None) -> []:
    compactor = []
    for abbrev_record in soup.find('table').find_all('tr'):
        for abbr_data in abbrev_record.find_all('td'):
            compactor.append(abbr_data.text)
    for idx in range(0, len(compactor)//2):
        ABBREVIATIONS.append(AbbreviationMap(idx + 1, compactor[2*idx], compactor[(2*idx)+1]))
