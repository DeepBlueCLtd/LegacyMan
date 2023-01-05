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
    # Assumption: There's going to be only one table in QuickLinksData/Abbreviations.html
    assert len(soup.find_all('table')) == 1, "InvalidAssumption: There's going to be only one table in " \
                                             "QuickLinksData/Abbreviations.html"

    compactor = []
    for abbrev_record in soup.find('table').find_all('tr'):

        # Assumption: Each row in this table contains two key-value pairs, side-by-side i.e.
        # <tr><td>Key1</td><td>Value1</td><td>Key2</td><td>Value2</td></tr>
        # In other words, row should have only 4 td elements
        assert len(abbrev_record.find_all('td')) == 4, "InvalidAssumption: Each row in this table contains " \
                                                       "two key-value pairs, side-by-side"

        for abbr_data in abbrev_record.find_all('td'):
            compactor.append(abbr_data.text)
    for idx in range(0, len(compactor)//2):
        ABBREVIATIONS.append(AbbreviationMap(idx + 1, compactor[2*idx], compactor[(2*idx)+1]))
