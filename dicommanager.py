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
from dicom.dataset import Dataset, FileDataset
import dicom.UID

# get settings
import dicommanagersettings as settings



class DicomManager:
    
    #--------------------------------------------------------------------------------------------
    # instantiation
    def __init__ ( self, init=True ):

        if init:
            self.settings = settings.DicomManagerSettings()
            self.init()

    
    #--------------------------------------------------------------------------------------------
    # sets up and verifies necessary resources
    def init ( self ):
        
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

        # check if the series' notes database table exists
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.settings.dbTblSeriesNotes )
            qResult = dbCur.fetchone()
        
        if qResult is None:
            # projects table doesn't exist - create table in database
            print "Database table '%s' not found. Creating it..." % self.settings.dbTblSeriesNotes
            qCreate = ("CREATE TABLE %s ( id INTEGER PRIMARY KEY, SeriesInstanceUID INTEGER, Note TEXT ); "
                       "CREATE INDEX SeriesInstanceUidIdx ON %s (SeriesInstanceUID); "
                       ) % ( self.settings.dbTblSeriesNotes, self.settings.dbTblSeriesNotes )
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.executescript(qCreate)
    
        # check root directory's existence
        if not os.path.exists(self.settings.rootDir):
            print "Root directory not found. You must create this!"
            return

        # check for dicom directory
        if not os.path.exists(self.settings.dicomDir):
            print "DICOM storage directory not found. Creating it..."
            os.makedirs(self.settings.dicomDir)



    #--------------------------------------------------------------------------------------------
    # finds file paths to DICOM files under the given directory
    def find ( self, dir, recursive=True ):
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
    # reads a given DICOM file to create a modified pydicom object
    def read ( self, dcmPath ):
        
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
        dcm = self.sanitizeDicom(dcm)

        # save DICOM source path
        dcm.path = dcmPath

        # add record ID
        dcm.recordID = None

        return dcm



    #--------------------------------------------------------------------------------------------
    # removes non-ascii characters from a pydicom object's header data
    def sanitizeDicom ( self, dcm ):

        # loop through DICOM tags we intend to record
        for dcmHeaderTag in self.settings.tagsToRecord:

            # check if tag is present
            if dcmHeaderTag in dcm:

                # enforce single ascii string
                dcm[dcmHeaderTag].value = "".join(i for i in ( str(dcm[dcmHeaderTag].value) ) if ord(i)<128)
                
        return dcm



    #--------------------------------------------------------------------------------------------
    # computes the storage path or directory for DICOM file based on its tags (i.e institution, demographics, etc.)
    def storagePath ( self, dcm, directory=False):
        os_path_join = os.path.join

        # Checks if DICOM has values in each of the following tags. For certain tags, values are required so 'none' is returned. 
        if 0x00181000 in dcm:
            modality = dcm.Modality.replace('/','')
        else:
            modality = 'UnknownModality'

        if 0x00080080 in dcm:
            institutionName = dcm.InstitutionName.replace('/','')
        else:
            institutionName = 'UnknownInstitution'
        
        if 0x00080070 in dcm:
            manufacturer = dcm.Manufacturer.replace('/','')
        else:
            manufacturer = 'UnknownManufacturer'

        if 0x00081090 in dcm:
            model = dcm.ManufacturersModelName.replace('/','')
        else:
            model = 'UnknownModelName'
        
        if 0x00181000 in dcm:
            deviceSerialNumber = dcm.DeviceSerialNumber.replace('/','')
        else:
            deviceSerialNumber = 'UnknownSerialNumber'
        
        if 0x00100020 in dcm:
            patientId = dcm.PatientID.replace('/','')
        else:
            print "DICOM doesn't have PatientID. Can't generate storage path for file: %s" % dcm.path
            return None
        
        if 0x00100010 in dcm:
            patientName = dcm.PatientName.replace('/','')
        else:
            patientName = 'UnknownPatientName'
        
        if 0x00100040 in dcm:
            patientSex = dcm.PatientSex.replace('/','')
        else:
            patientSex = 'UnknownSex'
        
        if 0x00101010 in dcm:
            patientAge = dcm.PatientAge.replace('/','')
        else:
            patientAge = 'UnknownAge'
        
        if 0x00080020 in dcm:
            studyDate = dcm.StudyDate.replace('/','')
        else:
            studyDate = 'UnknownDate'
        
        if 0x00080050 in dcm:
            accessionNumber = dcm.AccessionNumber.replace('/','')
        else:
            print "DICOM doesn't have AccessionNumber. Can't generate storage path for file: %s" % dcm.path
            return None
        
        if 0x00081030 in dcm:
            studyDescription = dcm.StudyDescription.replace('/','')
        else:
            studyDescription = 'UnknownDescription'
        
        if 0x0020000e in dcm:
            seriesUID = dcm.SeriesInstanceUID.replace('/','')
        else:
            print "DICOM doesn't have SeriesInstanceUID. Can't generate storage path for file: %s" % dcm.path
            return None
        
        if 0x00181030 in dcm:
            seriesProtocol = dcm.ProtocolName.replace('/','')
        else:
            seriesProtocol = 'UnknownProtocol'
        
        if 0x0008103e in dcm:
            seriesDescription = dcm.SeriesDescription.replace('/','')
        else:
            seriesDescription = 'UnknownDescription'
        
        # Create names for level of the file tree hierarchy (i.e ..., study, series, image)
        scannerSlug = '_'.join([ manufacturer, model, deviceSerialNumber ]).replace(' ','_')
        patientSlug = '_'.join([ patientId, patientName, patientSex ]).replace(' ','_')
        studySlug = '_'.join([ studyDate, patientAge, accessionNumber, studyDescription ]).replace(' ','_')
        seriesSlug = '_'.join([ seriesDescription, seriesProtocol, seriesUID ]).replace(' ','_')

        # Creates path beginning with default starting point
        modaliltyDir = os_path_join( self.settings.dicomDir, modality.lower() )
        institutionDir = os_path_join( modaliltyDir, institutionName.lower() )
        scannerDir = os_path_join( institutionDir, scannerSlug.lower() )
        patientDir = os_path_join( scannerDir, patientSlug.lower() )
        studyDir = os_path_join( patientDir, studySlug.lower() )
        seriesDir = os_path_join( studyDir, seriesSlug.lower() )

        # option - return storage directory
        if directory:

            # sanitize path for unix-based systems
            return self.sanitizeStoragePath(seriesDir)

        # option - return storage path
        else:

            # check for SOP Instance UID
            if 0x00080018 in dcm:
                imageUID = dcm.SOPInstanceUID.replace('/','')
            else:
                print "DICOM doesn't have SOPInstanceUID. Can't generate storage path for file: %s" % dcm.path
                return None
            
            # create path
            dcmPath = os_path_join( seriesDir, '%s.dcm' % imageUID.lower() )

            # sanitize path for unix-based systems
            return self.sanitizeStoragePath(dcmPath)



    #--------------------------------------------------------------------------------------------
    # removes all special charachters in a path string
    def sanitizeStoragePath ( self, path ):
             
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
    # records DICOM series header data into an SQLite database
    def record ( self, dcm ):
        recordID = None
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
                # search for series in database
                qCheck = "SELECT id, SeriesInstanceUID FROM %s WHERE SeriesInstanceUID = ? LIMIT 1" % self.settings.dbTblSeries
                dbCur.execute( qCheck, (dcm.SeriesInstanceUID,) )
                qResult = dbCur.fetchone()

                # if series not in database
                if qResult is None:
                    # record series header data in database
                    qInsertSeries = "INSERT INTO %s ( %s ) VALUES ( %s )" % ( self.settings.dbTblSeries, ', '.join(cols), ', '.join([ '?' for i in xrange(len(vals)) ]) )
                    qSeriesLastInsertId = "SELECT last_insert_rowid()"
                    dbCur.execute( qInsertSeries, vals)
                    dbCur.execute( qSeriesLastInsertId )
                    qResult = dbCur.fetchone()

                recordID = str( qResult[0] )

            # catch
            except Exception, e:
                print repr(e)
                print "DICOM could not be recorded: %s" % dcm.path
                return None
        
        return recordID
        


    #--------------------------------------------------------------------------------------------
    # copies a DICOM file into a human-readable filetree
    def store ( self, dcm ):
        dcmPath = dcm.path

        # check that the dicom exists
        if not os.path.isfile(dcmPath):
            print "Dicom not found: %s" % dcmPath
            return None

        # determine where to store the DICOM
        storeDst = self.storagePath(dcm)
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

            # increment NumberOfDicoms field in database
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute( "UPDATE %s SET NumberOfDicoms = NumberOfDicoms + 1 WHERE SeriesInstanceUID = '%s'" % ( self.settings.dbTblSeries, dcm.SeriesInstanceUID ) )

        # return storage destination
        return storeDst



    #--------------------------------------------------------------------------------------------
    # convenience function to read, record, store, and delete DICOM files
    def manage ( self, dcmPaths, deleteDcm=False, recordDcm=True, storeDcm=True ):
    
        # check if multiple DICOM paths are provided
        if isinstance(dcmPaths, list):

            numPaths = len( dcmPaths )
            progress = 0
            for dcmIdx, dcmPath in enumerate( dcmPaths ):

                # recursive call to manage each DICOM
                self.manage(dcmPath, deleteDcm, recordDcm, storeDcm)

                # display progress
                progress = ((dcmIdx * 100) / numPaths)
                sys.stdout.write( " Progress: %d%% \r" % progress )
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
                recordID = self.record(dcm)
                if recordID == None:
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
    # creates a pydicom object containing the database record of a DICOM series
    def getSeriesRecord ( self, recordID=None, seriesUID=None, accessionNumber=None, patientID=None ):
        whereClause = None
        queryArg = None

        # set SQL where clause to search database
        if recordID is not None:
            whereClause = " WHERE id = ? "
            queryArg = recordID

        elif seriesUID is not None:
            whereClause = " WHERE SeriesInstanceUID = ? "
            queryArg = seriesUID

        elif accessionNumber is not None:
            whereClause = " WHERE AccessionNumber = ? "
            queryArg = accessionNumber

        elif patientID is not None:
            whereClause = " WHERE PatientID = ? "
            queryArg = patientID

        else:
            return None

        # get series record from database
        qFind = "SELECT * FROM %s %s LIMIT 1" % (self.settings.dbTblSeries, whereClause)
        series = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( qFind, (queryArg,) )
            series = dbCur.fetchone()

        # check record exists
        if series is None:
            print "Can't get series record with given arg: %s" % str(queryArg)
            return None

        # create new DICOM object
        dcm = FileDataset(None,{},None)

        # fill object from record
        for dcmHeaderTag in self.settings.tagsToRecord:
            tagName = DicomDictionary[dcmHeaderTag][4]
            if series[tagName]:
                setattr( dcm, tagName, series[tagName] )

        # add record ID
        dcm.recordID = series['id']

        return dcm



    #--------------------------------------------------------------------------------------------
    # conveniece function to compute the storage directory of a recorded DICOM series
    def getSeriesDir ( self, recordID=None, seriesUID=None, accessionNumber=None, patientID=None ):

        # get DICOM object representation of series record
        dcm = self.getSeriesRecord(recordID, seriesUID, accessionNumber, patientID)
        if dcm == None:
            print "Can't generate series directory."
            return

        # compute storage directory path for this series
        seriesDir = self.storagePath(dcm, directory=True)

        return seriesDir



    #--------------------------------------------------------------------------------------------
    # copies managed DICOM files to a given location with optional formatting
    def export(self, recordIDs, dstRoot, ageBreakdown=False, directoryTree=True, readableSeriesSlug=True):

        # check if multiple series record IDs were provided
        if isinstance(recordIDs, list):
            numRecords = len( recordIDs )
            progress = 0

            # loop through series IDs
            for idx, recordID in enumerate( recordIDs ):

                # recursive call to manage each DICOM
                self.export(recordID, dstRoot, ageBreakdown, directoryTree, readableSeriesSlug)

                # display progress
                progress = ((idx * 100) / numRecords)
                sys.stdout.write( " Progress: %d%% \r" % progress )
                sys.stdout.flush()

            # progress
            sys.stdout.write( "                         \r" )
            sys.stdout.flush()

        # check for single series record ID
        elif isinstance(recordIDs, int):
            recordID = recordIDs

            # make functions local variables for speed
            os_path_exists = os.path.exists
            os_path_join = os.path.join
            
            # find series record in SQLite database
            dcm = self.getSeriesRecord(recordID)
            if dcm is None:
                # series not found in database
                print "Series record with id %d not found!" % recordID
                return
                        
            # determine source-series directory
            srcSeriesDir = self.storagePath(dcm, directory=True)
            
            # check that source-series directory exists
            if not os_path_exists( srcSeriesDir ):
                print "Source series directory not found: %s" % srcSeriesDir
                return
            
            # check that destination-root directory exists
            if not os_path_exists( dstRoot ):
                print "Destination root directory not found: %s" % dstRoot
                return

            # option: do/don't breakdown exported DICOMs by age
            if ageBreakdown:

                # determine patient age in days at scan time
                ageInDays = None
                with self.dbCon:
                    dbCur = self.dbCon.cursor()
                    qAge = "SELECT julianday(substr(StudyDate, 1,4) || '-' || substr(StudyDate,5,2)  || '-' || substr(StudyDate, 7,2)) - julianday(substr(PatientBirthDate, 1,4) || '-' || substr(PatientBirthDate,5,2)  || '-' || substr(PatientBirthDate, 7,2)) FROM %s WHERE id = ? LIMIT 1" % self.settings.dbTblSeries
                    dbCur.execute( qAge, (recordID,) )
                    ageInDays = dbCur.fetchone()[0]
            
                # modify destination root directory accordingly
                for ageRange in self.settings.ageBreakdown:
                    # determine age range
                    if ageInDays >= ageRange['minDay'] and ageInDays <= ageRange['maxDay']:
                        dstRoot = os_path_join(dstRoot, ageRange['name'])

            # option: do/don't replicate storage file-tree for exported DICOMs
            if directoryTree:
                # create destination path
                dstSeriesDir = srcSeriesDir.replace( self.settings.dicomDir, dstRoot )

            else:
                # create destination path
                seriesSlug = os.path.basename(srcSeriesDir)
                dstSeriesDir = os_path_join( dstRoot, seriesSlug )

            # option: do/don't keep human readable series slug
            if not readableSeriesSlug:

                # alter destination path
                dstSeriesDir = os_path_join( os.path.dirname(dstSeriesDir), dcm.SeriesInstanceUID )

            # check that series destination doesn't exist yet
            if os_path_exists( dstSeriesDir ):
                print "Destination series directory already exists, skipping: %s" % dstSeriesDir
                return
        
            # copy source to destination
            shutil.copytree( srcSeriesDir, dstSeriesDir )



    #--------------------------------------------------------------------------------------------
    # deletes managed DICOM files
    def delete(self, recordIDs):

        # check if multiple series record IDs were provided
        if isinstance(recordIDs, list):
            numRecords = len( recordIDs )
            progress = 0

            # loop through series IDs
            for idx, recordID in enumerate( recordIDs ):

                # recursive call to manage each DICOM
                self.delete(recordID)

                # display progress
                progress = ((idx * 100) / numRecords)
                sys.stdout.write( " Progress: %d%% \r" % progress )
                sys.stdout.flush()

            # progress
            sys.stdout.write( "                         \r" )
            sys.stdout.flush()

        # check for single series record ID
        elif isinstance(recordIDs, int):
            recordID = recordIDs

            # find storage directory
            seriesDir = self.getSeriesDir(recordID=recordID)
            if seriesDir == None:
                # series storage directory not found
                print "Can't delete series with id %d." % recordID

            else:
                # check that storage directory exists
                if not os.path.exists( seriesDir ):
                    print "Can't delete DICOMs. Series directory not found: %s" % seriesDir

                else:
                    # delete series directory
                    shutil.rmtree( seriesDir )                    

            # delete series record from database
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                #dbCur.execute( "DELETE FROM %s WHERE SeriesInstanceUID=?" % self.settings.dbTblSeriesNotes, (recordID,) )
                dbCur.execute( "DELETE FROM %s WHERE id=?" % self.settings.dbTblSeries, (recordID,) )


    
    #--------------------------------------------------------------------------------------------
    # records notes about DICOM series
    def note(self, seriesInstanceUIDs, note):
            
        # check for series IDs list
        if not isinstance( seriesInstanceUIDs, list ):
            print "Error! Must provide a list of series IDs"
            return
        
        # check that series IDs list is not empty
        numIds = len( seriesInstanceUIDs )
        if numIds == 0:
            print "No series IDs provided!"
            return
        
        # loop through list of series ids
        for seriesInstanceUID in seriesInstanceUIDs:
        
            # check that series is owned by this project
            with self.dbCon:
                dbCur = self.dbCon.cursor()

                # record note
                dbCur.execute( "INSERT INTO %s ( SeriesInstanceUID, Note ) VALUES ( ?, ? )" % self.settings.dbTblSeriesNotes, (seriesInstanceUID, note) )

            
            
    #--------------------------------------------------------------------------------------------
    # deletes DICOM series notes
    def deleteNotes(self, noteIds):
            
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

                # delete note
                dbCur.execute( "DELETE FROM %s WHERE id = ?" % self.settings.dbTblSeriesNotes, (noteId,) )


                    