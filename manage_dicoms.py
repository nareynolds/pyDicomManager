# run_import_dicoms.py

# imports
import os
import sys
import shutil
import fnmatch
import dicommanager

# add working directory to search path
sys.path.insert(0, os.path.realpath(__file__))

# instantiate dicom manager
M = dicommanager.DicomManager()

# get the path to the root directory containing the DICOMs
rootDir = raw_input("Enter path to root directory of DICOMs to manage: ").strip().replace('\\','')

# inquire about deleting original dicoms
deleteSrcDicoms = False
deleteSrcTree = False
ans = raw_input("Delete original dicoms? (y/n): ").strip()
if ans == "y":
    deleteSrcDicoms = True
    
    # inquire about deleting file tree under 'dcmRoot'
    ans = raw_input("Delete file tree under 'root directory'? (y/n): ").strip()
    if ans == "y":
        deleteSrcTree = True

# find DICOMs under given directory
print "Finding DICOMs to manage..."
dcmPaths = M.find(rootDir)
print "Found %d DICOMs." % len(dcmPaths)

# mange all found DICOMs
print "Reading, recording, and storing DICOMs..."
M.manage( dcmPaths, deleteSrcDicoms )
print "Done."

# delete file tree under 'dcmRoot' if requested
if deleteSrcDicoms and deleteSrcTree:
    
    # check for any residual dicoms in the file tree
    print "Checking for residual DICOMs..."
    dcmPaths = []
    for root, dirnames, filenames in os.walk( rootDir ):
        for filename in fnmatch.filter( filenames, '*.dcm' ):
            dcmPaths.append( os.path.join( root, filename ) )
    numPaths = len( dcmPaths )

    if numPaths != 0:
        # there are residual dicoms - don't delete file tree!
        print "Warning! Some DICOMs were not imported:"
        for dcmIdx, dcmPath in enumerate( dcmPaths ):
            print str(dcmIdx) + ".  " + dcmPath
            
    else:
        # delete the file tree
        print "None found, good. Deleting file tree under %s..." % rootDir
        for root, dirs, files in os.walk(rootDir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        print "Done.                     "

