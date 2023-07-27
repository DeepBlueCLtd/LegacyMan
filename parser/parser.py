
import sys
import time
import os
import shutil
import subprocess
from bs4 import BeautifulSoup
import xml.dom.minidom


def delete_directory(path):
    if os.path.exists(path):
        os.system('rm -rf {}'.format(path))
        print('Target directory deleted')
    else:
        print('Target directory does not exist')

def create_directory(name):
    try:
        os.mkdir(name)
        print(f'{name} directory created')
    except FileExistsError:
        print(f'The directory {name} already exists')

def copy_files(source_dir, target_dir, file_names):
    #create the target dir if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    #copy files
    for file_name in file_names:
        source_file = os.path.join(source_dir, file_name)
        target_file = os.path.join(target_dir, file_name)
        #print('copy ', source_file, ' ', target_dir)
        shutil.copy(source_file, target_dir)

def prettify_xml(xml_code):
    dom = xml.dom.minidom.parseString(xml_code)
    return dom.toprettyxml()

def process_regions():
    #copy the world-map.gif file
    source_dir = "data/PlatformData/Content/images/"
    target_dir = "target/dita/regions/content/images"
    copy_files(source_dir, target_dir, ["world-map.gif"])

    #read the PD_1.html file
    with open("data/PlatformData/PD_1.html", "r") as f:
         html_string = f.read()

    #set Beautifulsoup objects to parse HTML and DITA files
    soup = BeautifulSoup(html_string, 'html.parser')
    dita_soup = BeautifulSoup('', 'lxml-xml')

    #Parse the HTML string, parser the <map> and the <img> elements
    img_element = soup.find('img', {'usemap': '#image-map'})
    map_element = soup.find('map', {'name': 'image-map'})

    #Create the html <image> element in the DITA file
    dita_image = dita_soup.new_tag('image')
    dita_image['href'] = img_element['src'].lower()

    #Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, 'xml')

    #Create a body,title and imagemap elements
    dita_body = dita_soup.new_tag('body')
    dita_imagemap = dita_soup.new_tag('imagemap')
    dita_title = dita_soup.new_tag('title')
    dita_title.string = "Regions"

    #Append the image and the map in the imagemap
    dita_imagemap.append(dita_image)
    for area in map_element.find_all('area'):
        dita_shape = dita_soup.new_tag('shape')
        dita_shape.string = area['shape']

        dita_coords = dita_soup.new_tag('coords')
        dita_coords.string = area['coords']

        dita_xref = dita_soup.new_tag('xref')
        dita_xref['format'] = 'dita'
        dita_xref['href'] = "./regions.dita"

        #if link starts with ../ create a dita file for the country => example ../Britain/Britain1.html
        link = area['href']
        country_name = area['alt']
        if link.startswith("../"):
            process_ns_countries(country_name, link[3:]) #remove the first 2 chars of the link ../

        dita_area = dita_soup.new_tag('area')
        dita_area.append(dita_shape)
        dita_area.append(dita_coords)
        dita_area.append(dita_xref)

        dita_imagemap.append(dita_area)

    dita_body.append(dita_imagemap)

    #Create a <topic> element in the DITA file and append the <map> and the <image> elements
    dita_topic = dita_soup.new_tag('topic')
    dita_topic['id'] = "links_1"

    dita_topic.append(dita_title)
    dita_topic.append(dita_body)

    #Append the <topic> element to the BeautifulSoup object
    dita_soup.append(dita_topic)

    #Write the DITA file
    dita_output = 'target/dita/regions'
    create_directory(dita_output)

    #Prettify the code
    prettified_code = prettify_xml(str(dita_soup))

    with open(f'{dita_output}/regions.dita', 'wb') as f:
        f.write(prettified_code.encode('utf-8'))

def process_ns_countries(country_name, link):
    #read the html file
    with open(f'data/{link}', "r") as f:
         html_string = f.read()

    #set Beautifulsoup objects to parse HTML and DITA files
    soup = BeautifulSoup(html_string, 'html.parser')

    #Parse the HTML string, parser the <map> and the <img> elements
    img_links_table = soup.find('div', {'id': 'ImageLinksTable'})
    if img_links_table is None:
        raise ValueError("ImageLinksTable not found in the HTML file")

    #Create the DITA document type declaration string
    dita_doctype = '<!DOCTYPE rich-collection SYSTEM "../../dtd/rich-collection.dtd">'
    dita_soup = BeautifulSoup(dita_doctype, 'xml')

     #Create dita elements: <rich-collection>,<title>,<table>,<tbody>,<tgroup>...
    dita_rich_collection = dita_soup.new_tag('rich-collection')
    dita_title = dita_soup.new_tag('title')
    dita_title.string = country_name
    dita_rich_collection.append(dita_title)

    #Create DITA elements <xref>,<image>,
    dita_row = dita_soup.new_tag('row')

    for img_link in img_links_table.find_all('a'):
        dita_xref = dita_soup.new_tag('xref')
        dita_xref["href"] = img_link["href"]
        dita_xref["format"] = "dita"

        dita_bold = dita_soup.new_tag('b')
        dita_bold.string = img_link.text.strip()

        dita_img = dita_soup.new_tag('image')
        dita_img['width'] = '400px'
        dita_img['href'] = img_link.img['src']

        dita_xref.append(dita_bold)
        dita_xref.append(dita_img)

        dita_entry = dita_soup.new_tag('entry')
        dita_entry.append(dita_xref)

        dita_row.append(dita_entry)

    dita_tbody = dita_soup.new_tag('tbody')
    dita_tbody.append(dita_row)

    dita_tgroup = dita_soup.new_tag('tgroup')
    dita_tgroup["cols"] = "2"
    dita_tgroup.append(dita_tbody)

    dita_table = dita_soup.new_tag('table')
    dita_table.append(dita_tgroup)

    dita_body = dita_soup.new_tag('body')
    dita_body.append(dita_table)

    dita_rich_collection.append(dita_body)

    #Append the rich-collection element to the dita_soup object
    dita_soup.append(dita_rich_collection)

    #Write the DITA file
    dita_output = f'target/dita/regions/{country_name}'
    create_directory(dita_output)

    #Prettify the code
    prettified_code = prettify_xml(str(dita_soup))

    with open(f'{dita_output}/{country_name}.dita', 'wb') as f:
        f.write(prettified_code.encode('utf-8'))

def parse_from_root(args):
    print(f'LegacyMan parser running, with these arguments: {args}')
    start_time = time.time()

    #remove existing target directory and recreate it
    delete_directory(os.path.join(os.getcwd(), "target"))
    create_directory("target")

    #copy index.dita and welcome.dita from data dir to target/dita
    source_dir = "data"
    target_dir = os.path.join("target", "dita")
    copy_files(source_dir, target_dir, ["index.ditamap", "welcome.dita"])

    #Produce the world map
    process_regions()

    #Run DITA-OT command to transform the index.ditamap file to html
    dita_command = ["dita", "-i", "./target/dita/index.ditamap", "-f", "html5", "-o", "./target/html"]
    subprocess.run(dita_command)

    end_time = time.time()
    parse_time = end_time - start_time
    print(f'Publish complete after {parse_time} seconds. Root file at /target/dita/index.ditamap')

if __name__ == '__main__':
    args = sys.argv[1:]
    parse_from_root(args)