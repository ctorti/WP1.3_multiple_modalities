# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:12:23 2020

@author: ctorti
"""


"""
ROI copying tools



Make a Direct or Relationship-preserving copy of a single contour/segmentation 
in a given ROI/segment in a Source RTS/SEG for a given slice to one or more
contours/segmentations in a new (if making a relationship-preserving copy) or 
existing (if making a direct copy) ROI/segment in a new Target RTS/SEG either 
using the original Target RTS/SEG (if one has been provided) or using the 
Source RTS/SEG (if a Target RTS/SEG was not provided) as a template.  

For Direct copies the in-plane coordinates (currently the (x,y) coords) will be
preserved only, whilst for a Relationship-preserving copy, all coordinates are 
spatially preserved.

There are five possible Main Use Cases (indicated by the numbers 1 to 5)
and two Sub-cases (indicated by the letters a or b) that apply for a subset
of the Main Use Cases that are accommodated.  The characters i and ii will 
further split Main Use Case #3 into two: i for a sub-case that considers a
copy from a high to low voxel sampling image, and ii for the sub-case that
considers a copy from a low to a high voxel sampling image.  In all cases a 
single contour/segmentation will be copied from the Source RTS/SEG within the 
ROI/segment collection containing the ROIName/SegmentLabel that matches the
characters in a search string (FromSearchString):

1a. Direct copy of the Source contour/segmentation on slice FromSliceNum to a 
    new/existing ROI/segment for slice ToSliceNum in Target. 
    The Source and Target images are the same. 

1b. Relationship-preserving copy of the Source contour/segmentation on slice 
    FromSliceNum to a new ROI/segment for slice ToSliceNum in Target. 
    The Source and Target images are the same. 
    
2a. Direct copy of the Source contour/segmentation on slice FromSliceNum to a 
    new/existing ROI for slice ToSliceNum in Target. 
    The Source and Target images have the same FOR, IOP, IPP, and VS.

2b. Relationship-preserving copy of the Source contour/segmentation on slice 
    FromSliceNum to a new ROI/segment for slice ToSliceNum in Target. 
    The Source and Target images have the same FOR, IOP, IPP, and VS. 

3a. Direct copy of the Source contour/segmentation on slice FromSliceNum to a 
    new/existing ROI/segment for slice ToSliceNum in Target. 
    The Source and Target images have the same FOR and IOP but have 
    different VS (they will likely also have different IPP).
    
3b. Relationship-preserving copy of the Source contour/segmentation on slice 
    FromSliceNum to a new ROI/segment for any number of slices in Target.
    The Source and Target images have the same FOR and IOP but have 
    different VS (they will likely also have different IPP).

4.  Relationship-preserving copy of the Source contour/segmentation on slice 
    FromSliceNum to a new ROI/segment for any number of slices in Target.
    The Source and Target images have the same FOR but have different IOP 
    and IPP, and possibly different VS.
   
5.  Relationship-preserving copy of the Source contour/contour on slice 
    FromSliceNum to a new ROI/segment for any number of slices in Target.
    The Source and Target images have different FOR, likely different IPP and 
    IOP, and possibly different VS.
    
