import subprocess
import os
import sys

dita_ot = None
if 'DITA_OT' in os.environ:
    print("Using DITA-OT from environment ("+os.environ["DITA_OT"]+")")
    dita_ot = os.environ["DITA_OT"]
else:
    sys.exit("No DITA-OT")
    
dita_ot_path = dita_ot+'/bin/dita'

def validate(dita_xml_file, dtd_file):
    print('Validate regions.dita...')
    
    command = f'"{dita_ot_path}" -i "{dita_xml_file}" -f dita -v'
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)

    if completed_process.returncode == 0:
        print("Command executed successfully.")
    else:
        error_message = completed_process.stderr
        print("Error occurred during command execution:")
        print("DITA-OT ERROR : ", error_message)

def get_dita():
    return dita_ot