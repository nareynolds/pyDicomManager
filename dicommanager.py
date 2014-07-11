# dicom_manager.py


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

# get settings
import dicommanagersettings as settings





class DicomManager:
    
    #--------------------------------------------------------------------------------------------
    def __init__(self, init=True):

        if init:
            self.settings = settings.DicomManagerSettings()
            self.init()

    
    #--------------------------------------------------------------------------------------------
    def init(self):
        
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
            dcmHeaderNames = [ DicomDictionary[dcmHeaderKey][4] for dcmHeaderKey in self.settings.tagsToRecord ]
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
    def find (self, dir, recursive=True):
        #Function takes in dir of dicom files
        dicoms=[]

        # make local refs for speed
        os_path_join = os.path.join
        os_path_isfile = os.path.isfile
        os_path_isdir = os.path.isdir

        # progress
        sys.stdout.write( " Searching...\r" )
        sys.stdout.flush()

        # loop through directory listings
        for listing in os.listdir(dir):

            # get full path of listing
            fullPath = os_path_join(dir, listing)

            # check if listing is a file
            if os_path_isfile(fullPath):

                # check if listing is DICOM
                if listing.endswith(('.dcm', '.dicom')):

                    # adds it to the dicoms list
                    dicoms.append(fullPath)

            # check if should search subdirectories
            if recursive:

                # check if listing is a directory
                if os_path_isdir(fullPath):

                    # recursive call to search subdirectory
                    dicoms.extend( self.find(fullPath, True) )

        # progress
        sys.stdout.write( "                   \r" )
        sys.stdout.flush()

        return dicoms
        


    #--------------------------------------------------------------------------------------------
    def read( self, dcmPath ):
        
        # check that the dicom exists
        if not os.path.isfile(dcmPath):
            print "Dicom not found: %s" % dcmPath
            return

        # read dicom file
        dcm = None
        try:
            dcm = dicom.read_file(dcmPath)
        except Exception, e:
            print repr(e)
            print "DICOM could not be read: %s" % dcmPath
            return None

        # check if DICOM has require tags
        if (0x00100020 not in dcm) or (not dcm.PatientID):
            print "DICOM doesn't have PatientID. Refusing to read: %s" % dcmPath
            return None

        if (0x00080050 not in dcm) or (not dcm.AccessionNumber):
            print "DICOM doesn't have AccessionNumber. Refusing to read: %s" % dcmPath
            return None

        if (0x0020000e not in dcm) or (not dcm.SeriesInstanceUID):
            print "DICOM doesn't have SeriesInstanceUID. Refusing to read: %s" % dcmPath
            return None

        if (0x00080018 not in dcm) or (not dcm.SOPInstanceUID):
            print "DICOM doesn't have SOPInstanceUID. Refusing to read: %s" % dcmPath
            return None

        # sanitize
        dcm = self.sanitize(dcm)

        # save DICOM source path
        dcm.path = dcmPath

        return dcm



    #--------------------------------------------------------------------------------------------
    def sanitize( self, dcm ):

        # loop through DICOM tags we intend to record
        for dcmHeaderTag in self.settings.tagsToRecord:

            # check if tag is present
            if dcmHeaderTag in dcm:

                # enforce single ascii string without quotes
                dcm[dcmHeaderTag].value = "".join(i for i in ( str(dcm[dcmHeaderTag].value) ) if ord(i)<128)
                
        return dcm



    #--------------------------------------------------------------------------------------------
    # Creates storage directory for DICOM file based on its tags (i.e institution, demographics, etc.)
    def storage_path( self, dcm ):

        os_path_join = os.path.join

        # Checks if DICOM has values in each of the following tags. For certain tags, values are required so 'none' is returned. 
        if 0x00181000 in dcm:
            modality = dcm.Modality.replace('/','')
        else:
            modality = 'Unknown'

        if 0x00080080 in dcm:
            institutionName = dcm.InstitutionName.replace('/','')
        else:
            institutionName = 'Unknown'
        
        if 0x00080070 in dcm:
            manufacturer = dcm.Manufacturer.replace('/','')
        else:
            manufacturer = 'Unknown'

        if 0x00081090 in dcm:
            model = dcm.ManufacturersModelName.replace('/','')
        else:
            model = 'Unknown'
        
        if 0x00181000 in dcm:
            deviceSerialNumber = dcm.DeviceSerialNumber.replace('/','')
        else:
            deviceSerialNumber = 'Unknown'
        
        if 0x00100020 in dcm:
            patientId = dcm.PatientID.replace('/','')
        else:
            print "DICOM doesn't have PatientID. Can't generate storage path: %s" % dcm.path
            return None
        
        if 0x00100010 in dcm:
            patientName = dcm.PatientName.replace('/','')
        else:
            patientName = 'Unknown'
        
        if 0x00100040 in dcm:
            patientSex = dcm.PatientSex.replace('/','')
        else:
            patientSex = 'Unknown'
        
        if 0x00101010 in dcm:
            patientAge = dcm.PatientAge.replace('/','')
        else:
            patientAge = 'Unknown'
        
        if 0x00080020 in dcm:
            studyDate = dcm.StudyDate.replace('/','')
        else:
            studyDate = 'Unknown'
        
        if 0x00080050 in dcm:
            accessionNumber = dcm.AccessionNumber.replace('/','')
        else:
            print "DICOM doesn't have AccessionNumber. Can't generate storage path: %s" % dcm.path
            return None
        
        if 0x00081030 in dcm:
            studyDescription = dcm.StudyDescription.replace('/','')
        else:
            studyDescription = 'Unknown'
        
        if 0x0020000e in dcm:
            seriesUID = dcm.SeriesInstanceUID.replace('/','')
        else:
            print "DICOM doesn't have SeriesInstanceUID. Can't generate storage path: %s" % dcm.path
            return None
        
        if 0x00181030 in dcm:
            seriesProtocol = dcm.ProtocolName.replace('/','')
        else:
            seriesProtocol = 'Unknown'
        
        if 0x0008103e in dcm:
            seriesDescription = dcm.SeriesDescription.replace('/','')
        else:
            seriesDescription = 'Unknown'
        
        if 0x00080018 in dcm:
            imageUID = dcm.SOPInstanceUID.replace('/','')
        else:
            print "DICOM doesn't have SOPInstanceUID. Can't generate storage path: %s" % dcm.path
            return None
        
        # Creates names for level of the file tree hierarchy (i.e ..., study, series, image)
        scannerSlug = '_'.join([ manufacturer, model, deviceSerialNumber ]).replace(' ','_')
        patientSlug = '_'.join([ patientId, patientName, patientSex ]).replace(' ','_')
        studySlug = '_'.join([ studyDate, patientAge, accessionNumber, studyDescription ]).replace(' ','_')
        seriesSlug = '_'.join([ seriesDescription, seriesProtocol, seriesUID ]).replace(' ','_')

        # Creates path beginning with default starting point
        modaliltyDir = os_path_join( self.settings.dicomsDir, modality.lower() )
        institutionDir = os_path_join( modaliltyDir, institutionName.lower() )
        scannerDir = os_path_join( institutionDir, scannerSlug.lower() )
        patientDir = os_path_join( scannerDir, patientSlug.lower() )
        studyDir = os_path_join( patientDir, studySlug.lower() )
        seriesDir = os_path_join( studyDir, seriesSlug.lower() )
        dcmPath = os_path_join( seriesDir, '%s.dcm' % imageUID.lower() )

        # sanitize path for unix-based systems
        dcmPath = self.sanitize_unix_path(dcmPath)

        return dcmPath



    #--------------------------------------------------------------------------------------------
    # Replace (sanitize) all special charachters in a path.
    def sanitize_unix_path( self, path ):
             
        path = path.replace('`','') \
                .replace('~','') \
                .replace('!','') \
                .replace('@','') \
                .replace('#','') \
                .replace('$','') \
                .replace('%','') \
                .replace('^','') \
                .replace('&','') \
                .replace('*','') \
                .replace('(','') \
                .replace(')','') \
                .replace('{','') \
                .replace('}','') \
                .replace('[','') \
                .replace(']','') \
                .replace('|','') \
                .replace('\\','') \
                .replace(':','') \
                .replace(';','') \
                .replace("'",'') \
                .replace('"','') \
                .replace('<','') \
                .replace('>','') \
                .replace(',','') \
                .replace('?','') \
                .replace(' ','_')
        return path



    #--------------------------------------------------------------------------------------------
    # Moves DICOM from original location to managed file tree.  
    def store( self, dcm ):
        dcmPath = dcm.path

        # check that the dicom exists
        if not os.path.isfile(dcmPath):
            print "Dicom not found: %s" % dcmPath
            return None

        # determine where to store the DICOM
        storeDst = self.storage_path(dcm)
        if storeDst == None:
            print "Couldn't store DICOM: %s" % dcmPath
            return None
        storeDir = os.path.dirname(storeDst)

        # check if directory exists
        if not os.path.isdir(storeDir):

            # create storage directory
            os.makedirs(storeDir)

        # check if file exists
        if not os.path.isfile(storeDst):
    
            # copy file to new destination
            try:
                shutil.copyfile(dcmPath, storeDst)
            except Exception, e:
                print repr(e)
                print "Failed to store DICOM: %s" % dcmPath
                return None

            # return storage destination
            return storeDst

        else:

            # return nothing
            return None




    #--------------------------------------------------------------------------------------------
    def record( self, dcm ):
        
        seriesId = None
        cols = []
        vals = []

        # collect column names and values for database entry
        for dcmHeaderTag in self.settings.tagsToRecord:
            if dcmHeaderTag in dcm:
                cols.append( DicomDictionary[dcmHeaderTag][4] )
                vals.append( dcm[dcmHeaderTag].value )

        # begin databse transaction
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            
            # try
            try:
                # check if this series is already recorded in database
                qCheck = "SELECT id, SeriesInstanceUID FROM %s WHERE SeriesInstanceUID = ? LIMIT 1" % self.settings.dbTblSeries
                dbCur.execute( qCheck, (dcm.SeriesInstanceUID,) )
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

            # catch
            except Exception, e:
                print repr(e)
                print "DICOM could not be recorded: %s" % dcm.path
                return None
        
        return seriesId
        


    #--------------------------------------------------------------------------------------------
    def manage( self, dcmPaths, deleteDcm=False, recordDcm=True, storeDcm=True ):
    
        # check if multiple DICOM paths are provided
        if isinstance(dcmPaths, list):

            numPaths = len( dcmPaths )
            writeProgress = 0
            for dcmIdx, dcmPath in enumerate( dcmPaths ):

                # recursive call to manage each DICOM
                self.manage(dcmPath, deleteDcm, recordDcm, storeDcm)

                # display progress
                writeProgress = ((dcmIdx * 100) / numPaths)
                sys.stdout.write( " Progress: %d%% \r" % writeProgress )
                sys.stdout.flush()

            # progress
            sys.stdout.write( "                         \r" )
            sys.stdout.flush()

        # check for single DICOM path
        elif isinstance(dcmPaths, basestring):
            dcmPath = dcmPaths

            # read DICOM
            dcm = self.read(dcmPath)
            if dcm == None:
                print "Couldn't read. Unable to manage DICOM: %s" % dcmPath
                return None

            if recordDcm:
                # record DICOM in DB
                seriesId = self.record(dcm)
                if seriesId == None:
                    print "Couldn't record. Unable to manage DICOM: %s" % dcmPath
                    return None

            if storeDcm:
                # store DICOM in managed file tree
                dstPath = self.store(dcm)
                if dstPath == None:
                    print "Couldn't store. Unable to manage DICOM: %s" % dcmPath
                    return None

            if deleteDcm:
                # delete source DICOM
                os.remove(dcmPath)
        
        












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
        institutionName = self.linux_path_sanitize( series['InstitutionName'] )
        patientId = self.linux_path_sanitize( series['PatientID'] )
        studyDate = self.linux_path_sanitize( series['StudyDate'] )
        patientAge = self.linux_path_sanitize( series['PatientAge'] )
        accessionNumber = self.linux_path_sanitize( series['AccessionNumber'] )
        studyDescription = self.linux_path_sanitize( series['StudyDescription'] )
        seriesDescription = self.linux_path_sanitize( series['SeriesDescription'] )
        studySlug = '_'.join([ studyDate, patientAge, accessionNumber, studyDescription ]).replace(' ','_')
        seriesSlug = '_'.join([ seriesDescription, str(seriesId) ]).replace(' ','_')
        srcSeriesDir = os.path.join( self.settings.dicomsDir, institutionName, patientId, studySlug, seriesSlug )
        
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
            patientDir = os_path_join( institutionDir, patientId )
            if not os_path_exists( patientDir ):
                print "| Patient directory '%s' being created..." % patientId
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
            
            # modify tags for path search
            institutionName = self.linux_path_sanitize( series['InstitutionName'] )
            patientId = self.linux_path_sanitize( series['PatientID'] )
            studyDate = self.linux_path_sanitize( series['StudyDate'] )
            patientAge = self.linux_path_sanitize( series['PatientAge'] )
            accessionNumber = self.linux_path_sanitize( series['AccessionNumber'] )
            studyDescription = self.linux_path_sanitize( series['StudyDescription'] )
            seriesDescription = self.linux_path_sanitize( series['SeriesDescription'] )

            # delete series alias in 'by_age' tree
            age = patientAge
            if 'D' in age:
                age = 'day_%s' % age.strip().replace('D','')
            elif 'W' in age:
                age = 'week_%s' % age.strip().replace('W','')
            elif 'M' in age:
                age = 'month_%s' % age.strip().replace('M','')
            elif 'Y' in age:
                age = 'year_%s' % age.strip().replace('Y','')

            studySlug = '_'.join([ studyDate, institutionName, patientId, accessionNumber, studyDescription ]).replace(' ','_')
            seriesSlug = '_'.join([ seriesDescription, str(seriesId) ]).replace(' ','_')
            byAgeAlias = os.path.join( self.settings.byAgeDir, age, studySlug, seriesSlug )
            if os.path.exists( byAgeAlias ):
                self.rm_alias( byAgeAlias )

            # delete series alias in 'by_patient' tree
            studySlug = '_'.join([ studyDate, patientAge, accessionNumber, studyDescription ]).replace(' ','_')
            byPatientAlias = os.path.join( self.settings.byPatientDir, institutionName, patientId, studySlug, seriesSlug )
            if os.path.exists( byPatientAlias ):
                self.rm_alias( byPatientAlias )


            # find series dicom directory
            seriesDir = os.path.join( self.settings.dicomsDir, institutionName, patientId, studySlug, seriesSlug )

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

        # modify tags for path search
        institutionName = self.linux_path_sanitize( repSeries['InstitutionName'] )
        patientId = self.linux_path_sanitize( repSeries['PatientID'] )
        studyDate = self.linux_path_sanitize( repSeries['StudyDate'] )
        patientAge = self.linux_path_sanitize( repSeries['PatientAge'] )
        accessionNumber = self.linux_path_sanitize( repSeries['AccessionNumber'] )
        studyDescription = self.linux_path_sanitize( repSeries['StudyDescription'] )
        seriesDescription = self.linux_path_sanitize( repSeries['SeriesDescription'] )


        # delete study folder in 'by_age' tree
        age = patientAge
        if 'D' in age:
            age = 'day_%s' % age.strip().replace('D','')
        elif 'W' in age:
            age = 'week_%s' % age.strip().replace('W','')
        elif 'M' in age:
            age = 'month_%s' % age.strip().replace('M','')
        elif 'Y' in age:
            age = 'year_%s' % age.strip().replace('Y','')

        studySlug = '_'.join([ studyDate, institutionName, patientId, accessionNumber, studyDescription ]).replace(' ','_')
        byAgeStudyDir = os.path.join( self.settings.byAgeDir, age, studySlug )
        if os.path.exists( byAgeStudyDir ):
            os.rmdir( byAgeStudyDir )
    
        # delete study folder in 'by_patient' tree
        studySlug = '_'.join([ studyDate, patientAge, accessionNumber, studyDescription ]).replace(' ','_')
        byPatientStudyDir = os.path.join( self.settings.byPatientDir, institutionName, patientId, studySlug )
        if os.path.exists( byPatientStudyDir ):
            os.rmdir( byPatientStudyDir )
                
        # find study directory in 'dicoms' tree
        institutionDir = os.path.join( self.settings.dicomsDir, institutionName )
        patientDir = os.path.join( institutionDir, patientId )
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



'''





    
    
'''











