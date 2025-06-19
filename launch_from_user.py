#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import re
import time
from pathlib import Path
import toml


def verbose_print(msg):
    print(f"[INFO] {msg}")


def run_command(command):
    verbose_print(f"Running command: {command}")
    try:
        result = subprocess.run(
            command, shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed:\n{e.stderr}")
        sys.exit(1)


def parse_experiments(file_path):
    experiments = []
    with open(file_path, "r") as file:
        content = file.read()
        groups = content.split("--\n")
        for group in groups:
            lines = group.strip().split("\n")
            if len(lines) >= 3:
                experiment_name = lines[0].strip()
                match = re.search(r"Path template\s*:\s*(.+)", group)
                if match:
                    experiments.append({
                        "name": experiment_name,
                        "path_template": match.group(1).strip()
                    })
    return experiments


def main():
    parser = argparse.ArgumentParser(
        description="Prepare and submit harpverify experiments using DEODE."
    )

    if len(sys.argv) == 1:
        print("[ERROR] No arguments provided.\n")
        parser.print_help()
        sys.exit(1)

    parser.add_argument("config_file", help="Path to harpverify_plugin.toml")
    parser.add_argument("deode_user", help="DEODE user")
    parser.add_argument("experiment", help="Experiment name")
    parser.add_argument("year", help="Year (YYYY)")
    parser.add_argument("month", help="Month (MM)")
    parser.add_argument("day", help="Day (DD)")
    parser.add_argument("--event_type", help="Event type (required if indexing is 'yes')")
    parser.add_argument("--order", help="Order (required if indexing is 'yes')")
    parser.add_argument("--csc_res", help="CSC resolution (required if indexing is 'yes')")

    args = parser.parse_args()

    # Load TOML config
    verbose_print(f"Loading TOML configuration from {args.config_file}")
    config = toml.load(args.config_file)

    try:
        VERIF_HOME = config['submission']['harpverify_group']['ENV']['VERIF_HOME']
        DW_DIR = config['submission']['harpverify_group']['ENV']['DW_DIR']
        DEODE_PLUGINS = config['general']['plugin_registry']['plugins']['harpverify']
        ECFS_ARCHIVE_RELPATH_DEODEOUTPUT = config['submission']['harpverify_group']['ENV']['ECFS_ARCHIVE_RELPATH_DEODEOUTPUT']
        USE_OPERATIONAL_INDEXING = config['submission']['harpverify_group']['ENV']['USE_OPERATIONAL_INDEXING']
    except KeyError as e:
        print(f"[ERROR] Missing key in config: {e}")
        sys.exit(1)

    CASES_FILE = os.path.join(VERIF_HOME, "single_case_to_verify.yml")

    if USE_OPERATIONAL_INDEXING not in ('yes', 'no'):
        print(f"[ERROR] Invalid USE_OPERATIONAL_INDEXING: {USE_OPERATIONAL_INDEXING}")
        sys.exit(1)

    if USE_OPERATIONAL_INDEXING == 'yes':
        if not (args.event_type and args.order and args.csc_res):
            print("[ERROR] USE_OPERATIONAL_INDEXING is 'yes', but --event_type, --order, and --csc_res are missing.")
            sys.exit(1)
    elif USE_OPERATIONAL_INDEXING == 'no':
        if args.event_type or args.order or args.csc_res:
            print("[ERROR] USE_OPERATIONAL_INDEXING is 'no', but extra arguments were provided.")
            sys.exit(1)

    # Write CASES_FILE
    verbose_print(f"Writing to CASES_FILE at {CASES_FILE}")
    with open(CASES_FILE, "w") as f:
        f.write(f"{args.experiment}\n")
        f.write("File templates : ['GRIBDEOD+%LLLHh%LMm%LSs.sfx', 'GRIBPFDEOD+%LLLHh%LMm%LSs']\n")
        if USE_OPERATIONAL_INDEXING == 'no':
            f.write(f"Path template : ec:/{args.deode_user}/{ECFS_ARCHIVE_RELPATH_DEODEOUTPUT}/{args.experiment}/archive/{args.year}/{args.month}/{args.day}\n")
        else:
            f.write(f"Path template : ec:/{args.deode_user}/{ECFS_ARCHIVE_RELPATH_DEODEOUTPUT}/{args.year}/{args.month}/{args.day}/00/{args.event_type}/{args.order}/{args.csc_res}/mbr001\n")
        f.write("--\n")

    # Validate file existence
    if not os.path.isfile(CASES_FILE):
        print(f"[ERROR] File {CASES_FILE} not found!")
        sys.exit(1)

    # Change directory
    verbose_print(f"Changing directory to {DW_DIR}")
    os.chdir(DW_DIR)

    # Parse experiments
    experiments = parse_experiments(CASES_FILE)

    for exp in experiments:
        experiment_name = exp["name"]

        if USE_OPERATIONAL_INDEXING == 'no':
            path_template_config = f"ec:/{args.deode_user}/{ECFS_ARCHIVE_RELPATH_DEODEOUTPUT}/{experiment_name}/"
        else:
            path_template_config = f"ec:/{args.deode_user}/{ECFS_ARCHIVE_RELPATH_DEODEOUTPUT}/{args.year}/{args.month}/{args.day}/00/{args.event_type}/{args.order}/{args.csc_res}/mbr001"

        source_config = f"{path_template_config}/config.toml"
        dw_config = f"{VERIF_HOME}/config_files/{args.year}/{args.month}/{args.day}/config_{experiment_name}.toml"
        dw_harp_config = os.path.join(DW_DIR, "configuration_harp_plugin")

        os.makedirs(os.path.dirname(dw_config), exist_ok=True)

        verbose_print(f"Copying config from {source_config} to {dw_config}")
        run_command(f"ecp {source_config} {dw_config}")
        time.sleep(1)

        if not os.path.exists(dw_config):
            print(f"[ERROR] Config file {dw_config} not found after ecp.")
            sys.exit(1)

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
                    verbose_print(f"Updated 'case' line to: {new_line.strip()}")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        with open(dw_config, "w") as f:
            f.writelines(updated_lines)

        if not case_updated:
            print("[WARNING] 'case =' line not found or unchanged.")

        # Write plugin config
        with open(dw_harp_config, "w") as harp_config:
            harp_config.write(f"--config-file\n{dw_config}\n{DEODE_PLUGINS}/harpverify/harpverify_plugin.toml\n")
        verbose_print(f"Wrote harp plugin configuration to {dw_harp_config}")

        # Run deode
        config_harp_file = f"{VERIF_HOME}/config_files/{args.year}/{args.month}/{args.day}/config_harp_{experiment_name}.toml"
        run_command(f"deode case ?{dw_harp_config} -o {config_harp_file} --start-suite")
        verbose_print(f"Deode run completed for experiment: {experiment_name}")

    verbose_print("All experiments processed successfully.")


if __name__ == "__main__":
    main()

