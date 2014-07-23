# examples.py

'''

'''

# instantiate
import dicommanager
M = dicommanager.DicomManager()


# find DICOMs to manage
dcmDir = '/path/to/directory/of/dicoms'
dcmPaths = M.find( dcmDir, recursive=True )
dcmPath = dcmPaths[0]


# read DICOM into object
dcm = M.read( dcmPath )


# record DICOM series data in SQLite database
M.record( dcm )


# store DICOM in managed file tree
M.store( dcm )


# manage DICOMs
M.manage( dcmPaths=dcmPaths, deleteDcm=False, recordDcm=True, storeDcm=True )


# get a manageed series' record from the database (various args)
M.getSeriesRecord( recordID=1 )
M.getSeriesRecord( seriesUID="1.2.840.113619.2.135.2025.2073408.4720.1102388196.443" )
M.getSeriesRecord( accessionNumber=1234567 )
M.getSeriesRecord( accessionNumber="1234567" )
M.getSeriesRecord( patientID=7654321 )
M.getSeriesRecord( patientID="7654321" )


# get the path to a managed series' storage location (various args)
M.getSeriesDir( recordID=1 )
M.getSeriesDir( seriesUID="1.2.840.113619.2.135.2025.2073408.4720.1102388196.443" )
M.getSeriesDir( accessionNumber=1234567 )
M.getSeriesDir( accessionNumber="1234567" )
M.getSeriesDir( patientID=7654321 )
M.getSeriesDir( patientID="7654321" )


# copy selected managed DICOMs to another location
recordIDs = [1,2,3,4,5,6,7,8,9]
dstRoot = "/some/other/location"
M.export( recordIDs=recordIDs, dstRoot=dstRoot, ageBreakdown=False, directoryTree=True, readableSeriesSlug=True )


# delete a DICOM series from the manager using the record ID
M.delete( 1 )


# delete multiple DICOM series from the manager using the record ID
M.delete( [1,2,3,4,5] )


# record note about multiple series
seriesInstanceUIDs = [
"1.2.840.113619.2.135.2025.2073408.4720.1102388196.443",
"1.2.840.113619.2.135.2025.2073408.4720.1102388196.530",
"1.2.840.113619.2.135.2025.2073408.4720.1102388196.622",
"1.2.840.113619.2.135.2025.2073408.4720.1102388196.877",
"1.2.840.113619.2.135.2025.2073408.4720.1102388196.970"
]
note = "#greatscan #3D #T1"
M.note( seriesInstanceUIDs, note )


# delete series notes 
M.delete_notes( [1,2,3,4,5] )



