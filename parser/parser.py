
import sys
import time
import os
import shutil
import subprocess


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

    #Run DITA-OT command to transform the index.ditamap file to html
    dita_command = ["dita", "-i", "./target/dita/index.ditamap", "-f", "html5", "-o", "./target/dita/html"]
    subprocess.run(dita_command)

    end_time = time.time()
    parse_time = end_time - start_time
    print(f'Publish complete after {parse_time} seconds. Root file at /target/dita/index.ditamap')

if __name__ == '__main__':
    args = sys.argv[1:]
    parse_from_root(args)