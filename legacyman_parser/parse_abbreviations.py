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
    assert len(soup.find_all('table')) == 2, "InvalidAssumption: There's going to be only two tables in " \
                                             "QuickLinksData/Abbreviations.html => {}".format(parsed_url)

    compactor = []
    for abbrev_record in soup.find('table').find_all('tr'):

        assert len(abbrev_record.find_all('td')) == 4, "InvalidAssumption: Each row in this table contains " \
                                                       "two key-value pairs, side-by-side => {}".format(parsed_url)

        for abbr_data in abbrev_record.find_all('td'):
            compactor.append(abbr_data.text)
    for idx in range(0, len(compactor)//2):
        ABBREVIATIONS.append(AbbreviationMap(idx + 1, compactor[2*idx], compactor[(2*idx)+1]))
