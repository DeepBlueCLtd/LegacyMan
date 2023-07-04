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
    doctype_str = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">'

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

        relative_path_utl = os.path.relpath(DITA_REGIONS_EXPORT_FILE,region.url)
        xref.setAttribute('href', relative_path_utl)
        xref.setAttribute('format', '')
        area.appendChild(xref)

    xml_string = root.toprettyxml(indent ="\t") 
    xml_string_with_doctype = f"{doctype_str}\n{xml_string}"

    print("Create / Save regions.dita : ", DITA_REGIONS_EXPORT_FILE)

    dita_dir = dirname(abspath(DITA_REGIONS_EXPORT_FILE))
    isExist = os.path.exists(dita_dir)
    if not isExist:
        os.makedirs(dita_dir)

    copy_tree(sourcepath+"/PlatformData/content", dita_dir+"/content")

    with open(DITA_REGIONS_EXPORT_FILE, "w") as f:
       f.write(xml_string_with_doctype) 
