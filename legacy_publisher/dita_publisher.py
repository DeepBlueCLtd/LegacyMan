import json
import os 

from xml.dom import minidom
from os.path import dirname, abspath
from legacyman_parser.utils.constants import DITA_REGIONS_EXPORT_FILE
from distutils.dir_util import copy_tree


"""This module will handle post parsing enhancements for DITA publishing"""
# DITA_EXPORT_FILE = DITA_REGIONS_EXPORT_FILE

def publish_regions(regions=None, sourcepath=None):
    root = minidom.Document()
    doctype_str = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">\n'

    xml = root.createElement('topic') 
    xml.setAttribute('id', 'links_1')
    root.appendChild(xml)
    
    title = root.createElement('title')
    text_content = root.createTextNode('Regions')
    title.appendChild(text_content)
    xml.appendChild(title)

    body = root.createElement('body')
    xml.appendChild(body)

    imagemap = root.createElement('imagemap')
    body.appendChild(imagemap)

    image = root.createElement('image')
    image.setAttribute('href', regions.url)
    imagemap.appendChild(image)

    for region in regions.regions:
        area = root.createElement('area')
        imagemap.appendChild(area)

        coords = root.createElement('coords')
        text_coords = root.createTextNode(region.coords)
        coords.appendChild(text_coords)
        area.appendChild(coords)

        shape = root.createElement('shape')
        text_shape = root.createTextNode(region.shape)
        shape.appendChild(text_shape)
        area.appendChild(shape)

        xref = root.createElement('xref')
        text_name = root.createTextNode(region.region)
        xref.appendChild(text_name)

        relative_path_utl = os.path.relpath(region.url, dirname(DITA_REGIONS_EXPORT_FILE))
        xref.setAttribute('href', relative_path_utl)
        xref.setAttribute('format', 'html')
        area.appendChild(xref)

    root = root.childNodes[0]
    xml_string = root.toprettyxml(indent='  ')

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_string_with_doctype = xml_declaration + doctype_str + xml_string

    print("Create / Save regions.dita : ", DITA_REGIONS_EXPORT_FILE)

    dita_dir = dirname(abspath(DITA_REGIONS_EXPORT_FILE))
    isExist = os.path.exists(dita_dir)
    if not isExist:
        os.makedirs(dita_dir)

    # copy map image
    image_url = abspath(regions.url);
    target_dir = dirname(dirname(dirname(abspath(DITA_REGIONS_EXPORT_FILE))))
    new_path = image_url.replace(target_dir, "")
    source_path = dirname(abspath(sourcepath));

    print('copy ('+source_path+new_path+') to ('+dita_dir+new_path+')')
    isDestExist = os.path.exists(dirname(dita_dir+new_path))
    if not isDestExist:
        os.makedirs(dirname(dita_dir+new_path))
    os.system('cp '+source_path+new_path+' '+dita_dir+new_path)

    with open(DITA_REGIONS_EXPORT_FILE, "w") as f:
       f.write(xml_string_with_doctype) 
