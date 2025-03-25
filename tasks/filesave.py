"""Example Task."""
import os
import subprocess
from ..methods import ConfigHarpverify
from deode.tasks.base import Task
from deode.tasks.batch import BatchJob


class Filesave(Task):
    """List a grib file."""

    def __init__(self, config):
        """Construct object.

        Args:
            config (deode.ParsedConfig): Configuration
        """
        Task.__init__(self, config, __name__)

        self.config_verif = ConfigHarpverify(self.config)
        self.binary = "python3"
        self.batch = BatchJob(os.environ)

    def execute(self):

        #Archive only at ecfs for now, all files found in ["verif"]["verif_path"]
        #Next line is unnecessary here, but is needed if everything below is moved to another task
        #Instead of reading yaml file, it generates it again but it doesn't write the output file
        config_yaml_filename,exp_args = self.config_verif.write_config_yml(write=False)
        csc = self.config_verif.csc
        case = self.config_verif.case
        #These lines come from linkobsfctables.py and are adapted here to fill the config file for harp's R script
        #Extract it from the sqlites_exp_path variable (i.e /YYYY/MM/DD/HH//{type_of_extreme}/{order_of_run}
        sqlites_relpath=self.config_verif.sqlites_exp_path.replace(self.config_verif.huser,self.config_verif.duser).split('deode')[1]
        exp_relpath=sqlites_relpath.split('sqlite')[0]
        # The lines above should be something like '/2024/12/03/00//convection/1/HARMONIE_AROME_500m/sqlite/FCTABLE/' (without the last 2 for the second one)

        print(exp_args)
        verif_path=exp_args["verif"]["verif_path"][0]
        plot_output=exp_args["post"]["plot_output"][0]
        end_date=self.config_verif.endyyyymmddhh
        harp_scripts=self.config_verif.harpscripts_home
        print(harp_scripts)
        os.chdir(harp_scripts)
        print(verif_path)
        print(case)
        print(self.config_verif.ecfs_archive_relpath_harpoutput)
        print(self.config_verif.huser)
        print(' copying files from' + str(os.path.join(verif_path,case))+ ' to ec:../'+self.config_verif.huser + '/'+os.path.join(self.config_verif.huser,self.config_verif.ecfs_archive_relpath_harpoutput,exp_relpath.lstrip('/')))
        self.config_verif.replicate_structure_to_ec(os.path.join(verif_path,case),'ec:../'+self.config_verif.huser + '/'+os.path.join(self.config_verif.huser,self.config_verif.ecfs_archive_relpath_harpoutput,exp_relpath.lstrip('/')))
        
        print(' copying files from' + str(os.path.join(plot_output,case))+ ' to ec:../'+self.config_verif.huser + '/'+os.path.join(self.config_verif.huser,self.config_verif.ecfs_archive_relpath_harpoutput,exp_relpath.lstrip('/')))
        self.config_verif.replicate_structure_to_ec(os.path.join(plot_output,case),'ec:../'+self.config_verif.huser + '/'+os.path.join(self.config_verif.huser,self.config_verif.ecfs_archive_relpath_harpoutput,exp_relpath.lstrip('/')))

