# dicom_hoi.py
# This is a list of all the dicom headers that are to be put into the SQLite database

dcm_HOI = [
           0x00080008, #Image Type
           0x00080016, #SOP Class UID
           #0x00080018, #SOP Instance UID
           0x00080020, #Study Date
           0x00080021, #Series Date
           0x00080022, #Acquisition Date
           0x00080023, #Content Date
           #0x00080030, #Study Time
           #0x00080031, #Series Time
           #0x00080032, #Acquisition Time
           #0x00080033, #Content Time
           0x00080050, #Accession Number
           0x00080060, #Modality
           0x00080070, #Manufacturer
           0x00080080, #Institution Name
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
           #0x00180091, #Echo Train Length
           #0x00180093, #Percent Sampling
           #0x00180094, #Percent Phase Field of View
           #0x00180095, #Pixel Bandwidth
           0x00181000, #Device Serial Number
           0x00181020, #Software Version0xs)
           0x00181030, #Protocol Name
           #0x00181250, #Receive Coil Name
           #0x00181310, #Acquisition Matrix
           #0x00181312, #In-plane Phase Encoding Direction
           #0x00181314, #Flip Angle
           #0x00181315, #Variable Flip Angle Flag
           0x00185100, #Patient Position
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
