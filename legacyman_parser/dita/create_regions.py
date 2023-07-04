from xml.dom import minidom
import os 

root = minidom.Document()

# Create the doctype declaration
doctype_str = '<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">'

def create_regions_dita(save_path_file, regions):  

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

        relative_path_utl = os.path.relpath(save_path_file,region.url)
        xref.setAttribute('href', relative_path_utl)
        xref.setAttribute('format', '')
        area.appendChild(xref)

    xml_string = root.toprettyxml(indent ="\t") 
    xml_string_with_doctype = f"{doctype_str}\n{xml_string}"

    print("Create / Save regions.dita : ", save_path_file)
    
    with open(save_path_file, "w") as f:
        f.write(xml_string_with_doctype) 
