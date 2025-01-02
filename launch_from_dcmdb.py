import os
import sys
from pathlib import Path
import toml
import re
from datetime import datetime


# Load configuration from harpverify_plugin.toml
#usage: scriptname.py path_to_harpverify_plugin.toml start_date end_date
config_file = sys.argv[1]
config = toml.load(config_file)

# Define paths from the configuration file
VERIF_HOME = config['submission']['harpverify_group']['ENV']['VERIF_HOME']
DW_DIR = config['submission']['harpverify_group']['ENV']['DW_DIR']
DCMDB_DIR=config['submission']['harpverify_group']['ENV']['DCMDB_DIR']
DUSER=config['submission']['harpverify_group']['ENV']['DUSER']
DEODE_PLUGINS=config['general']['plugin_registry']['plugins']['harpverify']

START_DATE = sys.argv[2]
END_DATE = sys.argv[3]

CASES_FILE = os.path.join(VERIF_HOME, "cases_to_verify.yml")
# Execute dcmdb command to find new runs between dates; make sure dcmdb is updated
os.chdir(DCMDB_DIR)
os.system(f"dcmdb chase -list -v | grep -B 2 {DUSER}/DE_NWP > {CASES_FILE}")
print(f"New experiments to verify have been listed in {CASES_FILE}.")

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



# Helper function to check if a date is within range
def is_date_in_range(date_str, start_date, end_date):
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    start_obj = datetime.strptime(start_date, "%Y%m%d")
    end_obj = datetime.strptime(end_date, "%Y%m%d")
    return start_obj <= date_obj <= end_obj

# Process each experiment
for experiment in experiments:
    experiment_name = experiment["name"]
    path_template = experiment["path_template"]

    # Extract date components from the path template
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", path_template)
    if not match:
        print(f"Could not extract date from path template: {path_template}")
        continue

    year, month, day = match.groups()
    experiment_date = f"{year}{month}{day}"

    # Skip experiments not within the date range
    if not is_date_in_range(experiment_date, START_DATE, END_DATE):
        print(f"Skipping {experiment_name} as it is outside the date range.")
        continue

    # Define source and destination for the config file
    source_config = f"{path_template}/config.toml"
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

