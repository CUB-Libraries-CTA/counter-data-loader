⚠️ This repository is archived and is no longer maintained or in use. It remains available for reference only.

# counter-data-loader
Loads COUNTER database from JR1 report spreadsheets

## Requirements

* python3  (tested with 3.9)
* pip      (tested with 22.2)
* setuptools   (tested with 63.4)

## Python Environment Installation

These instructions use the "pip" python package manager.   

Unlike the "conda" package manager, the desired python, pip, and setuptools versions must be pre-installed on the local machine.

Using "pip" should be fine, as long as all projects on the local machine can use the same version of python, pip, and setuptools.
```
    # Install python virtual environment manager, if it doesn't already exist
    pip install virtualenv
    
    # Change directory to the parent folder for the cloned counter-data-loader repo.
    cd /path/to/counter-data-loader
    cd ..
    
    # Create a virtual environment 'counter-data-loader` that uses python 3.
    # Note that unlike conda, pip requires that whatever python version you want is already installed locally.
    virtualenv counter-python-env -p `which python3`
    
    # Activate the python environment
    . ./counter-python-env/bin/activate
    
    # Install the dependencies needed for counter-data-loader project.
    # NOTE: make sure the "activate" command has been run and you're in the counter-python-env environment.    
    pip install -r counter-data-loader/requirements.txt
    
    # To exit the python environment, simply type:
    deactivate    
```
**NOTE: All python commands related to counter-data-loader must be run from within the python environment.**

To uninstall or re-install the environment:

* First deactivate the environment:  `deactivate`
* Then delete the folder "counter-python-env":  `rm -rf counter-python-env`
* Then follow the instructions above to recreate the environment.



