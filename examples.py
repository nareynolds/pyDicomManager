# examples.py

'''
*****************************************************
Example use:

# instantiate
import dicommanager
M = dicommanager.DicomManager()

# import a single dicom file
M.import_dicom("")

# import all dicoms under given directory
M.import_dicoms("")

# export a single series by series ID
M.export_dicom(1, "", directoryTree=True)

# export multiple series by series ID
M.export_dicoms([1,2,3,4,5,...], "/Volumes/mi2b2/3/Pediatric_Brain_Atlas/processing/reviewing", ageBreakdown=False, directoryTree=True, keepSeriesSlug=True)

# delete a single series by series ID
M.delete_a_series(1)

# delete multiple series by series ID
M.delete_series([1,2,3,4,5,...])
    
# delete study by accession number
M.delete_study('11340432')

# delete patient by institution and MRN
M.delete_patient('MGH', '2853644')

# print patient MRNs
M.print_patient_ids()
    
# print study accession numbers
M.print_accession_numbers()
    
# add accession numbers of wanted studies
M.add_wanted_studies( ['12345', '67890'], "note")
    
# print wanted studies
M.print_wanted_studies()

# print wanted studies you don't have
M.print_studies_to_get()

# record note for multiple series
M.add_series_notes([1,2,3,...], "note")
    
# delete multiple series notes by note id
M.delete_series_notes([1,2,3,...]):
    
*****************************************************
'''
