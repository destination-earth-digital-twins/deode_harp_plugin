import os
import sys
from pathlib import Path
import toml
import re
from datetime import datetime
sys.path.insert(0,'/ec/res4/hpcperm/snh02/DE_Verification/verif_tools/dcmdb/')
sys.path.insert(0,'/ec/res4/hpcperm/snh02/DE_Verification/verif_tools/Upath')
import dcmdb
from pathlib import Path



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
# Interrogate dcmdb to find new runs between dates; NOTE: make sure dcmdb is updated!
os.chdir(DCMDB_DIR)
collection=dcmdb.collect_cases(path=Path('cases'))
with open(CASES_FILE, "w") as f:
    for exp in collection.experiments:
        print(exp.schema_version)
        if exp.schema_version == 'v1':
            f.write(f"{exp.name}\n")
            f.write(f"File templates : {exp.metadata['runs'][0]['file_templates']}\n")
            f.write(f"Path template : {exp.metadata['runs'][0]['stores'][0]['path_template']}\n")
            f.write(f"time_coverage_start : {exp.metadata['runs'][0]['setup']['time_coverage_start']}\n")
            f.write(f"--\n")
    print(f"New experiments to verify have been listed in {CASES_FILE}.\n")

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
                time_coverage_start_match = re.search(r"time_coverage_start\s*:\s*(.+)", group)
                time_coverage_start = time_coverage_start_match.group(1).strip()

                if path_template:
                    experiments.append({
                        "name": experiment_name,
                        "path_template": path_template.group(1).strip(),
                        "time_coverage_start": time_coverage_start
                    })
    return experiments

experiments = parse_experiments(CASES_FILE)
#print('parsed experimetns are')
#print(experiments)


# Helper function to check if a date is within range
def is_date_in_range(date_str, start_date, end_date):
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    start_obj = datetime.strptime(start_date, "%Y%m%d")
    end_obj = datetime.strptime(end_date, "%Y%m%d")
    return start_obj <= date_obj <= end_obj

# Process each experiment
for experiment in experiments:
    print('experiment is')
    print(experiment)
    experiment_name = experiment["name"]
    path_template = experiment["path_template"]
    date_coverage= experiment["time_coverage_start"]

    # Try to extract date components from the path template
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", path_template)
    if match:
        year, month, day = match.groups()
        experiment_date = f"{year}{month}{day}"
    else:
        print(f"Could not extract date from path template: {path_template}")
        try:
            dt = datetime.strptime(date_coverage, "%Y-%m-%d %H:%M:%S")
            experiment_date = dt.strftime("%Y%m%d")
            print(f"Falling back to date_coverage: {experiment_date}")
            year = dt.strftime("%Y")
            month = dt.strftime("%m")
            day = dt.strftime("%d")
        except ValueError:
            print(f"Invalid date_coverage format: {date_coverage}")
            continue  # skip this experiment

    # Skip experiments not within the date range
    if not is_date_in_range(experiment_date, START_DATE, END_DATE):
        print(f"Skipping {experiment_name} as it is outside the date range.")
        continue
    # Replace placeholders in path if needed
    resolved_path_template = path_template.replace("%Y", year).replace("%m", month).replace("%d", day).replace("%H", "00")

    # Define source and destination for the config file
    source_config = f"{resolved_path_template}/config.toml"
    dw_config = f"{VERIF_HOME}/config_files/{year}/{month}/{day}/config_{experiment_name}.toml"
    dw_harp_config = os.path.join(DW_DIR, "configuration_harp_plugin"+experiment_name)

    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(dw_config), exist_ok=True)

    # Copy the config file
    print('executing ecp retrieval')
    print(f"ecp {source_config} {dw_config}")
    os.system(f"ecp {source_config} {dw_config}")
    print(f"Copied config.toml from {source_config} to {dw_config}")
    if not os.path.exists(dw_config):
        print(f"[ERROR] Config file {dw_config} not found after ecp.")
        continue # Go to the next experiment in the loop

    # ASCII-edit 'case = ...' in dw_config to insert @CASE_PREFIX@
    with open(dw_config, "r") as f:
        lines = f.readlines()
    updated_lines = []
    case_updated = False
    for line in lines:
        if line.strip().startswith("case"):
            match = re.match(r'(case\s*=\s*["\'])(.*?)(["\'])', line.strip())
            if match and not match.group(2).startswith("@CASE_PREFIX@"):
                new_line = f'{match.group(1)}@CASE_PREFIX@{match.group(2)}{match.group(3)}\n'
                updated_lines.append(new_line)
                case_updated = True
                print(f"Updated 'case' line to: {new_line.strip()}")
            else:
                updated_lines.append(line)
        elif line.strip().startswith("bdmember"):
                new_line = "# bdmember \n"
                updated_lines.append(new_line)
        else:
            updated_lines.append(line)
    with open(dw_config, "w") as f:
        f.writelines(updated_lines)
    if not case_updated:
        print("[WARNING] 'bdmember ' line not found or unchanged.")

    # Write the harp plugin configuration

    with open(dw_harp_config, "w") as harp_config:
        harp_config.write(f"--config-file\n{dw_config}\n{DEODE_PLUGINS}/harpverify/harpverify_plugin.toml\n")

    # Run the deode commands
    config_harp_file = f"{VERIF_HOME}/config_files/{year}/{month}/{day}/config_harp_{experiment_name}.toml" 
    #os.system("poetry run deode -h")
    os.system(f"echo deode case ?{dw_harp_config} -o {config_harp_file} --start-suite >> verifsuites.txt")

print("Script completed.")

