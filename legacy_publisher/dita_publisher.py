import json
import os 

from xml.dom import minidom
from os.path import dirname, abspath
from legacyman_parser.utils.constants import DITA_REGIONS_EXPORT_FILE
from distutils.dir_util import copy_tree
from legacy_publisher.dita_helper import create_dita_root, write_dita_doc, create_topic, create_body,create_table,create_xref,create_richcollection, create_table_body, create_image, create_classlist, create_flag, create_classlist_body, create_classlisttable_body,create_class

from legacy_publisher.dita_helper import create_images, create_section, create_classtable, create_bullets
from legacyman_parser.dita_ot_validator import validate, get_dita

dita_ot = get_dita()
doctype_str = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">\n'
doctype_richcollection_str = '<!DOCTYPE rich-collection SYSTEM "../../../../dtd/rich-collection.dtd">\n'
doctype_classlist_str = '<!DOCTYPE classlist SYSTEM "../../../../../dtd/classlist.dtd">\n'
doctype_class_str = '<!DOCTYPE class SYSTEM "../../../../../dtd/class.dtd">\n'


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

def publish_country_collection(country_collection=None):
    print("Publish country...")
 
    for classlist in country_collection:
        current=classlist
        pstr = "regions/"
        parent_folder = os.path.basename(dirname(str(classlist.flag.parent)))
        folder_name = os.path.basename(dirname(str(classlist.url)))
        file_name = os.path.basename(str(classlist.url)).replace(".html", "")

        export_dita = dirname(DITA_REGIONS_EXPORT_FILE)+"/"+pstr+parent_folder+"/"+folder_name+"/"+file_name+".dita"
        root = create_collection_page(classlist=classlist,export_dita=export_dita)

        isDestExist = os.path.exists(dirname(export_dita))
        if not isDestExist:
            os.makedirs(dirname(export_dita))
        print("export_dita :", export_dita)
        write_dita_doc(root, export_dita, doctype_str=doctype_classlist_str)

        if(dita_ot != None):
            xml_file = abspath(export_dita)
            dtd_file = '../dtd/classlist.dtd'
            validate(xml_file, dtd_file)

def publish_country_class(class_data=None): 
    for iclass in class_data:
        current=iclass
        pstr = "regions/"

        parent_folder = os.path.basename(dirname(str(iclass.parent)))
        folder_name = os.path.basename(dirname(str(iclass.url)))
        file_name = os.path.basename(str(iclass.url)).replace(".html", "")

        export_dita = dirname(DITA_REGIONS_EXPORT_FILE)+"/"+pstr+parent_folder+"/"+folder_name+"/"+file_name+".dita"
        root = create_class_page(class_data=iclass,export_dita=export_dita)

        isDestExist = os.path.exists(dirname(export_dita))
        if not isDestExist:
            os.makedirs(dirname(export_dita))
        print("export_dita :", export_dita)
        write_dita_doc(root, export_dita, doctype_str=doctype_class_str)

        if(dita_ot != None):
            xml_file = abspath(export_dita)
            dtd_file = '../dtd/class.dtd'
            validate(xml_file, dtd_file)


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
        dtd_file = '../dtd/rich-collection.dtd'
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
            img_dest_root = dirname(export_dita)+str(col.src).replace("../", "/")
            href_src_root = dirname(dirname(richcollection.url))+str(col.href).replace("../", "/")

            relative_path_url = "#" if col.href == None else os.path.relpath(href_src_root, dirname(export_dita))
            relative_path_img_url = "#" if col.src == None else str(col.src).replace("../", "")
            
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

def create_collection_page(classlist=None,export_dita=None):
    root = create_dita_root(doctype_str=None)
    topic = create_classlist(root=root,id=classlist.title)
    flag = create_flag(root=root,url=".."+classlist.flag.flag_dest.replace(os.path.basename(dirname(dirname(export_dita))), ""),topic=topic)

    print("Copy flags ")
    img_dest = dirname(dirname(dirname(export_dita)))+"/"+classlist.flag.flag_dest
    print('copy ('+classlist.flag.flag+') to ('+img_dest+')')
    isDestExist = os.path.exists(dirname(img_dest))
    if not isDestExist:
        os.makedirs(dirname(img_dest))
    os.system('cp '+abspath(classlist.flag.flag)+' '+img_dest)

    body = create_classlist_body(root=root,topic=topic)
    tbody = create_classlisttable_body(root=root,body=body, cols=str(classlist.cols))

    for irow in classlist.rows:
        row = root.createElement('row')
        for col in irow:
            entry = root.createElement('entry')
            if len(irow) < 7:
                namest="col1" 
                nameend="col7"
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
        tbody.appendChild(row)

    return root



def create_class_page(class_data=None,export_dita=None):
    root = create_dita_root(doctype_str=None)
    title = os.path.basename(str(export_dita)).replace(".dita","")
    topic = create_class(root=root,id=title)
    body = create_body(root=root,topic=topic)
    images = create_images(root=root,body=body)

    if len(class_data.summary.table) != 0 : 
        summary = create_section(root=root,body=body, section=str(class_data.summary.title), title_str=None)
        tbody = create_classtable(root=root,section=summary, cols=str(class_data.colspan))
        process_section(class_data.summary.table,root,tbody)

    if len(class_data.signatures.table) != 0 : 
        signatures = create_section(root=root,body=body, section=str(class_data.signatures.title), title_str=str(class_data.signatures.title))
        tbodysignatures = create_classtable(root=root,section=signatures, cols=str(class_data.colspan))
        process_complex_section(class_data.signatures.table,root,tbodysignatures, class_data.colspan, 4)

    if len(class_data.propulsion.table) != 0 : 
        propulsion = create_section(root=root,body=body, section=str(class_data.propulsion.title), title_str=str(class_data.propulsion.title))
        tbodypropulsion = create_classtable(root=root,section=propulsion, cols=str(4))
        process_complex_section(class_data.propulsion.table,root,tbodypropulsion, 4, 4)

    if len(class_data.remarks.table) != 0 and class_data.remarks.title != None: 
        remarks = create_section(root=root,body=body, section=str(class_data.remarks.title), title_str=str(class_data.remarks.title))
        remarks_body = create_bullets(root=root,section=remarks, bullets=class_data.remarks.table)
    
    return root


def process_section(section=None,root=None,tbody=None):
    for irow in section:
        row = root.createElement('row')
        for col in irow:
            entry = root.createElement('entry')
        
            relative_path_url = "#" if col[1] == None else col[1]
            if col[1] != None :
                xref = create_xref(root=root,text=col[0] ,url=relative_path_url,format="html")
                entry.appendChild(xref) 
            else : 
                text_content = root.createTextNode(col[0])
                entry.appendChild(text_content)

            row.appendChild(entry)
            
        tbody.appendChild(row)

def process_complex_section(section=None,root=None,tbody=None,colspan=None, colspantr=None):
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

    