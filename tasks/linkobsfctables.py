"""Example Task."""	
import os
import glob
from ..methods import ConfigHarpverify
from deode.tasks.base import Task

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
        if os.path.exists(self.config_verif.sqlites_exp_path.replace(self.config_verif.huser,self.config_verif.duser).split('FCTABLE')[0]+'FCTABLE/'+self.config_verif.case):
           print('FCTABLES for case exp exist in $SCRATCH: retrieve from archive not needed')
           if not os.path.exists(os.path.join(self.config_verif.home,f"FCTABLE/"+self.config_verif.case)):
             print('linking FCTABLES for case exp...')
             os.symlink(self.config_verif.sqlites_exp_path.replace(self.config_verif.huser,self.config_verif.duser).split('FCTABLE')[0] + 
             'FCTABLE/'+self.config_verif.case,os.path.join(self.config_verif.home,f"FCTABLE/"+self.config_verif.case))
           else:
             print('link to FCTABLES for case exp exists already, linking command skipped') 
        else:
           print('making dir for FCTABLES and downloading from ecfs:')
           local_exp_sqlites_path=os.makedirs(os.path.join(self.config_verif.home,"FCTABLE",self.config_verif.case,self.config_verif.startyyyy,self.config_verif.startmm))
           ecfs_exp_sqlites_path=os.path.join('ec:..',self.config_verif.duser,'deode',self.config_verif.case,'sqlites/*')
           subprocess.run(["ecp", ecfs_exp_sqlites, local_exp_sqlites], check=True)           
        if os.path.exists(os.path.join(self.config_verif.sqlites_ref_path,self.config_verif.ref_name)):
             print('linking FCTABLES for REF exp...')
             if not os.path.exists(os.path.join(self.config_verif.home,f"FCTABLE/"+self.config_verif.ref_name)):
                    print('linking FCTABLES for REF exp...')
                    os.symlink(os.path.join(self.config_verif.sqlites_ref_path,self.config_verif.ref_name),os.path.join(self.config_verif.home,f"FCTABLE/"+self.config_verif.ref_name))
             else:
                    print('link to FCTABLES for REF exp exists already, linking command skipped') 	
        dir_path = os.path.join(self.config_verif.sqlites_obs_path, "*")
        subdirs = glob.glob(dir_path)
        if subdirs:
           arg1=self.config_verif.sqlites_obs_path
           arg2=os.path.join(self.config_verif.home, "OBSTABLE/")
           print("Found files in original path: linking obs sqlite files...")
           self.config_verif.link_files(arg1,arg2)	
        else:
           print('No observations sqlite files available')

