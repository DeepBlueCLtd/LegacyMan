"""
The default urljoin isn't working consistently, and hence will be replaced by urljoin2 defined here
➜ DeepBlueCLtd-LegacyMan-1b7ef97 python3
Python 3.9.2 (default, Feb 28 2021, 17:03:44)
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from urllib.parse import urljoin
>>> parsed_url='data\PlatformData\PD_1.html'
>>> rela='Europe.html'
>>> parsed_region_url = urljoin(parsed_url, rela)
>>> parsed_region_url
'Europe.html'
>>>
"""
import os


def urljoin2(parsed_url: str, relative: str):
    return os.path.join(os.path.dirname(parsed_url), relative)
