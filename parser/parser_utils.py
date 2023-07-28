import shutil
import xml.dom.minidom
import os

def delete_directory(path):
    if os.path.exists(path):
        os.system('rm -rf {}'.format(path))
        print('Target directory deleted')
    else:
        print('Target directory does not exist')

def create_directory(name):
    try:
        os.makedirs(name)
        print(f'{name} directory created')
    except FileExistsError:
        print(f'The directory {name} already exists')

def copy_directory(src_folder, dst_folder):
    shutil.copytree(src_folder, dst_folder)

def copy_files(source_dir, target_dir, file_names):
    #create the target dir if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    #copy files
    for file_name in file_names:
        source_file = os.path.join(source_dir, file_name)
        target_file = os.path.join(target_dir, file_name)
        shutil.copy(source_file, target_dir)

def prettify_xml(xml_code):
    dom = xml.dom.minidom.parseString(xml_code)
    return dom.toprettyxml()

__all__ = ['delete_directory', 'create_directory', 'copy_directory', 'copy_files', 'prettify_xml']