FOR = FrameOfReferenceUID, IPP = ImagePositionPatient, 
IOP = ImageOrientationPatient, VS = Voxel spacings
"""




"""
******************************************************************************
******************************************************************************
WHICH USE CASE APPLIES?
******************************************************************************
******************************************************************************
"""

def WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, LogToConsole=False):
    """
    Determine which of 5 Use Cases applies.
    
    Inputs:
    ------
    
    SrcDcmDir : string
        Directory containing the Source DICOMs.
                       
    TrgDcmDir : string
        Directory containing the Target DICOMs.
                            
    ToSliceNum : integer
        Slice index within the Target DICOM stack where the segmentation is to
        be copied to (counting from 0).  This only applies for Direct copies.
                        
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.

              
    Outputs:
    ------
        
    UseCase : string
        String that denotes the Use Case that applies.
    """
    
    from DicomTools import GetDicomUids
    from ImageTools import GetImageAttributes
    from GeneralTools import AreListsEqualToWithinEpsilon
    
    # Get the DICOM UIDs:
    SrcStudyuid, SrcSeriesuid, SrcFORuid,\
    SrcSOPuids = GetDicomUids(DicomDir=SrcDcmDir)
    
    TrgStudyuid, TrgSeriesuid, TrgFORuid,\
    TrgSOPuids = GetDicomUids(DicomDir=TrgDcmDir)
    
    if LogToConsole:
        print(f'\nToSliceNum = {ToSliceNum}')
        print(f'len(TrgSOPuids) = {len(TrgSOPuids)}')
        
    if ToSliceNum:
        if ToSliceNum > len(TrgSOPuids) - 1:
            msg = f'The input argument "ToSliceNum" = {ToSliceNum} (zero-'\
                  + 'indexed) exceeds the number of Target DICOMs '\
                  + f'({len(TrgSOPuids)}).'
            
            raise Exception(msg)
    
    
    # Get the Image Attributes for Source and Target using SimpleITK:
    SrcSize, SrcSpacing, SrcST, SrcIPPs,\
    SrcDirs = GetImageAttributes(DicomDir=SrcDcmDir, Package='sitk')
    
    TrgSize, TrgSpacing, TrgST, TrgIPPs,\
    TrgDirs = GetImageAttributes(DicomDir=TrgDcmDir, Package='sitk')
    
    # Are the Source and Target part of the same study, series and do they have
    # the same SOP UIDs?
    if SrcStudyuid == TrgStudyuid:
        SameStudy = True
    else:
        SameStudy = False
        
    if SrcSeriesuid == TrgSeriesuid:
        SameSeries = True
    else:
        SameSeries = False
        
    if SrcFORuid == TrgFORuid:
        SameFOR = True
    else:
        SameFOR = False
        
    if SrcSOPuids == TrgSOPuids:
        SameSOPs = True
    else:
        SameSOPs = False
    
    # Are the Source and Target spacings, directions and origins equal to  
    # within 1e-06?
    SameSpacings = AreListsEqualToWithinEpsilon(SrcSpacing, TrgSpacing)
    SameDirs = AreListsEqualToWithinEpsilon(SrcDirs, TrgDirs)
    SameOrigins = AreListsEqualToWithinEpsilon(SrcIPPs[0], TrgIPPs[0])
    SameST = AreListsEqualToWithinEpsilon([SrcST], [TrgST])
    
    if SrcSize == TrgSize:
        SameSize = True
    else:
        SameSize = False
    
        
    # Check which case follows:
    if SameFOR:
        if SameDirs:
            if SameSpacings and SameOrigins:
                if SameSeries:
                    if isinstance(ToSliceNum, int):
                        UseCase = '1a' # Direct copy
                    else:
                        UseCase = '1b' # Relationship-preserving copy
                else:
                    if isinstance(ToSliceNum, int):
                        UseCase = '2a' # Direct copy
                    else:
                        UseCase = '2b' # Relationship-preserving copy
            else:
                if isinstance(ToSliceNum, int):
                    UseCase = '3a' # Direct copy
                else:
                    UseCase = '3b' # Relationship-preserving copy
        else:
            """ May need to break UseCase 4 into a and b for Direct and
            Relationship-preserving copies. """
            UseCase = '4'
    else:
        """ May need to break UseCase 5 into a and b for Direct and
        Relationship-preserving copies. """
        UseCase = '5'
    
        
    # Print comparisons to the console:    
    if LogToConsole:
        #CompareImageAttributes(SrcDcmDir, TrgDcmDir)
        
        print('\n\nThe Source and Target are in the/have:')
        
        if SameStudy:
            print('\n   same study')
        else:
            print('\n   different studies')
        
        if SameFOR:
            print('\n   same Frame of Reference')
        else:
            print('\n   different Frames of Reference')
            
        if SameSeries:
            print('\n   same series')
        else:
            print('\n   different series')
            
        if SameSOPs:
            print('\n   same DICOMs')
        else:
            print('\n   different DICOMs')
        
        if SameSize:
            print('\n   same image size\n',
                  f'      Source/Target: {SrcSize}')
        else:
            print('\n   different image sizes:\n',
                  f'      Source: {SrcSize} \n',
                  f'      Target: {TrgSize}')
        
        if SameSpacings:
            print('\n   same voxel sizes\n',
                  f'      Source/Target: {SrcSpacing}')
        else:
            print('\n   different voxel sizes:\n',
                  f'      Source: {SrcSpacing} \n',
                  f'      Target: {TrgSpacing}')
        
        if SameST:
            print('\n   same slice thickness\n',
                  f'      Source/Target: {SrcST}')
        else:
            print('\n   different slice thickness:\n',
                  f'      Source: {SrcST} \n',
                  f'      Target: {TrgST}')
        
        if SameOrigins:
            print('\n   same origin\n',
                  f'      Source/Target: {SrcIPPs[0]}')
        else:
            print('\n   different origins:\n',
                  f'      Source: {SrcIPPs[0]} \n',
                  f'      Target: {TrgIPPs[0]}')
            
        if SameDirs:
            print('\n   same patient orientation\n',
                  f'      Source/Target: [{SrcDirs[0]}, {SrcDirs[1]}, {SrcDirs[2]},\n',
                  f'                      {SrcDirs[3]}, {SrcDirs[4]}, {SrcDirs[5]},\n',
                  f'                      {SrcDirs[6]}, {SrcDirs[7]}, {SrcDirs[8]}]')
        else:
            print('\n   different patient orientations:\n',
                  f'      Source: [{SrcDirs[0]}, {SrcDirs[1]}, {SrcDirs[2]},\n',
                  f'               {SrcDirs[3]}, {SrcDirs[4]}, {SrcDirs[5]},\n',
                  f'               {SrcDirs[6]}, {SrcDirs[7]}, {SrcDirs[8]}]\n',
                  f'      Target: [{TrgDirs[0]}, {TrgDirs[1]}, {TrgDirs[2]},\n',
                  f'               {TrgDirs[3]}, {TrgDirs[4]}, {TrgDirs[5]},\n',
                  f'               {TrgDirs[6]}, {TrgDirs[7]}, {TrgDirs[8]}]')
        
        
    return UseCase






"""
******************************************************************************
******************************************************************************
COPY A CONTOUR
******************************************************************************
******************************************************************************
"""

def CopyRts(SrcRts, FromSearchString, SrcDcmDir, FromSliceNum, TrgDcmDir,
            TrgRts=None, ToSliceNum=None, AddText='', LogToConsole=False):
    """
    
    Inputs:
    ------
    
    SrcRts : Pydicom object
        Source RTS object.
                             
    FromSearchString : string
        All or part of the Source ROI Name of the ROI containing the contour to
        be copied.
    
    SrcDcmDir : string
        Directory containing the Source DICOMs.
                            
    FromSliceNum : integer
        Slice index of the Source DICOM stack corresponding to the contour to
        be copied (counting from 0).
    
    TrgDcmDir : string
        Directory containing the Target DICOMs.
        
    TrgRts : Pydicom object (optional; None by default)
        Target RTS object that the contour is to be copied to. TrgRts is only 
        non-None if a Direct copy of the contour is to be made and added to 
        existing Direct-copied contour(s).     
        
    ToSliceNum : integer (optional; None by default)
        Slice index within the Target DICOM stack where the contour is to
        be copied to (counting from 0).  This only applies for Direct copies,
        hence the default value None.
    
    AddText : string (optional, '' by default)
        Sting of text to pass to ModifyRts/ModifySeg to be used when generating
        a filename for the new Target RTS/SEG.
                           
    LogToConsole : boolean (default False)
        Denotes whether some results will be logged to the console.
          
                  
    Outputs:
    -------
        
    TrgRts : Pydicom object
        The new (if making a Relationship-preserving copy) or the modified (if
        making a Direct copy of a contour to an existing Direct-copied contour)
        Target RTS object.
    """
    
    import importlib
    import RtsTools
    importlib.reload(RtsTools)
    import ConversionTools
    importlib.reload(ConversionTools)
    import GeneralTools
    importlib.reload(GeneralTools)
    
    from copy import deepcopy
    from GeneralTools import PrintTitle
    from GeneralTools import UniqueItems
    from DicomTools import GetRoiNum
    from RtsTools import GetPtsInContour
    from GeneralTools import GetPixelShiftBetweenSlices
    from GeneralTools import ShiftFrame
    from GeneralTools import MeanPixArr
    from RtsTools import InitialiseRts
    from RtsTools import ModifyRts
    
    # Set the threshold level for binarising of the transformed labelmap (for
    # UseCase 5):
    Thresh = 0.1
    
    # Verify that FromSearchString exists:
    #SrcRoiLabels = GetRoiLabels(SrcRts)
    FromRoiNum = GetRoiNum(Roi=SrcRts, SearchString=FromSearchString)
    
    
    PtsToCopy = GetPtsInContour(Rts=SrcRts, DicomDir=SrcDcmDir, 
                                SearchString=FromSearchString, 
                                SliceNum=FromSliceNum)
    
    print(f'\n\nThe contour to be copied from slice {FromSliceNum} has',
          f'{len(PtsToCopy)} points.')# and CStoSliceIndsToCopy =',
          #f'{CStoSliceIndsToCopy}.')
    
    
    # Determine which Use Case applies:
    UseCase = WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, LogToConsole)
    
    if True:#LogToConsole:
        PrintTitle(f'Case {UseCase} applies.')
    
    """
    **************************************************************************
    What follows is UseCase-specific.
    **************************************************************************
    """
    
    if 'a' in UseCase:
        from RtsTools import GetPtsInRoi
        from RtsTools import AddCopiedPtsByCnt
        from ImageTools import GetImageAttributes
        from ConversionTools import Contour2Indices
        from GeneralTools import ChangeZinds
        from ConversionTools import Indices2Points
        
        
    if UseCase in ['1a', '2a']:
        """
        The contour will be copied to a different slice location, so the
        z-components of the coordinates will need to be modified.  For 
        UseCase 3a this operation will be done in index space (i.e. by
        shifting pixels).
        """
        
        SrcSize, SrcSpacings, SrcST,\
        SrcIPPs, SrcDirs = GetImageAttributes(DicomDir=SrcDcmDir)
        
        # Convert PtsToCopy to indices:
        IndsToCopy = Contour2Indices(Points=PtsToCopy, Origin=SrcIPPs[0], 
                                     Directions=SrcDirs, 
                                     Spacings=SrcSpacings, 
                                     Rounding=False)
        
        if LogToConsole:
            print(f'\n\nIndsToCopy prior to changing z-index = {IndsToCopy[:6]}...')
        
        # Modify the z-component (k) of the indices to ToSliceNum:
        IndsToCopy = ChangeZinds(Indices=IndsToCopy, NewZind=ToSliceNum)
        
        if LogToConsole:
            print(f'\n\nIndsToCopy after changing z-index = {IndsToCopy[:6]}...')
        
            print(f'\n\nPtsToCopy prior to changing z-index = {PtsToCopy[:6]}...')
        
        # Convert back to physical points:
        PtsToCopy = Indices2Points(Indices=IndsToCopy, Origin=SrcIPPs[0], 
                                   Directions=SrcDirs, Spacings=SrcSpacings)
        
        if LogToConsole:
            print(f'\n\nPtsToCopy after changing z-index = {PtsToCopy[:6]}...')
        
        """
        Since this is a Direct copy, any existing contours in Target with ROI
        label matching FromSearchString are to be preserved.
        """
        
        # Get all points (by contour) in the Target ROI containing the contour
        # to be copied:
        TrgPtsInRoiByCnt,\
        TrgCStoSliceIndsInRoi = GetPtsInRoi(Rts=TrgRts, 
                                            DicomDir=TrgDcmDir,
                                            SearchString=FromSearchString)
        
        print('\nThe Target ROI containing the contour to be copied has',
              f'{len(TrgPtsInRoiByCnt)} contours. \nTrgCStoSliceIndsInRoi =',
              f'{TrgCStoSliceIndsInRoi}.')
        
        
        """
        PtsToCopy need to be added to previously Direct-copied contour points
        in TrgPtsInRoiByCnt.  The contour-sequence-to-slice-index will be
        [ToSliceNum] rather than [FromSliceNum].
        
        Note:
            Since PtsToCopy is a list of points it needs to be enclosed in []
            so that it is a list (of length 1) of a list of points so that it
            is in the form expected of PtsToAddByCnt.
        """
        
        if LogToConsole:
            print('\n\nInputs to AddCopiedPtsByCnt:')
            print(f'   len(TrgPtsInRoiByCnt) = {len(TrgPtsInRoiByCnt)}')
            [print(f'   len(TrgPtsInRoiByCnt[{i}]) = {len(TrgPtsInRoiByCnt[i])}') for i in range(len(TrgPtsInRoiByCnt))]
            print(f'   TrgCStoSliceIndsInRoi = {TrgCStoSliceIndsInRoi}')
            print(f'   len(PtsToCopy) = {len(PtsToCopy)}')
            print(f'   ToSliceNum = {ToSliceNum}')
        
        
        
        TrgCntDataByCnt,\
        TrgPtsByCnt,\
        TrgCStoSliceInds = AddCopiedPtsByCnt(OrigPtsByCnt=TrgPtsInRoiByCnt, 
                                             OrigCStoSliceInds=TrgCStoSliceIndsInRoi, 
                                             PtsToAddByCnt=[PtsToCopy], 
                                             CStoSliceIndsToAddByCnt=[ToSliceNum],
                                             LogToConsole=LogToConsole)
        
    
    if UseCase in ['1b', '2b']:
        """
        TrgPtsByCnt is simply [PtsToCopy], so that it is a list (of length 1, 
        for the single contour).  Likewise for TrgCntDataByCnt.  The Target
        contour-sequence-to-slice-index will be [FromSliceNum].
        """
        
        from ConversionTools import Points2ContourData
        
        TrgPtsByCnt = [deepcopy(PtsToCopy)]
        
        TrgCntDataByCnt = [Points2ContourData(PtsToCopy)]
        
        #TrgCStoSliceInds = deepcopy(CStoSliceIndsToCopy)
        TrgCStoSliceInds = deepcopy([FromSliceNum])
        
        #print(f'\n\nlen(PtsToCopy) = {len(PtsToCopy)}')
        #print(f'len(TrgPtsByCnt[0]) = {len(TrgPtsByCnt[0])}')
        #print(f'len(TrgCntDataByCnt[0]) = {len(TrgCntDataByCnt[0])}')
        
        
    
    if UseCase in ['3a', '3b', '4', '5']:
        from ImageTools import ImportImage
        from ImageTools import ResampleImage
        from ImageTools import GaussianBlurImage
        from ImageTools import BinaryThresholdImage
        from ImageTools import GetImageInfo
        from ConversionTools import ConvertImagePixelType
        from RtsTools import GetMaskFromRts
        from ConversionTools import PixArr2Image
        from ConversionTools import Image2PixArr
        #from ConversionTools import PixArr2Contours
        from ConversionTools import PixArr2PtsByContour
        
        
        # Import the 3D images:
        SrcIm = ImportImage(SrcDcmDir)
        TrgIm = ImportImage(TrgDcmDir)
        
        
        """
        ***********************************************************************
        Convert the contour to be copied to a 3D labelmap image.
        ***********************************************************************
        """    
        # Convert the contour data to be copied to a 2D mask:
        PixArrToCopy = GetMaskFromRts(Rts=SrcRts, 
                                      SearchString=FromSearchString, 
                                      SliceNum=FromSliceNum, 
                                      DicomDir=SrcDcmDir, 
                                      RefImage=SrcIm)
        
        print(f'\nPixArrToCopy.shape = {PixArrToCopy.shape}')
        
        # Convert PixArrToCopy to a labelmap image:
        LabmapImToCopy = PixArr2Image(PixArr=PixArrToCopy,
                                      FrameToSliceInds=[FromSliceNum],
                                      RefIm=SrcIm)
        
        print(f'\nLabmapImToCopy.GetSize() = {LabmapImToCopy.GetSize()}')
        
    
    if '3' in UseCase:
        
        """ First try resampling the image using a NearestNeighbor 
        interpolation. """
        interp = 'NearestNeighbor'
        
        if True:#LogToConsole:
            print('\nUsing', interp, 'interpolation...')
        
        # Resample LabmapImToCopy to the Target image's grid:
        ResLabmapImToCopy = ResampleImage(Image=LabmapImToCopy, 
                                          RefImage=TrgIm, 
                                          Interpolation=interp)
        
        #print(f'\nResLabmapImToCopy.GetSize() = {ResLabmapImToCopy.GetSize()}')
        
        if True:#LogToConsole:
            print('\nAfter resampling:')
            PixID, PixIDTypeAsStr, UniqueVals,\
            F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
            
        """ 
        If resampling to a smaller grid size aliasing can occur, leading to
        the appearent disappearance of segmentations (i.e. F2Sinds = []). 
        
        Try suggestions from Ziv Yaniv here:
            https://github.com/SimpleITK/SimpleITK/issues/1277
                
        1. Use the sitkLabelGaussian interpolator.
        
        2. Gaussian blur the segmentation, then resample using a linear 
        interpolator, and then threshold so that values in [a<1<b] are mapped
        to 1. You will need to select appropriate values for a, b.
        
        3. Compute the distance map of the segmentation, then resample using a
        linear interpolator, and then threshold the absolute value of the 
        distance map (sitk.Abs(lowres_distance_map)<dist_threshold). Again, you 
        need to select an appropriate dist_threshold.

        Tried:
        
        1. Resulting Gaussian interpolated resampled image had zeros only 
        (the image was converted to float prior to resampling).
        
        2. Works for UseCase 3B-i_SEG with FromSliceNum = 26 with binary
        threshold value of 0.04.
        
        
        Comment from Bradley Lowecamp:
            The implementation of the sitkLabelGaussian interpolator in the 
            ResampleImageFilter sets the sigma to the pixel spacing of the 
            input image to the resample filter. This is why it does not do a 
            better job in reducing aliasing.
        """
        #Workaround = 1
        Workaround = 2
        
        
        if not F2Sinds:
            print('\nThe resampled image has no non-zero frames (e.g. due to',
                  f'aliasing).  \nTry workaround #{Workaround}.')
            
            # Convert LabmapImToCopy from 32-bit unsigned integer to a float:
            LabmapImToCopy = ConvertImagePixelType(Image=LabmapImToCopy, 
                                                   NewPixelType='sitkFloat32')
            
            if True:#LogToConsole:
                print('\nAfter converting to float:')
                PixID, PixIDTypeAsStr, UniqueVals,\
                F2Sinds = GetImageInfo(LabmapImToCopy, LogToConsole=True)
        
            if Workaround == 1:
                print(f'\nTrying workaround #{Workaround}...')
                
                interp = 'Gaussian' # <-- get zeros only (image was converted 
                # to float prior to resampling)
                
                if True:#LogToConsole:
                    print('\nUsing', interp, 'interpolation...')
                    
                # Resample LabmapImToCopy to the Target image's grid:
                ResLabmapImToCopy = ResampleImage(Image=LabmapImToCopy, 
                                                  RefImage=TrgIm, 
                                                  Interpolation=interp)
                
                if True:#LogToConsole:
                    print('\nAfter resampling:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
                    
                    
                """ Will need to convert back to unsigned int and may need to
                do some binary thresholding, but only proceed if there are
                non-zero frames in the resampled image. """
                
                if not F2Sinds:
                    Workaround = 2 # try Workaround #2
                    
                    
            if Workaround == 2:
                print(f'\nTrying workaround #{Workaround}...')
                      
                # Gaussian blur the image:
                LabmapImToCopy = GaussianBlurImage(LabmapImToCopy)
                
                if True:#LogToConsole:
                    print('\nAfter applying Gaussian blur:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(LabmapImToCopy, LogToConsole=True)
                
                if not F2Sinds:
                    Workaround = 3 # try Workaround #3
                    
                # Linearly resample the blurred image:
                interp = 'Linear'
                
                if True:#LogToConsole:
                    print('\nUsing', interp, 'interpolation...')
                    
                # Resample LabmapImToCopy to the Target image's grid:
                ResLabmapImToCopy = ResampleImage(Image=LabmapImToCopy, 
                                                  RefImage=TrgIm, 
                                                  Interpolation=interp)
                
                if True:#LogToConsole:
                    print('\nAfter resampling:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
                
                
                """ Prior to converting back to unsigned integer, must first
                binary threshold the image. """
                # Thresh values with results for Case3B-i_SEG and 
                # FromSliceNum = 26 (max value in Pix array prior to binary
                # thresholding = 0.0468482):
                #Thresh = 0.5 # no frames
                #Thresh = 0.005 # two frames (slices 10 & 11)
                Thresh = 0.04 # one frame (slice 11)
                ResLabmapImToCopy = BinaryThresholdImage(ResLabmapImToCopy, 
                                                         Thresh)
                
                if True:#LogToConsole:
                    print(f'\nAfter binary thresholding with Thresh = {Thresh}:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
            
                
                
            if Workaround == 3:
                print(f'\nTrying workaround #{Workaround}...')
                      
                print('\nStill need to write Workaround 3...')
        
        
        
        """ Ensure that ResLabmapImToCopy is a 32-bit unsigned integer. """
        if not PixID == 5:
            print(f'\nPixelID = {PixID} ({PixIDTypeAsStr})). Converting to',
                  f'unsigned 32-bit integer (sitkUInt32)..')
            
            # Convert ResLabmapImToCopy from float to 32-bit unsigned integer:
            ResLabmapImToCopy = ConvertImagePixelType(Image=ResLabmapImToCopy, 
                                                      NewPixelType='sitkUInt32')
            
            if True:#LogToConsole:
                print('\nAfter converting to 32-bit unsigned int:')
                PixID, PixIDTypeAsStr, UniqueVals,\
                F2Sinds = GetImageInfo(ResLabmapImToCopy, 
                                       LogToConsole=True)
        
        
        
        # Convert ResLabmapImToCopy to a pixel array:
        ResPixArrToCopy,\
        TrgCStoSliceInds = Image2PixArr(LabmapIm=ResLabmapImToCopy)
        
        print(f'\nResPixArrToCopy.shape = {ResPixArrToCopy.shape}')
        
        unique = UniqueItems(Items=ResPixArrToCopy, IgnoreZero=False)
        print(f'\nThere are {len(unique)} unique items in ResPixArrToCopy')
        
        F = ResPixArrToCopy.shape[0]
        
        print(f'\nThe segmentation (from the contour) on slice {FromSliceNum}',
              f'has been resampled to {F} frames (contours).\nTrgCStoSliceInds',
              f'= {TrgCStoSliceInds}.')
        
    
        
    if UseCase == '3a':
        """
        For a Direct copy, one contour/segment is always copied to a single
        contour/segmentation (irrespective of how many frames are in the 
        resampled labelmap-image-to-copy).  So if after resampling there is 
        more than one frame, the frames will be averaged.
        """
        
        if F > 1: 
            print(f'The {F} frames will be averaged...')
            
            # The pixel-by-pixel mean across all frames in ResPixArrToCopy:
            ResPixArrToCopy = MeanPixArr(ResPixArrToCopy)
            
            print(f'\nResPixArrToCopy.shape = {ResPixArrToCopy.shape}')
            
            F = ResPixArrToCopy.shape[0]
            
            print(f'\nResPixArrToCopy now has {F} frames')
        
        
        # Get pixel shift between FromSliceNum in SrcIm and ToSliceNum in 
        # TrgIm in the Target image domain:
        PixShift = GetPixelShiftBetweenSlices(Image0=SrcIm, 
                                              SliceNum0=FromSliceNum, 
                                              Image1=TrgIm,
                                              SliceNum1=ToSliceNum,
                                              RefImage=TrgIm)
        
        print(f'\nPixShift = {PixShift}')
        
        # Shift the the in-plane elements in ResPixArrToCopy:
        ResPixArrToCopy = ShiftFrame(Frame=ResPixArrToCopy, PixShift=PixShift)
        
        unique = UniqueItems(Items=ResPixArrToCopy, IgnoreZero=False)
        print(f'\nThere are {len(unique)} unique items in ResPixArrToCopy',
              'after shifting the frame.')
        
        # Modify TrgCStoSliceInds to reflect the slice to which ResPixArrToCopy
        # relates to:
        TrgCStoSliceInds = deepcopy([ToSliceNum])
        
        
            
    if '3' in UseCase:
        # Convert ResPixArrToCopy to a list of ContourData by contour and a
        # list of points by contour: 
        #TrgCntDataByCnt, TrgPtsByCnt = PixArr2Contours(PixArr=ResPixArrToCopy)
        TrgPtsByCnt,\
        TrgCntDataByCnt = PixArr2PtsByContour(PixArr=ResPixArrToCopy,
                                              FrameToSliceInds=TrgCStoSliceInds,
                                              DicomDir=TrgDcmDir)
        
        """
        03/12/20: The z-coordinates are suspiciously all the same.  Should look
        into this.
        """
        
        print(f'\nAfter converting ResPixArrToCopy to ContourData and points',
              f'TrgCStoSliceInds = {TrgCStoSliceInds}.')
        
        print(f'\nlen(TrgCntDataByCnt) = {len(TrgCntDataByCnt)}')
        print(f'\nlen(TrgPtsByCnt) = {len(TrgPtsByCnt)}')
        
    
    
    if UseCase == '3a':
        if TrgRts:
            """
            Since this is a Direct copy, any existing contours in Target with 
            ROI label matching FromSearchString are to be preserved.
            """
            
            # Get all points (by contour) in the Target ROI containing the 
            # contour to be copied:
            TrgPtsInRoiByCnt,\
            TrgCStoSliceIndsInRoi = GetPtsInRoi(Rts=TrgRts, 
                                                DicomDir=TrgDcmDir,
                                                SearchString=FromSearchString)
            
            print('\nThe Target ROI containing the contour to be copied has',
                  f'{len(TrgPtsInRoiByCnt)} contours. \nTrgCStoSliceIndsInRoi',
                  f'= {TrgCStoSliceIndsInRoi}.')
            
            
            """
            The contour points that arose from ResPixArrToCopy (TrgPtsByCnt)  
            needs to be added to previously Direct-copied contour points 
            TrgPtsInRoiByCnt.
            """
            
            TrgCntDataByCnt,\
            TrgPtsByCnt,\
            TrgCStoSliceInds = AddCopiedPtsByCnt(OrigPtsByCnt=TrgPtsInRoiByCnt, 
                                                 OrigCStoSliceInds=TrgCStoSliceIndsInRoi, 
                                                 PtsToAddByCnt=TrgPtsByCnt, 
                                                 CStoSliceIndsToAddByCnt=TrgCStoSliceInds,
                                                 LogToConsole=LogToConsole)
        else:
            """
            A Target RTS was not provided.
            """
            
            #TrgPtsByCnt = deepcopy()
            #TrgCntDataByCnt = deepcopy()
            #TrgCStoSliceInds = deepcopy()
            
        
    #if UseCase == '4':
    
    
    if UseCase == '5':
        from ImageTools import RegisterImages
        from ImageTools import TransformImage
        from ImageTools import BinaryThresholdImage
    
        # Register the images using an affine transformation:
        RegSrcIm, RegImFilt = RegisterImages(FixIm=TrgIm, MovIm=SrcIm, 
                                             Tx='affine',
                                             LogToConsole=LogToConsole)
        
        # Transform LabmapImToCopy using RegImFilt:
        TxLabmapImToCopy = TransformImage(Im=LabmapImToCopy, 
                                          RegImFilt=RegImFilt,
                                          Interpolation='Nearestneighbor')
        
        """ This isn't required: """
        if False:
            # Store the pre-transformed labelmap image (LabmapImToCopy) and the 
            # pre-binary thresholded labelmap image (TxLabmapImToCopy):
            ListOfLabmapIms = [LabmapImToCopy, TxLabmapImToCopy]
            
            # Convert LabmapImToCopy to a pixel array:
            PixArrToCopy,\
            F2Sinds = Image2PixArr(LabmapIm=LabmapImToCopy)
            
            # Convert TxLabmapImToCopy to a pixel array:
            TxPixArrPreBinary,\
            F2SindsPreBinary = Image2PixArr(LabmapIm=TxLabmapImToCopy)
            
            unique = UniqueItems(Items=TxPixArrPreBinary, IgnoreZero=False)
            print(f'\nThere are {len(unique)} unique items in TxPixArrToCopy',
                  'prior to binary thresholding TxLabmapImToCopy')
        """ end """
        
        
        
        """
        21/12/20:  
            Following the use of a nearestneighbor interpolator when 
            transforming LabmapImToCopy, i.e.:
            
            TxMap[0]["ResampleInterpolator"] = ["FinalNearestNeighborInterpolator"]
            
            it's no longer necessary to perform the binary thresholding step.
            
        # Binary threshold TxLabmapImToCopy:
        TxLabmapImToCopy = BinaryThresholdImage(Im=TxLabmapImToCopy,
                                                Thresh=Thresh)
            
        # Convert TxLabmapImToCopy to a pixel array:
        TxPixArrToCopy,\
        TrgCStoSliceInds = Image2PixArr(LabmapIm=TxLabmapImToCopy)
        
        unique = UniqueItems(Items=TxPixArrToCopy, IgnoreZero=False)
        print(f'\nThere are {len(unique)} unique items in TxPixArrToCopy',
              'after binary thresholding TxLabmapImToCopy')
        """
        
        F = TxPixArrToCopy.shape[0]
        
        print(f'\nThe segmentation (from the contour) on slice {FromSliceNum}',
              f'has been registered to {F} frames (contours):',
              f'{TrgCStoSliceInds}.')
        
        
        if False:
            # Append the post-binary thresholded labelmap image (TxLabmapImToCopy):
            ListOfLabmapIms.append(TxLabmapImToCopy)
            
            # Create lists of the pre-transformed, pre-binary thresholded and 
            # post-binary thresholded pixel arrays and frame-to-slice indices:
            ListOfPixArrs = [PixArrToCopy, TxPixArrPreBinary, TxPixArrToCopy]
            ListOfFrameToSliceInds = [F2Sinds, F2SindsPreBinary, TrgCStoSliceInds]
            ListOfPlotTitles = ['PixArrToCopy', 'TxPixArrToCopyPreBinary', 
                                'TxPixArrToCopyPostBinary']
        
            return ListOfLabmapIms, ListOfPixArrs, ListOfFrameToSliceInds,\
                   ListOfPlotTitles
        
        
        if False:
            import PlottingTools
            importlib.reload(PlottingTools)
            from PlottingTools import Plot_PixelArrays
            
            Plot_PixelArrays(ListOfPixArrs=ListOfPixArrs, 
                             ListOfFrameToSliceInds=ListOfFrameToSliceInds, 
                             ListOfPlotTitles=ListOfPlotTitles)
        
        
            
    
        #return LabmapImToCopy, RegImFilt
        
        
        # Convert TxPixArrToCopy to a list of ContourData by contour and a
        # list of points by contour: 
        #TrgCntDataByCnt, TrgPtsByCnt = PixArr2Contours(PixArr=TxPixArrToCopy)
        TrgPtsByCnt,\
        TrgCntDataByCnt = PixArr2PtsByContour(PixArr=TxPixArrToCopy,
                                              FrameToSliceInds=TrgCStoSliceInds,
                                              DicomDir=TrgDcmDir)
    
    
    
    #if 'a' in UseCase:
    #    """ 
    #    For UseCases 1a/b, 2a/b or 3a, there will always be a single 
    #    ContourImageSequence, and the single index will be slice ToSliceNum. 
    #    Over-write previous TrgCStoSliceInds.
    #    """
    #    
    #    TrgCStoSliceInds = [ToSliceNum]
    #    
    #    print(f'\nTrgCStoSliceInds over-written to {TrgCStoSliceInds}')
    
    
    """ 
    If UseCase is 1a/2a/3a (i.e. a Direct copy is to be made) and a RTS has 
    been provided for Target this is not a clean copy, i.e. the copied contour
    is to be added to an existing ROI containing previously copied contour(s). 
    If a Relationship-preserving copy is to be made or if a Target RTS has not 
    been provided, the Source RTS will be used as a template.
    """
    #if not 'a' in UseCase or not TrgRts:
    #    TrgRts = InitialiseRts(RtsTemplate=SrcRts, RoiNum=FromRoiNum,
    #                           CStoSliceInds=TrgCStoSliceInds, 
    #                           DicomDir=TrgDcmDir, LogToConsole=LogToConsole)
    
    if LogToConsole:
        print('\n\nInputs to InitialiseRts:')
        print(f'   FromRoiNum = {FromRoiNum}')
        print(f'   TrgCStoSliceInds = {TrgCStoSliceInds}')
    
    
    if TrgRts:
        """ Use TrgRts to initialise the Target RTS. """
        TrgRts = InitialiseRts(RtsTemplate=TrgRts, RoiNum=FromRoiNum,
                               CStoSliceInds=TrgCStoSliceInds, 
                               DicomDir=TrgDcmDir, NamePrefix=AddText,
                               LogToConsole=LogToConsole)
    else:
        """ Use SrcRts to initialise the Target RTS. """
        TrgRts = InitialiseRts(RtsTemplate=SrcRts, RoiNum=FromRoiNum,
                               CStoSliceInds=TrgCStoSliceInds, 
                               DicomDir=TrgDcmDir, NamePrefix=AddText,
                               LogToConsole=LogToConsole)
    
    if LogToConsole:
        print('\n\nInputs to ModifyRts:')
        print(f'   len(TrgCntDataByCnt) = {len(TrgCntDataByCnt)}')
        [print(f'   len(TrgCntDataByCnt[{i}]) = {len(TrgCntDataByCnt[i])}') for i in range(len(TrgCntDataByCnt))]
        print(f'   len(TrgPtsByCnt) = {len(TrgPtsByCnt)}')
        [print(f'   len(TrgPtsByCnt[{i}]) = {len(TrgPtsByCnt[i])}') for i in range(len(TrgPtsByCnt))]
        print(f'   TrgCStoSliceInds = {TrgCStoSliceInds}')
    
    # Modify the tags in TrgRts:
    TrgRts = ModifyRts(Rts=TrgRts, CntDataByCnt=TrgCntDataByCnt, 
                       PtsByCnt=TrgPtsByCnt, CStoSliceInds=TrgCStoSliceInds,
                       DicomDir=TrgDcmDir, LogToConsole=LogToConsole)
    
    
    return TrgRts






