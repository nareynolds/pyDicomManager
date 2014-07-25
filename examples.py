# examples.py
# Here are some example use cases of how to use

# instantiate
import dicommanager
M = dicommanager.DicomManager()


# find DICOMs to manage
dcmDir = '/path/to/directory/of/dicoms'
dcmPaths = M.find( dcmDir, recursive=True )
dcmPath = dcmPaths[0]


# read DICOM into pydicom object
dcm = M.read( dcmPath )


# record DICOM series data in SQLite database
M.record( dcm )


# store DICOM in managed file tree
M.store( dcm )


# manage DICOMs = read, record, store, optionally delete original
M.manage( dcmPaths=dcmPaths, deleteDcm=False, recordDcm=True, storeDcm=True )


# get a pydicom object loaded with the series' record from the database (various args)
dcm = M.getSeriesRecord( recordID=1 )
M.getSeriesRecord( seriesUID="1.2.840.113619.2.135.2025.2073408.4720.1102388196.443" )
M.getSeriesRecord( accessionNumber=1234567 )
M.getSeriesRecord( accessionNumber="1234567" )
M.getSeriesRecord( patientID=7654321 )
M.getSeriesRecord( patientID="7654321" )


# get the path to a stored series' directory in the managed filetree (various args)
M.getSeriesDir( recordID=1 )
M.getSeriesDir( seriesUID="1.2.840.113619.2.135.2025.2073408.4720.1102388196.443" )
M.getSeriesDir( accessionNumber=1234567 )
M.getSeriesDir( accessionNumber="1234567" )
M.getSeriesDir( patientID=7654321 )
M.getSeriesDir( patientID="7654321" )


# copy selected series in the managed filetree to a location of choice
recordIDs = [1,2,3,4,5,6,7,8,9]
dstRoot = "/some/other/location"
M.export( recordIDs=recordIDs, dstRoot=dstRoot, ageBreakdown=False, directoryTree=True, readableSeriesSlug=True )


# delete a DICOM series from the managed filetree along with its database record
recordID = 1
M.delete( recordID )


# delete multiple DICOM series from the manager using the record ID
recordIDs = [1,2,3,4,5,6,7,8,9]
M.delete( recordIDs )


# record note about multiple series
seriesInstanceUIDs = [
"1.2.840.113619.2.135.2025.3762954.8545.1102935470.773",
"1.2.840.113619.2.135.2025.3762954.8545.1102935470.860",
"1.2.840.113619.2.135.2025.3762954.8545.1102935470.947"
]
note = "#greatscan #3D #T1"
M.note( seriesInstanceUIDs, note )


# delete series notes 
noteIDs = [1,2,3,4,5]
M.deleteNotes( noteIDs )


# here is an executable python script to perform DicomManager.manage()
# which means you enter this directly in the terminal window
cd ~/the/location/of/these/files
python manage_dicoms.py



