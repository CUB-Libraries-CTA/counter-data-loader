# PyCharm Debug Server Configuration

Tested with PyCharm 2022.2.3 (Professional Edition) on a Mac Laptop running OSX 12.6.

* The pycharm debug library referenced in the screenshot should already be installed via requirements.txt, but if a newer version of Pycharm is being used, you may have to install a later version of the debug library.  Make sure you are installing it in the python environment "counter-python-env" designed specifically for this workflow.  This means the python env must be activated, and "pip install" should be run.
* In PyCharm, create a Python Debug Server configuration using the settings in the screenshot.
* Include the python code mentioned in the screenshot within the python script being debugged.   If debugging is not desired, this line should be commented out.
* Run the Debug Server by clicking the "Bug" icon in PyCharm.  
* Now, running python code should connect with the Debug Server, stop at breakpoints, and allow program state to be checked.