"""
******************************************************************************
******************************************************************************
COPY A SEGMENTATION
******************************************************************************
******************************************************************************
"""



def CopySeg(SrcSeg, FromSearchString, SrcDcmDir, FromSliceNum, TrgDcmDir,
            TrgSeg=None, ToSliceNum=None, AddText='', LogToConsole=False):
                                
    """
    Inputs:
    ------
    
    SrcSeg : Pydicom object
        Source DICOM SEG object.
                             
    FromSearchString : string
        All or part of the Source Segment Label of the segment containing the 
        segmentation to be copied.
                     
    SrcDcmDir : string
        Directory containing the Source DICOMs.
                            
    FromSliceNum : integer
        Slice index of the Source DICOM stack corresponding to the segmentation
        to be copied (counting from 0).
    
    TrgDcmDir : string
        Directory containing the Target DICOMs.
                 
    TrgSeg : Pydicom object (optional; None by default)
        Target SEG object that the segmentation is to be copied to. TrgSeg is  
        only non-None if a Direct copy of the segmentation is to be made and 
        added to existing Direct-copied segmentation(s).
               
    ToSliceNum : integer (default = None)
        Slice index within the Target DICOM stack where the segmentation is to
        be copied to (counting from 0).  This only applies for Direct copies,
        hence the default value None.
    
    AddText : string (optional, '' by default)
        Sting of text to pass to ModifyRts/ModifySeg to be used when generating
        a filename for the new Target RTS/SEG.
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
          
                  
    Outputs:
    -------
        
    TrgSeg : Pydicom object
        The new (if making a Relationship-preserving copy) or modified (if
        making a Direct copy of a segmentation to an existing Direct-copied 
        contour) Target SEG object.
    """
    
    import importlib
    
    import SegTools
    importlib.reload(SegTools)
    import DicomTools
    importlib.reload(DicomTools)
    import ImageTools
    importlib.reload(ImageTools)
    import GeneralTools
    importlib.reload(GeneralTools)
    import ConversionTools
    importlib.reload(ConversionTools)
    
    from copy import deepcopy
    import numpy as np
    from DicomTools import GetRoiNum
    from SegTools import GetFrameFromPixArr
    from GeneralTools import PrintTitle
    from GeneralTools import UniqueItems
    from ImageTools import ImportImage
    from SegTools import InitialiseSeg
    from SegTools import ModifySeg
    from ImageTools import GetImageInfo
    
    # Set the threshold level for binarising of the transformed labelmap (for
    # UseCase 5):
    Thresh = 0.1
    
    # Verify that FromSearchString exists:
    #SrcSearchStrings = GetRoiLabels(SrcSeg)
    FromSegNum = GetRoiNum(Roi=SrcSeg, SearchString=FromSearchString)
    
    print(f'\n\n\n***FromSegNum = {FromSegNum}')
    
    #ToSegNum = GetRoiNum(Roi=TrgSeg, SearchString=FromSearchString) # 04/12
        
        
    # Print the list of PFFGStoSliceInds:
    """This isn't required but useful."""
    from DicomTools import GetDicomSOPuids
    from SegTools import GetPFFGStoSliceIndsBySeg
    
    SegSOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    
    SegPFFGStoSliceIndsBySeg = GetPFFGStoSliceIndsBySeg(Seg=SrcSeg, 
                                                        SOPuids=SegSOPuids)
    
    SegPFFGStoSliceIndsInSeg = SegPFFGStoSliceIndsBySeg[FromSegNum]
    
    print(f'\nThe Source SEG matching "{FromSearchString}" has segmentations',
          f'on slices {SegPFFGStoSliceIndsInSeg}.')
    """End of not-required code."""
    
    # The pixel array that only contains the frame to be copied:
    PixArrToCopy = GetFrameFromPixArr(Seg=SrcSeg, DicomDir=SrcDcmDir, 
                                      SearchString=FromSearchString, 
                                      SliceNum=FromSliceNum,
                                      LogToConsole=LogToConsole)
    
    
    # Determine which Use Case applies:
    UseCase = WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, LogToConsole)
    
    if True:#LogToConsole:
        PrintTitle(f'Case {UseCase} applies.')
    
    
    """
    **************************************************************************
    What follows is UseCase-specific.
    **************************************************************************
    """
    
    #if 'a' in UseCase:
    #    """ 
    #    For UseCases 1a/b, 2a/b or 3a, there will always be a single 
    #    PerFrameFunctionalGroupsSequence. 
    #    """
    #    
    #    TrgPFFGStoSliceInds = [FromSliceNum] # moved to end
        
    
    if 'a' in UseCase:
        """ 
        The segmentation will be copied to a different slice location, so the
        pixel shift between the indices at FromSliceNum and ToSliceNum needs to
        be determined.  This is common for all Direct copy sub-use cases.
        """
        
        from GeneralTools import GetPixelShiftBetweenSlices
        from GeneralTools import ShiftFrame
        from SegTools import GetPixArrInSeg
        from SegTools import AddCopiedPixArr
        
        print(f'\nCopying slice {FromSliceNum} from Source SEG to slice',
              f'{ToSliceNum} in Target SEG..')
        
        # Import the Source 3D image:
        SrcIm = ImportImage(SrcDcmDir)
        TrgIm = ImportImage(TrgDcmDir)
        
        # Get pixel shift between FromSliceNum in SrcIm and ToSliceNum in
        # TrgIm in the Target image domain:
        PixShift = GetPixelShiftBetweenSlices(Image0=SrcIm, 
                                              SliceNum0=FromSliceNum, 
                                              Image1=TrgIm,
                                              SliceNum1=ToSliceNum,
                                              RefImage=TrgIm)
        
        print(f'\nPixShift = {PixShift}')
        
        
    if UseCase in ['1a', '2a']:
        # Shift the the in-plane elements in PixArrToCopy:
        PixArrToCopy = ShiftFrame(Frame=PixArrToCopy, 
                                  PixShift=PixShift)
        
        if TrgSeg:
            """
            Since this is a Direct copy, any existing segmentations in Target 
            with segment label matching FromSearchString are to be preserved.
            """
            
            # Get all frames in the Target segment containing the segmentation 
            # to be copied:
            TrgPixArrInSeg,\
            TrgPFFGStoSliceIndsInSeg = GetPixArrInSeg(Seg=TrgSeg, 
                                                      DicomDir=TrgDcmDir,
                                                      SearchString=FromSearchString)
            
            """
            PixArrToCopy needs to be added to previously Direct-copied 
            segmentations in TrgPixArrInSeg.
            """
            
            TrgPixArr,\
            TrgPFFGStoSliceInds = AddCopiedPixArr(OrigPixArr=TrgPixArrInSeg, 
                                                  OrigPFFGStoSliceInds=TrgPFFGStoSliceIndsInSeg, 
                                                  PixArrToAdd=PixArrToCopy, 
                                                  PFFGStoSliceIndsToAdd=[ToSliceNum])
            
        else:
            """
            A Target SEG was not provided.
            """
            TrgPixArr = deepcopy(PixArrToCopy)
            
            TrgPFFGStoSliceInds = deepcopy([ToSliceNum]) # 15/12 verify?
    
    
    if UseCase in ['1b', '2b']:
        
        TrgPixArr = deepcopy(PixArrToCopy)
        
        TrgPFFGStoSliceInds = deepcopy([FromSliceNum]) # 04/12 verify?
    
        
        
    if UseCase in ['3a', '3b', '4', '5']:
        from ConversionTools import PixArr2Image
        from ConversionTools import Image2PixArr
        from ImageTools import ResampleImage
        from ImageTools import GaussianBlurImage
        from ImageTools import BinaryThresholdImage
        from ConversionTools import ConvertImagePixelType
        
        # Import the 3D images:
        if not 'a' in UseCase:
            SrcIm = ImportImage(SrcDcmDir)
            TrgIm = ImportImage(TrgDcmDir)
        
        # Convert PixArrToCopy to a labelmap image:
        LabmapImToCopy = PixArr2Image(PixArr=PixArrToCopy,
                                      FrameToSliceInds=[FromSliceNum],
                                      RefIm=SrcIm)
        
        if True:#LogToConsole:
            #from ImageTools import ImageMax
            #from ImageTools import ImageMin
            unique = UniqueItems(Items=PixArrToCopy, IgnoreZero=False)
            print('\nPrior to resampling:')
            #print(f'type(LabmapImToCopy) = {type(LabmapImToCopy)}')
            #print(f'LabmapImToCopy.GetPixelIDTypeAsString() = {LabmapImToCopy.GetPixelIDTypeAsString()}')
            #print(f'PixArrToCopy.shape = {PixArrToCopy.shape}')
            #print(f'There are {len(unique)} unique items in PixArrToCopy')
            #print(f'Max of LabmapImToCopy = {ImageMax(LabmapImToCopy)}')
            #print(f'Min of LabmapImToCopy = {ImageMin(LabmapImToCopy)}')
            #print(f'LabmapImToCopy.GetSize() = {LabmapImToCopy.GetSize()}')
            PixID, PixIDTypeAsStr, UniqueVals,\
            F2Sinds = GetImageInfo(LabmapImToCopy, LogToConsole=True)
            
        
        
    if '3' in UseCase:
        
        #import SimpleITK as sitk
        
        
        """ First try resampling the image using a NearestNeighbor 
        interpolation. """
        interp = 'NearestNeighbor'
        
        if True:#LogToConsole:
            print('\nUsing', interp, 'interpolation...')
            
        # Resample LabmapImToCopy to the Target image's grid:
        ResLabmapImToCopy = ResampleImage(Image=LabmapImToCopy, 
                                          RefImage=TrgIm, 
                                          Interpolation=interp)
        
        if True:#LogToConsole:
            print('\nAfter resampling:')
            PixID, PixIDTypeAsStr, UniqueVals,\
            F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
            
        
        
        """ 
        If resampling to a smaller grid size aliasing can occur, leading to
        the appearent disappearance of segmentations (i.e. F2Sinds = []). 
        
        Try suggestions from Ziv Yaniv here:
            https://github.com/SimpleITK/SimpleITK/issues/1277
                
        1. Use the sitkLabelGaussian interpolator.
        
        2. Gaussian blur the segmentation, then resample using a linear 
        interpolator, and then threshold so that values in [a<1<b] are mapped
        to 1. You will need to select appropriate values for a, b.
        
        3. Compute the distance map of the segmentation, then resample using a
        linear interpolator, and then threshold the absolute value of the 
        distance map (sitk.Abs(lowres_distance_map)<dist_threshold). Again, you 
        need to select an appropriate dist_threshold.

        Tried:
        
        1. Resulting Gaussian interpolated resampled image had zeros only 
        (the image was converted to float prior to resampling).
        
        2. Works for UseCase 3B-i_SEG with FromSliceNum = 26 with binary
        threshold value of 0.04.
        
        
        Comment from Bradley Lowecamp:
            The implementation of the sitkLabelGaussian interpolator in the 
            ResampleImageFilter sets the sigma to the pixel spacing of the 
            input image to the resample filter. This is why it does not do a 
            better job in reducing aliasing.
        """
        #Workaround = 1
        Workaround = 2
        
        if not F2Sinds:
            print('\nThe resampled image has no non-zero frames (e.g. due to',
                  f'aliasing).  \nTry workaround #{Workaround}.')
            
            # Convert LabmapImToCopy from 32-bit unsigned integer to a float:
            LabmapImToCopy = ConvertImagePixelType(Image=LabmapImToCopy, 
                                                   NewPixelType='sitkFloat32')
            
            if True:#LogToConsole:
                print('\nAfter converting to float:')
                PixID, PixIDTypeAsStr, UniqueVals,\
                F2Sinds = GetImageInfo(LabmapImToCopy, LogToConsole=True)
        
            if Workaround == 1:
                print(f'\nTrying workaround #{Workaround}...')
                
                interp = 'Gaussian' # <-- get zeros only (image was converted 
                # to float prior to resampling)
                
                if True:#LogToConsole:
                    print('\nUsing', interp, 'interpolation...')
                    
                # Resample LabmapImToCopy to the Target image's grid:
                ResLabmapImToCopy = ResampleImage(Image=LabmapImToCopy, 
                                                  RefImage=TrgIm, 
                                                  Interpolation=interp)
                
                if True:#LogToConsole:
                    print('\nAfter resampling:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
                    
                    
                """ Will need to convert back to unsigned int and may need to
                do some binary thresholding, but only proceed if there are
                non-zero frames in the resampled image. """
                
                if not F2Sinds:
                    Workaround = 2 # try Workaround #2
                    
                    
            if Workaround == 2:
                print(f'\nTrying workaround #{Workaround}...')
                      
                # Gaussian blur the image:
                LabmapImToCopy = GaussianBlurImage(LabmapImToCopy)
                
                if True:#LogToConsole:
                    print('\nAfter applying Gaussian blur:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(LabmapImToCopy, LogToConsole=True)
                
                if not F2Sinds:
                    Workaround = 3 # try Workaround #3
                    
                # Linearly resample the blurred image:
                interp = 'Linear'
                
                if True:#LogToConsole:
                    print('\nUsing', interp, 'interpolation...')
                    
                # Resample LabmapImToCopy to the Target image's grid:
                ResLabmapImToCopy = ResampleImage(Image=LabmapImToCopy, 
                                                  RefImage=TrgIm, 
                                                  Interpolation=interp)
                
                if True:#LogToConsole:
                    print('\nAfter resampling:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
                
                
                """ Prior to converting back to unsigned integer, must first
                binary threshold the image. """
                # Thresh values with results for Case3B-i_SEG and 
                # FromSliceNum = 26 (max value in Pix array prior to binary
                # thresholding = 0.0468482):
                Thresh = 0.5 # no frames
                Thresh = 0.005 # two frames (slices 10 & 11)
                Thresh = 0.04 # one frame (slice 11)
                ResLabmapImToCopy = BinaryThresholdImage(ResLabmapImToCopy, 
                                                         Thresh)
                
                if True:#LogToConsole:
                    print('\nAfter binary thresholding:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
                    
                
                """ Following code was moved outside loop since useful to run
                under all conditions. """
                #""" ... then convert back to unsigned integer. """
                #if not PixID == 5:
                #    print(f'\nPixelID (= {PixID}) != 5 (sitkUInt32 = Unsigned',
                #          '32 bit integer).  Converting to sitkUInt32..')
                #    
                #    # Convert ResLabmapImToCopy from float to 32-bit unsigned 
                #    # integer:
                #    ResLabmapImToCopy = ConvertImagePixelType(Image=ResLabmapImToCopy, 
                #                                              NewPixelType='sitkUInt32')
                #    
                #    if True:#LogToConsole:
                #        print('\nAfter converting to unsigned int:')
                #        PixID, PixIDTypeAsStr, UniqueVals,\
                #        F2Sinds = GetImageInfo(ResLabmapImToCopy, 
                #                               LogToConsole=True)
                
                
            if Workaround == 3:
                print(f'\nTrying workaround #{Workaround}...')
                      
                print('\nStill need to write Workaround 3...')
                
        
        
        #""" 16/12:
        #    Instead of using NearestNeighbor, use a BSpline interpolation, then
        #    binary threshold the image using a low threshold (much lower than
        #    0.5).
        #"""
        #interp = 'BSpline'
        #interp = 'Linear'
        #interp = 'NearestNeighbor'
        #interp = 'Gaussian' # <-- get zeros only (image was converted to float 
        # prior to resampling)
        
        
            
        
        """ For some reason when binary thresholding an empty image, the 
        threshold value SetLowerThreshold is being rounded down to 0, resulting
        in a non-binary image.  So only apply binary thresholding if there are
        at least 2 unique values in the input image. """
        if False:
            PixArr, F2Sinds = Image2PixArr(LabmapIm=ResLabmapImToCopy)
            unique = UniqueItems(Items=PixArr, IgnoreZero=False)
            
            if len(unique) < 2:
                ResLabmapImToCopy = BinaryThresholdImage(ResLabmapImToCopy, Thresh=0.5)
                
                if True:#LogToConsole:
                    print('\nAfter binary thresholding:')
                    PixID, PixIDTypeAsStr, UniqueVals,\
                    F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
            
        
        
        """ Ensure that ResLabmapImToCopy is a 32-bit unsigned integer. """
        if not PixID == 5:
            print(f'\nPixelID = {PixID} ({PixIDTypeAsStr})). Converting to',
                  f'unsigned 32-bit integer (sitkUInt32)..')
            
            # Convert ResLabmapImToCopy from float to 32-bit unsigned 
            # integer:
            ResLabmapImToCopy = ConvertImagePixelType(Image=ResLabmapImToCopy, 
                                                      NewPixelType='sitkUInt32')
            
            if True:#LogToConsole:
                print('\nAfter converting to 32-bit unsigned int:')
                PixID, PixIDTypeAsStr, UniqueVals,\
                F2Sinds = GetImageInfo(ResLabmapImToCopy, 
                                       LogToConsole=True)
                        
                        
        # Convert ResLabmapImToCopy back to a pixel array:
        ResPixArrToCopy,\
        PFFGStoSliceIndsToCopy = Image2PixArr(LabmapIm=ResLabmapImToCopy)
        
        if True:#LogToConsole:
            print('\nAfter converting to a pixel array:')
            PixID, PixIDTypeAsStr, UniqueVals,\
            F2Sinds = GetImageInfo(ResLabmapImToCopy, LogToConsole=True)
            for i in range(ResPixArrToCopy.shape[0]):
                maxval = np.amax(ResPixArrToCopy[i])
                minval = np.amin(ResPixArrToCopy[i])
                
                print(f'Frame {i} has max = {maxval}, min = {minval}')
        
        #from ImageTools import BinaryThresholdImage
        #
        #if not 'earest' in interp:
        #    ResLabmapImToCopy = BinaryThresholdImage(ResLabmapImToCopy, 
        #                                             Thresh=0.5)
        
    
        
        
    if UseCase == '3a':
        """
        For a Direct copy, one segmentation is always copied to a single
        segmentation, so if after resampling there is more than one frame, the
        frames will need to be averaged.
        """
        from GeneralTools import MeanPixArr
        
        unique = UniqueItems(Items=ResPixArrToCopy, IgnoreZero=False)
        print(f'\nThere are {len(unique)} unique items in ResPixArrToCopy')
        
        F = ResPixArrToCopy.shape[0]
        
        print(f'\nThe segmentation on FromSliceNum = {FromSliceNum} has been',
              f'resampled to {F} frames: {PFFGStoSliceIndsToCopy}')
        
        if F > 1:
            print(f'\nResPixArrToCopy has {F} frames so the pixel arrays will',
                  'be averaged...')
            
            # Take pixel-by-pixel mean across all frames in ResPixArrToCopy:
            ResPixArrToCopy = MeanPixArr(ResPixArrToCopy)
            
            F = ResPixArrToCopy.shape[0]
            
            print(f'\nResPixArrToCopy now has {F} frames')
        else:
            print(f'\nResPixArrToCopy has F frames')
            
        
        # Shift the in-plane elements in ResPixArrToCopy:
        ResPixArrToCopy = ShiftFrame(Frame=ResPixArrToCopy, PixShift=PixShift)
        
        unique = UniqueItems(Items=ResPixArrToCopy, IgnoreZero=False)
        print(f'\nThere are {len(unique)} unique items in ResPixArrToCopy',
              'after shifting the frame.')
        
        
        if TrgSeg:
            """
            Since this is a Direct copy, any existing segmentations in Target
            with segment label matching FromSearchString are to be preserved.
            """
            
            # Get all frames in the Target segment containing the segmentation 
            # to be copied:
            TrgPixArrInSeg,\
            TrgPFFGStoSliceIndsInSeg = GetPixArrInSeg(Seg=TrgSeg, 
                                                      DicomDir=TrgDcmDir,
                                                      SearchString=FromSearchString)
            
            """
            ResPixArrToCopy needs to be added to previously Direct-copied 
            segmentations in TrgPixArrInSeg.
            """
            
            TrgPixArr,\
            TrgPFFGStoSliceInds = AddCopiedPixArr(OrigPixArr=TrgPixArrInSeg, 
                                                  OrigPFFGStoSliceInds=TrgPFFGStoSliceIndsInSeg, 
                                                  PixArrToAdd=ResPixArrToCopy, 
                                                  PFFGStoSliceIndsToAdd=[ToSliceNum])
        else:
            """
            A Target SEG was not provided.
            """
            TrgPixArr = deepcopy(ResPixArrToCopy)
            
            TrgPFFGStoSliceInds = deepcopy([ToSliceNum]) # 04/12 verify?
            
    
    
    if UseCase == '3b':
        TrgPixArr = deepcopy(ResPixArrToCopy)
        
        TrgPFFGStoSliceInds = deepcopy(PFFGStoSliceIndsToCopy)
        
        
    
    #if UseCase == '4':
    
        
    if UseCase == '5':
        from ImageTools import RegisterImages
        from ImageTools import TransformImage
        from ImageTools import BinaryThresholdImage
    
        # Register the images using an affine transformation:
        RegSrcIm, RegImFilt = RegisterImages(FixIm=TrgIm, MovIm=SrcIm, 
                                             Tx='affine',
                                             LogToConsole=LogToConsole)
        
        # Transform LabmapImToCopy using RegImFilt:
        TxLabmapImToCopy = TransformImage(Im=LabmapImToCopy, 
                                          RegImFilt=RegImFilt,
                                          Interpolation='Nearestneighbor')
        
        if True:#LogToConsole:
                print('\nAfter transforming LabmapImToCopy by the registration',
                      'transformation:')
                PixID, PixIDTypeAsStr, UniqueVals,\
                F2Sinds = GetImageInfo(TxLabmapImToCopy, 
                                       LogToConsole=True)
        
        """
        21/12/20:  
            Following the use of a nearestneighbor interpolator when 
            transforming LabmapImToCopy, i.e.:
            
            TxMap[0]["ResampleInterpolator"] = ["FinalNearestNeighborInterpolator"]
            
            it's no longer necessary to perform the binary thresholding step.
        
        # Binary threshold TxLabmapImToCopy:
        TxLabmapImToCopy = BinaryThresholdImage(Im=TxLabmapImToCopy, 
                                                Thresh=Thresh)
        
        if True:#LogToConsole:
                print('\nAfter binary thresholding with Thresh = {Thresh}:')
                PixID, PixIDTypeAsStr, UniqueVals,\
                F2Sinds = GetImageInfo(TxLabmapImToCopy, 
                                       LogToConsole=True)
        """
        
        
        # Convert TxLabmapImToCopy to a pixel array:
        TrgPixArr,\
        TrgPFFGStoSliceInds = Image2PixArr(LabmapIm=TxLabmapImToCopy)
        
        unique = UniqueItems(Items=TrgPixArr, IgnoreZero=False)
        print(f'\nThere are {len(unique)} unique items in TrgPixArr')
        
        F = TrgPixArr.shape[0]
        
        print(f'\nThe segmentation on slice {FromSliceNum} has been',
              f'registered to {F} frames: {TrgPFFGStoSliceInds}.')
    
    
    
    #if 'a' in UseCase:
    #    """ 
    #    For UseCases 1a/b, 2a/b or 3a, there will always be a single 
    #    PerFrameFunctionalGroupsSequence, and the single index will be slice
    #    ToSliceNum.  Over-write previous TrgPFFGStoSliceInds. 
    #    """
    #    
    #    TrgPFFGStoSliceInds = [ToSliceNum]
    #    
    #    print(f'\nTrgPFFGStoSliceInds over-written to {TrgPFFGStoSliceInds}')
        
        
    """ 
    If UseCase is 1a/2a/3a (i.e. a Direct copy is to be made) and a SEG has 
    been provided for Target this is not a clean copy, i.e. the copied 
    segmentation is to be added to an existing segment containing previously 
    copied segmentation(s). If a Relationship-preserving copy is to be made or 
    if a Target SEG has not been provided, the Source SEG will be used as a 
    template.
    """
    #if not 'a' in UseCase or not TrgSeg:
    #    TrgSeg = InitialiseSeg(SegTemplate=SrcSeg, SegNum=FromSegNum,
    #                           PFFGStoSliceInds=TrgPFFGStoSliceInds, 
    #                           DicomDir=TrgDcmDir, LogToConsole=LogToConsole)
    
    if LogToConsole:
        print('\n\nInputs to InitialiseSeg:')
        print(f'   SegNum = {FromSegNum}')
        print(f'   TrgPFFGStoSliceInds = {TrgPFFGStoSliceInds}')
        
    """ 
    09/12: When downsampling some resulting images have no segmentations,
    hence TrgPFFGStoSliceInds = [].  This results in 
    Seg.NumberOfFrames = f"{len(PFFGStoSliceInds)}"
    in InitialiseSeg.
    Until the cause of the above is determined, raise an exception if 
    TrgPFFGStoSliceInds = [].
    """
    if TrgPFFGStoSliceInds == []:
        msg = 'TrgPFFGStoSliceInds = []. There must be at least one slice '\
              + 'number in TrgPFFGStoSliceInds.'
        
        raise Exception(msg)
    
        
    if TrgSeg:
        """ Use TrgSeg to initialise the Target SEG. """
        #TrgSeg = InitialiseSeg(SegTemplate=TrgSeg, SegNum=ToSegNum,
        TrgSeg = InitialiseSeg(SegTemplate=TrgSeg, SearchString=FromSearchString,
                               PFFGStoSliceInds=TrgPFFGStoSliceInds, 
                               DicomDir=TrgDcmDir, NamePrefix=AddText,
                               LogToConsole=LogToConsole)
    else:
        """ Use SrcSeg to initialise the Target SEG. """
        TrgSeg = InitialiseSeg(SegTemplate=SrcSeg, SearchString=FromSearchString,
                               PFFGStoSliceInds=TrgPFFGStoSliceInds, 
                               DicomDir=TrgDcmDir, NamePrefix=AddText,
                               LogToConsole=LogToConsole)
        
    print(f'\n\n\n***FromSegNum = {FromSegNum}')
    
    if LogToConsole:
        print('\n\nInputs to ModifySeg:')
        print(f'   TrgPixArr.shape = {TrgPixArr.shape}')
        [print(f'   np.amax(TrgPixArr[{i}]) = {np.amax(TrgPixArr[i])}') for i in range(TrgPixArr.shape[0])]
        print(f'   TrgPFFGStoSliceInds = {TrgPFFGStoSliceInds}')
        
    # Modify the tags in TrgSeg:
    TrgSeg = ModifySeg(Seg=TrgSeg, PixArr=TrgPixArr,
                       PFFGStoSliceInds=TrgPFFGStoSliceInds, 
                       DicomDir=TrgDcmDir, LogToConsole=LogToConsole)
    
    
    """ Had 1040 lines of code. Now 207. """
    
    return TrgSeg






"""
******************************************************************************
******************************************************************************
COPY A CONTOUR / SEGMENTATION
******************************************************************************
******************************************************************************
"""
    

def CopyRoi(SrcRoi, FromSearchString, SrcDcmDir, FromSliceNum, TrgDcmDir,
            TrgRoi=None, ToSliceNum=None, AddText='', LogToConsole=False):
    """
    
    Inputs:
    ------
    
    SrcRoi : Pydicom object
        Source RTS/SEG object.
                             
    FromSearchString : string
        All or part of the Source ROIName/SegmentLabel of the ROI/segment 
        containing the contour/segmentation to be copied.
    
    SrcDcmDir : string
        Directory containing the Source DICOMs.
                            
    FromSliceNum : integer
        Slice index of the Source DICOM stack corresponding to the contour/
        segmentation to be copied (counting from 0).
    
    TrgDcmDir : string
        Directory containing the Target DICOMs.
        
    TrgRts : Pydicom object (optional; None by default)
        Target RTS object that the contour(s)/segmentation(s) is to be copied 
        to. TrgRts is only non-None if a Direct copy of the contour/
        segmentation is to be made and added to existing Direct-copied 
        contour(s)/segmentation(s).     
        
    ToSliceNum : integer (optional; None by default)
        Slice index within the Target DICOM stack where the contour/
        segmentation is to be copied to (counting from 0).  This only applies 
        for Direct copies, hence the default value None.
    
    AddText : string (optional, '' by default)
        Sting of text to pass to ModifyRts/ModifySeg to be used when generating
        a filename for the new Target RTS/SEG.
        
    LogToConsole : boolean (default False)
        Denotes whether some results will be logged to the console.
          
                  
    Outputs:
    -------
        
    TrgRts : Pydicom object
        The new (if making a Relationship-preserving copy) or the modified (if
        making a Direct copy of a contour/segmentation to an existing Direct-
        copied contour(s)/segmentation(s)) Target RTS/SEG object.
    """

    import time
    from DicomTools import IsSameModalities
    
    # Start timing:
    times = []
    times.append(time.time())
    
    # Compare the modalities of the RTSs/SEGs:
    SrcModality = SrcRoi.Modality
    
    if TrgRoi:
        TrgModality = TrgRoi.Modality
        
        if not IsSameModalities(SrcRoi, TrgRoi):
            msg = f"The Source ({SrcModality}) and Target ({TrgModality}) " \
                  + "modalities are different."
            
            raise Exception(msg)
            
    
    if SrcModality == 'RTSTRUCT':
        NewTrgRoi = CopyRts(SrcRoi, FromSearchString, SrcDcmDir, FromSliceNum, 
                            TrgDcmDir, TrgRoi, ToSliceNum, AddText,
                            LogToConsole)
    
    elif SrcModality == 'SEG':
        NewTrgRoi = CopySeg(SrcRoi, FromSearchString, SrcDcmDir, FromSliceNum, 
                            TrgDcmDir, TrgRoi, ToSliceNum, AddText,
                            LogToConsole)
        
    else:
        msg = f'The Source modality ({SrcModality}) must be either "RTS" or '\
              + '"SEG".'
        
        raise Exception(msg)

    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if True:#LogToConsole:
        print(f'\n\nDone.  Took {Dtime} s to run.')
        
    return NewTrgRoi







"""
******************************************************************************
******************************************************************************
CHECK FOR ERRORS IN NEW TARGET RTS / SEG
******************************************************************************
******************************************************************************
"""

def ErrorCheckSeg(Seg, DicomDir, LogToConsole=False):
    """
    Check a SEG for errors in dependencies based on provided directory of
    the DICOMs that relate to the SEG.  
    
    Inputs:
    ------
    
    Seg : Pydicom object
        SEG object to be error checked.
        
    DicomDir : string
        Directory containing the DICOMs that relate to Seg.
        
    LogToConsole : boolean (default False)
        Denotes whether some results will be logged to the console.
                           
    
    Outputs:
    -------
    
    ErrorList : list of strings
        A list of strings that describe any errors that are found.  If no 
        errors are found an empty list ([]) will be returned.
    """
    
    import importlib
    import GeneralTools
    importlib.reload(GeneralTools)
    
    from copy import deepcopy
    from DicomTools import GetDicomSOPuids
    from DicomTools import ImportDicom
    from ImageTools import GetImageAttributes
    from GeneralTools import AreItemsEqualToWithinEpsilon
    from GeneralTools import AreListsEqualToWithinEpsilon
    
    SOPuids = GetDicomSOPuids(DicomDir)
    
    Dicom = ImportDicom(DicomDir)
    
    #Size, Spacings, ST,\
    #IPPs, Dirs = GetImageAttributes(DicomDir=DicomDir, Package='sitk')
    Size, Spacings, ST,\
    IPPs, Dirs = GetImageAttributes(DicomDir=DicomDir, Package='pydicom')
    
    # The number of frames, rows and columns in the SEG's pixel array:
    if len(Seg.pixel_array.shape) > 2:
        PixArrF, PixArrR, PixArrC = Seg.pixel_array.shape
    else:
        PixArrR, PixArrC = Seg.pixel_array.shape
        PixArrF = 1
    
    #NumOfDicoms = len(SOPuids)
    
    ErrorList = []
    
    
    """Determine whether MediaStorageSOPInstanceUID matches SOPInstanceUID."""
    MSSOPuid = deepcopy(Seg.file_meta.MediaStorageSOPInstanceUID)
    SOPuid = deepcopy(Seg.SOPInstanceUID)
    
    if not MSSOPuid == SOPuid:
        msg = f'"MediaStorageSOPInstanceUID" ({MSSOPuid}) does not match '\
              + f'"SOPInstanceUID" ({SOPuid}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    """Determine whether the number of sequences in 
    ReferencedInstanceSequence matches the number of DICOMs."""
    
    RIS = deepcopy(Seg.ReferencedSeriesSequence[0]\
                      .ReferencedInstanceSequence)
    
    if len(SOPuids) != len(RIS):
        msg = f'The number of "SOPInstanceUID"s ({len(SOPuids)}) does not'\
              + ' match the number of sequences in '\
              + f'"ReferencedInstanceSequence" ({len(RIS)}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    """Determine whether any of the ReferencedSOPInstanceUIDs do not
    match the SOPInstanceUIDs."""        
    RefSOPuidsInRIS = [RIS[i].ReferencedSOPInstanceUID for i in range(len(RIS))]
    
    # Determine whether the Ref SOP UIDs match the SOP UIDs:
    IsMatch = [RefSOPuid in SOPuids for RefSOPuid in RefSOPuidsInRIS]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching Ref SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if NumOfMatches == 0:
        NonMatchingUids = [RefSOPuidsInRIS[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'"ReferencedSOPInstanceUID" {uid} in '\
                  + f'"ReferencedInstanceSequence" {i+1} does not match any '\
                  + '"SOPInstanceUID".'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
                
                
    
    """Determine whether any of the SOPInstanceUIDs do not match the
    ReferencedSOPInstanceUIDs."""        
    
    # Determine whether the SOP UIDs match the Referenced SOP UIDs:
    IsMatch = [SOPuid in RefSOPuidsInRIS for SOPuid in SOPuids]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if NumOfMatches == 0:
        NonMatchingUids = [SOPuids[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'"SOPInstanceUID" {uid} is not referenced in any '\
                  + '"ReferencedSOPInstanceUID" in '\
                  + '"ReferencedInstanceSequence".'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
    
    
                           
    if Seg.ReferencedSeriesSequence[0].SeriesInstanceUID != Dicom.SeriesInstanceUID:
        msg = f'SEG "SeriesInstanceUID" in "ReferencedSeriesSequence" '\
              + f'({Seg.PatientName}) does not match DICOM "SeriesInstanceUID"'\
              + f'({Dicom.SeriesInstanceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
            
       
    if Seg.PatientName != Dicom.PatientName:
        msg = f'SEG "PatientName" ({Seg.PatientName}) does not match DICOM '\
              + f'"PatientName" ({Dicom.PatientName}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
        
    if Seg.PatientID != Dicom.PatientID:
        msg = f'SEG "PatientID" ({Seg.PatientID}) does not match the DICOM '\
              + f'"PatientID" ({Dicom.PatientID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)

    if Seg.StudyInstanceUID != Dicom.StudyInstanceUID:
        msg = f'SEG "StudyInstanceUID" ({Seg.StudyInstanceUID}) does not '\
              + 'match the DICOM tag "StudyInstanceUID" '\
              + f'({Dicom.StudyInstanceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    #if Seg.StudyID != Dicom.StudyID:
    #    msg = f'The SEG "StudyID" ({Seg.StudyID}) does not match the '\
    #          + f'DICOM "StudyID" ({Dicom.StudyID}).'
    #    
    #    ErrorList.append(msg)
    #    
    #    if LogToConsole:
    #        print('\n' + msg)
            
    if Seg.FrameOfReferenceUID != Dicom.FrameOfReferenceUID:
        msg = 'SEG "FrameOfReferenceUID" ({Seg.FrameOfReferenceUID}) '\
              + 'does not match DICOM "FrameOfReferenceUID" '\
              + f'({Dicom.FrameOfReferenceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    if int(Seg.NumberOfFrames) != PixArrF:
        msg = f'"NumberOfFrames" ({Seg.NumberOfFrames}) does not match the '\
              + f'number of frames in "PixelData" ({PixArrF}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    if Seg.Rows != Dicom.Rows:
        msg = f'SEG "Rows" ({Seg.Rows}) does not match DICOM "Rows" '\
              + f'({Dicom.Rows}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    if Seg.Columns != Dicom.Columns:
        msg = f'SEG "Columns" ({Seg.Columns}) does not match DICOM "Columns" '\
              + f'({Dicom.Columns}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    """There should only be one sequence in SegmentSequence."""
    N = len(Seg.SegmentSequence)
    
    if N > 1:
        msg = 'There are {N} sequences in "SegmentSequence".  There should '\
              + f'be only 1.'
              
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    
    """Verify that the SegmentNumber in SegmentSequence is 1."""
    N = deepcopy(Seg.SegmentSequence[0].SegmentNumber)
    
    if N != 1:
        msg = '"SegmentNumber" in "SegmentSequence" is {N}.  It should be 1.'
              
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
            
    """Check various tags in SharedFunctionalGroupsSequence."""
    SegIOP = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                         .PlaneOrientationSequence[0]\
                         .ImageOrientationPatient)
    
    SegIOP = [float(item) for item in SegIOP]
    
    DcmIOP = [float(item) for item in Dicom.ImageOrientationPatient]
    
    #if SegIOP != Dicom.ImageOrientationPatient:
    if not AreListsEqualToWithinEpsilon(SegIOP, DcmIOP):
        msg = 'SEG "ImageOrientationPatient" in '\
              + f'"SharedFunctionalGroupsSequence" ({SegIOP}) does not match '\
              + f'DICOM "ImageOrientationPatient" ({DcmIOP}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
       
    
    SegST = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                        .PixelMeasuresSequence[0]\
                        .SliceThickness)
    
    """ The SliceThickness appears to be the z-Spacing rather than the
    SliceThickness from the DICOM metadata. """
    
    #if float(SegST) != Spacings[2]:
    if not AreItemsEqualToWithinEpsilon(float(SegST), Spacings[2], epsilon=1e-05):
        print(f'\n{float(SegST) - Spacings[2]}')
        
        msg = 'SEG "SliceThickness" in "SharedFunctionalGroupsSequence" '\
              + f'({SegST}) does not match the slice thickness calculated '\
              + 'from DICOM "ImagePositionPatient" and '\
              + f'"ImageOrientationPatient" ({Spacings[2]}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    SegSBS = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                         .PixelMeasuresSequence[0]\
                         .SpacingBetweenSlices)
    
    #if float(SegSBS) != Spacings[2]:
    if not AreItemsEqualToWithinEpsilon(float(SegSBS), Spacings[2], epsilon=1e-05):
        print(f'\n{float(SegSBS) - Spacings[2]}')
        
        msg = 'SEG "SpacingBetweenSlices" in "SharedFunctionalGroupsSequence"'\
              + f' ({SegSBS}) does not match the slice thickness calculated '\
              + 'from the DICOM "ImagePositionPatient" and '\
              + f'"ImageOrientationPatient" ({Spacings[2]}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)

    
    SegPS = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                        .PixelMeasuresSequence[0]\
                        .PixelSpacing)
    
    SegPS = [float(item) for item in SegPS]
    
    DcmPS = [float(item) for item in Dicom.PixelSpacing]
    
    #if SegPS != Dicom.PixelSpacing:
    if not AreListsEqualToWithinEpsilon(SegPS, DcmPS):
        msg = 'SEG "PixelSpacing" in "SharedFunctionalGroupsSequence '\
              + f'({SegPS}) does not match DICOM "PixelSpacing" ({DcmPS}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    
    
    """Verify that the number of sequences in PerFrameFunctionalGroupsSequence
    is equal to NumberOfFrames."""
    PFFGS = deepcopy(Seg.PerFrameFunctionalGroupsSequence)
    
    if len(PFFGS) != int(Seg.NumberOfFrames):
        msg = f'The number of sequences in "PerFrameFunctionGroupsSequence" '\
              + f'({len(PFFGS)}) does not match "NumberOfFrames" '\
              + f'({Seg.NumberOfFrames}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    """Determine whether any of the ReferencedSOPInstanceUIDs in the
    PerFrameFunctionGroupsSequence do not match the SOPInstanceUIDs."""        
    RefSOPuidsInPFFGS = [PFFGS[i].DerivationImageSequence[0]\
                                 .SourceImageSequence[0]\
                                 .ReferencedSOPInstanceUID for i in range(len(PFFGS))]
    
    # Determine whether the Ref SOP UIDs match the SOP UIDs:
    IsMatch = [RefSOPuid in SOPuids for RefSOPuid in RefSOPuidsInPFFGS]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching Ref SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if NumOfMatches == 0:
        NonMatchingUids = [RefSOPuidsInPFFGS[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'"ReferencedSOPInstanceUID" {uid} in '\
                  + '"PerFrameFunctionalGroupsSequence" {i+1} does not match '\
                  + 'any DICOM "SOPInstanceUID".'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
                
    
    
    """Determine whether the DimensionIndexValues are sensible integers,
    and if the indexed ReferencedSOPInstanceUID agrees with the 
    ReferencedSOPInstance UID within the SourceImageSequence."""
    DIVs = [PFFGS[i].FrameContentSequence[0]\
                    .DimensionIndexValues for i in range(len(PFFGS))]
    
    # Determine whether any of the first elements in the DIVs are not 1  
    # (there should only be one segment, so the first element should always
    # be 1):
    FirstElements = [int(DIVs[i][0]) for i in range(len(DIVs))]
    
    #NumOfMatches = FirstElements.count('1')
    
    # Find the indices of any non-matching elements:
    Inds = [i for i, x in enumerate(FirstElements) if x != 1]
    
    if Inds:
        divs = [DIVs[i] for i in Inds]
        
        for i in range(len(Inds)):
            msg = f'The first element in "DimensionalIndexValue" {i+1} '\
                  + f'({divs[i]}) is not "1".'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
                
    # Determine if any of the second elements in the DIVs exceed the number
    # of sequences in ReferencedInstanceSequence:
    SecondElements = [int(DIVs[i][1]) for i in range(len(DIVs))]
    
    # Find the indices of any elements that exceed len(RIS):
    Inds = [i for i, x in enumerate(SecondElements) if x > len(RIS)]

    if Inds:
        #divs = [DIVs[i] for i in Inds]
        
        for i in range(len(Inds)):
            msg = f'The second element in "DimensionalIndexValue" {i+1} '\
                  + f'({DIVs[i]}) exceeds the number of sequences in '\
                  + f'"ReferencedInstanceSequence" (N = {len(RIS)}).'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
                
    """Determine if the ReferencedSOPInstanceUID in the 
    ReferencedInstanceSequence indexed by the second elements in the DIVs 
    match the ReferencedSOPInstanceUID in the SourceImageSequence."""
    for i in range(len(SecondElements)):
        RefSOPinPFFGS = RefSOPuidsInPFFGS[i]
        
        # Need to -1 since i is zero-indexed:
        ind = SecondElements[i] - 1
        
        RefSOPinRIS = RefSOPuidsInRIS[ind]
        
        if RefSOPinPFFGS != RefSOPinRIS:
            msg = '"ReferencedSOPInstanceUID" referenced in '\
                  + f'"SourceImageSequence" {i+1} does not match '\
                  + '"ReferencedSOPInstanceUID" referenced in '\
                  + '"ReferencedInstanceSequence" as indexed by the second '\
                  + f'element in "DimensionalIndexValue" {i+1} ({DIVs[i]}).'
                  
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
    
    
    """Determine if ImagePositionPatient in PerFrameFunctionalGroupsSequence 
    matches ImagePositionPatient of the DICOM as indexed by the DIVs."""
    IPPsInPFFGS = [PFFGS[i].PlanePositionSequence[0]\
                           .ImagePositionPatient for i in range(len(PFFGS))]
    
    # Convert from strings to floats:
    IPPsInPFFGS = [[float(item) for item in IPP] for IPP in IPPsInPFFGS]
    
    for i in range(len(IPPsInPFFGS)):
        ind = SOPuids.index(RefSOPuidsInPFFGS[i])
        
        IPP = IPPs[ind]
        
        #if IPPsInPFFGS[i] != IPP:
        if not AreListsEqualToWithinEpsilon(IPPsInPFFGS[i], IPP):
            msg = f'"ImagePositionPatient" ({IPPsInPFFGS[i]}) referenced in '\
                  + f'"PlanePositionSequence" {i+1} does not match DICOM '\
                  + f'"ImagePositionPatient" ({IPP}) as indexed by the second'\
                  + f' element ({SecondElements[i]}) in '\
                  + f'"DimensionalIndexValue" {i+1} ({DIVs[i]}).'
                  
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
    
    
    """Determine whether any of the ReferencedSegmentNumber are not 1 (there
    should only be one segment)."""
    RSNs = [PFFGS[i].SegmentIdentificationSequence[0]\
                    .ReferencedSegmentNumber for i in range(len(PFFGS))]
    
    # Find the indices of any non-matching elements:
    Inds = [i for i, x in enumerate(RSNs) if x != 1]
    
    if Inds:        
        for i in range(len(Inds)):
            msg = f'"ReferencedSegmentNumber" {i+1} is not 1.'\
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
    
    
    """Determine if the dimensions of the pixel array in PixelData do not
    match the expected dimensions (the number of frames (PixArrF) has 
    already been compared to NumberOfFrames)."""
    if PixArrR != Seg.Rows:
        msg = f'The number of rows in "PixelData" ({PixArrR}) does not '\
              + f'match the number of SEG "Rows" ({Seg.Rows}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    if PixArrC != Seg.Columns:
        msg = f'The number of columns in "PixelData" ({PixArrC}) does not'\
              + f' match the number of SEG "Columns" ({Seg.Columns}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    print(f'\nThere were {len(ErrorList)} errors found in the SEG.')
            
    return ErrorList







def ErrorCheckRts(Rts, DicomDir, LogToConsole=False):
    """
    Check a RTS for errors in dependencies based on provided directory of
    the DICOMs that relate to the RTS.  
    
    Inputs:
    ------
    
    Rts : Pydicom object
        RTS object to be error checked.
        
    DicomDir : string
        Directory containing the DICOMs that relate to Rts.
        
    LogToConsole : boolean (default False)
        Denotes whether some results will be logged to the console.
                           
    
    Outputs:
    -------
    
    ErrorList : list of strings
        A list of strings that describe any errors that are found.  If no 
        errors are found an empty list ([]) will be returned.
    """        
    
    from copy import deepcopy
    from DicomTools import GetDicomSOPuids
    from DicomTools import ImportDicom
    from ImageTools import GetImageAttributes
    
    SOPuids = GetDicomSOPuids(DicomDir)
    
    Dicom = ImportDicom(DicomDir)
    
    Size, Spacings, ST,\
    IPPs, Dirs = GetImageAttributes(DicomDir=DicomDir, Package='sitk')
    
    
    ErrorList = []
    
    """Determine whether MediaStorageSOPInstanceUID matches SOPInstanceUID."""
    MSSOPuid = deepcopy(Rts.file_meta.MediaStorageSOPInstanceUID)
    SOPuid = deepcopy(Rts.SOPInstanceUID)
    
    if not MSSOPuid == SOPuid:
        msg = f'"MediaStorageSOPInstanceUID" ({MSSOPuid}) does not match '\
              + f'"SOPInstanceUID" ({SOPuid}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    if Rts.PatientName != Dicom.PatientName:
        msg = f'RTS "PatientName" ({Rts.PatientName}) does not match DICOM '\
              + f'"PatientName" ({Dicom.PatientName}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
        
    if Rts.PatientID != Dicom.PatientID:
        msg = f'RTS "PatientID" ({Rts.PatientID}) does not match DICOM '\
              + f'"PatientID" ({Dicom.PatientID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)

    if Rts.StudyInstanceUID != Dicom.StudyInstanceUID:
        msg = f'RTS "StudyInstanceUID" ({Rts.StudyInstanceUID}) does not '\
              + 'match DICOM tag "StudyInstanceUID" '\
              + f'({Dicom.StudyInstanceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    #if Rts.StudyID != Dicom.StudyID:
    #    msg = f'The RTS "StudyID" ({Rts.StudyID}) does not match the '\
    #          + f'DICOM "StudyID" ({Dicom.StudyID}).'
    #    
    #    ErrorList.append(msg)
    #    
    #    if LogToConsole:
    #        print('\n' + msg)
            
    if Rts.FrameOfReferenceUID != Dicom.FrameOfReferenceUID:
        msg = 'RTS "FrameOfReferenceUID" ({Rts.FrameOfReferenceUID}) does not'\
              + 'match the DICOM "FrameOfReferenceUID" '\
              + f'({Dicom.FrameOfReferenceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
      
    
    RFORS = deepcopy(Rts.ReferencedFrameOfReferenceSequence[0])
    
    FORuidInRFORS = deepcopy(RFORS.FrameOfReferenceUID)
    
    if FORuidInRFORS != Dicom.FrameOfReferenceUID:
        msg = '"FrameOfReferenceUID" in "ReferencedFrameOfReferenceSequence" '\
              + f'({FORuidInRFORS}) does not match DICOM '\
              + f'"FrameOfReferenceUID" ({Dicom.FrameOfReferenceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    """Verify that the ReferencedSOPInstanceUID in 
    ReferencedFrameOfReferenceSequence matches the RTS StudyInstanceUID."""
    RefSOPuid = RFORS.RTReferencedStudySequence[0].ReferencedSOPInstanceUID
    
    if RefSOPuid != Rts.StudyInstanceUID:
        msg = '"ReferencedSOPInstanceUID" in '\
              + f'"ReferencedFrameOfReferenceSequence" ({RefSOPuid}) does not'\
              + f' match the RTS "StudyInstanceUID" ({Rts.StudyInstanceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    """Verify that the SeriesInstanceUID in ReferencedFrameOfReferenceSequence
    matches the DICOM SeriesInstanceUID."""
    RtsSeriesuid = deepcopy(RFORS.RTReferencedStudySequence[0]\
                                 .RTReferencedSeriesSequence[0]\
                                 .SeriesInstanceUID)
    
    if RtsSeriesuid != Dicom.SeriesInstanceUID:
        msg = '"SeriesInstanceUID" in "ReferencedFrameOfReferenceSequence" '\
              + f'({RtsSeriesuid}) does not match DICOM "SeriesInstanceUID" '\
              + f'({Dicom.SeriesInstanceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    
    """Verify that the ReferencedSOPInstanceUIDs in 
    ReferencedFrameOfReferenceSequence match the DICOM SOPInstanceUIDs."""
    CIS = deepcopy(RFORS.RTReferencedStudySequence[0]\
                        .RTReferencedSeriesSequence[0]\
                        .ContourImageSequence)
    
    RefSOPuidsInRFORS = [CIS[i].ReferencedSOPInstanceUID for i in range(len(CIS))]
    
    # Determine whether the Ref SOP UIDs match the SOP UIDs:
    IsMatch = [RefSOPuid in SOPuids for RefSOPuid in RefSOPuidsInRFORS]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching Ref SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if NumOfMatches == 0:
        NonMatchingUids = [RefSOPuidsInRFORS[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'"ReferencedSOPInstanceUID" {uid} in '\
                  + '"ContourImageSequence" {i+1} does not match any DICOM '\
                  + '"SOPInstanceUID".'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
            
            
            
    """Verify that the StructureSetROISequence has only 1 sequence."""
    N = len(Rts.StructureSetROISequence)
    
    if N > 1:
        msg = f'There are {N} sequences in "StructureSetROISequence". There '\
              + 'should be 1.'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
    
    """Verify that the ROINumber in StructureSetROISequence is 1."""
    N = int(deepcopy(Rts.StructureSetROISequence[0].ROINumber))
    
    if N != 1:
        msg = f'"ROINumber" in "StructureSetROISequence" is {N}.  It should '\
              + 'be "1".'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    """Verify that the ReferencedFrameOfReferenceUID in StructureSetROISequence
    matches the DICOM FrameOfReferenceUID."""
    RefFORuidInSSRS = deepcopy(Rts.StructureSetROISequence[0]\
                                  .ReferencedFrameOfReferenceUID)
    
    if RefFORuidInSSRS != Dicom.FrameOfReferenceUID:
        msg = '"ReferencedFrameOfReferenceUID" in "StructureSetROISequence" '\
              + f'({RefFORuidInSSRS}) does not match DICOM '\
              + f'"FrameOfReferenceUID" ({Dicom.FrameOfReferenceUID}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
            
    
    """Verify that the ROIContourSequence has only 1 sequence."""
    N = len(Rts.ROIContourSequence)
    
    if N > 1:
        msg = f'There are {N} sequences in "ROIContourSequence". There should'\
              + ' be 1.'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)


    """Verify that the number of sequences in ContourSequence matches the
    number of sequences in ContourImageSequence."""
    CS = deepcopy(Rts.ROIContourSequence[0].ContourSequence)
    
    if len(CS) != len(CIS):
        msg = f'The number of sequences in "ContourSequence" ({len(CS)}) does'\
              + ' not match the number of sequences in "ContourImageSequence"'\
              + f' ({len(CIS)}).'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)

    
    """Verify that the ReferencedSOPInstanceUIDs in ContourSequence
    match the ReferencedSOPInstanceUIDs in ContourImageSequence."""
    RefSOPuidsInRCS = [CS[i].ContourImageSequence[0].ReferencedSOPInstanceUID for i in range(len(CS))]
    
    # Determine whether the Ref SOP UIDs match the SOP UIDs:
    IsMatch = [uid in RefSOPuidsInRFORS for uid in RefSOPuidsInRCS]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching Ref SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if NumOfMatches == 0:
        NonMatchingUids = [RefSOPuidsInRCS[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'"ReferencedSOPInstanceUID" {uid} in "ContourSequence" '\
                  + f'{i+1} does not match any "ReferencedSOPInstanceUID" in '\
                  + '"ContourImageSequence".'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
                
    
    
    """Verify that the ContourNumbers in each ContourSequence range from 1 to
    len(CS)."""
    ExpectedNums = list(range(1, len(CS)+1))
    
    ContourNums = [int(CS[i].ContourNumber) for i in range(len(CS))]
    
    # Determine whether the contour numbers match the expected contour numbers:
    IsMatch = [ContourNums[i] == ExpectedNums[i] for i in range(len(CS))]
    #IsMatch = [ContourNums[i] == i+1 for i in range(len(CS))]
    
    # Find the indices of any non-matching contour numbers:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if Inds == 0:        
        for i in range(len(Inds)):
            cn = ContourNums[Inds[i]]
            en = ExpectedNums[Inds[i]]
            
            msg = f'"ContourNumber" {i+1} is {cn} but is expected to be {en}.'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
    
    
    
    """Verify that the number of elements in ContourData is 3x 
    NumberOfContourPoints for each ContourSequence."""
    NCP = [int(CS[i].NumberOfContourPoints) for i in range(len(CS))]
    
    NCD = [len(CS[i].ContourData) for i in range(len(CS))]
    
    IsMatch = [NCD[i] == 3*NCP[i] for i in range(len(CS))]
    
    # Find the indices of any non-zero modulos:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if Inds == 0:        
        for i in range(len(Inds)):
            ncp = NCP[Inds[i]]
            
            ncd = NCD[Inds[i]]
            
            msg = f'The number of elements in "ContourData" ({ncd}) is not 3x'\
                  + f' "NumberOfContourPoints" ({ncp}) for "ContourSequence" '\
                  + f'{i+1}.'
        
            ErrorList.append(msg)
            
            if LogToConsole:
                print('\n' + msg)
    
    
    """Verify that the ReferencedROINumber in ROIContourSequence is 1."""
    N = int(deepcopy(Rts.ROIContourSequence[0].ReferencedROINumber))
    
    if N != 1:
        msg = f'"ReferencedROINumber" in "ROIContourSequence" is {N}.  It '\
              + 'should be 1.'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    
    
    """Verify that the ROIObservationsSequence has only 1 sequence."""
    N = len(Rts.RTROIObservationsSequence)
    
    if N > 1:
        msg = f'There are {N} sequences in "RTROIObservationsSequence". There'\
              + ' should be 1.'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)


    
    """Verify that the ObservationNumber is 1."""
    N = int(deepcopy(Rts.RTROIObservationsSequence[0].ObservationNumber))
    
    if N != 1:
        msg = f'"ObservationNumber" in "RTROIObservationsSequence" is {N}. '\
              + 'It should be 1.'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
            
            
            
    """Verify that the ReferencedROINumber is 1."""
    N = int(deepcopy(Rts.RTROIObservationsSequence[0].ReferencedROINumber))
    
    if N != 1:
        msg = f'"ReferencedROINumber" in "RTROIObservationsSequence" is {N}. '\
              + 'It should be 1.'
        
        ErrorList.append(msg)
        
        if LogToConsole:
            print('\n' + msg)
    
    
    print(f'\nThere were {len(ErrorList)} errors found in the RTS.')
    
    return ErrorList








def ErrorCheckRoi(Roi, DicomDir, LogToConsole=False):
    """
    Check a RTS/SEG for errors in dependencies based on provided directory of
    the DICOMs that relate to the RTS/SEG.  
    
    Inputs:
    ------
    
    Roi : Pydicom object
        RTS/SEG ROI object to be error checked.
        
    DicomDir : string
        Directory containing the DICOMs that relate to Roi.
        
    LogToConsole : boolean (default False)
        Denotes whether some results will be logged to the console.
                           
    
    Outputs:
    -------
    
    ErrorList : list of strings
        A list of strings that describe any errors that are found.  If no 
        errors are found an empty list ([]) will be returned.
    """
    
    if Roi.Modality == 'RTSTRUCT':
        ErrorList = ErrorCheckRts(Roi, DicomDir, LogToConsole)
        
    elif Roi.Modality == 'SEG':
        ErrorList = ErrorCheckSeg(Roi, DicomDir, LogToConsole)
    
    return ErrorList






"""
******************************************************************************
******************************************************************************
EXPORT NEW TARGET RTS / SEG TO DISK
******************************************************************************
******************************************************************************
"""

def ExportTrgRoi(TrgRoi, SrcRoiFpath, ExportDir, NamePrefix=''):
    """
    Export RTS/SEG to disk.  
    
    Inputs:
    ------
    
    TrgRoi : Pydicom object
        Target RTS/SEG ROI object to be exported.
        
    SrcRoiFpath : string
        Full path of the Source RTS/SEG file (used to generate the filename of
        the new RTS/SEG file).
                              
    ExportDir : string
        Directory where the new RTS/SEG is to be exported.
    
    NamePrefix : string (optional; '' by default)
        Prefix to be added to the assigned filename (after the DateTime stamp), 
        e.g. 'Case3b-i'.
                           
    
    Outputs:
    -------
    
    TrgRoiFpath : string
        Full path of the exported Target RTS/SEG file.
    """
    
    import os
    import time
    
    # Get the filename of the original RTS/SEG file:
    #SrcRoiFname = os.path.split(SrcRoiFpath)[1]
    
    CurrentDateTime = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    
    #FnamePrefix = CurrentDateTime + '_' + NamePrefix + '_from_' 
    FnamePrefix = CurrentDateTime + '_' + NamePrefix
    
    # Create a new filename (this will appear under Label in XNAT):
    #TrgRoiFname = FnamePrefix + SrcRoiFname
    #TrgRoiFname = FnamePrefix
    TrgRoiFname = FnamePrefix + '.dcm' # 'dcm' was missing (found 18/12)
    
    TrgRoiFpath = os.path.join(ExportDir, TrgRoiFname)
    
    TrgRoi.save_as(TrgRoiFpath)
        
    print('\nNew Target RTS/SEG exported to:\n\n', TrgRoiFpath)
    
    return TrgRoiFpath