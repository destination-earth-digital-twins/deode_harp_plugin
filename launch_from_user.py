import os
import sys
from pathlib import Path
import toml
import re
from datetime import datetime
import dcmdb
from pathlib import Path



# Load configuration from harpverify_plugin.toml
#usage: scriptname.py path_to_harpverify_plugin.toml deode_user experiment_name yyyy mm dd
config_file = sys.argv[1]
config = toml.load(config_file)

# Define paths from the configuration file
VERIF_HOME = config['submission']['harpverify_group']['ENV']['VERIF_HOME']
DW_DIR = config['submission']['harpverify_group']['ENV']['DW_DIR']
DUSER=sys.argv[2]
DEODE_PLUGINS=config['general']['plugin_registry']['plugins']['harpverify']
ECFS_ARCHIVE_RELPATH_DEODEOUTPUT=config['submission']['harpverify_group']['ENV']['ECFS_ARCHIVE_RELPATH_DEODEOUTPUT']
CASES_FILE = os.path.join(VERIF_HOME, "single_case_to_verify.yml")
YYYY=sys.argv[4]
MM=sys.argv[5]
DD=sys.argv[6]
experiment=sys.argv[3]
with open(CASES_FILE, "w") as f:
            f.write(f"{experiment}\n")
            f.write(f"File templates : ['GRIBDEOD+%LLLHh%LMm%LSs.sfx', 'GRIBPFDEOD+%LLLHh%LMm%LSs']\n")
            f.write(f"Path template : ec:/{DUSER}/{ECFS_ARCHIVE_RELPATH_DEODEOUTPUT}/{experiment}/archive/{YYYY}/{MM}/{DD}\n")
            f.write(f"--\n")
            print(f"New experiment to verify has been listed in {CASES_FILE}.\n")

# Check if the input file exists
if not os.path.isfile(CASES_FILE):
    print(f"File {CASES_FILE} not found!")
    sys.exit(1)

#Cd into DW_DIR, from where verifications will be launched using deode command:
os.chdir(DW_DIR)

# Read subfolder names from the input file
with open(CASES_FILE, "r") as infile:
    subfolder_names = infile.readlines()

# Parse experiments from cases_to_verify.yml
def parse_experiments(file_path):
    experiments = []
    with open(file_path, "r") as file:
        content = file.read()
        groups = content.split("--\n")
        for group in groups:
            lines = group.strip().split("\n")
            if len(lines) >= 3:
                experiment_name = lines[0].strip()
                path_template = re.search(r"Path template\s*:\s*(.+)", group)
                if path_template:
                    experiments.append({
                        "name": experiment_name,
                        "path_template": path_template.group(1).strip()
                    })
    return experiments

experiments = parse_experiments(CASES_FILE)



# Process each experiment
for experiment in experiments:
    experiment_name = experiment["name"]
    path_template = experiment["path_template"]
    path_template_config=f"ec:/{DUSER}/{ECFS_ARCHIVE_RELPATH_DEODEOUTPUT}/{experiment_name}/"
    year=YYYY
    month=MM
    day = DD
    experiment_date = f"{year}{month}{day}"

    # Define source and destination for the config file
    source_config = f"{path_template_config}/config.toml"
    dw_config = f"{VERIF_HOME}/config_files/{year}/{month}/{day}/config_{experiment_name}.toml"
    dw_harp_config = os.path.join(DW_DIR, "configuration_harp_plugin")

    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(dw_config), exist_ok=True)

    # Copy the config file
    print('executing ecp retrieval')
    print(f"ecp {source_config} {dw_config}")
    os.system(f"ecp {source_config} {dw_config}")
    print(f"Copied config.toml from {source_config} to {dw_config}")

    # Write the harp plugin configuration
    with open(dw_harp_config, "w") as harp_config:
        harp_config.write(f"--config-file\n{dw_config}\n{DEODE_PLUGINS}/harpverify/harpverify_plugin.toml\n")

    # Run the deode commands
    config_harp_file = f"{VERIF_HOME}/config_files/{year}/{month}/{day}/config_harp_{experiment_name}.toml" 
    os.system(f"deode case ?{dw_harp_config} -o {config_harp_file} --start-suite")

print("Script completed.")

