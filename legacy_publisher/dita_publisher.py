import json
import os 

from xml.dom import minidom
from os.path import dirname, abspath
from legacyman_parser.utils.constants import DITA_REGIONS_EXPORT_FILE
from distutils.dir_util import copy_tree
from legacy_publisher.dita_helper import create_dita_root, write_dita_doc, create_topic, create_body,create_table,create_xref
from legacyman_parser.dita_ot_validator import validate, get_dita

dita_ot = get_dita()
doctype_str = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">\n'

"""This module will handle post parsing enhancements for DITA publishing"""
def publish_regions(regions=None, sourcepath=None):
    root = minidom.Document()

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

        shape = root.createElement('shape')
        text_shape = root.createTextNode(region.shape)
        shape.appendChild(text_shape)
        area.appendChild(shape)

        coords = root.createElement('coords')
        text_coords = root.createTextNode(region.coords)
        coords.appendChild(text_coords)
        area.appendChild(coords)

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

    if(dita_ot != None):
        xml_file = abspath('./target/dita/regions.dita')
        dtd_file = dita_ot+'/plugins/org.oasis-open.dita.v1_2/dtd/technicalContent/dtd/topic.dtd'
        validate(xml_file, dtd_file)


def publish_country_regions(regions=None, stcountries=None):
    countries = stcountries
    standard_countries = get_countries(regions=regions,stcountries=countries)

    for region in regions.regions:
        current_region = region.region
        if current_region in standard_countries:
            process_countries(region=current_region,countries=countries, current=current_region, nst=False)

def publish_ns_country_regions(regions=None, stcountries=None, nstcountries=None):
    countries = nstcountries
    standard_countries = get_countries(regions=regions, stcountries=stcountries)
    non_standard_countries = get_countries(regions=regions, stcountries=countries)

    for region in regions.regions:
        current_region = region.region
        if current_region not in standard_countries:
            process_countries(region=current_region,countries=countries, current=current_region, nst=False)

def get_countries(regions=None, stcountries=None):
    countries = []
    for region in regions.regions:
        current_region = region.region
        for country in stcountries:            
            if current_region not in countries and current_region == country.region.region:
                countries.append(current_region)

    return countries

def process_countries(region=None, countries=None,current=None,nst=True):
    current_region=current
    root = create_dita_root(doctype_str=None)
    topic = create_topic(root=root,id=current_region)
    body = create_body(root=root,topic=topic)

    number_country = 0
    for country in countries:
        if(current_region == country.region.region):
            number_country+=1

    pstr = "" if nst == True else "regions/"
    row = create_table(root=root,body=body, cols=str(number_country))
    export_dita = dirname(DITA_REGIONS_EXPORT_FILE)+"/"+pstr+current_region+"/"+current_region+".dita"

    for country in countries:
        if(current_region == country.region.region):
            entry = root.createElement('entry')
            relative_path_utl = "#" if country.url == None else os.path.relpath(country.url , dirname(export_dita))
            xref = create_xref(root=root,text=country.country,url=relative_path_utl,format="html")
            entry.appendChild(xref) 
            row.appendChild(entry)

    isDestExist = os.path.exists(dirname(export_dita))
    if not isDestExist:
        os.makedirs(dirname(export_dita))
    print("export_dita :", export_dita)
    write_dita_doc(root, export_dita)

    if(dita_ot != None):
        xml_file = abspath(export_dita)
        dtd_file = dita_ot+'/plugins/org.oasis-open.dita.v1_2/dtd/technicalContent/dtd/topic.dtd'
        validate(xml_file, dtd_file)
