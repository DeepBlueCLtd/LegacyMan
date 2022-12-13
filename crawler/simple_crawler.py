import hashlib
import logging
import os
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup


class Response:
    def __init__(self, status_code, reason):
        self.text = None
        self.status_code = status_code
        self.reason = reason


def open_file(url):
    status_code, reason = check_path(url)
    response = Response(status_code, reason)
    if response.status_code == 200:
        with open(url, 'rb') as f:
            response.text = f.read()
    return response


def check_path(path):
    """Return an HTTP status for the given filesystem path."""
    if os.path.isdir(path):
        return 400, "Path Not A File"
    elif not os.path.isfile(path):
        return 404, "File Not Found"
    elif not os.access(path, os.R_OK):
        return 403, "Access Denied"
    else:
        return 200, "OK"


class SimpleCrawler:
    def __init__(self, url=None, disable_crawler_log=None, userland_dict=None):
        self.start_page = url
        self.visited_child_resources = {}
        self.unreachable_child_resources = {}
        self.logger = logging.getLogger('SimpleCrawler')
        self.logger.disabled = disable_crawler_log
        self.userland_dict = userland_dict

    class Resources:
        def __init__(self, url, parent_url):
            m = hashlib.sha256()
            m.update(bytes(url, 'utf-8'))
            self.id = m.hexdigest()
            self.url = url
            self.parent_url = parent_url

    def retrieve_resource(self, resource):
        return self.visited_child_resources[resource.id]

    def crawl(self,
              url=None,
              parent_url=None,
              resource_processor_callback=None,
              crawl_recursively=None):
        self.logger.info("Checking {}".format(url))
        if url is None:
            url = self.start_page
        parsed_url = url
        resource = self.Resources(parsed_url, parent_url)
        page = open_file(parsed_url)

        crawl_child_resource = False
        child_resource_already_accessed = False

        if page.status_code == 200:
            child_resource_already_accessed = resource.id in self.visited_child_resources
            if not child_resource_already_accessed:
                self.visited_child_resources[resource.id] = resource
            crawl_child_resource = True
        else:
            self.logger.error("Reference {} not found. Referred from {}"
                              .format(parsed_url,
                                      "user input" if parent_url is None else parent_url))
            self.unreachable_child_resources[resource.id] = resource

        if child_resource_already_accessed:
            self.logger.warning(("\n-\nDuplicate reference {} detected and avoided from {}." +
                                 "\nReference already accessed from {}." +
                                 "\n--").format(parsed_url,
                                                parent_url,
                                                self.retrieve_resource(resource).parent_url))
            if resource_processor_callback is not None:
                already_access_soup = BeautifulSoup(page.text, "html.parser")
                resource_processor_callback(soup=already_access_soup,
                                            parsed_url=parsed_url,
                                            parent_url=parent_url,
                                            userland_dict=self.userland_dict)
            return

        if not crawl_child_resource:
            return

        soup = BeautifulSoup(page.text, "html.parser")
        if resource_processor_callback is not None:
            resource_processor_callback(soup=soup,
                                        parsed_url=parsed_url,
                                        parent_url=parent_url,
                                        userland_dict=self.userland_dict)

        if not crawl_recursively:
            return
        for link in soup.find_all('a'):
            child_parsed_url = urlparse(
                urljoin(parsed_url, urlparse(link.get('href')).path)).geturl()
            if child_parsed_url.startswith('/'):
                self.logger.warning("Absolute path {} referenced".format(child_parsed_url))
            self.crawl(child_parsed_url,
                       parsed_url,
                       resource_processor_callback)
