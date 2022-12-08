import hashlib
import logging
import os
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

logger = logging.getLogger('SimpleCrawler')


class Response:
    def __init__(self, status_code, reason):
        self.text = None
        self.status_code = status_code
        self.reason = reason


def open_file(url):
    # path = os.path.normcase(os.path.normpath(url))

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

    def retrieve_resource(self, resource):
        return self.visited_child_resources[resource.id]

    def crawl(self, url=None, parent_url=None, resource_processor_callback=None):
        logger.info("Checking {}".format(url))
        if url is None:
            url = self.start_page
        parsed_url = url
        resource = self.Resources(parsed_url, parent_url)
        page = open_file(parsed_url)

        crawl_child_resource = False
        child_resource_already_accessed = False

        if page.status_code == 200:
            child_resource_already_accessed = not self.add_visited_child_resource(resource)
            crawl_child_resource = True
        else:
            logger.error("Reference {} not found in {}".format(parsed_url, parent_url))
            self.add_unreachable_child_resource(resource)

        if child_resource_already_accessed:
            logger.warning("-")
            logger.warning("Duplicate reference {} detected and avoided from {}".format(parsed_url, parent_url))
            logger.warning("Reference already accessed from {}".format(self.retrieve_resource(resource).parent_url))
            logger.warning("--")
            return

        if not crawl_child_resource:
            return

        soup = BeautifulSoup(page.text, features="lxml")
        if resource_processor_callback is not None:
            resource_processor_callback(soup, parsed_url, parent_url)
        for link in soup.find_all('a'):
            child_parsed_url = urlparse(
                    urljoin(parsed_url, urlparse(link.get('href')).path)).geturl()
            if child_parsed_url.startswith('/'):
                logger.warning("Absolute path {} referenced".format(child_parsed_url))
            self.crawl(child_parsed_url,
                       parsed_url,
                       resource_processor_callback)
