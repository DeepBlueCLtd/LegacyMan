import json
import os 

from xml.dom import minidom
from os.path import dirname, abspath
from legacyman_parser.utils.constants import DITA_REGIONS_EXPORT_FILE
from distutils.dir_util import copy_tree

xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n' 
doctype_topic_str = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">\n'

def create_dita_root(doctype_str=None):
    if(doctype_str != None):
        doctype_topic_str = doctype_str

    return minidom.Document()

def write_dita_doc(root=None, export_path=None, doctype_str=None):
    doc_str = doctype_str if doctype_str != None else doctype_topic_str
    root = root.childNodes[0]
    xml_string = root.toprettyxml(indent='  ')
    xml_string_with_doctype = xml_declaration + doc_str + xml_string

    print("Create / Save ("+export_path+") : ", export_path)

    with open(export_path, "w") as f:
       f.write(xml_string_with_doctype) 

def create_topic(root=None,id=None):
    xml = root.createElement('topic') 
    xml.setAttribute('id', id)
    root.appendChild(xml)

    title = root.createElement('title')
    text_content = root.createTextNode(id)
    title.appendChild(text_content)
    xml.appendChild(title)

    return xml

def create_richcollection(root=None,id=None):
    xml = root.createElement('rich-collection') 
    xml.setAttribute('id', id)
    root.appendChild(xml)

    title = root.createElement('title')
    text_content = root.createTextNode(id)
    title.appendChild(text_content)
    xml.appendChild(title)

    return xml

def create_body(root=None,topic=None):
    body = root.createElement('body')
    topic.appendChild(body)

    return body


def create_table(root=None,body=None, cols=None):
    table = root.createElement('table')
    body.appendChild(table)

    # <tgroup cols="2">
    tgroup = root.createElement('tgroup')
    tgroup.setAttribute('cols', cols)
    table.appendChild(tgroup)

    # <tbody>
    tbody = root.createElement('tbody')
    tgroup.appendChild(tbody)

    # # <row>
    row = root.createElement('row')
    tbody.appendChild(row)

    return row

def create_table_body(root=None,body=None, cols=None):
    table = root.createElement('table')
    body.appendChild(table)

    # <tgroup cols="2">
    tgroup = root.createElement('tgroup')
    tgroup.setAttribute('cols', cols)
    table.appendChild(tgroup)

    # <tbody>
    tbody = root.createElement('tbody')
    tgroup.appendChild(tbody)

    return tbody


def create_xref(root=None,text=None,url=None,format=None):
    xref = root.createElement('xref')
    text_name = root.createTextNode(text.strip())
    xref.appendChild(text_name)
 
    xref.setAttribute('href', url)
    xref.setAttribute('format', format)
    
    return xref

def create_image(root=None,url=None,style=None):
    image = root.createElement('image') 
    image.setAttribute('href', url)
    width = str(style).replace("width:", "").replace("%","0px")
    relative_path_utl = width if width == None else "450px"
    image.setAttribute('width', width)
    return image
