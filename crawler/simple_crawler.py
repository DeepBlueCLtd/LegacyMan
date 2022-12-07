import hashlib
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


class SimpleCrawler:
    def __init__(self, url):
        self.start_page = url
        self.visited_child_resources = {}
        self.unreachable_child_resources = {}

    class Resources:
        def __init__(self, url, parent_url):
            m = hashlib.sha256()
            m.update(bytes(url, 'utf-8'))
            self.id = m.hexdigest()
            self.url = url
            self.parent_url = parent_url

    def add_visited_child_resource(self, resource):
        if resource.id in self.visited_child_resources:
            return False
        self.visited_child_resources[resource.id] = resource
        return True

    def add_unreachable_child_resource(self, resource):
        if resource.id in self.unreachable_child_resources:
            return False
        self.unreachable_child_resources[resource.id] = resource
        return True

    def crawl(self, url=None, parent_url=None, resource_processor_callback=None):
        if url is None:
            url = self.start_page
        parsed_url = url
        resource = self.Resources(parsed_url, parent_url)
        page = requests.get(parsed_url)
        crawl_resource = False
        if page.status_code == 200:
            crawl_resource = self.add_visited_child_resource(resource)
        else:
            print("Reference {} not found in {}".format(parsed_url, parent_url))
            self.add_unreachable_child_resource(resource)
        if not crawl_resource:
            return

        soup = BeautifulSoup(page.text, features="lxml")
        for link in soup.find_all('a'):
            child_parsed_url = urlparse(link.get('href')).geturl()
            if 'http' not in child_parsed_url[0:4]:
                child_parsed_url = urlparse(
                    urljoin(parsed_url, child_parsed_url)).geturl()
            self.crawl(child_parsed_url,
                       parsed_url,
                       resource_processor_callback)
