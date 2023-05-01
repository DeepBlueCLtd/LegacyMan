import re


def cleanse(item):
    if item is None:
        return item
    # Strip all leading spaces after new line
    item = re.sub('[\n][ ]+', '\n', item)
    # Replace all newlines with space
    item = re.sub('\r', '', item)
    item = re.sub('\n', ' ', item)
    item = item.strip()
    return item
