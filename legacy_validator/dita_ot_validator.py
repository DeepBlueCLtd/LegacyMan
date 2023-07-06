import subprocess
import os

# DITA-OT global path
dita_ot_path = '/Users/workspace_blue_python/update_3/LegacyMan/legacy_validator/dita-ot-3.7.2'

#os.environ["DITA-OT"] = dita_ot_path
dita_ot= os.environ['DITA-OT']
dita_ot_path = dita_ot+'/bin/dita'

# function to validate dita files
def validate_regions(dita_xml_file, dtd_file):
    print('Validate regions.dita...')
    
    # Command to execute
    command = dita_ot_path+' -i '+dita_xml_file+' -f dita -v'

    # ./dita -i input.dita -f dita -v
    # validate with dita-ot
    # Execute the command and capture the output
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Check the exit code
    if completed_process.returncode == 0:
        print("Command executed successfully.")
    else:
        error_message = completed_process.stderr
        print("Error occurred during command execution:")
        print("DITA-OT ERROR : ", error_message)
    

# Path to the XML and DTD files
xml_file = './dita/regions-invalid.dita '
dtd_file = dita_ot+'/plugins/org.oasis-open.dita.v1_2/dtd/technicalContent/dtd/topic.dtd'

# Calling function and validate regions
validate_regions(xml_file, dtd_file)