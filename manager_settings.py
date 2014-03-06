# manager_settings.py
#


# add working directory to search path
import os
import sys


class ManagerSettings:

    def __init__(self):

        # set the directory where to save the SQLite database used for management
        self.dbDir = os.path.dirname(os.path.realpath(__file__))
        if not self.dbDir:
            self.dbDir = raw_input("Enter the path where sqlite database is to be saved: ").strip().replace('\\','')
        
        # set the path to this management SQLite database
        self.dbPath = os.path.join( self.dbDir, 'dicom_manager.sqlite' )
    
        # set name of database table in which the dicom series' data are saved
        self.dbTblSeries = 'Series'
                
        # set name of database table in which the project's series ownerships are saved
        self.dbTblProjectSeries = 'ProjectSeries'

        # set name of database table in which a project's desired dicom series' data are saved
        self.dbTblWantedStudies = 'WantedStudies'
    
        # set name of database table in which the series' notes are saved
        self.dbTblSeriesNotes = 'SeriesNotes'
    
        # set the root directory of where all dicom data are stored
        self.rootDir = '/Users/nathanielreynolds/Documents/Python/dicom_manager/testing'
        if not self.rootDir:
            self.rootDir = raw_input("Enter the root directory where dicoms are to be managed: ").strip().replace('\\','')
    
        # set the directory where dicoms to be imported should be
        self.toImportDir = os.path.join( self.rootDir, 'to_import' )
        if not self.toImportDir:
            self.toImportDir = raw_input("Enter the path where dicoms are to be imported from: ").strip().replace('\\','')
        
        # set the directory where the dicoms are acutally written
        self.dicomsDir = os.path.join( self.rootDir, 'dicoms' )
                
        # set the root directory where all projects' organized aliases will be
        self.projectsDir = os.path.join( self.rootDir, 'projects' )
                
        # set the name of the project to manage (used to find and create files)
        self.projectName = 'atlas'
        if not self.projectName:
            self.projectName = raw_input("Enter the name of the project you want to manage: ").strip()
                
        # set the directory for the selected project's organized data
        self.selectedProjectDir = os.path.join( self.projectsDir, self.projectName )
    
        # set the directory for the selected project's data organized by patient
        self.byPatientDir = os.path.join( self.selectedProjectDir, 'by_patient' )

        # set the directory for the selected project's data organized by age
        self.byAgeDir = os.path.join( self.selectedProjectDir, 'by_age' )

