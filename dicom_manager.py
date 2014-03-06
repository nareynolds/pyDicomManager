# dicom_manager.py

'''
*****************************************************
Example use:

# instantiate
from dicom_manager import *
M = DicomManager()

# import a single dicom file
M.import_dicom("")

# import all dicoms under given directory
M.import_dicoms("")

# export a single series by series ID
M.export_dicom(1, "", exportFileTree=True)

# export multiple series by series ID
M.export_dicoms([1,2,3,4,5,...], "", exportFileTree=True)

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




# add working directory to search path
import os
import sys
sys.path.insert(0, os.path.realpath(__file__))

# get file management tools
import shutil
import fnmatch
import re

# get SQLite tools
import sqlite3

# get tools for reading dicoms
import dicom
from dicom._dicom_dict import DicomDictionary

# get list of dicom header tags to import into sqlite db: dcm_HOI
from dicom_hoi import *

# get settings
from manager_settings import *





class DicomManager:
    
    #--------------------------------------------------------------------------------------------
    def __init__(self):
        self.settings = ManagerSettings()
        self.setup()

    
    #--------------------------------------------------------------------------------------------
    def setup(self):
        
        print "Setting up the Dicom Manager..."
        
        # reduce check frequency to speed up things
        sys.setcheckinterval(1000)
        
        # check for the manager's SQLite database
        if not os.path.exists(self.settings.dbPath):
            print "Management database not found. Creating it..."
        
        # connect to SQLite database and enable dictionary access of rows
        self.dbCon = sqlite3.connect(self.settings.dbPath)
        self.dbCon.row_factory = sqlite3.Row
                
        # check if the dicom series database table exists
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.settings.dbTblSeries )
            qResult = dbCur.fetchone()

        if qResult is None:
            # series table doesn't exist - create table in database
            print "Database table '%s' not found. Creating it..." % self.settings.dbTblSeries
            dcmHeaderNames = [ DicomDictionary[dcmHeaderKey][4] for dcmHeaderKey in dcm_HOI ]
            qCreate = "CREATE TABLE " + self.settings.dbTblSeries + " ( id INTEGER PRIMARY KEY, NumberOfDicoms INTEGER DEFAULT 0 NOT NULL, " +  ' TEXT, '.join(dcmHeaderNames) + " TEXT )"
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute(qCreate)

        # check if the dicom project database table exists
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.settings.dbTblProjectSeries )
            qResult = dbCur.fetchone()
        
        if qResult is None:
            # projects table doesn't exist - create table in database
            print "Database table '%s' not found. Creating it..." % self.settings.dbTblProjectSeries
            qCreate = "CREATE TABLE %s ( Project TEXT, SeriesId INTEGER, PRIMARY KEY ( Project, SeriesId ) )" % self.settings.dbTblProjectSeries
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute(qCreate)
    
        # check if the list of wanted studies database table exists
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.settings.dbTblWantedStudies )
            qResult = dbCur.fetchone()
    
        if qResult is None:
            # projects table doesn't exist - create table in database
            print "Database table '%s' not found. Creating it..." % self.settings.dbTblWantedStudies
            qCreate = "CREATE TABLE %s ( Project TEXT, AccessionNumber TEXT, Note TEXT, PRIMARY KEY ( Project, AccessionNumber ) )" % self.settings.dbTblWantedStudies
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute(qCreate)

        # check if the series' notes database table exists
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.settings.dbTblSeriesNotes )
            qResult = dbCur.fetchone()
        
        if qResult is None:
            # projects table doesn't exist - create table in database
            print "Database table '%s' not found. Creating it..." % self.settings.dbTblSeriesNotes
            qCreate = ("CREATE TABLE %s ( id INTEGER PRIMARY KEY, Project TEXT, SeriesId INTEGER, Note TEXT ); "
                       "CREATE INDEX ProjectIdx ON %s (Project); "
                       "CREATE INDEX SeriesIdx ON %s (SeriesId); "
                       ) % ( self.settings.dbTblSeriesNotes, self.settings.dbTblSeriesNotes, self.settings.dbTblSeriesNotes )
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.executescript(qCreate)
    
        # check root directory's existence
        if not os.path.exists(self.settings.rootDir):
            print "Root directory not found. You must create this!"
            return

        # check for import directory
        if not os.path.exists(self.settings.toImportDir):
            print "'to_import' directory not found. Creating it..."
            os.makedirs(self.settings.toImportDir)
        
        # check for dicom directory
        if not os.path.exists(self.settings.dicomsDir):
            print "'dicom' directory not found. Creating it..."
            os.makedirs(self.settings.dicomsDir)

        # check for projects directory
        if not os.path.exists(self.settings.projectsDir):
            print "'projects' directory not found. Creating it..."
            os.makedirs(self.settings.projectsDir)

        # check for the selected project's directory
        if not os.path.exists(self.settings.selectedProjectDir):
            print "'%s' directory not found. Creating it..." % self.settings.projectName
            os.makedirs(self.settings.selectedProjectDir)

        # check for the selected project's directory containing data organized by patient
        if not os.path.exists(self.settings.byPatientDir):
            print "'by_patient' directory not found. Creating it..."
            os.makedirs(self.settings.byPatientDir)

        # check for the selected project's directory containing data organized by age
        if not os.path.exists(self.settings.byAgeDir):
            print "'by_age' directory not found. Creating it..."
            os.makedirs(self.settings.byAgeDir)
        
        print "Done!"


            
    #--------------------------------------------------------------------------------------------
    def print_patient_ids(self):

        # get a list of the patient MRNs associated with the current project
        ids = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT DISTINCT PatientID FROM %s WHERE id IN (SELECT SeriesID FROM %s WHERE Project = ?)" % (self.settings.dbTblSeries, self.settings.dbTblProjectSeries), (self.settings.projectName,) )
            qResult = dbCur.fetchall()
            if qResult is None:
                print "Error: Couldn't find any patients!"
                return
            else:
                ids = [row[0] for row in qResult]

        # print MRNs
        print "The project '%s' has %d patients:" % ( self.settings.projectName, len(ids) )
        for id in ids:
            print "%s" % id
    
            
            
    #--------------------------------------------------------------------------------------------
    def print_accession_numbers(self):
        
        # get a list of the patient MRNs associated with the current project
        ans = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT DISTINCT AccessionNumber FROM %s WHERE id IN (SELECT SeriesID FROM %s WHERE Project = ?)" % (self.settings.dbTblSeries, self.settings.dbTblProjectSeries), (self.settings.projectName,) )
            qResult = dbCur.fetchall()
            if qResult is None:
                print "Error: Couldn't find any accession numbers!"
                return
            else:
                ans = [row[0] for row in qResult]
        
        # print MRNs
        print "The project '%s' has %d accession numbers:" % ( self.settings.projectName, len(ans) )
        for an in ans:
            print "%s" % an


    #--------------------------------------------------------------------------------------------
    def normalize_institution_name(self, institutionName):
        if ('mgh' in institutionName.lower() or
            'massachusetts general' in institutionName.lower() or
            'mass general' in institutionName.lower() or
            'mass. general' in institutionName.lower()
            ):
            return 'MGH'
        else:
            return institutionName.replace(' ','_')


    #--------------------------------------------------------------------------------------------
    def import_dicom(self, dcmPath):
        
        # make functions local variables for speed
        os_path_exists = os.path.exists
        os_path_join = os.path.join
        
        # check that the dicom exists
        if not os_path_exists(dcmPath):
            print "Dicom not found: %s" % dcmPath
            return

        # read dicom file
        dcm = dicom.read_file(dcmPath)
    
        # check that dicom has necessary fields
        if ('InstitutionName' not in dcm or
            'PatientID' not in dcm or
            'StudyDate' not in dcm or
            'PatientAge' not in dcm or
            'AccessionNumber' not in dcm or
            'StudyDescription' not in dcm or
            'SeriesDescription' not in dcm
        ):
            print "Dicom doesn't have one of the required tags: %s" % dcmPath
            return

        # get available header values and associated column names
        cols = []
        vals = []
        for dcmHeaderKey in dcm_HOI:
            if dcmHeaderKey in dcm:
                # enforce single ascii string without quotes
                dcm[dcmHeaderKey].value = "".join(i for i in ( str(dcm[dcmHeaderKey].value).replace('\'','').replace('"','') ) if ord(i)<128)
                
                # collect column names and values for database entry
                cols.append( DicomDictionary[dcmHeaderKey][4] )
                vals.append( dcm[dcmHeaderKey].value )

        seriesId = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            
            # check if this series is already recorded in database
            qCheck = "SELECT id FROM %s WHERE %s LIMIT 1" % (self.settings.dbTblSeries, ' AND '.join([ col + ' = ?' for col in cols ]))
            dbCur.execute( qCheck, vals )
            qResult = dbCur.fetchone()

            if qResult is not None:
                # series already in database, check if series is owned by current project
                seriesId = str( qResult[0] )
                dbCur.execute( "SELECT count(*) FROM %s WHERE Project = ? AND SeriesId = ? LIMIT 1" % self.settings.dbTblProjectSeries, ( self.settings.projectName, seriesId ) )
                qResult = dbCur.fetchone()
                if qResult[0] == 0:
                    # study not owned by current project - add it
                    dbCur.execute( "INSERT INTO %s ( Project, SeriesId ) VALUES ( ?, ? )" % self.settings.dbTblProjectSeries, ( self.settings.projectName, seriesId ) )
        
            else:
                # series not in database - add it
                qInsertSeries = "INSERT INTO %s ( %s ) VALUES ( %s )" % ( self.settings.dbTblSeries, ', '.join(cols), ', '.join([ '?' for i in xrange(len(vals)) ]) )
                qSeriesLastInsertId = "SELECT last_insert_rowid()"
                qInsertProjectSeries = "INSERT INTO %s ( Project, SeriesId ) VALUES ( '%s', last_insert_rowid() )" % ( self.settings.dbTblProjectSeries, self.settings.projectName )
                dbCur.execute( qInsertSeries, vals)
                dbCur.execute( qSeriesLastInsertId )
                seriesId = str( dbCur.fetchone()[0] )
                dbCur.execute( qInsertProjectSeries )

        # normalize institution name for file tree consolidation
        institutionName = self.normalize_institution_name( dcm.InstitutionName )

        # check if institution directory exists
        institutionDir = os_path_join( self.settings.dicomsDir, institutionName )
        if not os_path_exists( institutionDir ):
            print "Institution directory '%s' being created..." % institutionName
            os.makedirs( institutionDir )

        # check if patient directory exists
        patientDir = os_path_join( institutionDir, dcm.PatientID )
        if not os_path_exists( patientDir ):
            print "| Patient directory '%s' being created..." % dcm.PatientID
            os.makedirs( patientDir )

        # check if study directory exists
        studySlug = re.sub( r'[/\\]', '', '_'.join([ dcm.StudyDate, dcm.PatientAge, dcm.AccessionNumber, dcm.StudyDescription ]).replace(' ','_') )
        studyDir = os_path_join( patientDir, studySlug )
        if not os_path_exists( studyDir ):
            print "|| Study directory '%s' being created..." % studySlug
            os.makedirs( studyDir )

        # check if series directory exists
        seriesSlug = re.sub( r'[/\\]', '', '_'.join([ dcm.SeriesDescription, seriesId ]).replace(' ','_') )
        seriesDir = os_path_join( studyDir, seriesSlug )
        if not os_path_exists( seriesDir ):
            print "||| Series directory '%s' being created..." % seriesSlug
            os.makedirs( seriesDir )

        # check if dicom has been filed already
        dcmDst = os_path_join( seriesDir,  os.path.basename( dcmPath ) )
        if not os_path_exists( dcmDst ):
            # copy dicom to manager file tree
            shutil.copyfile(dcmPath, dcmDst)
            
            # increment NumberOfDicoms field in database
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute( "UPDATE %s SET NumberOfDicoms = NumberOfDicoms + 1 WHERE id = %s" % ( self.settings.dbTblSeries, seriesId ) )

        # create alias in project's 'by_patient' directory
        institutionAlias = os_path_join( self.settings.byPatientDir, institutionName )
        if not os_path_exists( institutionAlias ):
            os.makedirs( institutionAlias )
        
        patientAlias = os_path_join( institutionAlias, dcm.PatientID )
        if not os_path_exists( patientAlias ):
            os.makedirs( patientAlias )
        
        studyAlias = os_path_join( patientAlias, studySlug )
        if not os_path_exists( studyAlias ):
            os.makedirs( studyAlias )
        
        seriesAlias = os_path_join( studyAlias, seriesSlug )
        if not os_path_exists( seriesAlias ):
            self.mk_alias( seriesDir, seriesAlias )

        # create alias in project's 'by_age' directory
        #age = dcm.PatientAge
        #if 'D' in age:
        #    age = 'day_%s' % age.strip().replace('D','')
        #elif 'W' in age:
        #    age = 'week_%s' % age.strip().replace('W','')
        #elif 'M' in age:
        #    age = 'month_%s' % age.strip().replace('M','')
        #elif 'Y' in age:
        #    age = 'year_%s' % age.strip().replace('Y','')
        #
        #ageAlias = os_path_join( self.settings.byAgeDir, age )
        #if not os_path_exists( ageAlias ):
        #    os.makedirs( ageAlias )
        #
        #studySlug = re.sub( r'[/\\]', '', '_'.join([ dcm.StudyDate, institutionName, dcm.PatientID, dcm.AccessionNumber, dcm.StudyDescription ]).replace(' ','_') )
        #studyAlias = os_path_join( ageAlias, studySlug )
        #if not os_path_exists( studyAlias ):
        #    os.makedirs( studyAlias )
        #
        #seriesAlias = os_path_join( studyAlias, seriesSlug )
        #if not os_path_exists( seriesAlias ):
        #    self.mk_alias( seriesDir, seriesAlias )


    #--------------------------------------------------------------------------------------------
    def import_dicoms(self, dcmRoot):

        # check that directory exists
        if not os.path.isdir( dcmRoot ):
            print "Directory passed as 'dcmRoot' doesn't exist!"
            return
        
        # inquire about deleting original dicoms
        deleteSrcDicoms = False
        deleteSrcTree = False
        ans = raw_input("Delete original dicoms? (y/n): ").strip()
        if ans == "y":
            deleteSrcDicoms = True
            
            # inquire about deleting file tree under 'dcmRoot'
            ans = raw_input("Delete file tree under 'dcmRoot'? (y/n): ").strip()
            if ans == "y":
                deleteSrcTree = True

        # recursively search for all dicom files under the provided root directory
        print "Finding dicoms to import..."
        dcmPaths = []
        for root, dirnames, filenames in os.walk( dcmRoot ):
            for filename in fnmatch.filter( filenames, '*.dcm' ):
                dcmPaths.append( os.path.join( root, filename ) )

        numPaths = len( dcmPaths )
        if numPaths == 0:
            print "No dicoms found!"
            return

        # loop through each dicom file
        writeProgress = 0
        sys.stdout.write( "Importing %d dicoms... \n" % numPaths )
        import_dicom = self.import_dicom # make local var for speed
        for dcmIdx, dcmPath in enumerate( dcmPaths ):
            
            # import dicom
            import_dicom(dcmPath)
                
            # remove src dicom if indicated
            if deleteSrcDicoms:
                os.remove(dcmPath)

            # display progress
            writeProgress = ((dcmIdx * 100) / numPaths)
            sys.stdout.write( " Progress: %d%% \r" % writeProgress )
            sys.stdout.flush()
        
        # delete file tree under 'dcmRoot' if requested
        if deleteSrcDicoms and deleteSrcTree:
            
            # check for any residual dicoms in the file tree
            print "Checking for residual dicoms..."
            dcmPaths = []
            for root, dirnames, filenames in os.walk( dcmRoot ):
                for filename in fnmatch.filter( filenames, '*.dcm' ):
                    dcmPaths.append( os.path.join( root, filename ) )
            numPaths = len( dcmPaths )

            if numPaths != 0:
                # there are residual dicoms - don't delete file tree!
                print "Warning! Some dicoms were not imported:"
                for dcmIdx, dcmPath in enumerate( dcmPaths ):
                    print str(dcmIdx) + ".  " + dcmPath
            else:
                # delete the file tree
                print "Deleting file tree under %s..." % dcmRoot
                for root, dirs, files in os.walk(dcmRoot):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))

        print "Done!                     "


    
    #--------------------------------------------------------------------------------------------
    def export_dicom(self, seriesId, dstRoot, ageBreakdown=False, directoryTree=True, keepSeriesSlug=True):

        # make functions local variables for speed
        os_path_exists = os.path.exists
        os_path_join = os.path.join
        
        # find series in SQLite database
        qFind = "SELECT * FROM %s WHERE id = ? LIMIT 1" % self.settings.dbTblSeries
        series = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( qFind, (seriesId,) )
            series = dbCur.fetchone()
        
        if series is None:
            # series not found in database
            print "Series with id %d not found!" % seriesId
            return
            
        # check that the given series belongs to the instance's project
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT count(*) FROM %s WHERE Project = ? AND SeriesId = ?" % self.settings.dbTblProjectSeries, ( self.settings.projectName, seriesId ) )
            if dbCur.fetchone()[0] == 0:
                print "Can't delete the series with id %d, because it is not owned by the project %s!" & ( seriesId, self.settings.projectName )
                return
        
        # determine source-series directory
        institutionName = self.normalize_institution_name( series['InstitutionName'] )
        studySlug = re.sub( r'[/\\]', '', '_'.join([ series['StudyDate'], series['PatientAge'], series['AccessionNumber'], series['StudyDescription'] ]).replace(' ','_') )
        seriesSlug = re.sub( r'[/\\]', '', '_'.join([ series['SeriesDescription'], str(seriesId) ]).replace(' ','_') )
        srcSeriesDir = os.path.join( self.settings.dicomsDir, institutionName, series['PatientID'], studySlug, seriesSlug )
        
        # check that source-series directory exists
        if not os_path_exists( srcSeriesDir ):
            print "Source series directory not found: %s" % srcSeriesDir
            return
        
        # check that destination-root directory exists
        if not os_path_exists( dstRoot ):
            print "Destination root directory not found: %s" % dstRoot
            return

        # option
        if not keepSeriesSlug:
            seriesSlug = 'series%d' % seriesId

        # option
        if ageBreakdown:
            # determine patient age in days at scan time
            ageInDays = None
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                qAge = "SELECT julianday(substr(StudyDate, 1,4) || '-' || substr(StudyDate,5,2)  || '-' || substr(StudyDate, 7,2)) - julianday(substr(PatientBirthDate, 1,4) || '-' || substr(PatientBirthDate,5,2)  || '-' || substr(PatientBirthDate, 7,2)) FROM %s WHERE id = ? LIMIT 1" % self.settings.dbTblSeries
                dbCur.execute( qAge, (seriesId,) )
                ageInDays = dbCur.fetchone()[0]
        
            # determine age range
            for ageRange in self.settings.ageBreakdown:
                if ageInDays >= ageRange['minDay'] and ageInDays <= ageRange['maxDay']:
                    # modify destination directory accordingly
                    dstRoot = os_path_join(dstRoot, ageRange['name'])

        # option
        seriesDir = None
        if directoryTree:
            # check if destination-institution directory exists
            institutionDir = os_path_join( dstRoot, institutionName )
            if not os_path_exists( institutionDir ):
                print "Institution directory '%s' being created..." % institutionName
                os.makedirs( institutionDir )

            # check if destination-patient directory exists
            patientDir = os_path_join( institutionDir, series['PatientID'] )
            if not os_path_exists( patientDir ):
                print "| Patient directory '%s' being created..." % series['PatientID']
                os.makedirs( patientDir )

            # check if destination-study directory exists
            studyDir = os_path_join( patientDir, studySlug )
            if not os_path_exists( studyDir ):
                print "|| Study directory '%s' being created..." % studySlug
                os.makedirs( studyDir )

            # check that destination-series directory doesn't exist
            seriesDir = os_path_join( studyDir, seriesSlug )
            if os_path_exists( seriesDir ):
                print "Destination series directory already exists, skipping: %s" % seriesDir
                return

        else:
            # check that destination-series directory doesn't exist
            seriesDir = os_path_join( dstRoot, seriesSlug )
            #seriesDir = os_path_join( dstRoot, 'series%d' % seriesId )
            if os_path_exists( seriesDir ):
                print "Destination series directory already exists, skipping: %s" % seriesDir
                return
        

        # copy source to destination
        shutil.copytree( srcSeriesDir, seriesDir )
        print "||| Series directory '%s' exported..." % seriesSlug



    #--------------------------------------------------------------------------------------------
    def export_dicoms(self, seriesIds, dstRoot, ageBreakdown=False, directoryTree=True, keepSeriesSlug=True):
        
        # check that at least 1 series was provided
        numIds = len( seriesIds )
        if numIds == 0:
            print "No series IDs provided!"
            return
        
        # loop through list of series ids
        exportProgress = 0
        sys.stdout.write( "Exporting %d series... \n" % numIds )
        for sIdx, seriesId in enumerate( seriesIds ):
            
            # export series
            self.export_dicom( seriesId, dstRoot, ageBreakdown, directoryTree, keepSeriesSlug )
            
            # display progress
            writeProgress = ((sIdx * 100) / numIds)
            sys.stdout.write( " Progress: %d%% \r" % writeProgress )
            sys.stdout.flush()
        
        sys.stdout.write( "Done!                                          \r" )
        sys.stdout.flush()



    #--------------------------------------------------------------------------------------------
    def delete_a_series(self, seriesId):

        # find series in SQLite database
        qFind = "SELECT * FROM %s WHERE id = ? LIMIT 1" % self.settings.dbTblSeries
        series = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( qFind, (seriesId,) )
            series = dbCur.fetchone()

        if series is None:
            # series not found in database
            print "Series with id %d not found!" % seriesId
        else:
            # check that the given series belongs to the instance's project
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute( "SELECT count(*) FROM %s WHERE Project = ? AND SeriesId = ?" % self.settings.dbTblProjectSeries, ( self.settings.projectName, seriesId ) )
                if dbCur.fetchone()[0] == 0:
                    print "Can't delete the series with id %d, because it is not owned by the project %s!" % ( seriesId, self.settings.projectName )
                    return
            
            # normalize institution name
            institutionName = self.normalize_institution_name( series['InstitutionName'] )

            # delete series alias in 'by_age' tree
            age = series['PatientAge']
            if 'D' in age:
                age = 'day_%s' % age.strip().replace('D','')
            elif 'W' in age:
                age = 'week_%s' % age.strip().replace('W','')
            elif 'M' in age:
                age = 'month_%s' % age.strip().replace('M','')
            elif 'Y' in age:
                age = 'year_%s' % age.strip().replace('Y','')

            studySlug = re.sub( r'[/\\]', '', '_'.join([ series['StudyDate'], institutionName, series['PatientID'], series['AccessionNumber'], series['StudyDescription'] ]).replace(' ','_') )
            seriesSlug = re.sub( r'[/\\]', '', '_'.join([ series['SeriesDescription'], str(seriesId) ]).replace(' ','_') )
            byAgeAlias = os.path.join( self.settings.byAgeDir, age, studySlug, seriesSlug )
            if os.path.exists( byAgeAlias ):
                self.rm_alias( byAgeAlias )

            # delete series alias in 'by_patient' tree
            studySlug = re.sub( r'[/\\]', '', '_'.join([ series['StudyDate'], series['PatientAge'], series['AccessionNumber'], series['StudyDescription'] ]).replace(' ','_') )
            byPatientAlias = os.path.join( self.settings.byPatientDir, institutionName, series['PatientID'], studySlug, seriesSlug )
            if os.path.exists( byPatientAlias ):
                self.rm_alias( byPatientAlias )


            # find series dicom directory
            seriesDir = os.path.join( self.settings.dicomsDir, institutionName, series['PatientID'], studySlug, seriesSlug )

            if not os.path.exists( seriesDir ):
                print "Recorded series directory not found: %s" % seriesDir
            else:
                # check that the given series belongs only to the current instance's project
                with self.dbCon:
                    dbCur = self.dbCon.cursor()
                    dbCur.execute( "SELECT count(DISTINCT Project) FROM %s WHERE SeriesId = ?" % self.settings.dbTblProjectSeries, (seriesId,) )
                    if dbCur.fetchone()[0] == 1:
                
                        # delete series dicoms directory
                        shutil.rmtree( seriesDir )

                        # delete series from SQLite database
                        with self.dbCon:
                            dbCur = self.dbCon.cursor()
                            dbCur.execute( "DELETE FROM %s WHERE Project=? AND SeriesId=?" % self.settings.dbTblSeriesNotes, (self.settings.projectName, seriesId) )
                            dbCur.execute( "DELETE FROM %s WHERE Project=? AND SeriesId=?" % self.settings.dbTblProjectSeries, (self.settings.projectName, seriesId) )
                            dbCur.execute( "DELETE FROM %s WHERE id=?" % self.settings.dbTblSeries, (seriesId,) )


    
    #--------------------------------------------------------------------------------------------
    def delete_series(self, seriesIds):
        
        # check for series IDs list
        if not isinstance( seriesIds, list ):
            print "Error! Must provide a list of series IDs"
            return
        
        # check that series IDs list is not empty
        numIds = len( seriesIds )
        if numIds == 0:
            print "No series IDs provided!"
            return
        
        # loop through list of series ids
        deleteProgress = 0
        deleteProgressNew = 0
        for sIdx, seriesId in enumerate( seriesIds ):
            
            # delete series
            self.delete_a_series( seriesId )

            # display progress
            deleteProgressNew = ((sIdx * 100) / numIds)
            if deleteProgress != deleteProgressNew:
                deleteProgress = deleteProgressNew
                sys.stdout.write( " Deleting %d series: %d%% \r" % (numIds, deleteProgress) )
                sys.stdout.flush()
        
        sys.stdout.write( "                                            \r" )
        sys.stdout.flush()



    #--------------------------------------------------------------------------------------------
    def delete_study(self, accessionNumber):
    
        # verify accession number is associated with a single study in the DicomManager
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( ("SELECT count(*) FROM ( "
                            "SELECT DISTINCT "
                                "StudyInstanceUID, "
                                "InstitutionName, "
                                "StudyDate, "
                                "PatientID, "
                                "AccessionNumber, "
                                "StudyDescription "
                            "FROM %s WHERE AccessionNumber=?"
                            ")") % self.settings.dbTblSeries, (accessionNumber,) )
            qResult = dbCur.fetchone()
            if qResult is None:
                print "Accession number not found!: %d" % accessionNumber
                return
            elif qResult[0] != 1:
                print "Accession number not associate with a unique study!: %d" % accessionNumber
                return
    
        # get a list of the series IDs associated with the study
        seriesIds = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT id FROM %s WHERE AccessionNumber=?" % self.settings.dbTblSeries, (accessionNumber,) )
            qResult = dbCur.fetchall()
            if qResult is None:
                print "Error: Couldn't find series IDs!"
                return
            else:
                seriesIds = [row[0] for row in qResult]

        # get study info from a one series in the study
        repSeries = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( ("SELECT DISTINCT "
                                "InstitutionName, "
                                "StudyDate, "
                                "PatientID, "
                                "PatientAge, "
                                "AccessionNumber, "
                                "StudyDescription "
                            "FROM %s WHERE AccessionNumber=? "
                            "LIMIT 1") % self.settings.dbTblSeries, (accessionNumber,) )
            repSeries = dbCur.fetchone()
            if qResult is None:
                print "Error: Couldn't get study info!"
                return
                    
        # delete all series associated with the study
        self.delete_series( seriesIds )

        # normalize institution name
        institutionName = self.normalize_institution_name( series['InstitutionName'] )

        # delete study folder in 'by_age' tree
        age = repSeries['PatientAge']
        if 'D' in age:
            age = 'day_%s' % age.strip().replace('D','')
        elif 'W' in age:
            age = 'week_%s' % age.strip().replace('W','')
        elif 'M' in age:
            age = 'month_%s' % age.strip().replace('M','')
        elif 'Y' in age:
            age = 'year_%s' % age.strip().replace('Y','')

        studySlug = re.sub( r'[/\\]', '', '_'.join([ repSeries['StudyDate'], institutionName, repSeries['PatientID'], repSeries['AccessionNumber'], repSeries['StudyDescription'] ]).replace(' ','_') )
        byAgeStudyDir = os.path.join( self.settings.byAgeDir, age, studySlug )
        if os.path.exists( byAgeStudyDir ):
            os.rmdir( byAgeStudyDir )
    
        # delete study folder in 'by_patient' tree
        studySlug = re.sub( r'[/\\]', '', '_'.join([ repSeries['StudyDate'], repSeries['PatientAge'], repSeries['AccessionNumber'], repSeries['StudyDescription'] ]).replace(' ','_') )
        byPatientStudyDir = os.path.join( self.settings.byPatientDir, institutionName, repSeries['PatientID'], studySlug )
        if os.path.exists( byPatientStudyDir ):
            os.rmdir( byPatientStudyDir )
                
        # find study directory in 'dicoms' tree
        institutionDir = os.path.join( self.settings.dicomsDir, institutionName )
        patientDir = os.path.join( institutionDir, repSeries['PatientID'] )
        studyDir = os.path.join( patientDir, studySlug )
        if not os.path.exists( studyDir ):
            print "Error: Study directory could not be found: %s" % studyDir
            return

        # delete study directory if empty
        if os.listdir( studyDir ) == []:
            os.rmdir( studyDir )
        else:
            print "Can't delete Study directory from 'dicoms' tree! It's not empty. It may be owned byanother project."
            return

        # delete patient directory if empty
        if os.listdir( patientDir ) == []:
            os.rmdir( patientDir )
    
        # delete institution directory if empty
        if os.listdir( institutionDir ) == []:
            os.rmdir( institutionDir )



    #--------------------------------------------------------------------------------------------
    def delete_patient(self, institution, patientId):
                
        # verify institution and patient id is unique in the DicomManager
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( ("SELECT count(*) FROM ( "
                                "SELECT DISTINCT "
                                "InstitutionName, "
                                "PatientID "
                                "FROM %s "
                                "WHERE InstitutionName=? AND PatientID=?"
                            ")") % self.settings.dbTblSeries, (institution, patientId) )
            qResult = dbCur.fetchone()
            if qResult is None:
                print "Institution/PatientID combination not found!: %s / %d" % (institution, patientId)
                return
            elif qResult[0] != 1:
                print "Institution/PatientID combination not a unique identifier!: %s / %d" % (institution, patientId)
                return
                
        # get a list of the studies associated with the patient
        accessionNumbers = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT DISTINCT AccessionNumber FROM %s WHERE InstitutionName=? AND PatientID=?" % self.settings.dbTblSeries, (institution, patientId) )
            qResult = dbCur.fetchall()
            if qResult is None:
                print "Error: Couldn't find studies' accession numbers!"
                return
            else:
                accessionNumbers = [row[0] for row in qResult]

        numANs = len( accessionNumbers )
        if numANs == 0:
            print "No series IDs provided!"
            return
                
        # loop through list of accession numbers
        print "Deleting %d studies..." % numANs
        deleteProgress = 0
        deleteProgressNew = 0
        for aIdx, accessionNumber in enumerate( accessionNumbers ):
            
            # delete study
            print " Deleting study %s..." % accessionNumber
            self.delete_study( accessionNumber )
        
        print "Done!"

            
                
    #--------------------------------------------------------------------------------------------
    def series_subset(self, seriesIds):

        # check that at least 1 series ID was provided
        numSeries = len( seriesIds )
        if numSeries < 1:
            print "Must provide a non-empty list of series IDs!"
            return
        
        # enforce uniqueness of series IDs
        seriesIds = list(set(seriesIds))
        
        # check if series exist in this project
        series = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT * FROM %s WHERE id IN ( %s )" % ( self.settings.dbTblSeries, ', '.join([ '?' for i in range(numSeries) ]) ), seriesIds )
            series = dbCur.fetchall()
            if series is None or len(series) == 0:
                print "Error: Couldn't find any series!"
                return



    #--------------------------------------------------------------------------------------------
    def add_wanted_studies(self, accessionNumbers, note):

        # check that at least 1 study accession number was provided
        numANs = len( accessionNumbers )
        if numANs == 0:
            print "No accession numbers provided!"
            return

        # loop through list of accession numbers
        numAddedANs = 0
        numRepeatANs = 0
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            for aIdx, accessionNumber in enumerate( accessionNumbers ):

                # check if accession number is already in table
                dbCur.execute( "SELECT count(*) FROM %s WHERE Project = ? AND AccessionNumber = ?" % self.settings.dbTblWantedStudies, ( self.settings.projectName, accessionNumber ) )
                if dbCur.fetchone()[0] > 0:
                    numRepeatANs += 1
                else:
                    # add accession number to table
                    dbCur.execute( "INSERT INTO %s ( Project, AccessionNumber, Note ) VALUES ( ?, ?, ? )" % self.settings.dbTblWantedStudies, ( self.settings.projectName, accessionNumber, note ) )
                    numAddedANs += 1

        if numRepeatANs > 0:
            print "%d accession number submited, %d already present, %d added" % ( numRepeatANs + numAddedANs, numRepeatANs, numAddedANs )


            
    #--------------------------------------------------------------------------------------------
    def print_wanted_studies(self):
        
        # get a list of accession numbers in WantedStudies table
        accessionNumbers = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT AccessionNumber FROM %s WHERE Project = ?" % self.settings.dbTblWantedStudies, (self.settings.projectName,) )
            qResult = dbCur.fetchall()
            if qResult is None:
                print "Error: Couldn't find any accession numbers!"
                return
            else:
                accessionNumbers = [row[0] for row in qResult]
        
        # print accession numbers
        print "The project '%s' has %d WANTED studies. Accession numbers:" % ( self.settings.projectName, len(accessionNumbers) )
        for accessionNumber in accessionNumbers:
            print "%s" % accessionNumber



    #--------------------------------------------------------------------------------------------
    def print_studies_to_get(self):
        
        # get a list of accession numbers in WantedStudies table that have not been imported
        accessionNumbers = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT AccessionNumber FROM %s WHERE Project = ? AND AccessionNumber NOT IN ( "
                                "SELECT DISTINCT AccessionNumber FROM %s WHERE id IN ( "
                                    "SELECT SeriesId FROM %s WHERE Project = ? "
                                ")"
                            ")" % ( self.settings.dbTblWantedStudies, self.settings.dbTblSeries, self.settings.dbTblProjectSeries ), ( self.settings.projectName, self.settings.projectName ) )
            qResult = dbCur.fetchall()
            if qResult is None:
                print "Error: Couldn't find any accession numbers!"
                return
            else:
                accessionNumbers = [row[0] for row in qResult]
        
        # print accession numbers
        print "The project '%s' still has %d studies to get. Accession numbers:" % ( self.settings.projectName, len(accessionNumbers) )
        for accessionNumber in accessionNumbers:
            print "%s" % accessionNumber



    #--------------------------------------------------------------------------------------------
    def add_series_notes(self, seriesIds, note):
            
        # check for series IDs list
        if not isinstance( seriesIds, list ):
            print "Error! Must provide a list of series IDs"
            return
        
        # check that series IDs list is not empty
        numIds = len( seriesIds )
        if numIds == 0:
            print "No series IDs provided!"
            return
        
        # loop through list of series ids
        for seriesId in seriesIds:
        
            # check that series is owned by this project
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute( "SELECT count(*) FROM %s WHERE Project = ? AND SeriesId = ?" % self.settings.dbTblProjectSeries, ( self.settings.projectName, seriesId ) )
                if dbCur.fetchone()[0] == 0:
                    print "The series with id %d is not found in the project %s!" % ( seriesId, self.settings.projectName )
                else:
                    # record note
                    dbCur.execute( "INSERT INTO %s ( Project, SeriesId, Note ) VALUES ( ?, ?, ? )" % self.settings.dbTblSeriesNotes, ( self.settings.projectName, seriesId, note ) )

            
            
    #--------------------------------------------------------------------------------------------
    def delete_series_notes(self, noteIds):
            
        # check for series IDs list
        if not isinstance( noteIds, list ):
            print "Error! Must provide a list of series IDs"
            return
        
        # check that at least 1 series ID was provided
        numIds = len( noteIds )
        if numIds == 0:
            print "No series IDs provided!"
            return
        
        # loop through list of series ids
        for noteId in noteIds:

            # check that series is owned by this project
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute( "SELECT count(*) FROM %s WHERE id = ? AND Project = ?" % self.settings.dbTblSeriesNotes, ( noteId, self.settings.projectName ) )
                if dbCur.fetchone()[0] == 0:
                    print "The series note with id %d is not found in the project %s!" % ( noteId, self.settings.projectName )
                else:
                    # delete note
                    dbCur.execute( "DELETE FROM %s WHERE id = ?" % self.settings.dbTblSeriesNotes, (noteId,) )


                    
    #--------------------------------------------------------------------------------------------
    def remove_non_ascii(self, s):

        # strip non-unicode characters
        return "".join(i for i in s if ord(i)<128)

    

    #--------------------------------------------------------------------------------------------
    def mk_alias(self, dst, alias):
        
        # check dst existence
        if not os.path.exists( dst ):
            print "Destination does not exist: '%s'" % dst
            return
        
        # create subprocess command
        cmd = 'ln -s %s %s' % ( dst, alias )
        cmd = cmd.replace('!','\!')
        cmd = cmd.replace('#','\#')
        cmd = cmd.replace('$','\$')
        cmd = cmd.replace('%','\%')
        cmd = cmd.replace('&','\&')
        cmd = cmd.replace('*','\*')
        cmd = cmd.replace('(','\(')
        cmd = cmd.replace(')','\)')
        cmd = cmd.replace('<','\<')
        cmd = cmd.replace('>','\>')
        cmd = cmd.replace(':','\:')
        cmd = cmd.replace('{','\{')
        cmd = cmd.replace('}','\}')
        cmd = cmd.replace('[','\[')
        cmd = cmd.replace(']','\]')
        cmd = cmd.replace('=','\=')
        os.system(cmd)
    
    
    
    #--------------------------------------------------------------------------------------------
    def rm_alias(self, alias):
        
        # create subprocess command
        cmd = 'rm %s' % alias
        cmd = cmd.replace('!','\!')
        cmd = cmd.replace('#','\#')
        cmd = cmd.replace('$','\$')
        cmd = cmd.replace('%','\%')
        cmd = cmd.replace('&','\&')
        cmd = cmd.replace('*','\*')
        cmd = cmd.replace('(','\(')
        cmd = cmd.replace(')','\)')
        cmd = cmd.replace('<','\<')
        cmd = cmd.replace('>','\>')
        cmd = cmd.replace(':','\:')
        cmd = cmd.replace('{','\{')
        cmd = cmd.replace('}','\}')
        cmd = cmd.replace('[','\[')
        cmd = cmd.replace(']','\]')
        cmd = cmd.replace('=','\=')
        os.system(cmd)



    #--------------------------------------------------------------------------------------------
    def rm_empty_dirs(rootDir):
        empty = True
        
        # loop through directory listing
        for listing in os.listdir( rootDir ):
            path = os.path.join( rootDir, listing )
            
            # check that listing is not a directory
            if not os.path.isdir( path ):
                # mark as not empty
                empty = False
            else:
                # recursively check subdirectories
                if not del_empty_dirs( path ):
                    empty = False

        if empty:
            # delete rootDir
            print('Empty directory! Deleteing: %s' % rootDir)
            os.rmdir(rootDir)
        
        return empty



'''





    
    
'''











