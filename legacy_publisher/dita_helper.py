import json
import os 
import re

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
    remove_whitespace(root)
    xml_string = root.toxml()

    # Remove line breaks around <li> elements
    clean_xml_string = re.sub(r'\s*<li>', '<li>', xml_string)
    clean_xml_string = re.sub(r'</li>\s*', '</li>', clean_xml_string)

    # Parse the XML string
    dom = minidom.parseString(clean_xml_string).childNodes[0]

    # Serialize the DOM object with proper indentation
    pretty_xml_string = dom.toprettyxml(indent="    ")

    xml_string_with_doctype = xml_declaration + doc_str + pretty_xml_string

    # print("Create / Save ("+export_path+") : ", export_path)

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

def create_dita_block(root=None,section=None, bullets=None):
    for element in bullets:
        if element.name == "p" and len(element.find_all("img")) >= 1 :
            image = element.find_all("img")
            href = None
            for image in element.find_all('img'):
                href = image.get('src')
                fig = root.createElement('fig')
                image = root.createElement('image')
                image.setAttribute('href', href)
                fig.appendChild(image)
                section.appendChild(fig)

        elif element.name != "div":
            html_element = minidom.parseString(str(element)).documentElement
            section.appendChild(html_element)
        elif element.name == "div":
            image = element.find_all("img")
            table = element.find("table")

            if len(element.find_all("img")) >= 1:
                href = None
                for image in element.find_all('img'):
                    href = image.get('src')
                    fig = root.createElement('fig')
                    image = root.createElement('image')
                    image.setAttribute('href', href)
                    fig.appendChild(image)
                    section.appendChild(fig)

            if len(element.find_all("table")) >= 1:
                tbodypropulsion = create_classtable(root=root,section=section, cols=str(4))
                rows_propulson = process_rows(table=table,colspan=4)
                process_complex_rows(rows_propulson,root,tbodypropulsion, 4, 4)

    return  section

def remove_whitespace(node):
    if node.nodeType == node.TEXT_NODE:
        node.data = node.data.strip().replace('\n', '').replace('\r', '')
    elif node.nodeType == node.ELEMENT_NODE:
        for child_node in node.childNodes:
            remove_whitespace(child_node)

def process_rows(table=None, colspan=None):
    rows_propulson = []
    if table != None:
        first_row = table.find('tr')
        columns = first_row.find('td')
        
        i = 1
        for row in table.find_all('tr'):
            tr = []
            for td in row.find_all('td'):
                href = None
                for link in td.find_all('a'):
                    href = link.get('href')
                trcolspan = None
                if td.get('colspan') != None:
                    trcolspan = td.get('colspan')

                trrowsspan = None
                if td.get('rowspan') != None:
                    trrowsspan = td.get('rowspan')


                tr.append([td.text, href, trcolspan, trrowsspan])

            rows_propulson.append(tr)
            i += 1

    return rows_propulson

def process_complex_rows(section=None,root=None,tbody=None,colspan=None, colspantr=None):
    pnamest=None
    pnameend=None
    for irow in section:
        row = root.createElement('row')
        i = 1

        for col in irow:
            entry = root.createElement('entry')

            if len(irow) == 1:
                namest="col1" 
                nameend="col"+str(colspan)
                pnamest=None
                pnameend=None
            else :
                if col[2] != None:
                    if pnameend != None:
                        namest="col"+str(pnameend+1)
                        nameend="col"+ (str(int(pnameend+1)+int(col[2]) -1 ))

                        pnamest = pnameend+1
                        pnameend = int(pnameend+1)+int(col[2]) -1 
                    else: 
                        namest="col"+str(i) 
                        nameend="col"+ (str(int(i)+int(col[2]) -1 ))

                        pnamest = i
                        pnameend = int(i)+int(col[2]) -1 


                else:
                    namest="col"+str(i) 
                    nameend="col"+str(i) 

                    pnamest=None
                    pnameend=None

            if i == colspantr:
                pnamest=None
                pnameend=None

            if len(col) == 4 and col[3] != None:
                entry.setAttribute('morerows', str(int(col[3]) - 1))

            entry.setAttribute('namest', namest)
            entry.setAttribute('nameend', nameend)


            relative_path_url = "#" if col[1] == None else col[1]

            if col[1] != None :
                xref = create_xref(root=root,text=col[0] ,url=relative_path_url,format="html")
                entry.appendChild(xref) 
            else : 
                text_content = root.createTextNode(col[0])
                entry.appendChild(text_content)

            row.appendChild(entry)
            i += 1
        tbody.appendChild(row)
