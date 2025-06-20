"""Example Task."""
import os
import subprocess
from ..methods import ConfigHarpverify
from deode.tasks.base import Task
from deode.tasks.batch import BatchJob


class Verification(Task):
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
        print('self.config_verif.home es ' + self.config_verif.home)
        #print(f"verif home es {self.config_verif.home} (clase) y {os.environ.get("VERIF_HOME")} (entorno)")
        os.chdir(self.config_verif.home)
        config_yaml_filename,exp_args = self.config_verif.write_config_yml()
        verif_path=exp_args["verif"]["verif_path"][0]
        plot_verif_path=exp_args["post"]["plot_output"][0]
        #Create paths where RDS and pngs will be saved
        os.makedirs(plot_verif_path, exist_ok=True)
        os.makedirs(verif_path, exist_ok=True)
        print(config_yaml_filename)
        start_date=self.config_verif.startyyyymmddhh
        end_date=self.config_verif.endyyyymmddhh
        harp_scripts=self.config_verif.harpscripts_home
        print(harp_scripts)
        print(os.getenv("HOME"))
        os.chdir(harp_scripts)
        Renv_conf=self.config_verif.Renv_conf
        self.batch.run(f"source {Renv_conf} ; Rscript {harp_scripts}/verification/point_verif.R -config_file {config_yaml_filename} -start_date {start_date} -end_date {start_date} -params_list=T2m,S10m,CCtot,S,D,RH,T,Pcp,AccPcp1h,Gmax,T2m,S10m,Pcp,AcccPcp3h,AccPcp6h,AccPcp12h,AccPcp24h -params_file {self.config_verif.set_params}")



