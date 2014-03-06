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
        self.projectName = 'MyProject'
        if not self.projectName:
            self.projectName = raw_input("Enter the name of the project you want to manage: ").strip()
                
        # set the directory for the selected project's organized data
        self.selectedProjectDir = os.path.join( self.projectsDir, self.projectName )
    
        # set the directory for the selected project's data organized by patient
        self.byPatientDir = os.path.join( self.selectedProjectDir, 'by_patient' )

        # set the directory for the selected project's data organized by age
        self.byAgeDir = os.path.join( self.selectedProjectDir, 'by_age' )

        # set ranges for age breakdown
        self.ageBreakdown = [
            {
                'minDay': 0,
                'maxDay': 6,
                'name': 'day0000-0006_week0_year0'
            },
            {
                'minDay': 7,
                'maxDay': 13,
                'name': 'day0007-0013_week1_year0'
            },
            {
                'minDay': 14,
                'maxDay': 20,
                'name': 'day0014-0020_week2_year0'
            },
            {
                'minDay': 21,
                'maxDay': 27,
                'name': 'day0021-0027_week3_year0'
            },
            {
                'minDay': 28,
                'maxDay': 59,
                'name': 'day0028-0059_month1_year0'
            },
            {
                'minDay': 60,
                'maxDay': 89,
                'name': 'day0060-0089_month2_year0'
            },
            {
                'minDay': 90,
                'maxDay': 119,
                'name': 'day0090-0119_month3_year0'
            },
            {
                'minDay': 120,
                'maxDay': 149,
                'name': 'day0120-0149_month4_year0'
            },
            {
                'minDay': 150,
                'maxDay': 179,
                'name': 'day0150-0179_month5_year0'
            },
            {
                'minDay': 180,
                'maxDay': 209,
                'name': 'day0180-0209_month6_year0'
            },
            {
                'minDay': 210,
                'maxDay': 239,
                'name': 'day0210-0239_month7_year0'
            },
            {
                'minDay': 240,
                'maxDay': 269,
                'name': 'day0240-0269_month8_year0'
            },
            {
                'minDay': 270,
                'maxDay': 299,
                'name': 'day0270-0299_month9_year0'
            },
            {
                'minDay': 300,
                'maxDay': 329,
                'name': 'day0300-0329_month10_year0'
            },
            {
                'minDay': 330,
                'maxDay': 365,
                'name': 'day0330-0364_month11_year0'
            },
            {
                'minDay': 365,
                'maxDay': 394,
                'name': 'day0365-0394_month12_year1'
            },
            {
                'minDay': 395,
                'maxDay': 424,
                'name': 'day0395-0424_month13_year1'
            },
            {
                'minDay': 425,
                'maxDay': 454,
                'name': 'day0425-0454_month14_year1'
            },
            {
                'minDay': 455,
                'maxDay': 484,
                'name': 'day0455-0484_month15_year1'
            },
            {
                'minDay': 485,
                'maxDay': 514,
                'name': 'day0485-0514_month16_year1'
            },
            {
                'minDay': 515,
                'maxDay': 544,
                'name': 'day0515-0544_month17_year1'
            },
            {
                'minDay': 545,
                'maxDay': 574,
                'name': 'day0545-0574_month18_year1'
            },
            {
                'minDay': 575,
                'maxDay': 604,
                'name': 'day0575-0604_month19_year1'
            },
            {
                'minDay': 605,
                'maxDay': 634,
                'name': 'day0605-0634_month20_year1'
            },
            {
                'minDay': 635,
                'maxDay': 664,
                'name': 'day0635-0664_month21_year1'
            },
            {
                'minDay': 665,
                'maxDay': 694,
                'name': 'day0665-0694_month22_year1'
            },
            {
                'minDay': 695,
                'maxDay': 729,
                'name': 'day0695-0729_month23_year1'
            },
            {
                'minDay': 730,
                'maxDay': 819,
                'name': 'day0730-0819_month24-26_year2'
            },
            {
                'minDay': 820,
                'maxDay': 909,
                'name': 'day0820-0909_month27-29_year2'
            },
            {
                'minDay': 910,
                'maxDay': 999,
                'name': 'day0910-0999_month30-32_year2'
            },
            {
                'minDay': 1000,
                'maxDay': 1094,
                'name': 'day1000-1094_month33-35_year2'
            },
            {
                'minDay': 1095,
                'maxDay': 1184,
                'name': 'day1095-1184_month36-38_year3'
            },
            {
                'minDay': 1185,
                'maxDay': 1274,
                'name': 'day1185-1274_month39-41_year3'
            },
            {
                'minDay': 1275,
                'maxDay': 1364,
                'name': 'day1275-1364_month42-44_year3'
            },
            {
                'minDay': 1365,
                'maxDay': 1459,
                'name': 'day1365-1459_month45-47_year3'
            },
            {
                'minDay': 1460,
                'maxDay': 1824,
                'name': 'day1460-1824_month48-59_year4'
            },
            {
                'minDay': 1825,
                'maxDay': 2190,
                'name': 'day1825-2190_month60-71_year5'
            }
        ]




