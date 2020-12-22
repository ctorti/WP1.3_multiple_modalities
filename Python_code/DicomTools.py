# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 10:44:06 2020

@author: ctorti
"""



# Import packages:
#import os
#from pydicom import read_file
#import numpy as np
#from natsort import natsorted

##import importlib
##import ImageTools
##importlib.reload(ImageTools)

#from ImageTools import GetImageAttributes



"""
******************************************************************************
******************************************************************************
GENERAL DICOM FUNCTIONS
******************************************************************************
******************************************************************************
"""


def GetDicomFpaths(DicomDir, SortMethod='slices', LogToConsole=None):
    """
    Get a sorted list of full filepaths for all DICOM files in a directory
    
    Inputs:
    ------
    
    DicomDir : string
        Path to directory containing DICOMs.
        
    SortMethod : string (optional, 'slices' by default) 
        Denotes the method used for sorting of files fetched using 
        GetDicomFpaths() with acceptable values:
            -- 'none' (or 'None' or any other strings) = no sorting
            -- 'natural' (or 'Natural') = using natsort to sort the filenames
            -- 'slices' (or 'Slices') = sorted along the slice direction 
    
    
    Outputs:
    -------
    
    FilePaths : list of strings 
        List of the full filepaths of all DICOM files in DicomDir either:
            -- without sorting
            -- sorted in a natural way, 
            e.g. 3-1, 3-2, ..., 3-9, 3-10, 3-11, ...
            rather than 3-1, 3-10, 3-11, ... , 3-2, 3-20, ...
            -- sorted along the scan direction in ascending order
    """
    
    import os
    from natsort import natsorted
    from pydicom import read_file
    import numpy as np
    
    #print('\nSortMethod (input for GetDicomFpaths()) =', SortMethod)
    
    # Create an empty list of all Dicom file paths:
    FilePaths = []

    # Use os to get list of file paths of Dicom-only files:
    for DirName, SubDirList, FileList in os.walk(DicomDir):
        for FileName in FileList:
            if '.dcm' in FileName.lower():  # check for Dicom files only
                FilePaths.append(os.path.join(DirName,FileName))
                
    #print('FilePaths =', FilePaths)
    
    if FilePaths==[]:
        print('No DICOMs found.')
    else:
        if SortMethod in ['natural', 'Natural']:
            # Sort files in natural way:
            FilePaths = natsorted(FilePaths)
            
        if SortMethod in ['slices', 'Slices']:
            # Create an empty array to store the Positions:
            Positions = []
            
            for FilePath in FilePaths:
                #print('\nFilePath =', FilePath)
                
                # Read in Dicom:
                Dicom = read_file(FilePath)
                
                # Parse the Image Position (Patient):
                Position = [float(item) for item in Dicom.ImagePositionPatient]
                
                # Add Position for this Dicom to Positions:
                Positions.append(Position)
                
            # Convert to numpy array:
            Positions = np.array(Positions)
            
            #print('Positions =', Positions)
    
            # Get the maximum change of Positions along x, y and z:
            dPositions = np.max(Positions, axis=0) - np.min(Positions, axis=0)
            
            if LogToConsole:
                print('\n   The maximum change of Positions along x, y and z',
                      f'= {dPositions}')
    
            # Get the index of the axis with the greatest change of Position:
            ind = np.where(dPositions==np.max(dPositions))[0][0]
            
            if LogToConsole:
                print('\n   The index of the axis with the greatest change of',
                      f'Position = {ind}')
            
            # Convert ind to 'x', 'y' or 'z':
            if ind == 0:
                SortAxis = 'x'
            if ind == 1:
                SortAxis = 'y'
            if ind == 2:
                SortAxis = 'z'
                
            if LogToConsole:
                print('\n   The DICOM filepaths will be sorted along the ' \
                      + SortAxis + '-axis.')
            
                print('\n   The pre-sorted ' + SortAxis + '-positions are:\n')
                print([round(Positions[i][ind], 2) for i in range(len(Positions))])
            
            """
            Solution on how to sort along a specific column:
            
            https://stackoverflow.com/questions/22698687/how-to-sort-2d-array-numpy-ndarray-based-to-the-second-column-in-python
            
            The following are equivalent:
            
            Positions[Positions[:, 2].argsort()]
            Positions[np.argsort(Positions[:, 1])]
            
            """
            
            SortInds = Positions[:, ind].argsort()
            
            #PositionsSorted = Positions[SortInds]
            
            if LogToConsole:
                print('\n   The sorted ' + SortAxis + '-positions are:\n')
                print([round(Positions[i][ind], 2) for i in SortInds])
            
            # Sort FilePaths with SortInds:
            #FilePaths = FilePaths[SortInds] # <-- TypeError: list indices must be 
            # integers or slices, not list
            FilePaths = [FilePaths[i] for i in SortInds]
        
    
    return FilePaths





def ImportDicoms(DicomDir, SortMethod='slices', LogToConsole=False):
    """
    Import DICOM objects from a directory containing DICOM files.
    
    Inputs:
    -------
    
    DicomDir : string
        Path to directory containing DICOM files.
        
    SortMethod : string (optional, 'slices' by default) 
        Denotes the method used for sorting of files fetched using 
        GetDicomFpaths() with acceptable values:
            -- 'none' (or 'None' or any other strings) = no sorting
            -- 'natural' (or 'Natural') = using natsort to sort the filenames
            -- 'slices' (or 'Slices') = sorted along the slice direction 
        
    Outputs:
    -------
    
    Dicoms : list of Pydicom objects
        List of DICOM objects.
    """
    
    from pydicom import read_file
    
    #print('\nSortMethod (input for GetDicoms()) =', SortMethod)
    
    fpaths = GetDicomFpaths(DicomDir, SortMethod, LogToConsole)
    
    Dicoms = []
    
    for f in range(len(fpaths)):
        fpath = fpaths[f]
        
        dicom = read_file(fpath)
        
        Dicoms.append(dicom)
        
    return Dicoms





def ImportDicom(DicomDir, SortMethod='slices', InStackNum=0, 
                LogToConsole=False):
    """
    Import a single DICOM object from a directory containing DICOM file(s).
    
    Inputs:
    -------
    
    DicomDir : string
        Path to directory containing DICOM files.
        
    SortMethod : string (optional, 'slices' by default) 
        Denotes the method used for sorting of files fetched using 
        GetDicomFpaths() with acceptable values:
            -- 'none' (or 'None' or any other strings) = no sorting
            -- 'natural' (or 'Natural') = using natsort to sort the filenames
            -- 'slices' (or 'Slices') = sorted along the slice direction
            
    InStackNum : integer (optional; 0 by default)
        The in-stack index of the file within the sorted list of DICOM 
        filepaths to import.  The first file is imported by default.
    
        
    Outputs:
    -------
    
    Dicoms : list of Pydicom objects
        List of DICOM objects.
    """
    
    from pydicom import read_file
    
    fpaths = GetDicomFpaths(DicomDir, SortMethod, LogToConsole)
    
    if InStackNum < len(fpaths):
        Dicom = read_file(fpaths[InStackNum])
        
        return Dicom
    
    else:
        msg = 'It is not possible to import a DICOM at InStackNum = '\
              + f'{InStackNum} since there are only {len(fpaths)} DICOMs in '\
              + 'the specified directory.'
              
        raise Exception(msg)
        
        return None






def GetDicomSOPuids(DicomDir):
    """
    Get a list of SOP Instance UIDs for a DICOM series.
    
    Inputs:
    ------
    
    DicomDir : string
        Directory containing the DICOMs.
        
    
    Outputs:
    -------
    
    SOPuids : list of strings
        List of the SOP UIDs of the DICOMs.
    """
    
    Dicoms = ImportDicoms(DicomDir=DicomDir, SortMethod='slices', 
                          LogToConsole=False)
    
    SOPuids = [] 
    
    for dicom in Dicoms:
        SOPuids.append(dicom.SOPInstanceUID)
        
    return SOPuids






def GetDicomUids(DicomDir):
    """
    Get the Study, Series, Frame of Reference and SOP Instance UIDs for a DICOM 
    series.
    
    Inputs:
    ------
    
    DicomDir : string
        Directory containing the DICOMs.
        
    
    Outputs:
    -------
    
    Studyuid : string
        Study Instance UID of the DICOM series.
        
    Seriesuid : string
        Series Instance UID of the DICOM series.
        
    FORuid : string
        Frame of Reference UID of the DICOM series.
        
    SOPuids : list of strings
        List of the SOP UIDs of the DICOMs.
    """
    
    Dicoms = ImportDicoms(DicomDir=DicomDir, SortMethod='slices', 
                          LogToConsole=False)
    
    SOPuids = [] 
    
    for dicom in Dicoms:
        SOPuids.append(dicom.SOPInstanceUID)
        
    Studyuid = Dicoms[0].StudyInstanceUID
    Seriesuid = Dicoms[0].SeriesInstanceUID
    FORuid = Dicoms[0].FrameOfReferenceUID
        
    return Studyuid, Seriesuid, FORuid, SOPuids







def GetRoiLabels(Roi):
    """
    Get the list of contour/segment labels in a RTS/SEG.
    
    Inputs:
    ------
    
    Roi : Pydicom object
        Object from a RTS/SEG file.
    
        
    Outputs:
    -------
    
    Labels : list of strings
        List (for each ROI/segment) of ROIName/SegmentLabel tag values.
    """
    
    Labels = [] 
    
    if 'RTSTRUCT' in Roi.Modality:
        sequences = Roi.StructureSetROISequence
        
        for sequence in sequences:
            label = sequence.ROIName
            
            Labels.append(label)
            
    elif 'SEG' in Roi.Modality:
    
        sequences = Roi.SegmentSequence
        
        for sequence in sequences:
            label = sequence.SegmentLabel
            
            Labels.append(label) 
            
    else:
        msg = "The ROI object is not recognised as being RTS or SEG."
        
        raise Exception(msg)
        
    return Labels








def GetRoiNum(Roi, SearchString):
    """
    Get the ROI/segment number that matches SearchString.
    
    Inputs:
    ------
    
    Roi : Pydicom object
        RTS or SEG object.
        
    SearchString : string
        All or part of the ROIName/SegmentLabel of the ROI/segment of interest.
                       
                            
    Outputs:
    -------
    
    RoiNum : integer
        The index of the ROI that matches SearchString.
    """
    
    RoiLabels = GetRoiLabels(Roi)
    
    #print('\nRoiLabels =', RoiLabels)
    
    #print('\nRoiLabel to find =', SearchString)
    
    #RoiNum = RoiLabels.index(SearchString)
    RoiNum = [i for i, RoiLabel in enumerate(RoiLabels) if SearchString in RoiLabel]
    
    if not RoiNum:
        msg = 'There are no ROIs in the RTS/SEG that match "SearchString" = '\
              + f'"{SearchString}".'
        
        raise Exception(msg)
        
    return RoiNum[0]









def IsSameModalities(Roi0, Roi1):
    """
    Compare Modality tag of two RTS or two SEG objects. 
    """

    if Roi0.Modality == Roi1.Modality:
        return True
    
    else:
        return False










def InspectDicomStudyDir(StudyDir):
    import os
    from natsort import natsorted
    from ImageTools import GetImageAttributes
    
    # First get a list of DICOM scan directories
    ScanDirs = []
    ScanDirNames = []

    # Use os to get list of file paths of Dicom-only files:
    for DirName, SubDirList, FileList in os.walk(StudyDir):
        #print('DirName =', DirName)
        #print('SubDirList =', SubDirList)
        #print('FileList =', FileList)
        #print('\n\n')
        
        DicomsFound = 0
        
        for file in FileList:
            if '.dcm' in file:
                #print(FileList, 'contains at least 1 DICOM')
                DicomsFound += 1
                
        
        if DicomsFound:
            ScanDirs.append(DirName)
            
            # DirName is a directory containing DICOMs
            RootDir, ScanDir = os.path.split(DirName)
    
            ScanDirNames.append(ScanDir)
    
    
    # Sort the list of directory names using natsort:
    ScanDirNames = natsorted(ScanDirNames)
    
    """ 
    The DICOM scan directory names have the form:
        'N-Label'
        
    e.g.:
        '2-T1 SE SAG IPATX2-05296'
        
    where scan number = 2
    and scan label = 'T1 SE SAG IPATX2-05296'
    
    Get the scan numbers and labels separately.
    """
    ScanNums = []
    ScanLabels = []
    
    for ScanDirName in ScanDirNames:
        # Index of first '-':
        ind = ScanDirName.index('-')
        
        ScanNums.append(ScanDirName[0:ind])
        
        ScanLabels.append(ScanDirName[ind+1::])
    
    
    # Initialise the Origins, Directions, Spacings, Dims, and FORuids:
    Origins = []
    Dirs = []
    Spacings = []
    Size = []
    FORuids = []
    
    # Loop through each Scan directory:
    for ScanDir in ScanDirs:
    
        # Get the Image Attributes:
        Studyuid, Seriesuid, FORuid, size, spacings, ST,\
        IPPs, dirs = GetImageAttributes(ScanDir)
        
        # Get the DICOMs:
        DicomFpaths, Dicoms = ImportDicoms(DirPath=ScanDir, 
                                           SortMethod='slices', 
                                           Debug=False)
        
        Origins.append(IPPs[0])
        Dirs.append(dirs)
        Spacings.append(spacings)
        Size.append(size)
        FORuids.append(FORuid)
        
    
    # Create a dictionary:
    StudyDict = {'Scan num':ScanNums,
                 'Scan label':ScanLabels,
                 #'FOR UID':FORuids,
                 'Size':Size,
                 'Spacings':Spacings,
                 'Origin':Origins,
                 'Directions':Dirs
                 }
    
    #return StudyDict, ScanNums, ScanLabels, FORuids, Origins, Dirs, Dims, Spacings
    return StudyDict
    
    



def InspectDicomSubjectDir(SubjectDir): # THIS IS NOT COMPLETE!
    """
    This is not complete.
    """
    
    import os
    from natsort import natsorted
    
    # Get a list of study directories:
    StudyDirs = os.list(SubjectDir)
    
    # Sort using natsort:
    StudyDirs = natsorted(StudyDirs)
    
    
    """
    The directory names of the study directories have the form:
        'MM-DD-YYYY-MOD StudyLabel'
        
    where MOD is the modality (e.g. 'MRI', 'PET', 'CT')
    
    Get the date, modality and study label separately.
    """
    
    StudyDates = []
    Modalities = []
    StudyLabels = []
    
    for StudyDir in StudyDirs:
        # Get the study directory names:
        StudyDirRoot, StudyDirName = os.path.split(StudyDir)

        #StudyDates.append()
    

    return
