"""ExampleMethod."""
import os
from datetime import datetime, timedelta
from dateutil import parser
import pandas as pd
import yaml
import pyproj
import glob
import subprocess
import re
from deode.toolbox import Platform


class ConfigHarpverify(object):
    """description"""

    def __init__(self, config):
        """Construct base task.

        Args:
            config (deode.ParsedConfig): Configuration

        """
        self.config = config
        self.home = os.environ.get("VERIF_HOME")
        self.huser = os.environ.get("HUSER")
        self.duser= os.environ.get("DUSER")
        self.harpscripts_home=os.environ.get("HARPSCRIPTS_HOME")
        self.platform = Platform(config)      
        self.cnmexp = self.config["general.cnmexp"]
        self.csc = self.config["general.csc"]
        self.cycle = self.config["general.cycle"]
        self.domain_name = self.config["domain.name"]
        self.start = self.platform.get_value("general.times.start")
        self.end = self.platform.get_value("general.times.end")
        self.startyyyymmddhh=datetime.strptime(self.start, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H")
        self.startyyyy=datetime.strptime(self.start, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y")
        self.startmm=datetime.strptime(self.start, "%Y-%m-%dT%H:%M:%SZ").strftime("%m")
        self.startdd=datetime.strptime(self.start, "%Y-%m-%dT%H:%M:%SZ").strftime("%d")
        #self.endyyyymmddhh=datetime.strptime(self.end, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H")
        #self.endyyyymmddhh = (datetime.strptime(self.start, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=int(self.forecast_range.replace("PT", "").replace("h", "")))).strftime("%Y%m%d%H")
        self.cycle_length = self.platform.get_value("general.times.cycle_length")
        self.forecast_range = self.platform.get_value("general.times.forecast_range")
        self.endyyyymmddhh = (datetime.strptime(self.start, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=int(re.sub(r"\D", "", self.forecast_range)))).strftime("%Y%m%d%H")
        self.exp = self._set_exp()
        self.case = self.platform.get_value("general.case")
        self.sqlites_exp_path=self.platform.get_value("extractsqlite.sqlite_path")
        self.sqlites_ref_path=os.environ.get("REF_SQLITES")
        self.sqlites_obs_path=os.environ.get("OBSTABLES_PATH")
        self.rdss_path=os.environ.get("RDSS_PATH")
        self.pngs_path=os.environ.get("PNGS_PATH")
        self.ref_name=os.environ.get("REF_NAME")
        self._case_args = None
        self._exp_args = None
        self.config_yaml = None
        self.config_yaml_filename = None
        self.ecfs_archive_relpath = os.environ.get("ECFS_ARCHIVE_RELPATH")
        self.csc_resol=self.config["general.csc"]+'_'+str(self.config["domain.xdx"])+'m'

    def write_config_yml(self,write=True):
        """descrp.

        Args:
            case (str): Recipient of the greeting
        """
        print('self.home es ' + self.home)
        config_template = os.path.join(self.home,"config_files/deode_conf.yml")
        self.config_yaml_filename = os.path.join(self.home, f"config_files/",self.startyyyy,self.startmm,self.startdd,f"deode_conf_{self.case}.yml")
        print("config_template es")
        print(config_template)
        
        #These lines come from linkobsfctables.py and are adapted here to fill the config file for harp's R script
        #Extract it from the sqlites_exp_path variable (i.e /YYYY/MM/DD/HH//{type_of_extreme}/{order_of_run}
        sqlites_relpath=self.sqlites_exp_path.replace(self.huser,self.duser).split('deode')[1]
        exp_relpath=sqlites_relpath.split('sqlite')[0]
        # The lines above should be something like '/2024/12/03/00//convection/1/HARMONIE_AROME_500m/sqlite/FCTABLE/' (without the last 2 for the second one)
        exp_scratch=self.sqlites_exp_path.replace(self.huser,self.duser)
        #The line above should be something like /scratch/aut6432/DE_NWP/deode/2024/12/03/00//convection/1/HARMONIE_AROME_500m/sqlite/FCTABLE/
        local_fctables=os.path.join(self.home,f"FCTABLES/",exp_relpath.lstrip('/'),self.startyyyy,self.startmm)
        #The line above evaluates ~ /ec/res4/hpcperm/sp3c/deode_project/deode_harp_output/FCTABLES//2024/12/03/00//convection/1/HARMONIE_AROME_500m/YYYY/MM/
        local_fctables_ref=local_fctables.split(self.csc)[0] #This is where REF's folder with FCTABLES should be linked
        #The line above is where the Global_DT FCTABLES should be downloaded or linked for this experiment. It should be something like:
        #/ec/res4/hpcperm/sp3c/deode_project/deode_harp_output/FCTABLES/2024/12/03/00//convection/1/Global_DT

        if os.path.isfile(config_template):
            self._exp_args = ConfigHarpverify.load_yaml(config_template)
            self._exp_args["verif"]["fcst_model"]=[self.ref_name,self.csc_resol]
            self._exp_args["verif"]["project_name"]=[self.case]
            self._exp_args["verif"]["fcst_path"]=[local_fctables.split(self.csc)[0]]
            self._exp_args["verif"]["obs_path"]=[self.home + '/OBSTABLESOPER/']
            self._exp_args["verif"]["verif_path"]=[os.path.join(self.rdss_path,exp_relpath.lstrip('/').split(self.csc)[0])]
            self._exp_args["post"]["plot_output"]=[os.path.join(self.pngs_path,exp_relpath.lstrip('/').split(self.csc)[0])]
            self._exp_args["scorecards"]["ref_model"]=[self.ref_name]
            self._exp_args["scorecards"]["fcst_model"]=[self.csc_resol]
            if write==True:
               ConfigHarpverify.save_yaml(self.config_yaml_filename, self._exp_args)
               print("wrote yml file at"+self.config_yaml_filename)
        else:
            print("not found template config file")
        return self.config_yaml_filename,self._exp_args

    def _set_exp(self):
        """

        """
        return "_".join([self.cnmexp, self.csc, self.cycle, self.domain_name])

    @staticmethod
    def link_files(source_dir, destination_dir):
        # Get all files in the source directory
        files = glob.glob(os.path.join(source_dir, "*"))
        # Ensure the destination directory exists
        if not os.path.exists(destination_dir):
           os.makedirs(destination_dir) 
	   # Link each file individually

        for file in files:
               # Get the basename of the file (i.e., the file name without the path)
               filename = os.path.basename(file)
               destination_file = os.path.join(destination_dir, filename)
               # Create a hard link for the file
               # Check if the file already exists in the destination directory
               if not os.path.exists(destination_file):
                  # Create a hard link for the file if it doesn't already exist
                  os.symlink(file, destination_file)
               else:
                  print(f"File {destination_file} already exists, skipping.")
    @staticmethod
    def load_yaml(config_file):
        with open(config_file, 'r') as stream:
             data_loaded = yaml.load(stream, Loader=yaml.SafeLoader)
        return data_loaded
    @staticmethod
    def save_yaml(config_file, data):												
        with open(config_file, "w") as stream:
             yaml.dump(data, stream, default_flow_style=False, sort_keys=False)
    @staticmethod
    def replicate_structure_to_ec(origin_path, ec_base_path):
        print('start replicate function')
        print(origin_path)
        print(ec_base_path)
        # Walk through all directories and files in the origin path
        for dirpath, dirnames, filenames in os.walk(origin_path):
            print(dirpath)
            print(dirnames)
            print(filenames)

            # Compute relative path from the origin path
            rel_dir = os.path.relpath(dirpath, origin_path)
            print('rel_dir')
            print(rel_dir)
            # Construct the target directory path on the HPC (ec:../username/)
            ec_target_dir = os.path.join(ec_base_path, rel_dir)

            # Replace local file path separators with '/' for the HPC system (if necessary)
            ec_target_dir = ec_target_dir.replace("\\", "/")  # Ensure proper path format
            print('ec_target_dir')
            print(ec_target_dir)
            # Check if the target directory already exists on the HPC
            if ( subprocess.run(["els", ec_target_dir], capture_output=True, text=True).returncode == 1 ): #check_ec_directory_exists(ec_target_dir):
                # Create the target directory on the HPC using 'emkdir'
                try:
                    subprocess.run(["emkdir", ec_target_dir], check=True)
                    print(f"Created directory: {ec_target_dir}")
                except subprocess.CalledProcessError as e:
                    print(f"Error creating directory {ec_target_dir}: {e}")
            else:
                print(f"Directory {ec_target_dir} already exists, skipping creation.")

            # Copy each file in the current directory
            for filename in filenames:
                local_file = os.path.join(dirpath, filename)
                ec_target_file = os.path.join(ec_target_dir, filename)
    
                # Use 'ecp' to copy files to the HPC
                try:
                    subprocess.run(["ecp", local_file, ec_target_file], check=True)
                    print(f"Copied file: {local_file} to {ec_target_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Error copying file {local_file} to {ec_target_file}: {e}")
