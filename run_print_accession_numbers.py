# run_import_dicoms.py

# add working directory to search path
import os
import sys
sys.path.insert(0, os.path.realpath(__file__))

# import dicom manager
from dicom_manager import *

# instantiate dicom manager
M = DicomManager()

# import all dicoms under given directory
M.print_accession_numbers()

