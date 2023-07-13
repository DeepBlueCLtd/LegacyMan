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

def create_classlist(root=None,id=None):
    xml = root.createElement('classlist') 
    xml.setAttribute('id', id.lower().replace(" ", ""))
    root.appendChild(xml)

    title = root.createElement('title')
    text_content = root.createTextNode(id)
    title.appendChild(text_content)
    xml.appendChild(title)

    return xml

def create_class(root=None,id=None):
    xml = root.createElement('class') 
    xml.setAttribute('id', id.lower().replace(" ", ""))
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

def create_images(root=None,body=None):
    images = root.createElement('images')
    body.appendChild(images)

    return images

def create_section(root=None,body=None, section=None,title_str=None):
    section_element = root.createElement(section.lower())
    section_element.setAttribute('id', section.lower())
    body.appendChild(section_element)

    title_str =  title_str if title_str == None else section.capitalize()
    if title_str != None : 
        title = root.createElement('title')
        text_content = root.createTextNode(title_str)
        title.appendChild(text_content)
        section_element.appendChild(title)


    return section_element


#     <body>
#     <images></images>
#     <summary id="xx">
#       <table>
#         <tgroup cols="1">
#           <tbody>
#             <row>
#               <entry></entry>
#             </row>
#           </tbody>
#         </tgroup>
#       </table>
#     </summary>
#   </body>

def create_classlist_body(root=None,topic=None):
    classlistbody = root.createElement('classlistbody')
    topic.appendChild(classlistbody)

    return classlistbody


def create_flag(root=None,url=None,topic=None):
    flag = root.createElement('flag')
    fig = root.createElement('fig')
    flag.appendChild(fig)
    image = root.createElement('image') 
    url = url if url != None else "#" 
    image.setAttribute('href', url)
    image.setAttribute('alt', 'flag')
    fig.appendChild(image)

    topic.appendChild(flag)
    return flag

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

def create_classtable(root=None,section=None, cols=None):
    # table = root.createElement('table')
    # section.appendChild(table)

    # # <tgroup cols="2">
    # tgroup = root.createElement('tgroup')
    # tgroup.setAttribute('cols', cols)
    # table.appendChild(tgroup)

    # # <tbody>
    # tbody = root.createElement('tbody')
    # tgroup.appendChild(tbody)

    # # <row>
    # row = root.createElement('row')
    # tbody.appendChild(row)


    # <table colsep="1" rowsep="1">
    colsep = "1"
    rowsep = "1"
    table = root.createElement('table')
    table.setAttribute('colsep', colsep)
    table.setAttribute('rowsep', rowsep)
    section.appendChild(table)

    # <tgroup cols="7" colsep="1" rowsep="1">
    tgroup = root.createElement('tgroup')
    tgroup.setAttribute('cols', cols)
    tgroup.setAttribute('colsep', colsep)
    tgroup.setAttribute('rowsep', rowsep)
    table.appendChild(tgroup)

    #  <colspec colnum="1" colname="col1"/>
    for i in range(1, int(cols)+1):
        colspec = root.createElement('colspec')
        colspec.setAttribute('colnum', str(i))
        colspec.setAttribute('colname', "col"+str(i))
        tgroup.appendChild(colspec)

    # <tbody>
    tbody = root.createElement('tbody')
    tgroup.appendChild(tbody)

    return tbody

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

def create_classlisttable_body(root=None,body=None, cols=None):
    # <table colsep="1" rowsep="1">
    colsep = "1"
    rowsep = "1"
    table = root.createElement('table')
    table.setAttribute('colsep', colsep)
    table.setAttribute('rowsep', rowsep)
    body.appendChild(table)

    # <tgroup cols="7" colsep="1" rowsep="1">
    tgroup = root.createElement('tgroup')
    tgroup.setAttribute('cols', cols)
    tgroup.setAttribute('colsep', colsep)
    tgroup.setAttribute('rowsep', rowsep)
    table.appendChild(tgroup)

    #  <colspec colnum="1" colname="col1"/>
    for i in range(1, int(cols)+1):
        colspec = root.createElement('colspec')
        colspec.setAttribute('colnum', str(i))
        colspec.setAttribute('colname', "col"+str(i))
        tgroup.appendChild(colspec)

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
    # relative_path_utl = width if width == None else "450px"
    image.setAttribute('width', width)
    return image

def create_bullets(root=None,section=None, bullets=None):
    span = root.createElement('span')
    section.appendChild(span)

    ol = root.createElement('ol')
    span.appendChild(ol)

    for bullet in bullets:
        if bullet.strip() != "" : 
            li = root.createElement('li')
            text_li = root.createTextNode(bullet)
            li.appendChild(text_li)
            ol.appendChild(li)

    return span