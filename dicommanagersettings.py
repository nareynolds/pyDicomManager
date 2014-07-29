# manager_settings.py
#


# add working directory to search path
import os
import sys


class DicomManagerSettings:

    def __init__(self):

        # get directory of this file
        selfDir = os.path.dirname(os.path.realpath(__file__))

        # set the directory where to save the SQLite database used for management
        self.dbDir = selfDir
        if not self.dbDir:
            self.dbDir = raw_input("Enter the path where sqlite database is to be saved: ").strip().replace('\\','')
        
        # set the path to this management SQLite database
        dbName = 'dicommanager.sqlite'
        self.dbPath = os.path.join( self.dbDir, dbName )
    
        # set name of database table in which the dicom series' data are saved
        self.dbTblSeries = 'Series'
                
        # set name of database table in which the series' notes are saved
        self.dbTblSeriesNotes = 'Notes'
    
        # set the root directory of DICOM storage
        self.rootDir = os.path.join( selfDir, 'data' )
        if not self.rootDir:
            self.rootDir = raw_input("Enter the root directory where dicoms are to be stored and managed: ").strip().replace('\\','')
    
        # set the directory where the dicoms are acutally written
        self.dicomDir = os.path.join( self.rootDir, 'DICOM' )
                
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
            },
            {
                'minDay': 2191,
                'maxDay': 3650,
                'name': 'day2191-3650_month72-120_year6-10'
            },
            {
                'minDay': 3651,
                'maxDay': 18250,
                'name': 'day3651-18250_month121-600_year11-50'
            },
            {
                'minDay': 18251,
                'maxDay': 36500,
                'name': 'day18251-36500_month601-1200_year51-100'
            },
            {
                'minDay': 36501,
                'maxDay': 1000000,
                'name': 'day36501-up_month1200-up_year100-up'
            },
        ]

        # list of all the dicom tags that will be recorded in the SQLite database
        self.tagsToRecord = [
            0x00080008, #Image Type
            0x00080016, #SOP Class UID
            #0x00080018, #SOP Instance UID
            0x00080020, #Study Date
            0x00080021, #Series Date
            0x00080022, #Acquisition Date
            0x00080023, #Content Date
            0x00080030, #Study Time
            0x00080031, #Series Time
            0x00080032, #Acquisition Time
            0x00080033, #Content Time
            0x00080050, #Accession Number
            0x00080060, #Modality
            0x00080070, #Manufacturer
            0x00080080, #Institution Name
            0x00080082, #Institution Code Sequence
            0x00080090, #Referring Physician's Name
            0x00081010, #Station Name
            0x00081030, #Study Description
            0x0008103e, #Series Description
            0x00081040, #Institutional Department Name
            0x00081050, #Performing Physician's Name
            0x00081060, #Name of Physician0xs Reading Study
            0x00081070, #Operators' Name
            0x00081090, #Manufacturer's Model Name
            0x00100010, #Patient's Name
            0x00100020, #Patient ID
            0x00100030, #Patient's Birth Date
            0x00100040, #Patient's Sex
            0x00101010, #Patient's Age
            0x00101030, #Patient's Weight
            #0x00101080, #Military Rank
            #0x00101081, #Branch of Service
            0x001021b0, #Additional Patient History
            0x00180010, #Contrast/Bolus Agent
            0x00180015, #Body Part Examined
            0x00180020, #Scanning Sequence
            0x00180021, #Sequence Variant
            0x00180022, #Scan Options
            0x00180023, #MR Acquisition Type
            0x00180025, #Angio Flag
            0x00180050, #Slice Thickness
            0x00180080, #Repetition Time
            0x00180081, #Echo Time
            0x00180082, #Inversion Time
            0x00180083, #Number of Averages
            0x00180084, #Imaging Frequency
            #0x00180085, #Imaged Nucleus
            0x00180086, #Echo Number0xs)
            0x00180087, #Magnetic Field Strength
            0x00180088, #Spacing Between Slices
            0x00180091, #Echo Train Length
            0x00180093, #Percent Sampling
            0x00180094, #Percent Phase Field of View
            0x00180095, #Pixel Bandwidth
            0x00181000, #Device Serial Number
            0x00181002, #Device UID
            0x00181003, #Device ID
            0x00181020, #Software Version0xs)
            0x00181030, #Protocol Name
            0x00181040, #Contrast Bolus Route
            0x00181041, #Contrast/Bolus Volume
            0x00181250, #Receive Coil Name
            #0x00181310, #Acquisition Matrix
            #0x00181312, #In-plane Phase Encoding Direction
            #0x00181314, #Flip Angle
            #0x00181315, #Variable Flip Angle Flag
            0x00185100, #Patient Position
            0x00189075, #Diffusion Directionality
            0x00189076, #Diffusion Gradient Direction Sequence
            0x00189087, #Diffusion b-value
            0x00189089, #Diffusion Gradient Orientation
            0x00189107, #MR Spatial Saturation Sequence
            0x00189112, #MR Timing and Related Parameters Sequence
            0x00189114, #MR Echo Sequence
            0x00189115, #MR Modifier Sequence
            0x00189117, #MR Diffusion Sequence
            0x00189601, #Diffusion b-matrix Sequence
            0x00189602, #Diffusion b-value XX
            0x00189603, #Diffusion b-value XY
            0x00189604, #Diffusion b-value XZ
            0x00189605, #Diffusion b-value YY
            0x00189606, #Diffusion b-value YZ
            0x00189607, #Diffusion b-value ZZ
            0x0020000d, #Study Instance UID
            0x0020000e, #Series Instance UID
            0x00200010, #Study ID
            0x00200011, #Series Number
            #0x00200012, #Acquisition Number
            #0x00200013, #Instance Number
            #0x00200032, #Image Position 0xPatient)
            #0x00200037, #Image Orientation 0xPatient)
            #0x00200052, #Frame of Reference UID
            0x00201002, #Images in Acquisition
            #0x00201041, #Slice Location
            #0x00209056, #Stack ID
            #0x00209057, #In-Stack Position Number
            0x00280010, #Rows
            0x00280011, #Columns
            #0x00280030, #Pixel Spacing
            #0x00280100, #Bits Allocated
            #0x00280101, #Bits Stored
            #0x00280102, #High Bit
            #0x00280103, #Pixel Representation
            #0x00280106, #Smallest Image Pixel Value
            #0x00280107, #Largest Image Pixel Value
            #0x00281050, #Window Center
            #0x00281051, #Window Width
            0x00321030, #Reason for Study
            0x00321032, #Requesting Physician
            0x00324000  #Study Comments
            #0x00331004, #[Study Description]
            #0x0033100c, #[Reason for Study]
        ]



