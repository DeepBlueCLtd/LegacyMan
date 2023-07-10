import json
import os 

from xml.dom import minidom
from os.path import dirname, abspath
from legacyman_parser.utils.constants import DITA_REGIONS_EXPORT_FILE
from distutils.dir_util import copy_tree
from legacy_publisher.dita_helper import create_dita_root, write_dita_doc, create_topic, create_body,create_table,create_xref,create_richcollection, create_table_body, create_image
from legacyman_parser.dita_ot_validator import validate, get_dita

dita_ot = get_dita()
doctype_str = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">\n'
doctype_richcollection_str = '<!DOCTYPE rich-collection SYSTEM "../../../../dtd/rich-collection.dtd">\n'


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
            process_countries(region=current_region,countries=countries, current=current_region)

def publish_ns_country_regions(regions=None, nstcountries=None):
    for richcollection in nstcountries:
        rich_region = richcollection.title
        process_countries(region=rich_region, current=rich_region, nst=True, richcollection=richcollection)



def get_countries(regions=None, stcountries=None):
    countries = []
    for region in regions.regions:
        current_region = region.region
        for country in stcountries:            
            if current_region not in countries and current_region == country.region.region:
                countries.append(current_region)

    return countries

def process_countries(region=None, countries=None,current=None,nst=False, richcollection=None):
    current_region=current

    number_country = 0
    if countries != None:
        for country in countries:
            if(current_region == country.region.region):
                number_country+=1

    pstr = "regions/"
    export_dita = dirname(DITA_REGIONS_EXPORT_FILE)+"/"+pstr+current_region+"/"+current_region+".dita"
    root = create_nst_page(current_region=current_region,export_dita=export_dita, richcollection=richcollection) if nst == True else create_page(current_region=current_region,number_country=number_country,countries=countries,export_dita=export_dita)

    doc_str = doctype_richcollection_str if nst == True else None

    isDestExist = os.path.exists(dirname(export_dita))
    if not isDestExist:
        os.makedirs(dirname(export_dita))
    print("export_dita :", export_dita)
    write_dita_doc(root, export_dita, doctype_str=doc_str)

    if(dita_ot != None):
        xml_file = abspath(export_dita)
        dtd_file = dita_ot+'/plugins/org.oasis-open.dita.v1_2/dtd/technicalContent/dtd/topic.dtd'
        validate(xml_file, dtd_file)

def create_page(current_region=None,number_country=None,countries=None,export_dita=None):
    root = create_dita_root(doctype_str=None)
    topic = create_topic(root=root,id=current_region)
    body = create_body(root=root,topic=topic)
    row = create_table(root=root,body=body, cols=str(number_country))

    for country in countries:
        if(current_region == country.region.region):
            entry = root.createElement('entry')
            relative_path_utl = "#" if country.url == None else os.path.relpath(country.url , dirname(export_dita))
            xref = create_xref(root=root,text=country.country,url=relative_path_utl,format="html")
            entry.appendChild(xref) 
            row.appendChild(entry)
    return root

def create_nst_page(current_region=None,export_dita=None, richcollection=None):
    root = create_dita_root(doctype_str=None)
    topic = create_richcollection(root=root,id=current_region)
    body = create_body(root=root,topic=topic)
    tbody = create_table_body(root=root,body=body, cols=str(richcollection.cols))

    for irow in richcollection.rows:
        row = root.createElement('row')
        for col in irow:
            entry = root.createElement('entry')
            
            img_src_root = dirname(dirname(richcollection.url))+str(col.src).replace("../", "/")
            img_dest_root = dirname(dirname(export_dita))+str(col.src).replace("../", "/")
            href_src_root = dirname(dirname(richcollection.url))+str(col.href).replace("../", "/")

            relative_path_url = "#" if col.href == None else os.path.relpath(href_src_root, dirname(export_dita))
            relative_path_img_url = "#" if col.src == None else str(col.src)
            
            print("Copy images  ")
            print('copy ('+img_src_root+') to ('+img_dest_root+')')
            isDestExist = os.path.exists(dirname(img_dest_root))
            if not isDestExist:
                os.makedirs(dirname(img_dest_root))
            os.system('cp '+abspath(img_src_root)+' '+img_dest_root)

            image = create_image(root=root,url=relative_path_img_url,style=col.style)
            xref = create_xref(root=root,text=col.text ,url=relative_path_url,format="html")
            xref.appendChild(image)
            entry.appendChild(xref) 
            row.appendChild(entry)
        tbody.appendChild(row)
        
    return root

