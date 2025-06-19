"""Example Task."""	
import os
import re
import glob
from ..methods import ConfigHarpverify
from deode.tasks.base import Task
import subprocess

class LinkOBSFCTABLES(Task):
    """links OBSTABLES, FCTABLES from REF and EXPS to path directory"""

    def __init__(self, config):
        """Construct object.

        Args:
            config (deode.ParsedConfig): Configuration
        """
        Task.__init__(self, config, __name__)

        self.config_verif = ConfigHarpverify(self.config)
        self.binary = "python3"

    def execute(self):
        """link OBSTABLES, FCTABLES from REF and EXPS to path directory or retrieve from ECFS archive"""
        if self.config_verif.use_operational_indexing=="yes":
            #sqlites_exp_path is something like this:
            #/scratch/sp3c/DE_NWP/deode/2024/12/03/00//convection/1/HARMONIE_AROME_500m/sqlite/FCTABLE/
            #Retain the DEODE relative path to the experiment's gribs and sqlites. 
            #Extract it from the sqlites_exp_path variable (i.e /YYYY/MM/DD/HH//{type_of_extreme}/{order_of_run}
            print('Looking for FCTABLES in sqlites_exp_path:')
            print(self.config_verif.sqlites_exp_path)
            sqlites_relpath=self.config_verif.sqlites_exp_path.replace(self.config_verif.huser,self.config_verif.duser).split('deode')[1]
            exp_relpath=sqlites_relpath.split('sqlite')[0]
            # The 2 variables above should be something like '/2024/12/03/00//convection/1/HARMONIE_AROME_500m/sqlite/FCTABLE/' and '/2024/12/03/00//convection/1/HARMONIE_AROME_500m/'
            exp_scratch=self.config_verif.sqlites_exp_path.replace(self.config_verif.huser,self.config_verif.duser) #we must refer to deode user in case it's different than harp user
            #The line above should be something like /scratch/aut6432/DE_NWP/deode/2024/12/03/00//convection/1/HARMONIE_AROME_500m/sqlite/FCTABLE/
            local_fctables=os.path.join(self.config_verif.home,f"FCTABLES/",exp_relpath.lstrip('/'),self.config_verif.startyyyy,self.config_verif.startmm)
            # Remove substrings like 'mbr000', 'mbr123', etc.
            local_fctables = re.sub(r"mbr\d{3}", "", local_fctables)
            # Clean up possible double slashes
            local_fctables = os.path.normpath(local_fctables)
            #The line above evaluates ~ /ec/res4/hpcperm/sp3c/deode_project/deode_harp_output/FCTABLES//2024/12/03/00//convection/1/HARMONIE_AROME_500m/YYYY/MM/
            local_fctables_ref=local_fctables.split(self.config_verif.csc)[0] #This is where REF's folder with FCTABLES should be linked
            #The line above is where the Global_DT FCTABLES should be downloaded or linked for this experiment. It should be something like:
            #/ec/res4/hpcperm/sp3c/deode_project/deode_harp_output/FCTABLES/2024/12/03/00//convection/1/Global_DT
        else:
            #sqlites_exp_path is something like this:
            #/scratch/sp3c/deode/CY49t2_AROME_nwp_DEMO_60x80_2500m_20250209/archive/sqlite/FCTABLE/CY49t2_AROME_nwp_DEMO_60x80_2500m_20250209/2025/02
            sqlites_relpath=self.config_verif.sqlites_exp_path.split('deode')[1]
            yyyy_mm_string=str(self.config_verif.startyyyy)+'/'+str(self.config_verif.startmm) # get that 2025/02 part to get exp_scratch in the next line:
            exp_scratch=self.config_verif.sqlites_exp_path.replace(self.config_verif.huser,self.config_verif.duser) #we must refer to deode user in case it's different than harp user 
            #Construct local_fctables:
            local_fctables=os.path.join(self.config_verif.home,f"FCTABLES/",self.config_verif.case,self.config_verif.csc_resol,self.config_verif.startyyyy,self.config_verif.startmm)
            print('local_fctables path is:')
            print(local_fctables)
            #Construct local_fctables_ref:
            local_fctables_ref=os.path.join(self.config_verif.home,f"FCTABLES/",self.config_verif.case) #This is where REF's folder with FCTABLES should be linked
            exp_relpath=sqlites_relpath.split('sqlite')[0]    
        #Now, check if the experiment still exists in the $SCRATCH from DEODE's operational user 
        #(replace from huser to duser was needed because the config file is parsed from the local user
        print('checking if exists: '+exp_scratch)
        print('sqlites_relpath: ' + sqlites_relpath)
        print('exp_relpath: '+exp_relpath)
        #This should be improved because e.g. if the link to the duser directory exists but is not filled anymore, it will fail.
        if os.path.exists(exp_scratch) and os.listdir(exp_scratch):   #If the experiment path in scratch exists and has files on it (presumably FCTABLE)
            if not (os.path.exists(local_fctables) and os.listdir(local_fctables)):
             print(f"The path '{local_fctables}' does not exist or is empty.")
             #If FCTABLES links / downloads are not yet where neded in VERIF_HOME, create the folder and link them there
             print(f"linking FCTABLES for case exp {exp_scratch} in {local_fctables}")
             os.makedirs(local_fctables, exist_ok=True)
             for file_name in os.listdir(exp_scratch):
                 source_path = os.path.join(exp_scratch, file_name)
                 target_path = os.path.join(local_fctables, file_name)
                 # Create symlink only if it's a file and not already linked
                 if os.path.isfile(source_path) and not os.path.exists(target_path):
                  os.symlink(source_path, target_path)
            else:
             print('links to FCTABLES for case exp exist already, linking commands skipped') 
        else:  #If the experiment path in scratch does not exist or is empty, get the FCTABLES from ECFS archive:
           if self.config_verif.use_operational_indexing=="yes":
             ecfs_exp_sqlites_path='ec:..' + os.sep + self.config_verif.duser + os.path.join(self.config_verif.ecfs_archive_relpath_deodeoutput,sqlites_relpath.split('sqlite')[0].lstrip('/'),'*sqlite')
           else:  
             ecfs_exp_sqlites_path='ec:..' + os.sep + self.config_verif.duser + os.path.join(self.config_verif.ecfs_archive_relpath_deodeoutput,self.config_verif.case,self.config_verif.ecfs_archive_sqlites,'*sqlite')
           print('making dir for FCTABLES and downloading from ecfs:')
           print(self.config_verif.duser)
           print(local_fctables)
           print(ecfs_exp_sqlites_path)
           try:
              os.makedirs(local_fctables, exist_ok=True)
           except PermissionError as e:
              print(f"Permission error: {e}")
           except FileNotFoundError as e:
              print(f"File not found: {e}")
           except Exception as e:
              print(f"An error occurred: {e}")
           subprocess.run(["ecp", ecfs_exp_sqlites_path, local_fctables], check=True)           

        for ref_model in self.config_verif.ref_name:
           if os.path.exists(os.path.join(self.config_verif.sqlites_ref_path,ref_model)):
             print('linking FCTABLES for REF exp...')
             if not os.path.exists(os.path.join(local_fctables_ref,ref_model)): # If linked folder does not exist
                    print('linking FCTABLES path for REF exp...')
                    source_path = os.path.join(self.config_verif.sqlites_ref_path,ref_model)
                    destination_folder = local_fctables_ref
                    # Ensure the destination is a directory
                    if not os.path.isdir(destination_folder):
                        raise ValueError(f"{destination_folder} is not a valid directory.")
                    # Name the symlink inside the destination folder
                    link_name = os.path.join(destination_folder, os.path.basename(source_path))
                    # Create the symlink
                    try:
                        os.symlink(source_path, link_name)
                        print(f"Symlink created: {link_name} -> {source_path}")
                    except FileExistsError:
                        print(f"Symlink already exists: {link_name}")
                    except Exception as e:
                        print(f"Error creating symlink: {e}")
             else:
                    print('link to FCTABLES for REF exp exists already, linking command skipped') 	

        #Finally, link observations if needed (not needed anymore after managing observations through suites in snh02
        #dir_path = os.path.join(self.config_verif.sqlites_obs_path, "*")
        #subdirs = glob.glob(dir_path)
        #if subdirs:
        #   arg1=self.config_verif.sqlites_obs_path
        #   arg2=os.path.join(self.config_verif.home, "OBSTABLESOPER/")
        #   print("Found files in original path: linking obs sqlite files...")
        #   self.config_verif.link_files(arg1,arg2)	
        #else:
        #   print('No observations sqlite files available')

