# dicom_manager.py


# add working directory to search path
import os
import sys
sys.path.insert(0, os.path.realpath(__file__))

# get SQLite tools
import sqlite3

# get tools for reading dicoms
import dicom
from dicom._dicom_dict import DicomDictionary

# get dicommanager stuff
import dicommanager
import dicommanagersettings as settings



class DicomFeatures:
    
    #--------------------------------------------------------------------------------------------
    def __init__ ( self, dicomManager ):
        self.manager = dicomManager
        self.settings = dicomManager.settings
        self.dbCon = self.manager.dbCon

        # check if the dicom series database table exists
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.settings.dbTblSeries )
            qResult = dbCur.fetchone()

        if qResult is None:
            # series table doesn't exist - create table in database
            print "Database table '%s' not found. Can't compute features!" % self.settings.dbTblSeries
            return

        # check if the features database table exists
        qResult = None
        with self.dbCon:
            dbCur = self.dbCon.cursor()
            dbCur.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='Features'" )
            qResult = dbCur.fetchone()

        if qResult is None:
            # Features table doesn't exist - create table in database
            qCreate = '''
            CREATE TABLE Features ( 
                id INTEGER PRIMARY KEY,
                NumberOfDicoms INTEGER DEFAULT 0 NOT NULL,
                SeriesDescription TEXT,
                StudyDescription TEXT,
                Manufacturer TEXT, 
                ManufacturerModelName TEXT,
                InstitutionName TEXT,
                PatientSex TEXT,
                PatientAge,
                SliceThickness,
                SpacingBetweenSlices,
                MagneticFieldStrength,
                ProtocolName TEXT
                )
            '''
            with self.dbCon:
                dbCur = self.dbCon.cursor()
                dbCur.execute(qCreate)

        else:
            print "Features table already exists."



        # create features table

        # loop through series

            #  
