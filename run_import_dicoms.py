# run_import_dicoms.py

# add working directory to search path
import os
import sys
sys.path.insert(0, os.path.realpath(__file__))

# import dicom manager
from dicom_manager import *

# instantiate dicom manager
M = DicomManager()

# get the path to the root direcotry containing the dicoms
rootDir = raw_input("Enter root path of dicoms to import: ").strip().replace('\\','')

# import all dicoms under given directory
M.import_dicoms(rootDir)

