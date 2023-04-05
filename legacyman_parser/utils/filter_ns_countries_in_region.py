from bs4 import BeautifulSoup

"""
Filter out non-standard countries in regions
"""
NS_COUNTRY_IN_REGION_COLLECTION = []


def filter_ns_countries(soup: BeautifulSoup = None,
                        parsed_url: str = None,
                        parent_url: str = None,
                        userland_dict: dict = None) -> []:
    # get the PageLayer div
    class_list_all = soup.find_all('div', {"id": "PageLayer"})
    if len(class_list_all) == 0:
        NS_COUNTRY_IN_REGION_COLLECTION.append(userland_dict['country'])