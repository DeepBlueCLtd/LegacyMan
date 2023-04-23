PATH_CONTENT_CACHE_MAP = {}


def check_if_html_cached(path):
    return path in PATH_CONTENT_CACHE_MAP


def set_and_return_html_cache(path, html_string):
    PATH_CONTENT_CACHE_MAP[path] = html_string
    return PATH_CONTENT_CACHE_MAP[path]


def get_html_cache(path):
    return PATH_CONTENT_CACHE_MAP[path]
