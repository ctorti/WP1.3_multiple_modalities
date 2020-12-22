# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 11:54:12 2020

@author: ctorti
"""




# Import packages and functions:
#import os
#import time
#from copy import deepcopy
#import pydicom
#from pydicom.pixel_data_handlers.numpy_handler import pack_bits
#from pydicom.uid import generate_uid
#import numpy as np
#import SimpleITK as sitk




"""
******************************************************************************
******************************************************************************
SEGMENT FUNCTIONS
******************************************************************************
******************************************************************************
"""      


def GetFrameNums(Seg, SearchString, DicomDir):
    """
    Get the frame number(s) in a SEG's pixel array that matches the segment 
    label provided.
    
    Inputs:
    ------
    
    Seg : Pydicom object
        SEG object.
        
    SearchString : string
        All or part of the Segment Label containing the segmentation of
        interest.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
                            
    Outputs:
    -------
    
    FrameNums : list of integer
        List of the frame numbers that correspond to all frames in the SEG's 
        pixel array that belongs to the segment of interest.  If only one frame 
        corresponds to the segment, the returned list will be of length one 
        (e.g. [3]).
        
    PFFGStoSliceInds : list of integers
        List of the slice numbers that correspond to each Per-frame Functional 
        Groups Sequence in the segment of interest. 
    """
    
    from DicomTools import GetDicomSOPuids
    from DicomTools import GetRoiNum
    
    # Get the DimensionIndexValues (DIVs) and group the DIVs by segment.
    """ Note:  The DIVs are integers that start from 1. """
    DIVs = GetDIVs(Seg)
    
    # Get the DICOM SOP UIDs:
    SOPuids = GetDicomSOPuids(DicomDir)
    
    # Get the PerFrameFunctionalGroupsSequence-to-slice indices
    # (PFFGStoSliceInds) and PFFGStoSliceInds grouped by segment
    # (PFFGStoSliceIndsBySeg):
    """ Note:  The PFFGStoSliceInds are integers that start from 0. """
    PFFGStoSliceInds = GetPFFGStoSliceInds(Seg, SOPuids)
    
    PFFGStoSliceIndsBySeg = GroupListBySegment(ListToGroup=PFFGStoSliceInds, 
                                               DIVs=DIVs)
    
    SegNum = GetRoiNum(Seg, SearchString)
    
    # The PFFGStoSliceInds for the segment of interest:
    PFFGStoSliceInds = PFFGStoSliceIndsBySeg[SegNum]
    
    # The number of segments:
    S = len(PFFGStoSliceIndsBySeg)
    
    # The number of frames in the segment of interest:
    F = len(PFFGStoSliceInds)
    
    n = 0 # initialise frame number counter
    
    FrameNums = []
    
    for s in range(S):
        if s == SegNum:
            """ 
            This segment contains the frame(s) of interest, which are given by
            the index of PFFGStoSliceInds[f] in PFFGStoSliceIndsBySeg[s] plus 
            any frames that preceeded it (i.e. the frame counter n).
            """
            
            for f in range(F):
                FrameNum = n + PFFGStoSliceIndsBySeg[s].index(PFFGStoSliceInds[f])
                
                FrameNums.append(FrameNum)
            
        else:
            # Add to the frame counter the number of frames in this segment:
            n += len(PFFGStoSliceIndsBySeg[s])
    
    return FrameNums, PFFGStoSliceInds








def GetRSOPuidsInRIS(Seg):
    """
    Get the list of ReferencedSOPInstanceUIDs in the ReferencedInstanceSequence
    of a SEG.
    
    Inputs:
    ------
        
    Seg : Pydicom object
        ROI object from a SEG file.
    
        
    Outputs:
    -------
        
    RSOPuids : list of strings
        List of ReferencedSOPInstanceUIDs.
    """
    
    RSOPuids = [] 
    
    sequences = Seg.ReferencedSeriesSequence[0]\
                   .ReferencedInstanceSequence
    
    for sequence in sequences:
        uid = sequence.ReferencedSOPInstanceUID
        
        RSOPuids.append(uid)
        
    return RSOPuids





def GetRIStoSliceInds(Seg, SOPuids):
    """
    Get the slice numbers that correspond to each ReferencedInstanceSequence
    in a SEG.
    
    Inputs:
    ------
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
    SOPuids : list of strings
        List of SOPInstanceUIDs of the DICOMs.
        
    
    Outputs:
    -------
    
    RIStoSliceInds : list of integers
        Slice numbers that correspond to each ReferencedInstanceSequence in 
        Seg.
    """
    
    # Get the list of Referenced SOP Instance UIDs:
    RSOPuids = GetRSOPuidsInRIS(Seg)
    
    RIStoSliceInds = [] 
    
    for Ruid in RSOPuids:
        # Find the matching index of Ruid in SOPuids:
        RIStoSliceInds.append(SOPuids.index(Ruid))
        
    return RIStoSliceInds





def GetRSOPuidsInPFFGS(Seg):
    """
    Get the list of ReferencedSOPInstanceUIDs in the 
    Per-FrameFunctionalGroupsSequence of a SEG.
    
    Inputs:
    ------
        
    Seg : Pydicom object
        ROI object from a SEG file.
    
        
    Outputs:
    -------
    
    RSOPuids : list of strings
        List of ReferencedSOPUIDs.
    """
    
    RSOPuids = [] 
    
    sequences = Seg.PerFrameFunctionalGroupsSequence
    
    for sequence in sequences:
        uid = sequence.DerivationImageSequence[0]\
                      .SourceImageSequence[0]\
                      .ReferencedSOPInstanceUID
        
        RSOPuids.append(uid)
        
    return RSOPuids





def GetPFFGStoSliceInds(Seg, SOPuids):
    """
    Get a list of the slice numbers that correspond to each  
    Per-FrameFunctionalGroupsSequence in a SEG.
    
    Inputs:
    ------
        
    Seg : Pydcom object
        ROI object from a SEG file.
        
    SOPuids : list of strings
        SOPInstanceUIDs of the DICOMs.
        
    
    Outputs:
    -------
        
    PFFGStoSliceInds : list of integers
        List (for each frame) of the slice numbers that correspond to each 
        Per-FrameFunctionalGroupsSequence in Seg.
    """
    
    # Get the list of Referenced SOP Instance UIDs:
    RSOPuids = GetRSOPuidsInPFFGS(Seg)
    
    PFFGStoSliceInds = [] 
    
    for Ruid in RSOPuids:
        # Find the matching index of Ruid in SOPuids:
        PFFGStoSliceInds.append(SOPuids.index(Ruid))
        
    return PFFGStoSliceInds







def GetPFFGStoSliceIndsBySeg(Seg, SOPuids):
    """
    Get a list (per segment) of the slice numbers that correspond to each 
    Per-FrameFunctionalGroupsSequence in a SEG.
    
    Inputs:
    ------
        
    Seg : Pydcom object
        ROI object from a SEG file.
        
    SOPuids : list of strings
        SOPInstanceUIDs of the DICOMs.
        
    
    Outputs:
    -------
        
    PFFGStoSliceIndsBySeg : list of a list of integers
        List (for each segment) of a list (for each frame) of the slice numbers 
        that correspond to each Per-FrameFunctionalGroupsSequence in Seg.
    """
    
    PFFGStoSliceInds = GetPFFGStoSliceInds(Seg, SOPuids)
    
    DIVs = GetDIVs(Seg)
    
    PFFGStoSliceIndsBySeg = GroupListBySegment(ListToGroup=PFFGStoSliceInds, 
                                               DIVs=DIVs)
    
    return PFFGStoSliceIndsBySeg






    
    
def GetDIVs(Seg):
    """
    Get the DimensionIndexValues in a SEG.
    
    Inputs:
    ------
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
        
    Outputs:
    -------
    
    DIVs : list of lists of integers
        List of DimensionIndexValues in Seg.
        
    """
    
    # Initialise the list of DIVs:
    DIVs = [] 
    
    sequences = Seg.PerFrameFunctionalGroupsSequence
    
    for sequence in sequences:
        DIV = sequence.FrameContentSequence[0]\
                      .DimensionIndexValues
        
        DIVs.append(DIV)
        
    return DIVs






def GroupListBySegment(ListToGroup, DIVs):
    """
    Group a list of items by common segment/ROI using the DimensionIndexValues.
    
    Inputs:
    ------
    
    ListToGroup : list
        The list to be grouped.
        
    DIVs : list of lists of integers
        List of DimensionIndexValues.
        
        
    Outputs:
    -------
    
    GroupedList : list of lists
        ListToGroup grouped by ROI.
        
        
    Note:
    ----
    
    DIVs is a list of lists of the form:
            
    [ [1, 10], [1, 11], [1, 12], ... [2, 6], [2, 7], [2, 8], ... ]
    
    where each list of index values that belong to a common ROI are separated
    into separate lists.
    
    The goal is to group a list (of anything) by ROI.  In the case of the DIVs,
    that is:
        
    [ [ [1, 10], [1, 11], [1, 12], ... ],
      [ [2, 6], [2, 7], [2, 8], ... ],
      ... 
     ]
      
     
    If there's only one ROI, ListToGroup will still be nested in a list to 
    maintain continuity.  In the case of the DIVs with only one ROI:
        
    [ [ [1, 10], [1, 11], [1, 12], ... ]
     ]
    """
    
    # Get the list of ROI numbers:
    RoiNums = []
    
    for DIV in DIVs:
        RoiNums.append(DIV[0])
        
    UniqueRoiNums = list(set(RoiNums))
    
    if len(UniqueRoiNums) == 1:
        GroupedList = [ListToGroup]
        
    else:
        GroupedList = []
        
        for RoiNum in UniqueRoiNums:
            ListThisRoi = [] # initialise
            
            for i in range(len(ListToGroup)):
                if DIVs[i][0] == RoiNum:
                    ListThisRoi.append(ListToGroup[i])
        
            GroupedList.append(ListThisRoi)
             
    return GroupedList











def AddToPFFGS(Seg):
    """
    Append the last item in the Per-FrameFunctionalGroupsSequence of the
    SEG to itself (i.e. increase the length of the sequence by one). 
    
    Inputs:
    ------
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
    
    Outputs:
    -------
    
    NewSeg : Pydicom object
        Modified ROI object with Per-FrameFunctionalGroupsSequence lengthened
        by one.
    """
    
    from copy import deepcopy
    
    # Use Seg as a template for NewSeg: 
    NewSeg = deepcopy(Seg)
             
    # The last item in Per-frame Functional Groups Sequence:
    last = deepcopy(Seg.PerFrameFunctionalGroupsSequence[-1])
    
    # Append to the Per-frame Functional Groups Sequence:
    NewSeg.PerFrameFunctionalGroupsSequence.append(last)
             
    return NewSeg






def AddToSS(Seg):
    """
    Append the last item in the SegmentSequence of the SEG Object to itself 
    (i.e. increase the length of the sequence by one). 
    
    Inputs:
    ------
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
    
    Outputs:
    -------
    
    NewSeg : Pydicom object
        Modified Seg with SegmentSequence lengthened by one.
    """
    
    from copy import deepcopy
    
    # Use Seg as a template for NewSeg: 
    NewSeg = deepcopy(Seg)
             
    # The last item in Segment Sequence:
    last = deepcopy(Seg.SegmentSequence[-1])
    
    # Append to the Segment Sequence:
    NewSeg.SegmentSequence.append(last)
             
    return NewSeg







def ChangeNumOfSegSequences(Seg, Dicoms, NumOfFrames, LogToConsole=False):
    """
    Adjust the number of sequences in a SEG object based so that they are 
    consistent with the number of DICOMs in the series and the number of
    frames in the pixel array.
         
    
    Inputs:
    ------
                              
    Seg : Pydicom object
        SEG object.
        
    Dicoms : List of Pydicom objects
        List of DICOM objects that relate to the SEG object to be created.
    
    NumOfFrames : integer
        The number of frames in the SEG object's pixel array.
                         
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Outputs:
    -------
        
    Seg : Pydicom object
        SEG object with modified number of sequences.
    """
    
    
    """ 
    Modify the number of sequences in ReferencedSeriesSequence. 
    The number of sequences must be equal to the number of DICOMs.
    """
    
    from copy import deepcopy
    
    # The number of DICOMs:
    D = len(Dicoms)
    
    # The number of sequences in the ReferencedSeriesSequence:
    R = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
    
    
    # Add/remove sequences by appending/popping the last sequence N times, 
    # where N is the difference between D and R:
    if D > R:
        for i in range(D - R):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence\
               .append(deepcopy(Seg.ReferencedSeriesSequence[0]\
                                   .ReferencedInstanceSequence[-1]))          
    else:
        for i in range(R - D):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence.pop()

    
    """ 
    Modify the number of sequences in SegmentSequence. 
    There must be only one sequence - for the (one) new segment.
    """
    
    S = len(Seg.SegmentSequence)
    
    if S > 1:
        for i in range(S - 1):
            Seg.SegmentSequence.pop()
    
    
    """ 
    Modify the number of sequences in Per-FrameFunctionGroupsSequence. 
    The number of sequences must be equal to NumOfFrames.
    """
    
    # The number of sequences in the Per-FrameFunctionGroupsSequence:
    P = len(Seg.PerFrameFunctionalGroupsSequence)
    
    if NumOfFrames > P:
        for i in range(NumOfFrames - P):
            Seg.PerFrameFunctionalGroupsSequence\
               .append(deepcopy(Seg.PerFrameFunctionalGroupsSequence[-1]))          
    else:
        for i in range(P - NumOfFrames):
            Seg.PerFrameFunctionalGroupsSequence.pop()

    
    
    
    if True:#LogToConsole:       
        R2 = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
        
        S2 = len(Seg.SegmentSequence)
        
        P2 = len(Seg.PerFrameFunctionalGroupsSequence)
        
        print(f'\nThere are {D} DICOMs and there were {R} sequences in',
              f'ReferencedSeriesSequence. Now there are {R2} sequences.')
        
        print(f'\nThere were {S} sequences in SegmentSequence. Now there are',
              f'{S2} sequences.')
        
        print(f'\nThere are {NumOfFrames} frames in the pixel array and there',
              f'were {P} sequences in PerFrameFunctionalGroupsSequence. Now',
              f'there are {P2} sequences.')
        
    
    return Seg








def GetFrameFromPixArr(Seg, DicomDir, SearchString, SliceNum, LogToConsole):
    """
    Extract a single (2D) frame from a 3D pixel array that matches a given
    segment label.  
    
    Inputs:
    ------
    
    Seg : Pydicom object
        SEG object.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
    SearchString : string
        All or part of the Segment label containing the segmentation to be
        copied.
    
    SliceNum : integer
        Slice index of the Source DICOM stack corresponding to the segmentation
        to be copied (counting from 0).
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
        
    
    Outputs:
    -------
    
    Frame : Numpy array
        Frame from PixArr.
    """
    
    import numpy as np
    from DicomTools import GetDicomSOPuids
    from DicomTools import GetRoiLabels
    from DicomTools import GetRoiNum
    
    SegLabels = GetRoiLabels(Seg)
    
    # Determine which segment contains the segmentation to be copied, and
    # the corresponding frame number in the pixel array:
    """ Note:  SegNum is equivalent to SegmentNumber in SegmentSequence. """
    SegNum = GetRoiNum(Seg, SearchString)
    
    SOPuids = GetDicomSOPuids(DicomDir)
    
    PFFGStoSliceIndsBySeg = GetPFFGStoSliceIndsBySeg(Seg, SOPuids)
    
    PFFGStoSliceIndsInSeg = PFFGStoSliceIndsBySeg[SegNum]
    
    if not SliceNum in PFFGStoSliceIndsInSeg:
        msg = f'There is no segmentation in the segment matching the term '\
              + f'"{SearchString}" for slice {SliceNum} in the SEG.'
              
        raise Exception(msg)
    
    # Get the corresponding FrameNum:
    
    n = 0 # initialise frame number counter
    
    for i in range(len(SegLabels)):
        if i == SegNum:
            """ 
            This segment contains the frame to be copied, whose position is
            given by the index of FromSliceNum in 
            SrcPFFGStoSliceIndsBySeg[i] plus any frames that preceeded it 
            (i.e. the frame counter n).
            """
            FrameNum = n + PFFGStoSliceIndsBySeg[i].index(SliceNum)
            
        else:
            # Add to the frame counter the number of frames in this segment:
            n += len(PFFGStoSliceIndsBySeg[i]) 
    
    
    if LogToConsole:
        print('\n\nResults of GetFrameFromPixArr:')
        print(f'   SliceNum = {SliceNum} relates to FrameNum = {FrameNum} in',
              'PixelArray')
    
    PixArr = Seg.pixel_array
    
    if len(PixArr.shape) < 3:
        # This is a single-frame PixArr, i.e. shape (R, C). Reshape it to 
        # shape (1, R, C):
        R, C = PixArr.shape
        
        PixArr = np.reshape(PixArr, (1, R, C))
    else:
        # This is a multi-frame PixArr, i.e. shape (AllF, R, C).
        AllF, R, C = PixArr.shape
    
    # Initialise Frame:
    Frame = np.zeros((1, R, C), dtype='uint')
    
    Frame[0] = PixArr[FrameNum]
            
    return Frame








def GetFramesFromPixArr(Seg, DicomDir, SearchString, LogToConsole):
    """
    Extract all frames from a 3D pixel array that match a given segment label.  
    
    Inputs:
    ------
    
    Seg : Pydicom object
        SEG object.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
    SearchString : string
        All or part of the Segment Label of the segment containing the 
        segmentation to be copied.
    
    SliceNum : integer
        Slice index of the Source DICOM stack corresponding to the segmentation
        to be copied (counting from 0).
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
        
    
    Outputs:
    -------
    
    Frame : Numpy array
        Frame from PixArr.
    """
    
    import numpy as np
    from DicomTools import GetDicomSOPuids
    from DicomTools import GetRoiNum
    
    # Determine which segment contains the segmentation to be copied, and
    # the corresponding frame number in the pixel array:
    """ Note:  SegNum is equivalent to SegmentNumber in SegmentSequence. """
    SegNum = GetRoiNum(Seg, SearchString)
    
    SOPuids = GetDicomSOPuids(DicomDir)
    
    PFFGStoSliceIndsBySeg = GetPFFGStoSliceIndsBySeg(Seg, SOPuids)
    
    PFFGStoSliceIndsInSeg = PFFGStoSliceIndsBySeg[SegNum]
    
    # The number of frames in the segment of interest:
    F = len(PFFGStoSliceIndsInSeg)
    
    # Get the number of rows and columns required for Frames:
    PixArr = Seg.pixel_array
    
    if len(PixArr.shape) < 3:
        """ This is a single-frame PixArr, i.e. shape (1, R, C). """
        R, C = PixArr.shape
    else:
        """ This is a multi-frame PixArr, i.e. shape (AllF, R, C). """
        AllF, R, C = PixArr.shape
    
    Frames = np.zeros((F, R, C), dtype='uint')
    
    for f in range(F):
        SliceNum = PFFGStoSliceIndsInSeg[f]
        
        Frame = GetFrameFromPixArr(Seg, DicomDir, SearchString, SliceNum, 
                                   LogToConsole)
        
        Frames[f] = Frame
    
    if LogToConsole:
        print('\n\n***Result from GetFramesFromPixArr:')
        print(f'   There are {F} frames in the segment matching',
              f'"{SearchString}".')
        print(f'   PFFGStoSliceIndsInSeg = {PFFGStoSliceIndsInSeg}')
        print(f'   PixArr.shape = {PixArr.shape}')
        if len(PixArr.shape) > 2:
            [print(f'   np.amax(PixArr[{i}]) = {np.amax(PixArr[i])}') for i in range(PixArr.shape[0])]
        else:
            print(f'   np.amax(PixArr) = {np.amax(PixArr)}')
        print(f'   Frames.shape = {Frames.shape}')
        if len(Frames.shape) > 2:
            [print(f'   np.amax(Frames[{i}]) = {np.amax(Frames[i])}') for i in range(Frames.shape[0])]
        else:
            print(f'   np.amax(Frames) = {np.amax(Frames)}')
            
    return Frames








def GetPixArrInSeg(Seg, DicomDir, SearchString):
    """
    Get the frames in a SEG's pixel array that belong to a segment with
    specified label.
    
    Inputs:
    ------
    
    Seg : Pydicom object
        SEG object.
        
    DicomDir : string 
        Directory containing the corresponding DICOMs.
        
    SearchString : string
        All or part of the Segment Label containing the segment of interest.
                       
                            
    Outputs:
    -------
    
    PixArrInSeg : Numpy array
        Sub-array of the SEG's pixel array that contains the frames that belong
        to the segment of interest. 
        
    PFFGStoSliceIndsInSeg : List of integers
        List (for each segmentation) of the slice numbers that correspond to 
        each frame in PixArr.
    """
    
    import numpy as np
    
    AllPixArr = Seg.pixel_array
    
    AllF, R, C = AllPixArr.shape
    
    # Get the frame numbers of the SEG's pixel array that correspond to the 
    # segment of interest, and the corresponding Per-frame Functional Groups
    # Sequence-to-slice indices:
    FrameNumsInSeg, PFFGStoSliceIndsInSeg = GetFrameNums(Seg, SearchString, 
                                                         DicomDir)
    
    F = len(FrameNumsInSeg)
    
    PixArrInSeg = np.zeros((F, R, C), dtype='uint')
    
    for i in range(F):  
        PixArrInSeg[i] = AllPixArr[FrameNumsInSeg[i]]
    
        
    return PixArrInSeg, PFFGStoSliceIndsInSeg








def AddCopiedPixArr(OrigPixArr, OrigPFFGStoSliceInds, 
                    PixArrToAdd, PFFGStoSliceIndsToAdd):
    """
    Add frame(s) from a pixel array to an existing pixel array.
       
    
    Inputs:
    ------
    
    OrigPixArr : Numpy array
        A FxRxC (Frames x Rows x Columns) array of all frames that belong to
        the segment of interest. 
        
    OrigPFFGStoSliceInds : list of integers
        List (for each segmentation) of slice numbers that correspond to each 
        frame in OrigPixArr.
        
    PixArrToAdd : Numpy array
        A FxRxC (Frames x Rows x Columns) array of all frames that originated
        from a single segmentation.  F will be one if a single segmentation is
        to be copied, but may be greater than one, if, for example, the 
        segmentation to be copied was resampled to a number of segmentations.
        
    PFFGStoSliceIndsToAdd : list of integers
        List (for each segmentation) of slice numbers that correspond to each 
        frame in PixArrToAdd.
        
        
    Outputs:
    -------
    
    NewPixArr : Numpy array
        A FxRxC (Frames x Rows x Columns) array of all frames in 
        OrigPixArrInSeg and PixArrToAddToSeg. Note that F will not necessarily
        be the sum of the number of frames in OrigPixArrInSeg and 
        PixArrToAddToSeg.  Some frames in both pixel arrays may correspond
        to the same slice number, in which case, any duplicate frame(s) in
        OrigPixArrInSeg will be over-written with the frame(s) in
        PixArrToAddToSeg that correspond to the same slice number.
        
    NewPFFGStoSliceInds : list of integers
        Modified list (for each segmentation) of slice numbers that correspond   
        to each frame in NewPixArr.
    """
    
    import numpy as np
    from GeneralTools import UniqueItems
    
    # Combine OrigPFFGStoSliceInds and PFFGStoSliceIndsToAdd:
    NewPFFGStoSliceInds = OrigPFFGStoSliceInds + PFFGStoSliceIndsToAdd
    
    # Remove any duplicate slice numbers:
    NewPFFGStoSliceInds = UniqueItems(NewPFFGStoSliceInds)
    
    F = len(NewPFFGStoSliceInds)
    
    OrigF, R, C = OrigPixArr.shape
    
    NewPixArr = np.zeros((F, R, C), dtype='uint')
    
    for FrameNum in range(F):
        # The corresponding slice number for this frame:
        SliceNum = NewPFFGStoSliceInds[FrameNum]
        
        if SliceNum in PFFGStoSliceIndsToAdd:
            """
            This frame is to be over-written by the corresponding frame in
            PixArrToAdd.
            """
            
            ind = PFFGStoSliceIndsToAdd.index(SliceNum)
            
            NewPixArr[FrameNum] = PixArrToAdd[ind]
            
        else:
            """
            This existing frame (in OrigPixArr) is to be preserved.
            """
            
            ind = OrigPFFGStoSliceInds.index(SliceNum)
            
            NewPixArr[FrameNum] = OrigPixArr[ind]
    
    
    return NewPixArr, NewPFFGStoSliceInds










def InitialiseSeg(SegTemplate, SearchString, PFFGStoSliceInds, DicomDir, 
                  NamePrefix='', LogToConsole=False):
    """
    Initialise a SEG object based on an existing SEG object (SegTemplate).
         
    
    Inputs:
    ------
    
    SegTemplate : Pydicom object
        SEG object that will be used as a template to create the new object.

    SearchString : string
        All or part of the SegmentLabel of the segment of interest. 
        
    PFFGStoSliceInds : List of integers
        List (for each segmentation) of the slice numbers that correspond to 
        each frame in the SEG's pixel array.
                    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
    NamePrefix : string (optional; '' by default)
        Prefix to be added to the assigned filename (after the DateTime stamp), 
        e.g. 'Case3b-i'.
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Output:
    ------
        
    Seg : Pydicom object
        New SEG object.
    """
    
    from pydicom.uid import generate_uid
    import time
    from copy import deepcopy
    from DicomTools import GetRoiNum
    from DicomTools import GetDicomFpaths
    from DicomTools import ImportDicom
    from ImageTools import GetImageAttributes
    
    Dicom = ImportDicom(DicomDir)
    
    NumOfDicoms = len(GetDicomFpaths(DicomDir))
    
    Size, Spacings, ST,\
    IPPs, Dirs = GetImageAttributes(DicomDir=DicomDir, Package='sitk')
    
    SegNum = GetRoiNum(SegTemplate, SearchString)
    
    # The Segment Label of the segment containing the segmentation to be 
    # copied:
    SegLabel = SegTemplate.SegmentSequence[SegNum].SegmentLabel
    
    #print(f'\n\n***SegLabel = {SegLabel}')
    
    # Use SegTemplate as a template for Seg:
    Seg = deepcopy(SegTemplate)
    
    # Generate a new SOPInstance UID:
    Seg.SOPInstanceUID = generate_uid()
    
    # Generate a new SeriesInstance UID:
    Seg.SeriesInstanceUID = generate_uid()
    
    Seg.file_meta.MediaStorageSOPInstanceUID = deepcopy(Seg.SOPInstanceUID) # 18/12
    
    
    """Added on 16/12 to see if it solves the issues for UseCases 2b and 3b-i.
    It didn't resolve the issue.
    
    # Generate a new DimensionOrganizationUID:
    Seg.DimensionOrganizationSequence[0].DimensionOrganizationUID = generate_uid()
    
    # Set the DimensionOrganizationUIDs in DimensionIndexSequence to the new
    # uid:
    DOuid = deepcopy(Seg.DimensionOrganizationSequence[0].DimensionOrganizationUID)
    
    DIS = deepcopy(Seg.DimensionIndexSequence)
    
    for i in range(len(DIS)):
        Seg.DimensionIndexSequence[i].DimensionOrganizationUID = DOuid
    
    end of code added on 16/12."""
    
    # Modify the Series Description:
    #if 'SEG' in NamePrefix:
    #    SD = NamePrefix + '_from_' + Seg.SeriesDescription
    #else:
    #    SD = NamePrefix + '_SEG_from_' + Seg.SeriesDescription
        
    #Seg.SeriesDescription = SD
    Seg.SeriesDescription = NamePrefix
    
    # Modify the Content Date and Time to the present:
    NewDate = time.strftime("%Y%m%d", time.gmtime())
    NewTime = time.strftime("%H%M%S", time.gmtime())
    
    Seg.ContentDate = NewDate
    Seg.ContentTime = NewTime
    
    
    
    # Modify various tags to match the values in Dicoms:
    Seg.StudyDate = Dicom.StudyDate
    Seg.SeriesDate = Dicom.SeriesDate
    #Seg.ContentDate = Dicom.ContentDate
    Seg.StudyTime = Dicom.StudyTime
    Seg.SeriesTime = Dicom.SeriesTime
    #Seg.ContentTime = Dicom.ContentTime
    
    Seg.ReferencedSeriesSequence[0]\
       .SeriesInstanceUID = Dicom.SeriesInstanceUID # 15/12/20
    
    Seg.PatientName = Dicom.PatientName
    Seg.PatientID = Dicom.PatientID
    Seg.PatientBirthDate = Dicom.PatientBirthDate
    Seg.PatientSex = Dicom.PatientSex
    Seg.PatientAge = Dicom.PatientAge
    Seg.StudyInstanceUID = Dicom.StudyInstanceUID
    
    #Seg.StudyID = Dicom.StudyID # Leave StudyID unchanged (22/12/20)
    
    Seg.FrameOfReferenceUID = Dicom.FrameOfReferenceUID
    Seg.NumberOfFrames = f"{len(PFFGStoSliceInds)}"
    Seg.Rows = Dicom.Rows
    Seg.Columns = Dicom.Columns
    
    Seg.SharedFunctionalGroupsSequence[0]\
       .PlaneOrientationSequence[0]\
       .ImageOrientationPatient = Dicom.ImageOrientationPatient
       
    """ 
    Notes:
        
    1. The SliceThickness appears to be the z-Spacing rather than the
    SliceThickness from the DICOM metadata. 
    
    2. The character limit of VR DS is 16 characters.
    """
    Zspacing = f"{Spacings[2]}"
    
    if len(Zspacing) > 16:
        Zspacing = Zspacing[:16]
    
    Seg.SharedFunctionalGroupsSequence[0]\
       .PixelMeasuresSequence[0]\
       .SliceThickness = Zspacing
    
    Seg.SharedFunctionalGroupsSequence[0]\
       .PixelMeasuresSequence[0]\
       .SpacingBetweenSlices = Zspacing

    Seg.SharedFunctionalGroupsSequence[0]\
       .PixelMeasuresSequence[0]\
       .PixelSpacing = Dicom.PixelSpacing
       
       
    """ 
    Modify the number of sequences in ReferencedInstanceSequence (RIS). 
    The number of sequences RIS should be equal to the number of DICOMs.
    """
    # The original and required number of sequences in 
    # ReferencedInstanceSequence:
    OrigRIS = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)

    ReqRIS = NumOfDicoms
    
    # Add/remove sequences by appending/popping the last sequence N times, 
    # where N is the difference between ReqRIS and OrigRIS:
    if ReqRIS > OrigRIS:
        for i in range(ReqRIS - OrigRIS):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence\
               .append(deepcopy(Seg.ReferencedSeriesSequence[0]\
                                   .ReferencedInstanceSequence[-1]))          
    else:
        for i in range(OrigRIS - ReqRIS):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence.pop()
    
    
    """ 
    Modify the number of sequences in SegmentSequence. 
    There must be only one. Preserve the sequence that relates to the segment
    of interest and remove any others.
    """
    
    # Over-write the first SegmentSequence with the sequence to be preserved:
    Seg.SegmentSequence[0] = deepcopy(Seg.SegmentSequence[SegNum])
    
    OrigSS = len(Seg.SegmentSequence)
    
    ReqSS = 1
    
    if OrigSS > ReqSS:
        for i in range(OrigSS - ReqSS):
            Seg.SegmentSequence.pop()
    
    
    """ 
    Modify the number of sequences in Per-FrameFunctionGroupsSequence. 
    The number of sequences must be equal to the length of PFFGStoSliceInds.
    """

    OrigPFFGS = len(Seg.PerFrameFunctionalGroupsSequence)
    
    ReqPFFGS = len(PFFGStoSliceInds)
    
    if ReqPFFGS > OrigPFFGS:
        for i in range(ReqPFFGS - OrigPFFGS):
            Seg.PerFrameFunctionalGroupsSequence\
               .append(deepcopy(Seg.PerFrameFunctionalGroupsSequence[-1]))          
    else:
        for i in range(OrigPFFGS - ReqPFFGS):
            Seg.PerFrameFunctionalGroupsSequence.pop()

    
    
    #print(f'\n\n***Seg.SegmentSequence[0].SegmentLabel before change = {Seg.SegmentSequence[0].SegmentLabel}')
    
    """ 
    Modify the Segment Label to SegLabel.
    """
    Seg.SegmentSequence[0].SegmentLabel = SegLabel # 09/12/2020
    
    #print(f'\n\n***Seg.SegmentSequence[0].SegmentLabel after change = {Seg.SegmentSequence[0].SegmentLabel}')
    
    
    
    """
    Output some results to the console.
    """
    if True:#LogToConsole:       
        NewRIS = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
        
        NewSS = len(Seg.SegmentSequence)
        
        NewPFFGS = len(Seg.PerFrameFunctionalGroupsSequence)
        
        print(f'\nThere are {ReqRIS} DICOMs and there were {OrigRIS}',
              f'sequences in ReferencedSeriesSequence. Now there are {NewRIS}',
              'sequences.')
        
        print(f'\nThere were {OrigSS} sequences in SegmentSequence.',
              f'Now there are {NewSS} sequences.')
        
        print(f'\nThere are {ReqPFFGS} segmentations and there were',
              f'{OrigPFFGS} sequences in PerFrameFunctionalGroupsSequence.',
              f'Now there are {NewPFFGS} sequences.')
        
    return Seg

    
    
    







def ModifySeg(Seg, PixArr, PFFGStoSliceInds, DicomDir, LogToConsole=False):
    """
    Modify various tag values of a SEG so that they are consistent with the
    corresponding tag values of the DICOMs.
         
    
    Inputs:
    ------
                              
    Seg : Pydicom object
        The SEG ROI object to modify.
     
    PixArr : Numpy array
        The SEG's pixel array.
    
    PFFGStoSliceInds : List of integers
        List of slice numbers that correspond to each frame in PixArr.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
                         
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Output:
    ------
        
    Seg : Pydicom object
        Modified SEG ROI object.
    """
    
    from DicomTools import ImportDicoms
    from pydicom.pixel_data_handlers.numpy_handler import pack_bits
    import numpy as np
    
    F, R, C = PixArr.shape
    
    #if F == 0:
    #    PixArr = np.reshape(PixArr, (1, R, C))
    #    
    #    F, R, C = PixArr.shape
    
    print(f'\n\n\n*****PixArr.shape = {PixArr.shape}')
    
    P = len(PFFGStoSliceInds)
    
    if not F == P:
        raise Exception(f"There are {F} frames in PixArr and {P} indices in "\
                        + "PFFGStoSliceInds. They must be equal.")
    
    
    Dicoms = ImportDicoms(DicomDir)
    
    RIS = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
             
    if not RIS == len(Dicoms):
        raise Exception(f"There are {len(Dicoms)} DICOMs and {RIS} sequences "\
                        + "in ReferencedInstanceSequence. They must be equal.")
    
    # Modify ReferencedInstanceSequence:
    for i in range(len(Dicoms)):
        Seg.ReferencedSeriesSequence[0]\
           .ReferencedInstanceSequence[i]\
           .ReferencedSOPInstanceUID = Dicoms[i].SOPInstanceUID
    
    
    Seg.NumberOfFrames = f"{F}"
    
    # Modify SegmentSequence:
    Seg.SegmentSequence[0].SegmentNumber = 1
    
    # Get the ReferencedSOPInstanceUIDs in the ReferencedInstanceSequence:
    RefSOPs = GetRSOPuidsInRIS(Seg)
    
    # Modify PerFrameFunctionalGroupsSequence:
    for i in range(P):
        # The slice index for the i^th sequence:
        s = PFFGStoSliceInds[i]
        
        if LogToConsole:
            print('\n\nResults of ModifySeg:')
            print(f'   PFFGStoSliceInds[{i}] = {PFFGStoSliceInds[i]}')
            print(f'   DICOM slice number = {s}')
        
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .DerivationImageSequence[0]\
           .SourceImageSequence[0]\
           .ReferencedSOPInstanceUID = Dicoms[s].SOPInstanceUID
        
        # Modify the DimensionIndexValues (DIVs), ImagePositionPatient and
        # ReferencedSegmentNumber:
        """
        Since there is always only one segment, the first integer in the DIV 
        will always be 1, as is the Referenced Segment Number. The second 
        integer will be the 1 + the index of the SOP Instance UID for the s^th 
        DICOM within RefSOPs (+1 since ind is an integer counting from 0, 
        whereas the DIVs are integers counting from 1).
        """
        ind = RefSOPs.index(Dicoms[s].SOPInstanceUID)
        
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .FrameContentSequence[0]\
           .DimensionIndexValues = [1, ind + 1]
        
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .PlanePositionSequence[0]\
           .ImagePositionPatient = Dicoms[s].ImagePositionPatient
           
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .SegmentIdentificationSequence[0]\
           .ReferencedSegmentNumber = 1
           
        if LogToConsole:
              print(f'   DimensionIndexValues = {[1, ind + 1]}')
              print(f'   ReferencedSegmentNumber = {1}')
              
        
        
    
    
    if LogToConsole:
        print('\n   Prior to ravelling and packing bits:')
        print(f'   PixArr.shape = {PixArr.shape}')
        [print(f'   np.amax(PixArr[{i}]) = {np.amax(PixArr[i])}') for i in range(PixArr.shape[0])]
    
    

    # Ravel (to 1D array) PixArr and pack bits (see
    # https://github.com/pydicom/pydicom/issues/1230):
    packed = pack_bits(PixArr.ravel())
    
    # Convert PixArr to bytes:
    #Seg.PixelData = PixArr.tobytes() <-- doesn't work
    Seg.PixelData = packed + b'\x00' if len(packed) % 2 else packed
    
    
    if False:
        F, R, C = PixArr.shape
        
        # If there are more than one frames in PixArr:
        if F > 1:
            # Ravel (to 1D array) PixArr and pack bits (see
            # https://github.com/pydicom/pydicom/issues/1230):
            packed = pack_bits(PixArr.ravel())
            
            # Convert PixArr to bytes:
            Seg.PixelData = packed + b'\x00' if len(packed) % 2 else packed
            
            if LogToConsole:
                print(f'\n   len(packed) = {len(packed)}') 
                """ 
                = 39936 for UseCase 1a
                = 6656 for UseCase 1b
                """
        else:
            # Convert PixArr to bytes:
            #Seg.PixelData = PixArr.tobytes()
            
            #if LogToConsole:
                #print(f'\n   len(PixArr.tobytes()) = {len(PixArr.tobytes())}') 
                #""" 
                #=  for UseCase 1a
                #= 212992 for UseCase 1b
                #"""
            
            #PixArr = np.reshape(PixArr, (R, C))
            
            if LogToConsole:
                print('\n   There is only one frame in PixArr, so it was reshaped',
                      f'to shape {PixArr.shape}')
                print(f'   np.amax(PixArr) = {np.amax(PixArr)}')
            
            # Ravel (to 1D array) PixArr and pack bits (see
            # https://github.com/pydicom/pydicom/issues/1230):
            packed = pack_bits(PixArr.ravel())
            
            # Convert PixArr to bytes:
            Seg.PixelData = packed + b'\x00' if len(packed) % 2 else packed
            
            if LogToConsole:
                print(f'\n   len(packed) = {len(packed)}') 
                """ 
                = 39936 for UseCase 1a
                = 6656 for UseCase 1b
                """
        
        
    
    
    
    if LogToConsole:
        print(f'\n   len(packed) = {len(packed)}') 
        """ 
        = 39936 for UseCase 1a
        = 6656 for UseCase 1b
        """
                
        PixArr2 = Seg.pixel_array
        
        print('\n   After packing bits:')
        print(f'   PixArr2.shape = {PixArr2.shape}')
        if len(PixArr2.shape) > 2:
            [print(f'   np.amax(PixArr2[{i}]) = {np.amax(PixArr2[i])}') for i in range(PixArr2.shape[0])]
        else:
            print(f'   np.amax(PixArr2) = {np.amax(PixArr2)}')
    
                                          
    return Seg