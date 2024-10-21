# deode_harp_plugin
Plugin interface to run harp point verification for deode extreme weather cases.

# Prerrequisites:
- An installation of harpv02.2 or higher. Instructions can be found here: https://harphub.github.io/harp_training_2024/get-started.html
- Get the official harp scripts for operational use, available in https://github.com/harphub/oper-harp-verif

# Description:
This plugin needs a config.toml file from a deode run as input. Relevant configuration of the verification paths, etc. must be updated in the 
file harpverify_plugin.toml.
To create a verification suite from a config.toml and the harpverify_plugin.toml file, create a file -i.e. called configuration- in the Deode-Workflow home directory, with the following content:

> --config-file
> 
>   /path/to/config.toml
> 
>   /path/to/harpverify_plugin.toml

Then create and launch the verification suite with these commands: 

> poetry shell
> 
> deode case ?configuration -o verification_suite.toml
> 
> deode start suite --config-file verification_suite.tom

If everything went fine, a new suite will appear in your ecflow_ui, named just like the deode case, with a family called "Case_point_verification" and tasks to get the verification files, Verify, and save the files conveniently:

![Screenshot from 2024-10-21 10-59-18](https://github.com/user-attachments/assets/f68f5f10-2488-437b-932d-709bd8914d60)

  
