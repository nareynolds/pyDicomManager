pyDicomManager
================

Intended audience:
These modules were written to help in the examination, organization, and management of a large number of DICOM files.

Intended use:
This copies or moves DICOM files into a human-readable filetree.
This records DICOM header data into an SQLite database with series-level granularity.
This allows you to record notes about each series into the same database.
This allows you to export managed DICOM files to a location of your choice.

Details:
This was written for Python 2.7.X
This relies on pydicom ( https://code.google.com/p/pydicom/ ) and sqlite3 ( https://docs.python.org/2/library/sqlite3.html ) extensively.
All common use cases are presented in the file "examples.py"
Some settings, such as the location of managed filetree, can be set in the file "dicommanagersettings.py"
The default location of the SQLite database is in this directory.
The default location of the managed filetree is in "data/DICOM".
An example of the filetree structure can be seen in "data/DICOM_example_filetree".
The python executable "manage_dicoms.py" is a convenience script to execute DicomManager.manage().
It is also a good example of how to use these modules.

Have fun!