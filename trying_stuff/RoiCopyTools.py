# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:12:23 2020

@author: ctorti
"""


"""
ROI copying tools
"""



# Import packages and functions:
import pydicom
from pydicom.pixel_data_handlers.numpy_handler import pack_bits
import copy
import os
import time
import sys
#import natsort
import numpy as np
#import math
import SimpleITK as sitk
#from DicomTools import GetDicomFpaths
from DicomTools import ImportDicoms
from DicomTools import ImportImage
from DicomTools import GetImageAttributes
from DicomTools import GetDicomSOPuids
import matplotlib.pyplot as plt




"""
******************************************************************************
******************************************************************************
GENERAL UTILITY FUNCTIONS
******************************************************************************
******************************************************************************
"""


def GetExtremePoints(Image):

    pts = [Image.TransformIndexToPhysicalPoint((0, 0, 0)), 
           Image.TransformIndexToPhysicalPoint((Image.GetWidth(), 0, 0)),
           Image.TransformIndexToPhysicalPoint((Image.GetWidth(), Image.GetHeight(), 0)),
           Image.TransformIndexToPhysicalPoint((0, Image.GetHeight(), 0)),
           Image.TransformIndexToPhysicalPoint((0, 0, Image.GetDepth())), 
           Image.TransformIndexToPhysicalPoint((Image.GetWidth(), 0, Image.GetDepth())),
           Image.TransformIndexToPhysicalPoint((Image.GetWidth(), Image.GetHeight(), Image.GetDepth())),
           Image.TransformIndexToPhysicalPoint((0, Image.GetHeight(), Image.GetDepth()))]
    
    return pts




def ConvertPcsPointToIcs(PointPCS, Origin, Directions, Spacings):
    """
    Convert a point from the Patient Coordinate System (PCS) to the Image 
    Coordinate System (ICS).
    
    Input:
        PointPCS   - (List of floats) Points in the Patient Coordinate System, 
                     e.g. [x, y, z]
        
        Origin     - (List of floats) The 3D image origin 
                     (= ImagePositionPatient of the first slice in the DICOM 
                     series), e.g. [x0, y0, z0]
        
        Directions - (List of floats) The direction cosine along x (rows), 
                     y (columns) and z (slices) (= the cross product of the 
                     x and y direction cosines from ImageOrientationPatient 
                     appended to ImageOrientationPatient),
                     e.g. [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz]
        
        Spacings   - (List of floats) The pixel spacings along x, y and z 
                     (= SliceThickness appended to PixelSpacing), 
                     e.g. [di, dj, dk]
    
        
    Returns:
        PointICS   - (List of floats) PointPCS converted to the ICS,
                     e.g. [x, y, z]
        
    
    Equations:
    
    P = S + (di*i).X + (dj*j).Y + (dk*k).Z
    
    where P = (Px, Py, Pz) is the point in the Patient Coordinate System
    
          S = (Sx, Sy, Sz) is the origin in the Patient Coordinate System (i.e.
          the ImagePositionPatient)
          
          X = (Xx, Xy, Xz) is the direction cosine vector along rows (x) 
          
          Y = (Yx, Yy, Yz) is the direction cosine vector along columns (y)
          
          Z = (Zx, Zy, Zz) is the direction cosine vector along slices (z)
          
          di, dj and dk are the pixel spacings along x, y and z
          
          i, j, and k are the row (x), column (y) and slice (z) indices
          
          
    Solve for i, j and k, i.e.:
        
        Vx = Xx*di*i + Yx*dj*j + Zx*dk*k
        
        Vy = Xy*di*i + Yy*dj*j + Zy*dk*k
        
        Vz = Xz*di*i + Yz*dk*k + Zz*dk*k
        
    where Vx = Px - Sx
    
          Vy = Py - Sy
          
          Vz = Pz - Sz
          
    Solving for i, j and k results in the expressions:
        
        i = (1/di)*d/e
            
        j = (1/dj)*( (a/b)*di*i + c/b )
        
        k = (1/dk)*(1/Zz)*(Vz - Xz*di*i - Yz*dj*j)
        or
        k = (1/dk)*(1/Zz)*( Vz - (c/b)*Yz - (Xz + (a/b)*Yz)*di*i )
        
        (either expression for k should be fine)
        
    In the case where X = [1, 0, 0]
                      Y = [0, 1, 0]
                      Z = [0, 0, 1]
                      
    The expressions simplify to:
        
        a = 0
        
        b = 1
        
        c = Vy
        
        d = Vx
        
        e = 1
        
        i = Vx/di
        
        j = Vy/dj
        
        k = Vz/dk
        
    """
    
    # Define S, X, Y and Z:
    S = Origin # the origin
    
    X = Directions[0:3] # the row (x) direction cosine vector
    Y = Directions[3:6] # the column (y) direction cosine vector
    Z = Directions[6:] # the slice (z) direction cosine vector
    
    # The indeces of the largest direction cosines along rows, columns and 
    # slices:
    ind_i = X.index(max(X)) # typically = 0
    ind_j = Y.index(max(Y)) # typically = 1
    ind_k = Z.index(max(Z)) # typically = 2

    # The pixel spacings:
    di = Spacings[0]
    dj = Spacings[1]
    dk = Spacings[2] 
    
    # Simplifying expressions:
    Xx = X[ind_i]
    Xy = X[ind_j]
    Xz = X[ind_k]
    
    Yx = Y[ind_i]
    Yy = Y[ind_j]
    Yz = Y[ind_k]
    
    Zx = Z[ind_i]
    Zy = Z[ind_j]
    Zz = Z[ind_k]
    
    # Define simplifying expressions:
    Vx = PointPCS[0] - S[0]
    Vy = PointPCS[1] - S[1]
    Vz = PointPCS[2] - S[2]
    
    a = Xz*Zy/Zz - Xy
    
    b = Yy - Yz*Zy/Zz
    
    c = Vy - Vz*Zy/Zz
    
    d = Vx - (c/b)*Yx - (Zx/Zz)*(Vz - (c/b)*Yz)
    
    e = Xx + (a/b)*Yx - (Zx/Zz)*(Xz + (a/b)*Yz)
    
    # Solve for i, j and k:
    i = (1/di)*d/e
    
    j = (1/dj)*( (a/b)*di*i + c/b )
    
    k = (1/dk)*(1/Zz)*(Vz - Xz*di*i - Yz*dj*j)
    #k = (1/dk)*(1/Zz)*( Vz - (c/b)*Yz - (Xz + (a/b)*Yz)*di*i )
    
    PointICS = [i, j, k]
    
    return PointICS


    



def ConvertContourDataToIcsPoints(ContourData, DicomDir):
    """
    Convert contour data from a flat list of points in the Patient Coordinate
    System (PCS) to a list of [x, y, z] points in the Image Coordinate System. 
    
    Inputs:
        ContourData - (List of floats) Flat list of points in the PCS,
                      e.g. [x0, y0, z0, x1, y1, z1, ...]
        
        DicomDir    - (String) Directory containing DICOMs
        
        
    Returns:
        PointsICS   - (List of floats) List of a list of [x, y, z] coordinates
                      of each point in ContourData converted to the ICS,
                      e.g. [[x0, y0, z0], [x1, y1, z1], ...]
    """
    
    
    # Get the image attributes:
    #Origin, Directions, Spacings, Dimensions = GetImageAttributes(DicomDir)
    IPPs, Directions, Spacings, Dimensions = GetImageAttributes(DicomDir)
    
    # Initialise the array of contour points:
    PointsICS = []
    
    # Iterate for all contour points in threes:
    for p in range(0, len(ContourData), 3):
        # The point in Patient Coordinate System:
        pointPCS = [ContourData[p], ContourData[p+1], ContourData[p+2]]
        
        # Convert ptPCS to Image Coordinate System:
        #pointICS = ConvertPcsPointToIcs(pointPCS, Origin, Directions, Spacings)
        pointICS = ConvertPcsPointToIcs(pointPCS, IPPs[0], Directions, Spacings)
        
        PointsICS.append(pointICS)
        
    return PointsICS
        
    



def UnpackPoints(Points):
    """
    Unpack list of a list of [x, y, z] coordinates into lists of x, y and z
    coordinates.
    
    Input:
        Points - (List of floats) List of a list of [x, y, z] coordinates,
                 e.g. [[x0, y0, z0], [x1, y1, z1], ...]
        
    Returns:
        X      - (List of floats) List of all x coordinates in Points,
                 e.g. [x0, x1, x2, ...]
        
        Y      - (List of floats) List of all y coordinates in Points,
                 e.g. [y0, y1, y2, ...]
        
        Z      - (List of floats) List of all z coordinates in Points,
                 e.g. [z0, z1, z2, ...]
    """
    
    # Initialise unpacked lists:
    X = []
    Y = []
    Z = []
    
    # Unpack tuple and store in X, Y, Z:
    for x, y, z in Points:
        X.append(x)
        Y.append(y)
        Z.append(z)
        
    return X, Y, Z
    
                    




def PlotDicomsAndContours(DicomDir, RtsFpath, ExportPlot, ExportDir, 
                          LogToConsole=False):
    
    
    
    # Import the DICOMs:
    Dicoms = ImportDicoms(DicomDir=DicomDir)
    
    # Get the DICOM SOP UIDs:
    SOPuids = GetDicomSOPuids(DicomDir=DicomDir)
    
    # Import the RTS ROI:
    RtsRoi = pydicom.dcmread(RtsFpath)
    
    # Get the ContourImageSequence-to-DICOM slice indices:
    CIStoDcmInds = GetCIStoDcmInds(RtsRoi, SOPuids)
    
    # Get a list of the Contour Sequences in the ROI:
    ContourSequences = RtsRoi.ROIContourSequence[0].ContourSequence
    
    
    # Prepare the figure.
    
    # All DICOM slices that have contours will be plotted. The number of
    # slices to plot:
    Nslices = len(CIStoDcmInds)
    
    # Set the number of subplot rows and columns:
    Ncols = np.int8(np.ceil(np.sqrt(Nslices)))
    
    # Limit the number of rows to 5 otherwise it's difficult to make sense of
    # the images:
    if Ncols > 5:
        Ncols = 5
    
    Nrows = np.int8(np.ceil(Nslices/Ncols))
    
    # Create a figure with two subplots and the specified size:
    if ExportPlot:
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows), dpi=300)
        fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows), dpi=300)
    else:
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows))
        fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows))
        
    
    n = 0 # sub-plot number
    
    # Loop through each slice: 
    for i in range(Nslices):
        if LogToConsole:
                print('\ni =', i)
                
        n += 1 # increment sub-plot number
        
        # The DICOM slice number is:
        s = CIStoDcmInds[i]
        
        #plt.subplot(Nrows, Ncols, n)
        #plt.axis('off')
        ax = plt.subplot(Nrows, Ncols, n)

        #ax = plt.subplot(Nrows, Ncols, n, aspect=AR)
          
        # Plot the DICOM pixel array:
        ax.imshow(Dicoms[s].pixel_array, cmap=plt.cm.Greys_r)
        #ax.set_aspect(ar)
        
        # Get the Contour Sequence that corresponds to this slice:
        ContourSequence = ContourSequences[i]
        
        # Get the Contour Data:
        ContourData = [float(item) for item in ContourSequence.ContourData]
                
        # Convert contour data from Patient Coordinate System to Image 
        # Coordinate System:
        PointsICS = ConvertContourDataToIcsPoints(ContourData, DicomDir)
        
        # Unpack the points:
        X, Y, Z = UnpackPoints(PointsICS)
        
        # Plot the contour points:
        plt.plot(X, Y, linewidth=0.5, c='red');
        
        
        ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
        
        ax.set_title(f'Slice {s}')
        #plt.axis('off')
        
            
            
    if ExportPlot:
        RtsFullFname = os.path.split(RtsFpath)[1]
        
        RtsFname = os.path.splitext(RtsFullFname)[0]
        
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
        
        ExportFname = CurrentDateTime + '_' + RtsFname
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
        
    #print(f'PixAR = {PixAR}')
    #print(f'AxisAR = {AxisAR}')
        
    return





def PlotSitkImages_Src_ResSrc_Trg(SrcIm, ResSrcIm, TrgIm, Method, Interpolation,
                                  ExportPlot, ExportDir, SrcImLabel, TrgImLabel,
                                  LogToConsole=False, dpi=80):
    
    if LogToConsole:
        print('\nThe Source and Target image size:\n',
                      f'\n   Original Source:  {SrcIm.GetSize()} \n',
                      f'\n   Resampled Source: {ResSrcIm.GetSize()} \n',
                      f'\n   Target:           {TrgIm.GetSize()}')
            
        print('\nThe Source and Target voxel spacings:\n',
                      f'\n   Original Source:  {SrcIm.GetSpacing()} \n',
                      f'\n   Resampled Source: {ResSrcIm.GetSpacing()} \n',
                      f'\n   Target:           {TrgIm.GetSpacing()}')
            
        print('\nThe Source and Target Origin:\n',
                      f'\n   Original Source:  {SrcIm.GetOrigin()} \n',
                      f'\n   Resampled Source: {ResSrcIm.GetOrigin()} \n',
                      f'\n   Target:           {TrgIm.GetOrigin()}')
            
        print('\nThe Source and Target Direction:\n',
                      f'\n   Original Source:  {SrcIm.GetDirection()} \n',
                      f'\n   Resampled Source: {ResSrcIm.GetDirection()} \n',
                      f'\n   Target:           {TrgIm.GetDirection()}')

    
    
    # Convert from SimpleITK image to Numpy arrays:
    SrcNpa = sitk.GetArrayFromImage(SrcIm)
    ResSrcNpa = sitk.GetArrayFromImage(ResSrcIm)
    TrgNpa = sitk.GetArrayFromImage(TrgIm)
    
    # Prepare the figure:
    Nslices = max(SrcIm.GetSize()[2], TrgIm.GetSize()[2])
    
    # Set the number of subplot rows and columns:
    Ncols = 3
    
    Nrows = Nslices
    
    
    # Create a figure with two subplots and the specified size:
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows))
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Loop through each slice: 
    for i in range(Nslices):
        #if LogToConsole:
        #        print('\ni =', i)
        
        #plt.subplot(Nrows, Ncols, n)
        #plt.axis('off')
        #ax = plt.subplot(Nrows, Ncols, n)

        #ax = plt.subplot(Nrows, Ncols, n, aspect=AR)
         
        # Plot the Original Source slice:
        if i < SrcIm.GetSize()[2]:
            #maximum = SrcNpa[i].max()
            maximum = np.amax(SrcNpa[i])
            if maximum <= 1:
                maximum = 1
            
            ax = plt.subplot(Nrows, Ncols, n)
            im = ax.imshow(SrcNpa[i], cmap=plt.cm.Greys_r)
            cbar = fig.colorbar(im, ax=ax)
            cbar.mappable.set_clim(0, maximum)
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'Original Source slice {i}')
            
        n += 1 # increment sub-plot number
            
        # Plot the Resampled Source slice:
        if i < ResSrcIm.GetSize()[2]:
            #maximum = ResSrcNpa[i].max()
            maximum = np.amax(ResSrcNpa[i])
            if maximum <= 1:
                maximum = 1
                
            ax = plt.subplot(Nrows, Ncols, n)
            im = ax.imshow(ResSrcNpa[i], cmap=plt.cm.Greys_r)
            cbar = fig.colorbar(im, ax=ax)
            cbar.mappable.set_clim(0, maximum)
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'Resampled Source slice {i}')
            
        n += 1 # increment sub-plot number
        
        # Plot the Target slice:
        if i < TrgIm.GetSize()[2]:
            #maximum = TrgNpa[i].max()
            maximum = np.amax(TrgNpa[i])
            if maximum <= 1:
                maximum = 1
                
            ax = plt.subplot(Nrows, Ncols, n)
            im = ax.imshow(TrgNpa[i], cmap=plt.cm.Greys_r)
            cbar = fig.colorbar(im, ax=ax)
            cbar.mappable.set_clim(0, maximum)
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'Target slice {i}')
            
        n += 1 # increment sub-plot number
        
      
    
    #print(f'PixAR = {PixAR}')
    #print(f'AxisAR = {AxisAR}')
    
    if ExportPlot:
        # Short version of Interpolation for exported filename:
        if 'inear' in Interpolation:
            Interp = 'Lin'
        if 'pline' in Interpolation:
            Interp = 'BSp'
        if ('earest' and 'eighbo' or 'nn' or 'NN') in Interpolation:    
            Interp = 'NN'
            
        # Short version of ResampleImageFilter:
        if Method == 'ResampleImageFilter':
            Method = 'ResampleImFilt'
            
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
    
        ExportFname = CurrentDateTime + '_Orig' + SrcImLabel + '_Resamp' \
                      + SrcImLabel + '_' + TrgImLabel + '_images_' \
                      + Method + '_' + Interp + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return







"""
******************************************************************************
******************************************************************************
CONTOUR-RELATED FUNCTIONS
******************************************************************************
******************************************************************************
"""

def GetCIStoDcmInds(RtsRoi, SOPuids):
    """
    Get the DICOM slice numbers that correspond to each Contour Image Sequence
    in an RTSTRUCT ROI.
    
    Inputs:
        RtsRoi       - ROI Object from an RTSTRUCT file
        
        SOPuids      - List of strings of the SOP UIDs of the DICOMs
        
    Returns:
        CIStoDcmInds - List of integers of the DICOM slice numbers that
                       correspond to each Contour Image Sequence in RtsRoi
    """
    
    CIStoDcmInds = [] 
    
    # Loop through each Contour Image Sequence:
    sequences = RtsRoi.ReferencedFrameOfReferenceSequence[0]\
                      .RTReferencedStudySequence[0]\
                      .RTReferencedSeriesSequence[0]\
                      .ContourImageSequence
    
    for sequence in sequences:
        # Get the Reference SOP Instance UID:
        uid = sequence.ReferencedSOPInstanceUID
        
        # Find the matching index of this UID in SOPuids:
        CIStoDcmInds.append(SOPuids.index(uid))
        
    return CIStoDcmInds




def GetCStoDcmInds(RtsRoi, SOPuids):
    """
    Get the DICOM slice numbers that correspond to each Contour Sequence
    in an RTSTRUCT ROI.
    
    Inputs:
        RtsRoi      - ROI Object from an RTSTRUCT file
        
        SOPuids     - List of strings of the SOP UIDs of the DICOMs
        
    Returns:
        CStoDcmInds - List of integers of the DICOM slice numbers that 
                      correspond to each Contour Sequence in RtsRoi 
    """
    
    CStoDcmInds = [] 
    
    # Loop through each Contour Image Sequence:
    sequences = RtsRoi.ROIContourSequence[0].ContourSequence
    
    for sequence in sequences:
        # Get the Reference SOP Instance UID:
        uid = sequence.ContourImageSequence[0].ReferencedSOPInstanceUID
        
        # Find the matching index of this UID in SOPuids:
        CStoDcmInds.append(SOPuids.index(uid))
        
    return CStoDcmInds




def VerifyCISandCS(CIStoDcmInds, CStoDcmInds, LogToConsole=False):
    """
    Verify that the ContourImageSequence-to-DICOM slice indeces and the
    ContourSequence-to-DICOM slice indeces are the same.
    
    Inputs:
        CIStoDcmInds - List of integers of the DICOM slice numbers that 
                      correspond to each Contour Image Sequence
        
        CStoDcmInds  - List of integers of the DICOM slice numbers that 
                      correspond to each Contour Sequence
        
    Returns:
        (Boolean) True/False if they match/do not match  
    """
    
    if CIStoDcmInds != CStoDcmInds:
        if LogToConsole:
            print('\nThe ContourImageSequence-to-DICOM slice indices are not',
                  'the same as the ContourSequence-to-DICOM slice indices.')
            
        return False
    
    else:
        return True
    
    


def AddToRtsSequences(RtsRoi):
    """
    Append the last item in the following sequences in the RTS Object:
        Contour Image Sequence
        Contour Sequence
    
    Inputs:
        RtsRoi    - ROI Object from an RTSTRUCT file
        
    Returns:
        NewRtsRoi - Modified ROI Object with sequences lengthened by one
    """
    
    # Use RtsRoi as a template for NewRtsRoi: 
    NewRtsRoi = copy.deepcopy(RtsRoi)
        
    # The last item in Contour Image Sequence:
    last = copy.deepcopy(RtsRoi.ReferencedFrameOfReferenceSequence[0]\
                               .RTReferencedStudySequence[0]\
                               .RTReferencedSeriesSequence[0]\
                               .ContourImageSequence[-1])
    
    # Append to the Contour Image Sequence:
    NewRtsRoi.ReferencedFrameOfReferenceSequence[0]\
             .RTReferencedStudySequence[0]\
             .RTReferencedSeriesSequence[0]\
             .ContourImageSequence\
             .append(last)

    # The last item in Contour Sequence:
    last = copy.deepcopy(RtsRoi.ROIContourSequence[0]\
                               .ContourSequence[-1])
    
    # Append to the Contour Sequence:
    NewRtsRoi.ROIContourSequence[0]\
             .ContourSequence\
             .append(last)
             
    return NewRtsRoi




def AddIndToIndsAndSort(Inds, Ind):
    """
    Append the integer Ind to a list of intergers Inds and return the sorted
    list. 
    
    Inputs:
        Inds    - List of integers 
        
        Ind     - Integer
        
    Returns:
        NewInds - Appended and sorted list of integers
    """
    
    NewInds = copy.deepcopy(Inds)

    NewInds.append(Ind)
    
    NewInds.sort()
    
    return NewInds
    



def ModifyRtsTagVals(OrigRtsRoi, NewRtsRoi, FromSliceNum, ToSliceNum, Dicoms,
                     OrigCIStoDcmInds, NewCIStoDcmInds, LogToConsole=False):
    """
    Modify various tag values of the new RTS ROI so that they are consistent
    with the corresponding tag values of the DICOMs (e.g. SOPClassUID, 
    SOPInstanceUID), and so that the ROIContourSequence values are consistent
    with those of the original RTS ROI for existing contours, and with the
    contour that has been copied from the original RTS ROI.
         
    
    Inputs:
        OrigRtsRoi       - Original ROI Object 
        
        NewRtsRoi        - New/modified ROI Object
        
        FromSliceNum     - (Integer) Slice index in the DICOM stack
                           corresponding to the contour to be copied 
                           (counting from 0)
                          
        ToSliceNum       - (Integer) Slice index in the DICOM stack
                           where the contour will be copied to (counting from 
                           0)
                          
        Dicoms           - A list of DICOM Objects that include the DICOMs that
                           NewRtsRoi relate to
                          
        OrigCIStoDcmInds - List of integers of the DICOM slice numbers that 
                           correspond to each Contour Image Sequence in 
                           OrigRtsRoi
                          
        NewCIStoDcmInds  - List of integers of the DICOM slice numbers that 
                           correspond to each Contour Image Sequence in 
                           NewRtsRoi
                           
        LogToConsole     - (Boolean) Denotes whether or not some intermediate
                            results will be logged to the console
        
    Returns:
        NewRtsRoi        - Modified new ROI Object for the Target series
    """
    
    # Get the sequence number that corresponds to the slice number to be 
    # copied, and the slice number to be copied to:
    FromOrigSeqNum = OrigCIStoDcmInds.index(FromSliceNum)
    ToNewSeqNum = NewCIStoDcmInds.index(ToSliceNum)
    
    if LogToConsole:
            print(f'\nFromOrigSeqNum = {FromOrigSeqNum} -->',
                  f'OrigCIStoDcmInds[{FromOrigSeqNum}] =',
                  f'{OrigCIStoDcmInds[FromOrigSeqNum]}')
            
            print(f'ToNewSeqNum   = {ToNewSeqNum} -->',
                  f'NewCIStoDcmInds[{ToNewSeqNum}] =',
                  f'{NewCIStoDcmInds[ToNewSeqNum]}')
    
    # Loop through each index in NewCIStoDcmInds and modify the values:
    for i in range(len(NewCIStoDcmInds)):
        # The DICOM slice index for the i^th sequence:
        s = NewCIStoDcmInds[i]
        
        if LogToConsole:
            print(f'\nNewCIStoDcmInds[{i}] = {NewCIStoDcmInds[i]}')
            print(f'DICOM slice number = {s}')
        
        # Modify the Referenced SOP Class UID and Referenced SOP Instance UID 
        # so that they are consistent with the SOP Class UID and SOP Instance  
        # UID of their corresponding DICOMs:
        """ SOPClassUIDs will need to be modified for cases where the contour
        is being copied across different modality images. Not required for
        copying within the same series:
        NewRtsRoi.ReferencedFrameOfReferenceSequence[0]\
                 .RTReferencedStudySequence[0]\
                 .RTReferencedSeriesSequence[0]\
                 .ContourImageSequence[i]\
                 .ReferencedSOPClassUID = Dicoms[s].SOPClassUID
        """
        
        NewRtsRoi.ReferencedFrameOfReferenceSequence[0]\
                 .RTReferencedStudySequence[0]\
                 .RTReferencedSeriesSequence[0]\
                 .ContourImageSequence[i]\
                 .ReferencedSOPInstanceUID = Dicoms[s].SOPInstanceUID
        
        """ Ditto:
        NewRtsRoi.ROIContourSequence[0]\
                 .ContourSequence[i]\
                 .ContourImageSequence[0]\
                 .ReferencedSOPClassUID = Dicoms[s].SOPClassUID
        """
        
        NewRtsRoi.ROIContourSequence[0]\
                 .ContourSequence[i]\
                 .ContourImageSequence[0]\
                 .ReferencedSOPInstanceUID = Dicoms[s].SOPInstanceUID
                 
        
        
        # Modify the Contour Number to match the value of the Source contour
        #  being copied:
        NewRtsRoi.ROIContourSequence[0]\
                 .ContourSequence[i]\
                 .ContourNumber = f"{i + 1}"
                     
                     
        # Modify select values in ROIContourSequence:         
        if i == ToNewSeqNum: 
            if LogToConsole:
                print('\nThis is a new sequence.')
                print(f'Copying the {FromOrigSeqNum}th sequence from Source',
                      f'to the {i}th sequence in Target.')
                
            # This is the new sequence. Copy from FromSeqNum.
            # Modify the Number of Contour Points to match the value of the 
            # Source contour being copied:
            NewRtsRoi.ROIContourSequence[0]\
                     .ContourSequence[i]\
                     .NumberOfContourPoints = copy.deepcopy(OrigRtsRoi.ROIContourSequence[0]\
                                                                      .ContourSequence[FromOrigSeqNum]\
                                                                      .NumberOfContourPoints)
            
            # Modify the Contour Data to match the value of the Source contour
            # being copied:
            NewRtsRoi.ROIContourSequence[0]\
                     .ContourSequence[i]\
                     .ContourData = copy.deepcopy(OrigRtsRoi.ROIContourSequence[0]\
                                                            .ContourSequence[FromOrigSeqNum]\
                                                            .ContourData)
        
        else:
            # This is an existing sequence. Find the index of OrigCIStoDcmInds 
            # for this sequence number (of NewCIStoDcmInds):
            ind = OrigCIStoDcmInds.index(NewCIStoDcmInds[i])
            
            if LogToConsole:
                print('\nThis is an existing sequence.')
                print(f'Copying the {ind}th sequence from Source to the {i}th',
                      f'sequence in Target.')
                                          
            # Modify the Number of Contour Points to match the value of the 
            # Source contour being copied:
            NewRtsRoi.ROIContourSequence[0]\
                     .ContourSequence[i]\
                     .NumberOfContourPoints = copy.deepcopy(OrigRtsRoi.ROIContourSequence[0]\
                                                                      .ContourSequence[ind]\
                                                                      .NumberOfContourPoints)
            
            # Modify the Contour Data to match the value of the Source contour
            # being copied:
            NewRtsRoi.ROIContourSequence[0]\
                     .ContourSequence[i]\
                     .ContourData = copy.deepcopy(OrigRtsRoi.ROIContourSequence[0]\
                                                            .ContourSequence[ind]\
                                                            .ContourData)
                                          
    return NewRtsRoi
                                          
                                          
    
    



def CopyContourWithinSeries(SrcDcmDir, SrcRtsFpath, FromSliceNum, ToSliceNum, 
                            LogToConsole=False):
    """
    Copy a single contour on a given slice to another slice within the same
    DICOM series.
    
    
    Inputs:
        SrcDcmDir    - (String) Directory containing the Source (= Target) 
                       DICOMs
                            
        SrcRtsFpath  - (String) Full path of the Source (= Target) 
                       DICOM-RTSTRUCT file 
                             
        FromSliceNum - (Integer) Slice index of the Source (= Target) DICOM 
                       stack corresponding to the contour to be copied 
                       (counting from 0)
                             
        ToSliceNum   - (Integer) Slice index of the Target (= Source) DICOM 
                       stack where the contour will be copied to (counting from 
                       0)
                            
        LogToConsole - (Boolean) Denotes whether or not some intermediate
                       results will be logged to the console
                            
    Returns:
        TrgRtsRoi    - Modified Target (= Source) ROI object 
    
    """
    
    # Import the Source RTSTRUCT ROI:
    SrcRtsRoi = pydicom.dcmread(SrcRtsFpath)
    
    # Import the Source (= Target) DICOMs:
    SrcDicoms = ImportDicoms(DicomDir=SrcDcmDir)
    
    # Get the Source (= Target) DICOM SOP UIDs:
    SrcSOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    
    # Get the ContourImageSequence-to-DICOM slice indices, 
    # and ContourSequence-to-DICOM slice indices for the Source DICOMs:
    SrcCIStoDcmInds = GetCIStoDcmInds(SrcRtsRoi, SrcSOPuids)
    
    SrcCStoDcmInds = GetCStoDcmInds(SrcRtsRoi, SrcSOPuids)
    
    # Both indices should be the same.  Return if not:
    if not VerifyCISandCS(SrcCIStoDcmInds, SrcCStoDcmInds, LogToConsole):
        return
        
    
    # Verify that a contour exists for FromSliceNum (this check won't be 
    # necessary in the OHIF-Viewer but a bad input could occur here):
    if not FromSliceNum in SrcCIStoDcmInds:
        print(f'\nA contour does not exist on slice {FromSliceNum}.')
        
        return
    
    
    # Check if ToSliceNum already has a contour:
    """
    Note:
        If slice number ToSliceNum already has a contour, it will be 
        over-written with the contour data of slice number FromSliceNum.
        If it doesn't have a contour, ContourImageSequence and 
        ContourSequence need to be extended by one.
    """
    if ToSliceNum in SrcCIStoDcmInds:
        # Use SrcRtsRoi as a template for TrgRtsRoi: 
        TrgRtsRoi = copy.deepcopy(SrcRtsRoi)
        
        # Create a new list of CIStoDcmInds:
        TrgCIStoDcmInds = copy.deepcopy(SrcCIStoDcmInds)
        
    else:
        # Increase the length of the sequences:
        TrgRtsRoi = AddToRtsSequences(SrcRtsRoi)
        
        # Create a new list of CIStoDcmInds by adding the index ToSliceNum 
        # (representing the contour to be added to ContourImageSequence and to
        # ContourSequence) to SrcCIStoDcmInds:
        TrgCIStoDcmInds = AddIndToIndsAndSort(SrcCIStoDcmInds, ToSliceNum)
        
    
    if LogToConsole:
        print('\nSrcCIStoDcmInds =', SrcCIStoDcmInds)
        print('\nTrgCIStoDcmInds =', TrgCIStoDcmInds)
    
    # Modify select tags in TrgRtsRoi:
    TrgRtsRoi = ModifyRtsTagVals(SrcRtsRoi, TrgRtsRoi, FromSliceNum, ToSliceNum, 
                                 SrcDicoms, SrcCIStoDcmInds, TrgCIStoDcmInds,
                                 LogToConsole)
    
    
    
    # Generate a new SOP Instance UID:
    TrgRtsRoi.SOPInstanceUID = pydicom.uid.generate_uid()
    
    # Generate a new Series Instance UID:
    TrgRtsRoi.SeriesInstanceUID = pydicom.uid.generate_uid()
    
    
    return TrgRtsRoi





def DirectCopyContourAcrossSeries(SrcDcmDir, SrcRtsFpath, FromSliceNum, 
                                  TrgDcmDir, TrgRtsFpath, ToSliceNum, 
                                  LogToConsole=False):
    """
    Make a direct copy of a single contour on a given slice to another slice in 
    a different DICOM series.  A direct copy implies that the z-coordinates of
    the Target points (copy of Source points) do not relate to the 
    z-coordinates of the DICOM slice, since the voxels corresponding to the 
    Target ROI volume do not relate to the voxels of the Source ROI volume.
    
    
    Inputs:
        SrcDcmDir    - (String) Directory containing the Source DICOMs
                            
        SrcRtsFpath  - (String) Full path of the Source DICOM-RTSTRUCT file 
                             
        FromSliceNum - (Integer) Slice index of the Source DICOM stack 
                       corresponding to the contour to be copied (counting from 
                       0)
                       
        TrgDcmDir    - (String) Directory containing the Target DICOMs
                            
        TrgRtsFpath  - (String) Full path of the Target DICOM-RTSTRUCT file 
                             
        ToSliceNum   - (Integer) Slice index of the Target DICOM stack where
                       the contour will be copied to (counting from 0)
                            
        LogToConsole - (Boolean) Denotes whether or not some intermediate
                       results will be logged to the console
                            
    Returns:
        NewTrgRtsRoi  - Modified Target ROI object 
    
    """
    
    # Import the Source and Target RTSTRUCT ROI:
    SrcRtsRoi = pydicom.dcmread(SrcRtsFpath)
    TrgRtsRoi = pydicom.dcmread(TrgRtsFpath)
    
    # Import the Target DICOMs:
    TrgDicoms = ImportDicoms(DicomDir=TrgDcmDir)
    
    # Get the Source and Target DICOM SOP UIDs:
    SrcSOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    TrgSOPuids = GetDicomSOPuids(DicomDir=TrgDcmDir)
    
    # Get the ContourImageSequence-to-DICOM slice indices, 
    # and ContourSequence-to-DICOM slice indices for Source and Target:
    SrcCIStoDcmInds = GetCIStoDcmInds(SrcRtsRoi, SrcSOPuids)
    
    SrcCStoDcmInds = GetCStoDcmInds(SrcRtsRoi, SrcSOPuids)
    
    TrgCIStoDcmInds = GetCIStoDcmInds(TrgRtsRoi, TrgSOPuids)
    
    TrgCStoDcmInds = GetCStoDcmInds(TrgRtsRoi, TrgSOPuids)
    
    # Both indices should be the same.  Return if not:
    if not VerifyCISandCS(SrcCIStoDcmInds, SrcCStoDcmInds, LogToConsole):
        return
    
    if not VerifyCISandCS(TrgCIStoDcmInds, TrgCStoDcmInds, LogToConsole):
        return
        
    
    # Verify that a contour exists for FromSliceNum (this check won't be 
    # necessary in the OHIF-Viewer but a bad input could occur here):
    if not FromSliceNum in SrcCIStoDcmInds:
        print(f'\nA contour does not exist on slice {FromSliceNum} in the',
              'Source DICOM series.')
        
        return
    
    # Verify that the slice that a contour is to be copied to exists (this 
    # check won't be necessary in the OHIF-Viewer but a bad input could occur
    # here):
    if not ToSliceNum in list(range(len(TrgDicoms))):
        print(f'\nThe Target DICOM series does not have slice {ToSliceNum}.')
        
        return
    
    
    # Check if ToSliceNum already has a contour:
    """
    Note:
        If slice number ToSliceNum already has a contour, it will be 
        over-written with the contour data of slice number FromSliceNum.
        If it doesn't have a contour, ContourImageSequence and 
        ContourSequence need to be extended by one.
    """
    if ToSliceNum in TrgCIStoDcmInds:
        # Use TrgRtsRoi as a template for NewTrgRtsRoi: 
        NewTrgRtsRoi = copy.deepcopy(TrgRtsRoi)
        
        # Create a new list of NewTrgCIStoDcmInds:
        NewTrgCIStoDcmInds = copy.deepcopy(TrgCIStoDcmInds)
        
    else:
        # Increase the length of the sequences:
        NewTrgRtsRoi = AddToRtsSequences(TrgRtsRoi)
        
        # Create a new list of TrgCIStoDcmInds by adding the index ToSliceNum 
        # (representing the contour to be added to ContourImageSequence and to
        # ContourSequence) to TrgCIStoDcmInds:
        NewTrgCIStoDcmInds = AddIndToIndsAndSort(TrgCIStoDcmInds, ToSliceNum)
        
    
    if LogToConsole:
        print('\nSrcCIStoDcmInds    =', SrcCIStoDcmInds)
        print('\nTrgCIStoDcmInds    =', TrgCIStoDcmInds)
        print('\nNewTrgCIStoDcmInds =', NewTrgCIStoDcmInds)
    
    # Modify select tags in TrgRtsRoi:
    NewTrgRtsRoi = ModifyRtsTagVals(TrgRtsRoi, NewTrgRtsRoi, FromSliceNum, 
                                    ToSliceNum, TrgDicoms, 
                                    TrgCIStoDcmInds, NewTrgCIStoDcmInds,
                                    LogToConsole)
    
    
    
    # Generate a new SOP Instance UID:
    NewTrgRtsRoi.SOPInstanceUID = pydicom.uid.generate_uid()
    
    # Generate a new Series Instance UID:
    NewTrgRtsRoi.SeriesInstanceUID = pydicom.uid.generate_uid()
    
    
    return NewTrgRtsRoi





def MappedCopyContourAcrossSeries_OLD(SrcDcmDir, SrcRoiFpath, FromSliceNum, 
                                 TrgDcmDir, TrgRoiFpath, LogToConsole):
    """
    I need to work with labelmaps!!!  See MappedCopySegmentAcrossSeries...
    
    Make a relationship-preserving copy of a single contour on a given slice to  
    a different DICOM series.  Since the relationship is preserved, the voxels 
    corresponding to the points copied to the Target ROI volume spatially
    relate to the voxels corresponding to the points copied from the Source ROI
    volume.
    
    There are four possible cases that will need to be accommodated*:
        
        2. The Source and Target images have the same FOR, IOP, IPP, PS and ST 
        
        3. The Source and Target images have the same FOR and IOP but have
           different PS and/or ST (if different ST they will likely have 
           different IPP)
        
        4. The Source and Target images have the same FOR but have different
           IOP and IPP, and possibly different PS and/or ST
           
        5. The Source and Target images have different FOR (hence different IPP
           and IOP), and possibly different ST and/or PS
        
    FOR = FrameOfReferenceUID, IPP = ImagePositionPatient, 
    IOP = ImageOrientationPatient, ST = SliceThickness, PS = PixelSpacing
    
    * The numbering deliberately starts at 2 for consistency with the 5 overall
    cases.  The first case is covered by another function.
    
    
    Inputs:
        SrcDcmDir    - (String) Directory containing the Source DICOMs
                            
        SrcRoiFpath  - (String) Full path of the Source DICOM RTSTRUCT/SEG file
                             
        FromSliceNum - (Integer) Slice index of the Source DICOM stack 
                       corresponding to the contour/segment to be copied 
                       (counting from 0)
                       
        TrgDcmDir    - (String) Directory containing the Target DICOMs
                            
        TrgRoiFpath  - (String) Full path of the Target DICOM RTSTRUCT/SEG file 
                            
        LogToConsole - (Boolean) Denotes whether or not some intermediate
                       results will be logged to the console
                            
    Returns:
        NewTrgRoi  - Modified Target ROI object 
    
    """
    
    # Import the Source and Target RTSTRUCT/SEG ROI:
    SrcRoi = pydicom.dcmread(SrcRoiFpath)
    TrgRoi = pydicom.dcmread(TrgRoiFpath)
    
    # Get the modality of the ROI:
    SrcModality = SrcRoi.Modality
    TrgModality = TrgRoi.Modality
    
    # Both modalities should be the same.  Return if not:
    if SrcModality == TrgModality:
        Modality = SrcModality
        
    else:
        print(f'\nThe Source ({SrcModality}) and Target ({TrgModality})',
              'modalities are different.')
        
        return
    
    # Import the Source and Target DICOMs:
    SrcDicoms = ImportDicoms(DicomDir=SrcDcmDir, SortMethod='slices', Debug=False)
    TrgDicoms = ImportDicoms(DicomDir=TrgDcmDir, SortMethod='slices', Debug=False)
    
    # Get the Source and Target DICOM SOP UIDs:
    SrcSOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    TrgSOPuids = GetDicomSOPuids(DicomDir=TrgDcmDir)
    
    # Get the ContourImageSequence-to-DICOM slice indices and
    # ContourSequence-to-DICOM slice indices, or the 
    # ReferencedImageSequence-to-DICOM slice indices and 
    # PerFrameFunctionalGroupsSequence-to-DICOM slice indices for Source and 
    # Target:
    if Modality == 'RTSTRUCT':
        SrcCIStoDcmInds = GetCIStoDcmInds(SrcRoi, SrcSOPuids)
    
        SrcCStoDcmInds = GetCStoDcmInds(SrcRoi, SrcSOPuids)
        
        TrgCIStoDcmInds = GetCIStoDcmInds(TrgRoi, TrgSOPuids)
        
        TrgCStoDcmInds = GetCStoDcmInds(TrgRoi, TrgSOPuids)
        
        # Both indices should be the same.  Return if not:
        if not VerifyCISandCS(SrcCIStoDcmInds, SrcCStoDcmInds, LogToConsole):
            return
        
        if not VerifyCISandCS(TrgCIStoDcmInds, TrgCStoDcmInds, LogToConsole):
            return
        
        # Verify that a contour exists for FromSliceNum (this check won't be 
        # necessary in the OHIF-Viewer but a bad input could occur here):
        if not FromSliceNum in SrcCIStoDcmInds:
            print(f'\nA contour does not exist on slice {FromSliceNum} in the',
                  'Source DICOM series.')
            
            return
        
    if Modality == 'SEG':
        SrcRIStoDcmInds = GetRIStoDcmInds(SrcRoi, SrcSOPuids)
    
        SrcPFFGStoDcmInds = GetPFFGStoDcmInds(SrcRoi, SrcSOPuids)
        
        TrgRIStoDcmInds = GetRIStoDcmInds(TrgRoi, TrgSOPuids)
        
        TrgPFFGStoDcmInds = GetPFFGStoDcmInds(TrgRoi, TrgSOPuids)
        
        # Verify that a segment exists for FromSliceNum (this check won't be 
        # necessary in the OHIF-Viewer but a bad input could occur here):
        if not FromSliceNum in SrcPFFGStoDcmInds:
            print(f'\nA segment does not exist on slice {FromSliceNum} in the',
                  'Source DICOM series.')
            
            return
    
    
    
    
    # Get the Source and Target FrameOfReferenceUID:
    SrcFOR = SrcDicoms[0].FrameOfReferenceUID
    TrgFOR = TrgDicoms[0].FrameOfReferenceUID
    
    # Get the image attributes:
    SrcIPPs, SrcDirs, SrcSpacings, SrcDims = GetImageAttributes(ScrDicomDir)
    TrgIPPs, TrgDirs, TrgSpacings, TrgDims = GetImageAttributes(TrgDicomDir)
    
    
    # Check which case follows:
    if SrcFOR == TrgFOR:
        if SrcDirs == TrgDirs:
            if SrcSpacings == TrgSpacings:
                Case = 2
                
            else:
                Case = 3
            
        else:
            Case = 4
    
    else:
        Case = 5
    
    
    
    
    
    
    
    # Check if ToSliceNum already has a contour:
    """
    Note:
        If slice number ToSliceNum already has a contour, it will be 
        over-written with the contour data of slice number FromSliceNum.
        If it doesn't have a contour, ContourImageSequence and 
        ContourSequence need to be extended by one.
    """
    if ToSliceNum in TrgCIStoDcmInds:
        # Use TrgRtsRoi as a template for NewTrgRtsRoi: 
        NewTrgRtsRoi = copy.deepcopy(TrgRtsRoi)
        
        # Create a new list of NewTrgCIStoDcmInds:
        NewTrgCIStoDcmInds = copy.deepcopy(TrgCIStoDcmInds)
        
    else:
        # Increase the length of the sequences:
        NewTrgRtsRoi = AddToRtsSequences(TrgRtsRoi)
        
        # Create a new list of TrgCIStoDcmInds by adding the index ToSliceNum 
        # (representing the contour to be added to ContourImageSequence and to
        # ContourSequence) to TrgCIStoDcmInds:
        NewTrgCIStoDcmInds = AddIndToIndsAndSort(TrgCIStoDcmInds, ToSliceNum)
        
    
    if LogToConsole:
        print('\nSrcCIStoDcmInds    =', SrcCIStoDcmInds)
        print('\nTrgCIStoDcmInds    =', TrgCIStoDcmInds)
        print('\nNewTrgCIStoDcmInds =', NewTrgCIStoDcmInds)
    
    # Modify select tags in TrgRtsRoi:
    NewTrgRtsRoi = ModifyRtsTagVals(TrgRtsRoi, NewTrgRtsRoi, FromSliceNum, 
                                    ToSliceNum, TrgDicoms, 
                                    TrgCIStoDcmInds, NewTrgCIStoDcmInds,
                                    LogToConsole)
    
    
    
    # Generate a new SOP Instance UID:
    NewTrgRtsRoi.SOPInstanceUID = pydicom.uid.generate_uid()
    
    # Generate a new Series Instance UID:
    NewTrgRtsRoi.SeriesInstanceUID = pydicom.uid.generate_uid()
    
    
    return NewTrgRtsRoi






def ExportRtsRoi(TrgRtsRoi, SrcRtsFpath, NamePrefix, ExportDir):
    """
    Export contour ROI Object to disc.
    
    
    Inputs:
        TrgRtsRoi   - Target RT-STRUCT ROI object to be exported
        
        SrcRtsFpath - (String) Full path of the Source DICOM-RTSTRUCT file
                      (used to generate the filename of the new RTS file)
        
        NamePrefix  - (String) Prefix to be added to the assigned filename and
                      ROI Name (e.g. 'MR4_S9_s23_to_MR4_S9_s22') 
                            
        ExportDir   - (String) Directory where the RTSTRUCT is to be exported
                           
    
                            
    Returns:
        TrgRtsFpath - (String) Full path of the exported Target DICOM-RTSTRUCT 
                      file
    
    """
    
    """
    The following was moved into the main function CopyContourWithinSeries:
    # Generate a new SOP Instance UID:
    RtsRoi.SOPInstanceUID = pydicom.uid.generate_uid()
    
    # Generate a new Series Instance UID:
    RtsRoi.SeriesInstanceUID = pydicom.uid.generate_uid()
    """
    
    # Get the filename of the original RT-Struct file:
    SrcRtsFname = os.path.split(SrcRtsFpath)[1]
    
    # Modify the Structure Set Date and Time to the present:
    NewDate = time.strftime("%Y%m%d", time.gmtime())
    NewTime = time.strftime("%H%M%S", time.gmtime())
    
    TrgRtsRoi.StructureSetDate = NewDate
    TrgRtsRoi.StructureSetTime = NewTime
    
    FnamePrefix = NewDate + '_' + NewTime + '_' + NamePrefix + '_from_' 
    RoiNamePrefix = NamePrefix + '_from_'
    
    # Modify the Structure Set Label (this appears under Name in XNAT):
    #TrgRtsRoi.StructureSetLabel = 'Copy_of_' + TrgRtsRoi.StructureSetLabel
    TrgRtsRoi.StructureSetLabel = RoiNamePrefix + TrgRtsRoi.StructureSetLabel
    
    # Modify the ROI Name for the Structure Set ROI Sequence:             
    TrgRtsRoi.StructureSetROISequence[0].ROIName = RoiNamePrefix \
                                                  + TrgRtsRoi.StructureSetLabel
    
    # Create a new filename (this will appear under Label in XNAT):
    #TrgRoiFname = 'New_' + SrcRtsFname + '_' + NewDate + '_' + NewTime
    TrgRtsFname = FnamePrefix + SrcRtsFname
    
    TrgRtsFpath = os.path.join(ExportDir, TrgRtsFname)
    
    TrgRtsRoi.save_as(TrgRtsFpath)
        
    print('\nRTS ROI exported to:\n\n', TrgRtsFpath)
    
    return TrgRtsFpath
    
    
    





    

"""
******************************************************************************
******************************************************************************
SEGMENTATION-RELATED FUNCTIONS
******************************************************************************
******************************************************************************
"""


def GetRIStoDcmInds(SegRoi, SOPuids):
    """
    Get the DICOM slice numbers that correspond to each Referenced Instance
    Sequence in a SEG ROI.
    
    Inputs:
        SegRoi       - ROI Object from a SEG file
        
        SOPuids      - List of strings of the SOP UIDs of the DICOMs
        
    Returns:
        RIStoDcmInds - List of integers of the DICOM slice numbers that
                       correspond to each Referenced Instance Sequence in 
                       SegRoi
    """
    
    RIStoDcmInds = [] 
    
    # Loop through each Referenced Instance Sequence:
    sequences = SegRoi.ReferencedSeriesSequence[0]\
                      .ReferencedInstanceSequence
    
    for sequence in sequences:
        # Get the Reference SOP Instance UID:
        uid = sequence.ReferencedSOPInstanceUID
        
        # Find the matching index of this UID in SOPuids:
        RIStoDcmInds.append(SOPuids.index(uid))
        
    return RIStoDcmInds




def GetPFFGStoDcmInds(SegRoi, SOPuids):
    """
    Get the DICOM slice numbers that correspond to each Per-frame Functional
    Groups Sequence in a SEG ROI.
    
    Inputs:
        SegRoi         - ROI Object from a SEG file
        
        SOPuids        - List of strings of the SOP UIDs of the DICOMs
        
    Returns:
        PFFGStoDcmInds - List of integers of the DICOM slice numbers that
                         correspond to each Per-frame Functional Groups 
                         Sequence in SegRoi
    """
    
    PFFGStoDcmInds = [] 
    
    # Loop through each Referenced Instance Sequence:
    sequences = SegRoi.PerFrameFunctionalGroupsSequence
    
    for sequence in sequences:
        # Get the Reference SOP Instance UID:
        uid = sequence.DerivationImageSequence[0]\
                      .SourceImageSequence[0]\
                      .ReferencedSOPInstanceUID
        
        # Find the matching index of this UID in SOPuids:
        PFFGStoDcmInds.append(SOPuids.index(uid))
        
    return PFFGStoDcmInds





def AddToSegSequences(SegRoi):
    """
    Append the last item in the following sequences in the SEG Object: 
        Referenced Instance Sequence 
        Per-frame Functional Groups Sequence
    
    Inputs:
        SegRoi    - ROI Object from a SEG file
        
    Returns:
        NewSegRoi - Modified ROI Object with sequences lengthened by one
    """
    
    # Use SegRoi as a template for NewSegRoi: 
    NewSegRoi = copy.deepcopy(SegRoi)
        
    # The last item in Referenced Instance Sequence:
    last = copy.deepcopy(SegRoi.ReferencedSeriesSequence[0]\
                               .ReferencedInstanceSequence[-1])
    
    # Append to the Referenced Instance Sequence:
    NewSegRoi.ReferencedSeriesSequence[0]\
             .ReferencedInstanceSequence\
             .append(last)
             
    # The last item in Per-frame Functional Groups Sequence:
    last = copy.deepcopy(SegRoi.PerFrameFunctionalGroupsSequence[-1])
    
    # Append to the Per-frame Functional Groups Sequence:
    NewSegRoi.PerFrameFunctionalGroupsSequence\
             .append(last)
             
    return NewSegRoi





def ModifySegTagVals_OLD(SegRoi, NewSegRoi, FromSliceNum, ToSliceNum, Dicoms,
                     OrigPFFGStoDcmInds, NewPFFGStoDcmInds, LogToConsole):
    """
    Modify various tag values of the new SEG ROI so that they are consistent
    with the corresponding tag values of the DICOMs.
         
    
    Inputs:
        SegRoi             - Original ROI Object from a SEG file
        
        NewSegRoi          - New SEG ROI Object
        
        FromSliceNum       - (Integer) Slice index in the Source DICOM stack
                             corresponding to the segmentation to be copied 
                             (counting from 0)
                          
        ToSliceNum         - (Integer) Slice index in the Target DICOM stack 
                             where the segmentation will be copied to (counting 
                             from 0)
                          
        Dicoms             - A list of DICOM Objects that include the DICOMs 
                             that SegRoi relate to
                            
        OrigPFFGStoDcmInds - List of integers of the DICOM slice numbers that 
                             correspond to each Per-frame Functional Groups  
                             Sequence in SegRoi
                          
        NewPFFGStoDcmInds  - List of integers of the DICOM slice numbers that 
                             correspond to each Per-frame Functional Groups 
                             Sequence in NewSegRoi
                             
        LogToConsole       - (Boolean) Denotes whether or not some intermediate
                             results will be logged to the console
        

        *** I don't need the following but kept here for now:    
              
        OrigRIStoDcmInds   - List of integers of the DICOM slice numbers that 
                             correspond to each Referenced Instance Sequence in 
                             SegRoi
                            
        NewRIStoDcmInds    - List of integers of the DICOM slice numbers that 
                             correspond to each Referenced Instance Sequence in 
                             NewSegRoi
        ***
        
    Returns:
        NewSegRoi         - Modified new SEG ROI Object
    """
    
    # Get the sequence number that corresponds to the slice number to be 
    # copied, and the slice number to be copied to:
    FromOrigSeqNum = OrigPFFGStoDcmInds.index(FromSliceNum)
        
    ToNewSeqNum = NewPFFGStoDcmInds.index(ToSliceNum)
    
    if LogToConsole:
        print(f'\nFromOrigSeqNum = {FromOrigSeqNum} -->',
              f'OrigPFFGStoDcmInds[{FromOrigSeqNum}] =',
              f'{OrigPFFGStoDcmInds[FromOrigSeqNum]}')
        
        print(f'ToNewSeqNum    = {ToNewSeqNum} -->',
              f'NewPFFGStoDcmInds[{ToNewSeqNum}] =',
              f'{NewPFFGStoDcmInds[ToNewSeqNum]}')
    
    
    # Modify the Number of Frames in NewSegRoi:
    #NewSegRoi.NumberOfFrames = str(int(SegRoi.NumberOfFrames) + 1)
    
    # The 2D array to be copied is:
    #MaskToCopy = SegRoi.pixel_array[FromSliceNum]
    
    # The original 3D mask is:
    #Orig3dMask = NewSegRoi.pixel_array
    Orig3dMask = SegRoi.pixel_array
    
    # Let the new 3D mask be the original 3D mask with the last 2D mask 
    # appended to it:
    #New3dMask = np.append(Orig3dMask, Orig3dMask[-1], axis=0)
    
    # The shape of Orig3dMask:
    OrigShape = Orig3dMask.shape
    
    print('\nThe shape of the original 3D mask is', OrigShape)
    
    """
    # Re-shape New3DMask from (NumOfFrames, Rows, Columns) to 
    # (Rows, Columns, NumOfFrames):
    New3dMask = np.reshape(Orig3dMask, (OrigShape[1], OrigShape[2], OrigShape[0]))
    
    # Stack the last 2D array to the 3D array:
    New3dMask = np.dstack((New3dMask, New3dMask[:,:,-1]))
    
    # The shape of New3dMask:
    NewShape = New3dMask.shape
    
    # Reshape New3dMask to the original form:
    New3dMask = np.reshape(New3dMask, (NewShape[2], NewShape[0], NewShape[1]))
    """
    
    OrigNframes = OrigShape[0]
    OrigNrows = OrigShape[1]
    OrigNcols = OrigShape[2]
    
    NewNframes = OrigNframes + 1
    
    # Modify the Number of Frames in NewSegRoi:
    NewSegRoi.NumberOfFrames = str(NewNframes)
    
    # Create an empty 3D array with required shape:
    #New3dMask = np.zeros((NewNframes, OrigNrows, OrigNcols), dtype=int)
    New3dMask = np.zeros((NewNframes, OrigNrows, OrigNcols), dtype=bool)
    
    
    # The shape of New3dMask:
    #NewShape = New3dMask.shape
    #
    #print('\nThe shape of the new 3D mask is', NewShape)
    #
    # Convert New3dMask to bytes:
    #NewSegRoi.PixelArray = ConvertNumpyArrayToPixelArray(New3dMask) 
    #""" Note: The function ConvertNumpyArrayToPixelArray doesn't yet exist! """
    #
    #NewSegRoi.PixelData = New3dMask.tobytes()
    
    
    # Loop through each frame/sequence in NewSegRoi, modifying the relevant tag 
    # values and New3dMask:
    for i in range(NewNframes):
        # The DICOM slice index for the i^th sequence:
        s = NewPFFGStoDcmInds[i]
        
        if LogToConsole:
            print(f'\nNewPFFGStoDcmInds[{i}] = {NewPFFGStoDcmInds[i]}')
            print(f'DICOM slice number = {s}')
        
        # Modify the Referenced SOP Class UID and Referenced SOP Instance UID 
        # so that they are consistent with the SOP Class UID and SOP Instance  
        # UID of their corresponding DICOMs:
        """ SOPClassUIDs will need to be modified for cases where the contour
        is being copied across different modality images. Not required for
        copying within the same series:
        NewSegRoi.ReferencedSeriesSequence[0]\
                 .ReferencedInstanceSequence[i]\
                 .ReferencedSOPClassUID = Dicoms[s].SOPClassUID
        """
        
        NewSegRoi.ReferencedSeriesSequence[0]\
                 .ReferencedInstanceSequence[i]\
                 .ReferencedSOPInstanceUID = Dicoms[s].SOPInstanceUID
        
        """ Ditto:
        NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
                 .DerivationImageSequence[0]\
                 .SourceImageSequence[0]\
                 .ReferencedSOPClassUID = Dicoms[s].SOPClassUID
        """
        
        NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
                 .DerivationImageSequence[0]\
                 .SourceImageSequence[0]\
                 .ReferencedSOPInstanceUID = Dicoms[s].SOPInstanceUID
                 
        
        # Modify the tags in FrameContentSequence:
        #NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
        #         .FrameContentSequence[0]\
        #         .StackID = f'{i + 1}'
                 
        NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
                 .FrameContentSequence[0]\
                 .InStackPositionNumber = i + 1
                 
        
        NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
                 .FrameContentSequence[0]\
                 .DimensionIndexValues = [1, 1, i + 1]
                     
        # Modify the ImagePositionPatient:  
        NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
                 .PlanePositionSequence[0]\
                 .ImagePositionPatient = copy.deepcopy(Dicoms[s].ImagePositionPatient)
        
        
        # Modify New3dMask:         
        if i == ToNewSeqNum:
            if LogToConsole:
                print('\nThis is a new sequence.')
                print(f'Copying the {FromOrigSeqNum}th sequence from Source',
                      f'to the {i}th sequence in Target.')
                
            # This is the new sequence. Set the i^th 2D mask in New3DMask 
            # equal to the FromSeqNum^th 2D mask in Orig3dMask:
            New3dMask[i] = Orig3dMask[FromOrigSeqNum]
            #New3dMask[i,:,:] = Orig3dMask[FromOrigSeqNum,:,:]
        
        else:
            # This is an existing sequence. Find the index of 
            # OrigPFFGStoDcmInds for this sequence number (of 
            # NewPFFGStoDcmInds):
            ind = OrigPFFGStoDcmInds.index(NewPFFGStoDcmInds[i])
            
            if LogToConsole:
                print('\nThis is an existing sequence.')
                print(f'Copying the {ind}th sequence from Source to the {i}th',
                      f'sequence in Target.')
                                          
            # Set the i^th 2D mask in New3DMask equal to the ind^th 2D mask in 
            # Orig3dMask:
            New3dMask[i] = Orig3dMask[ind]
            #New3dMask[i,:,:] = Orig3dMask[ind,:,:]
        
    
    # The shape of New3dMask:
    NewShape = New3dMask.shape
    
    print('\nThe shape of the new 3D mask is', NewShape)
    
    # Ravel (to 1D array) New3dMask and pack bits 
    # (see https://github.com/pydicom/pydicom/issues/1230):
    packed = pack_bits(New3dMask.ravel())
    
    # Convert New3dMask to bytes:
    #NewSegRoi.PixelData = New3dMask.tobytes() <-- doesn't work
    NewSegRoi.PixelData = packed + b'\x00' if len(packed) % 2 else packed
                                          
    return NewSegRoi





def ModifySegTagVals(SrcSeg, SrcDicoms, FromSliceNum, 
                     TrgSeg, NewTrgSeg, TrgDicoms, ToSliceNum, 
                     SrcPFFGStoDcmInds, TrgPFFGStoDcmInds, NewTrgPFFGStoDcmInds, 
                     LogToConsole=False):
    """
    Modify various tag values of the new SEG ROI so that they are consistent
    with the corresponding tag values of the DICOMs.
         
    
    Inputs:
        SrcSegRoi
        
        TrgSegRoi             - Original ROI Object from a SEG file
        
        NewTrgSegRoi          - New SEG ROI Object
        
        FromSliceNum       - (Integer) Slice index in the Source DICOM stack
                             corresponding to the segmentation to be copied 
                             (counting from 0)
                          
        ToSliceNum         - (Integer) Slice index in the Target DICOM stack 
                             where the segmentation will be copied to (counting 
                             from 0)
                          
        SrcDicoms             - A list of DICOM Objects that include the DICOMs 
                             that SegRoi relate to
                             
        TrgDicoms
                    
           
        SrcPFFGStoDcmInds
        
        TrgPFFGStoDcmInds - List of integers of the DICOM slice numbers that 
                             correspond to each Per-frame Functional Groups  
                             Sequence in SegRoi
                          
        NewTrgPFFGStoDcmInds  - List of integers of the DICOM slice numbers that 
                             correspond to each Per-frame Functional Groups 
                             Sequence in NewSegRoi
                             
        LogToConsole       - (Boolean) Denotes whether or not some intermediate
                             results will be logged to the console
        

        *** I don't need the following but kept here for now:    
              
        OrigRIStoDcmInds   - List of integers of the DICOM slice numbers that 
                             correspond to each Referenced Instance Sequence in 
                             SegRoi
                            
        NewRIStoDcmInds    - List of integers of the DICOM slice numbers that 
                             correspond to each Referenced Instance Sequence in 
                             NewSegRoi
        ***
        
    Returns:
        NewTrgSegRoi         - Modified new SEG ROI Object
    """
    
    # Get the sequence number that corresponds to the slice number to be 
    # copied, and the slice number to be copied to:
    FromSrcSeqNum = SrcPFFGStoDcmInds.index(FromSliceNum)
        
    ToNewTrgSeqNum = NewTrgPFFGStoDcmInds.index(ToSliceNum)
    
    if LogToConsole:
        print(f'\nFromSrcSeqNum     = {FromSrcSeqNum} -->',
              f'ScrPFFGStoDcmInds[{FromSrcSeqNum}] =',
              f'{SrcPFFGStoDcmInds[FromSrcSeqNum]}')
        
        print(f'ToNewTrgSeqNum    = {ToNewTrgSeqNum} -->',
              f'NewTrgPFFGStoDcmInds[{ToNewTrgSeqNum}] =',
              f'{NewTrgPFFGStoDcmInds[ToNewTrgSeqNum]}')
    
    
    # Modify the Number of Frames in NewSegRoi:
    #NewSegRoi.NumberOfFrames = str(int(SegRoi.NumberOfFrames) + 1)
    
    # The 2D array to be copied is:
    #MaskToCopy = SegRoi.pixel_array[FromSliceNum]
    
    # The original 3D mask is:
    Src3dMask = SrcSeg.pixel_array
    Trg3dMask = TrgSeg.pixel_array
    
    # Let the new 3D mask be the original 3D mask with the last 2D mask 
    # appended to it:
    #New3dMask = np.append(Orig3dMask, Orig3dMask[-1], axis=0)
    
    # The shape of Trg3dMask:
    OrigShape = Trg3dMask.shape
    
    print('\nThe shape of the original Target 3D mask is', OrigShape)
    
    OrigNframes = OrigShape[0]
    OrigNrows = OrigShape[1]
    OrigNcols = OrigShape[2]
    
    NewNframes = OrigNframes + 1
    
    # Modify the Number of Frames in NewTrgSeg:
    NewTrgSeg.NumberOfFrames = str(NewNframes)
    
    # Create an empty 3D array with required shape:
    #New3dMask = np.zeros((NewNframes, OrigNrows, OrigNcols), dtype=int)
    NewTrg3dMask = np.zeros((NewNframes, OrigNrows, OrigNcols), dtype=bool)
    
    
    # Loop through each frame/sequence in NewTrgSeg, modifying the relevant tag 
    # values and NewTrg3dMask:
    for i in range(NewNframes):
        # The DICOM slice index for the i^th sequence:
        s = NewTrgPFFGStoDcmInds[i]
        
        if LogToConsole:
            print(f'\nNewTrgPFFGStoDcmInds[{i}] = {NewTrgPFFGStoDcmInds[i]}')
            print(f'DICOM slice number = {s}')
        
        # Modify the Referenced SOP Class UID and Referenced SOP Instance UID 
        # so that they are consistent with the SOP Class UID and SOP Instance  
        # UID of their corresponding DICOMs:
        """ SOPClassUIDs will need to be modified for cases where the contour
        is being copied across different modality images. Not required for
        copying within the same series:
        NewSegRoi.ReferencedSeriesSequence[0]\
                 .ReferencedInstanceSequence[i]\
                 .ReferencedSOPClassUID = Dicoms[s].SOPClassUID
        """
        
        NewTrgSeg.ReferencedSeriesSequence[0]\
                 .ReferencedInstanceSequence[i]\
                 .ReferencedSOPInstanceUID = TrgDicoms[s].SOPInstanceUID
        
        """ Ditto:
        NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
                 .DerivationImageSequence[0]\
                 .SourceImageSequence[0]\
                 .ReferencedSOPClassUID = Dicoms[s].SOPClassUID
        """
        
        NewTrgSeg.PerFrameFunctionalGroupsSequence[i]\
                 .DerivationImageSequence[0]\
                 .SourceImageSequence[0]\
                 .ReferencedSOPInstanceUID = TrgDicoms[s].SOPInstanceUID
                 
        
        # Modify the tags in FrameContentSequence:
        #NewSegRoi.PerFrameFunctionalGroupsSequence[i]\
        #         .FrameContentSequence[0]\
        #         .StackID = f'{i + 1}'
                 
        NewTrgSeg.PerFrameFunctionalGroupsSequence[i]\
                 .FrameContentSequence[0]\
                 .InStackPositionNumber = i + 1
                 
        
        NewTrgSeg.PerFrameFunctionalGroupsSequence[i]\
                 .FrameContentSequence[0]\
                 .DimensionIndexValues = [1, 1, i + 1]
                     
        # Modify the ImagePositionPatient:  
        NewTrgSeg.PerFrameFunctionalGroupsSequence[i]\
                 .PlanePositionSequence[0]\
                 .ImagePositionPatient = copy.deepcopy(TrgDicoms[s].ImagePositionPatient)
        
        
        # Modify NewTrg3dMask:         
        if i == ToNewTrgSeqNum:
            if LogToConsole:
                print('\nThis is a new sequence.')
                print(f'Copying the {FromSrcSeqNum}th sequence from Source',
                      f'to the {i}th sequence in Target.')
                
            # This is the new sequence. Set the i^th 2D mask in NewTrg3DMask 
            # equal to the FromSrcSeqNum^th 2D mask in Src3dMask:
            NewTrg3dMask[i] = Src3dMask[FromSrcSeqNum]
            #New3dMask[i,:,:] = Orig3dMask[FromOrigSeqNum,:,:]
        
        else:
            # This is an existing sequence. Find the index of 
            # TrgPFFGStoDcmInds for this sequence number (of 
            # NewTrgPFFGStoDcmInds):
            ind = TrgPFFGStoDcmInds.index(NewTrgPFFGStoDcmInds[i])
            
            if LogToConsole:
                print('\nThis is an existing sequence.')
                print(f'Copying the {ind}th sequence from Target to the {i}th',
                      f'sequence in Target.')
                                          
            # Set the i^th 2D mask in NewTrg3DMask equal to the ind^th 2D mask
            # in Trg3dMask:
            NewTrg3dMask[i] = Trg3dMask[ind]
            #New3dMask[i,:,:] = Orig3dMask[ind,:,:]
        
    
    # The shape of NewTrg3dMask:
    NewShape = NewTrg3dMask.shape
    
    print('\nThe shape of the new 3D mask is', NewShape)
    
    # Ravel (to 1D array) NewTrg3dMask and pack bits 
    # (see https://github.com/pydicom/pydicom/issues/1230):
    packed = pack_bits(NewTrg3dMask.ravel())
    
    # Convert NewTrg3dMask to bytes:
    #NewSegRoi.PixelData = New3dMask.tobytes() <-- doesn't work
    NewTrgSeg.PixelData = packed + b'\x00' if len(packed) % 2 else packed
                                          
    return NewTrgSeg






def CopySegmentWithinSeries(SrcDcmDir, SrcSegFpath, FromSliceNum, ToSliceNum, 
                            LogToConsole=False):
    """
    Copy a single segment on a given slice to another slice within the same
    DICOM series.
    
    
    Inputs:
        SrcDcmDir    - (String) Directory containing the Source DICOMs
                            
        SrcSegFpath  - (String) Full path of the Source DICOM SEG file 
                             
        FromSliceNum - (Integer) Slice index of the Source DICOM stack 
                       corresponding to the segment to be copied (counting from 
                       0)
                             
        ToSliceNum   - (Integer) Slice index in the Target DICOM stack where
                       the segment will be copied to (counting from 0)
                            
        LogToConsole - (Boolean) Denotes whether or not some intermediate
                       results will be logged to the console
                            
    Returns:
        NewSrcSegRoi - Modified Source SEG ROI object
    
    """
    
    # Import the Source SEG ROI:
    SegRoi = pydicom.dcmread(SrcSegFpath)
    
    # Import the Source DICOMs:
    Dicoms = ImportDicoms(DicomDir=SrcDcmDir)
    
    # Get the DICOM SOP UIDs:
    SOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    
    # Get the ReferencedImageSequence-to-DICOM slice indices, and the
    # Per-frameFunctionalGroupsSequence-to-DICOM slice indices:
    RIStoDcmInds = GetRIStoDcmInds(SegRoi, SOPuids)
    
    PFFGStoDcmInds = GetPFFGStoDcmInds(SegRoi, SOPuids)
    
    
    # Verify that a segment exists for FromSliceNum (this check won't be 
    # necessary in the OHIF-Viewer but a bad input could occur here):
    if not FromSliceNum in PFFGStoDcmInds:
        print(f'\nA segment does not exist on slice {FromSliceNum}.')
        
        return
    
    
    # Check if ToSliceNum already has a segment:
    """
    Note:
        If slice number ToSliceNum already has a segment, it will be 
        over-written with the segment data of slice number FromSliceNum.
        If it doesn't have a segment, ReferencedImageSequence and 
        PerFrameFunctionalGroupsSequence need to be extended by one.
    """
    if ToSliceNum in RIStoDcmInds:
        # Use SegRoi as a template for NewSegRoi: 
        NewSegRoi = copy.deepcopy(SegRoi)
        
        # Create a new list of RIStoDcmInds: <-- not needed?
        #NewRIStoDcmInds = copy.deepcopy(RIStoDcmInds)
        
        # Create a new list of PFFGStoDcmInds:
        NewPFFGStoDcmInds = copy.deepcopy(PFFGStoDcmInds)
        
    else:
        # Increase the length of the sequences:
        NewSegRoi = AddToSegSequences(SegRoi)
        
        # Create a new list of RIStoDcmInds by adding the index ToSliceNum 
        # (representing the segment to be added to ReferencedImageSequence)
        # to RIStoDcmInds: <-- not needed?
        #NewRIStoDcmInds = AddIndToIndsAndSort(RIStoDcmInds, ToSliceNum)
        
        # Create a new list of PFFGStoDcmInds by adding the index ToSliceNum 
        # (representing the segment to be added to 
        # PerFrameFunctionalGroupsSequence) to PFFGStoDcmInds:
        NewPFFGStoDcmInds = AddIndToIndsAndSort(PFFGStoDcmInds, ToSliceNum)
    
    
    if LogToConsole:
        print('\nPFFGStoDcmInds    =', PFFGStoDcmInds)
        print('\nNewPFFGStoDcmInds =', NewPFFGStoDcmInds)
        
    # Modify select tags in NewSegRoi:
    NewSegRoi = ModifySegTagVals(SegRoi, NewSegRoi, FromSliceNum, ToSliceNum,
                                 Dicoms, PFFGStoDcmInds, NewPFFGStoDcmInds,
                                 LogToConsole)
    
    
    
    # Generate a new SOP Instance UID:
    NewSegRoi.SOPInstanceUID = pydicom.uid.generate_uid()
    
    # Generate a new Series Instance UID:
    NewSegRoi.SeriesInstanceUID = pydicom.uid.generate_uid()
    
    
    return NewSegRoi





def DirectCopySegmentAcrossSeries(SrcDcmDir, SrcSegFpath, FromSliceNum, 
                                  TrgDcmDir, TrgSegFpath, ToSliceNum, 
                                  LogToConsole=False):
    """
    Copy a single segment on a given slice to another slice in a different 
    DICOM series.
    
    
    Inputs:
        SrcDcmDir    - (String) Directory containing the Source DICOMs
                            
        SrcSegFpath  - (String) Full path of the Source DICOM SEG file 
                             
        FromSliceNum - (Integer) Slice index of the Source DICOM stack 
                       corresponding to the segment to be copied (counting from 
                       0)
                       
        TrgDcmDir    - (String) Directory containing the Target DICOMs
                            
        TrgSegFpath  - (String) Full path of the Target DICOM SEG file 
                             
        ToSliceNum   - (Integer) Slice index of the Target DICOM stack where
                       the segment will be copied to (counting from 0)
                            
        LogToConsole - (Boolean) Denotes whether or not some intermediate
                       results will be logged to the console
                            
    Returns:
        NewTrgSegRoi  - Modified Target ROI object 
    
    """
    
    # Import the Source and Target SEG ROI:
    SrcSegRoi = pydicom.dcmread(SrcSegFpath)
    TrgSegRoi = pydicom.dcmread(TrgSegFpath)
    
    # Import the Target DICOMs:
    TrgDicoms = ImportDicoms(DicomDir=TrgDcmDir)
    
    # Get the Source and Target DICOM SOP UIDs:
    SrcSOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    TrgSOPuids = GetDicomSOPuids(DicomDir=TrgDcmDir)
    
    # Get the ReferencedImageSequence-to-DICOM slice indices, and the
    # Per-frameFunctionalGroupsSequence-to-DICOM slice indices for Source and 
    # Target:
    SrcRIStoDcmInds = GetRIStoDcmInds(SrcSegRoi, SrcSOPuids)
    
    SrcPFFGStoDcmInds = GetPFFGStoDcmInds(SrcSegRoi, SrcSOPuids)
    
    TrgRIStoDcmInds = GetRIStoDcmInds(TrgSegRoi, TrgSOPuids)
    
    TrgPFFGStoDcmInds = GetPFFGStoDcmInds(TrgSegRoi, TrgSOPuids)
        
    
    # Verify that a segment exists for FromSliceNum (this check won't be 
    # necessary in the OHIF-Viewer but a bad input could occur here):
    if not FromSliceNum in SrcPFFGStoDcmInds:
        print(f'\nA segment does not exist on slice {FromSliceNum} in the',
              'Source DICOM series.')
        
        return
    
    # Verify that the slice that a contour is to be copied to exists (this 
    # check won't be necessary in the OHIF-Viewer but a bad input could occur
    # here):
    if not ToSliceNum in list(range(len(TrgDicoms))):
        print(f'\nThe Target DICOM series does not have slice {ToSliceNum}.')
        
        return
    
    
    # Check if ToSliceNum already has a segment:
    """
    Note:
        If slice number ToSliceNum already has a segment, it will be 
        over-written with the segment data of slice number FromSliceNum.
        If it doesn't have a segment, ReferencedImageSequence and 
        PerFrameFunctionalGroupsSequence need to be extended by one.
    """
    if ToSliceNum in TrgRIStoDcmInds:
        # Use TrgSegRoi as a template for NewTrgSegRoi:
        NewTrgSegRoi = copy.deepcopy(TrgSegRoi)
        
        # Create a new list of TrgRIStoDcmInds: <-- not needed?
        #NewTrgRIStoDcmInds = copy.deepcopy(TrgRIStoDcmInds)
        
        # Create a new list of PFFGStoDcmInds:
        NewTrgPFFGStoDcmInds = copy.deepcopy(TrgPFFGStoDcmInds)
        
    else:
        # Increase the length of the sequences:
        NewTrgSegRoi = AddToSegSequences(TrgSegRoi)
        
        # Create a new list of TrgRIStoDcmInds by adding the index ToSliceNum 
        # (representing the contour to be added to ReferencedImageSequence) to 
        # TrgRIStoDcmInds: <-- not needed?
        #NewTrgRIStoDcmInds = AddIndToIndsAndSort(TrgRIStoDcmInds, ToSliceNum)
        
        # Create a new list of TrgPFFGStoDcmInds by adding the index ToSliceNum 
        # (representing the segment to be added to 
        # PerFrameFunctionalGroupsSequence) to TrgPFFGStoDcmInds:
        NewTrgPFFGStoDcmInds = AddIndToIndsAndSort(TrgPFFGStoDcmInds, ToSliceNum)
        
    
    if LogToConsole:
        print('\nTrgPFFGStoDcmInds    =', TrgPFFGStoDcmInds)
        print('\nNewTrgPFFGStoDcmInds =', NewTrgPFFGStoDcmInds)
    
    # Modify select tags in NewTrgSegRoi:
    NewTrgSegRoi = ModifySegTagVals(TrgSegRoi, NewTrgSegRoi, FromSliceNum, 
                                    ToSliceNum, TrgDicoms, 
                                    TrgPFFGStoDcmInds, NewTrgPFFGStoDcmInds,
                                    LogToConsole)
    
    
    
    # Generate a new SOP Instance UID:
    NewTrgSegRoi.SOPInstanceUID = pydicom.uid.generate_uid()
    
    # Generate a new Series Instance UID:
    NewTrgSegRoi.SeriesInstanceUID = pydicom.uid.generate_uid()
    
    
    return NewTrgSegRoi






def PixArr2LabMap(PixelArray, NumOfSlices, FrameToSliceInds):
    """
    Convert a 3D SEG pixel array to a 3D SEG labelmap.  The labelmap will 
    contain the 2D pixel arrays at the same frame position as the slice
    position of the corresponding DICOM series (with 2D zero masks in-between).
    
    Inputs:
        PixelArray       - (Numpy array) The SEG's PixelData loaded as a 
                           Numpy array with dtype uint8
        
        NumOfSlices      - (Integer) The number of slices in the DICOM series
        
        FrameToSliceInds - (List of integers) The DICOM slice numbers that
                           correspond to each frame in PixelArray,
                           e.g. PFFGStoDcmInds 
                           = PerFrameFunctionalGroupsSequence-to-DICOM slice
                           number
        
    Returns:
        LabelMap         - (Numpy array) A zero-padded version of PixelArray
                           with dtype uint

    """
    
    NumOfFrames, NumOfRows, NumOfCols = PixelArray.shape
    
    #print(f'\n\nThe maximum value in PixelArray is {PixelArray.max()}')
    
    # Initialise LabelMap:
    #LabelMap = np.zeros((NumOfSlices, NumOfRows, NumOfCols), dtype='bool')
    LabelMap = np.zeros((NumOfSlices, NumOfRows, NumOfCols), dtype='uint')
    
    # Over-write all frames in LabelMap with non-zero 2D masks from PixelArray:
    for i in range(len(FrameToSliceInds)):
        # The DICOM slice number for the i^th frame:
        s = FrameToSliceInds[i]
        
        LabelMap[s] = PixelArray[i]
        
    
    #print(f'\n\nThe maximum value in LabelMap is {LabelMap.max()}')
    
    return LabelMap





def PixArr2Image(PixelArray, Image, NumOfSlices, FrameToSliceInds):
    """
    Convert a 3D SEG pixel array to a 3D SimpleITK image using an intermediate
    conversion from 3D SEG pixel array to a Numpy array (using PixArr2LabMap).  
    
    Inputs:
        PixelArray       - (Numpy array) The SEG's PixelData loaded as a 
                           Numpy array with dtype uint8
                           
        Image            - (SimpleITK image) The 3D image that PixelArray
                           relates to
        
        NumOfSlices      - (Integer) The number of slices in the DICOM series
        
        FrameToSliceInds - (List of integers) The DICOM slice numbers that
                           correspond to each frame in PixelArray,
                           e.g. PFFGStoDcmInds 
                           = PerFrameFunctionalGroupsSequence-to-DICOM slice
                           number
        
    Returns:
        LabelMapImage    - (SimpleITK image) A zero-padded version of 
                           PixelArray

    """
    
    nda = PixArr2LabMap(PixelArray, NumOfSlices, FrameToSliceInds)
    
    LabelMapImage = sitk.GetImageFromArray(nda)
    
    # Set the Origin, Spacing and Direction of LabelMapImage to that of Image:
    LabelMapImage.SetOrigin(Image.GetOrigin())
    LabelMapImage.SetSpacing(Image.GetSpacing())
    LabelMapImage.SetDirection(Image.GetDirection())
    
    # Use MinimumMaximumImageFilter to get image maximum:
    #ImMaxFilt = sitk.MinimumMaximumImageFilter()
    #ImMaxFilt.Execute(LabelMapImage)
    #maximum = ImMaxFilt.GetMaximum()
    #
    #print(f'\n\nThe maximum value in nda is {nda.max()}')
    #print(f'\n\nThe maximum value in LabelMapImage is {maximum}')
    
        
    return LabelMapImage






def ResampleImage(Image, RefImage, Method, Interpolation):#, RefImageSpacings):
    
    #NewSrcImage = sitk.Resample(image=SrcImage, 
    #                            size=TrgSitkSize,
    #                            transform=sitk.Transform(),
    #                            interpolator=sitk.sitkLinear,
    #                            outputOrigin=TrgSitkOrigin,
    #                            outputSpacing=TrgSitkSpacing,
    #                            outputDirection=TrgSitkDirection,
    #                            defaultPixelValue=0,
    #                            outputPixelType=TrgImage.GetPixelID())
    
    
    # Define which interpolator to use:
    """ 
    Use the linear (or BSpline) interpolator for intensity images, and
    NearestNeighbour for binary images (e.g. segmentation) so that no new
    labels are introduced.
    """
    
    if 'inear' in Interpolation:
        Interpolator = sitk.sitkLinear
    if 'pline' in Interpolation:
        Interpolator = sitk.sitkBSpline
    if ('earest' and 'eighbo' or 'nn' or 'NN') in Interpolation:    
        Interpolator = sitk.sitkNearestNeighbor
            
        
    print('\nUsing', Interpolation, 'interpolation\n')
    
    Dimension = Image.GetDimension()
    

    
    if 'ResampleImageFilter' in Method:
        Resampler = sitk.ResampleImageFilter()
        
        Resampler.SetReferenceImage(RefImage)
        
        Resampler.SetInterpolator(Interpolator)
        
        if 'Identity' in Method:
            Resampler.SetTransform(sitk.Transform())
        if 'Affine' in Method:
            Resampler.SetTransform(sitk.AffineTransform(Dimension))
        
        Resampler.SetOutputSpacing(RefImage.GetSpacing())
        Resampler.SetSize(RefImage.GetSize())
        Resampler.SetOutputDirection(RefImage.GetDirection())
        Resampler.SetOutputOrigin(RefImage.GetOrigin())
        Resampler.SetDefaultPixelValue(Image.GetPixelIDValue())
        
        Resampler.AddCommand(sitk.sitkProgressEvent, lambda: print("\rProgress: {0:03.1f}%...".format(100*Resampler.GetProgress()),end=''))
        Resampler.AddCommand(sitk.sitkProgressEvent, lambda: sys.stdout.flush())
        
        ResImage = Resampler.Execute(Image)
    
    
    
    if 'Resample2' in Method:
        """
        Use the 2nd method listed in the SimpleITK Transforms and Resampling 
        tutorial (the new Size, Spacing, Origin and Direction will be 
        determined intrinsically from RefImage):
            
        https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/blob/master/Python/21_Transforms_and_Resampling.ipynb
        
        Also follow the example here:
            
        https://gist.github.com/zivy/79d7ee0490faee1156c1277a78e4a4c4
        """
        
        # Define the transform which maps RefImage to Image with the 
        # translation mapping the image origins to each other:
        Transform = sitk.AffineTransform(Dimension)
        #Transform.SetMatrix(Image.GetDirection())                                      # <-- 9:55 on 30/10
        Transform.SetMatrix(RefImage.GetDirection())                                    # <-- 9:55 on 30/10
        #Transform.SetTranslation(np.array(Image.GetOrigin()) - RefImage.GetOrigin())   # <-- 9:55 on 30/10
        Transform.SetTranslation(np.array(RefImage.GetOrigin()) - Image.GetOrigin())    # <-- 9:55 on 30/10
        
        if 'Centres' in Method:
            # Use the TransformContinuousIndexToPhysicalPoint to compute an 
            # indexed point's physical coordinates as this takes into account  
            # size, spacing and direction cosines. 
            """
            For the vast majority of images the direction cosines are the 
            identity matrix, but when this isn't the case simply multiplying 
            the central index by the spacing will not yield the correct 
            # coordinates resulting in a long debugging session. 
            """
            RefCentre = np.array(RefImage.TransformContinuousIndexToPhysicalPoint(np.array(RefImage.GetSize())/2.0))
            
            # Modify the transformation to align the centres of the original 
            # and reference image instead of their origins:
            CenteringTransform = sitk.TranslationTransform(Dimension)
            
            ImageCentre = np.array(Image.TransformContinuousIndexToPhysicalPoint(np.array(Image.GetSize())/2.0))
            
            CenteringTransform.SetOffset(np.array(Transform.GetInverse().TransformPoint(ImageCentre) - RefCentre))
            
            CenteredTransform = sitk.Transform(Transform)
            
            CenteredTransform.AddTransform(CenteringTransform)

            ResImage = sitk.Resample(Image, RefImage, CenteredTransform, 
                                     Interpolator, Image.GetPixelIDValue())
            
            
        if 'Origins' in Method:
            ResImage = sitk.Resample(Image, RefImage, Transform, Interpolator, 
                                     Image.GetPixelIDValue())
        
        
    
    
    if 'Resample3' in Method:
        """
        Use the 3rd method listed in the SimpleITK Transforms and Resampling 
        tutorial (explicitly define the new Size, Spacing, Origin and 
        Direction):
            
        https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/blob/master/Python/21_Transforms_and_Resampling.ipynb
        """
        
        NewSize = RefImage.GetSize()
        NewOrigin = RefImage.GetOrigin()
        NewSpacing = RefImage.GetSpacing()
        NewDirection = RefImage.GetDirection()
        
        
        # Define the transform which maps RefImage to Image with the 
        # translation mapping the image origins to each other:
        Transform = sitk.AffineTransform(Dimension)
        #Transform.SetMatrix(Image.GetDirection())                                     # <-- 10:03 on 30/10
        Transform.SetMatrix(RefImage.GetDirection())                                   # <-- 10:03 on 30/10
        #Transform.SetTranslation(np.array(Image.GetOrigin()) - RefImage.GetOrigin())  # <-- 10:03 on 30/10
        Transform.SetTranslation(np.array(RefImage.GetOrigin()) - Image.GetOrigin())   # <-- 10:03 on 30/10
        
        if 'Centres' in Method:
            # Use the TransformContinuousIndexToPhysicalPoint to compute an 
            # indexed point's physical coordinates as this takes into account  
            # size, spacing and direction cosines. 
            """
            For the vast majority of images the direction cosines are the 
            identity matrix, but when this isn't the case simply multiplying 
            the central index by the spacing will not yield the correct 
            # coordinates resulting in a long debugging session. 
            """
            RefCentre = np.array(RefImage.TransformContinuousIndexToPhysicalPoint(np.array(RefImage.GetSize())/2.0))
            
            # Modify the transformation to align the centres of the original 
            # and reference image instead of their origins:
            CenteringTransform = sitk.TranslationTransform(Dimension)
            
            ImageCentre = np.array(Image.TransformContinuousIndexToPhysicalPoint(np.array(Image.GetSize())/2.0))
            
            CenteringTransform.SetOffset(np.array(Transform.GetInverse().TransformPoint(ImageCentre) - RefCentre))
            
            CenteredTransform = sitk.Transform(Transform)
            
            CenteredTransform.AddTransform(CenteringTransform)
        
            ResImage = sitk.Resample(Image, NewSize, CenteredTransform, 
                                     Interpolator, NewOrigin, NewSpacing, 
                                     NewDirection, Image.GetPixelIDValue())  
            
            
        if 'Origins' in Method:
            ResImage = sitk.Resample(Image, NewSize, Transform, 
                                     Interpolator, NewOrigin, NewSpacing, 
                                     NewDirection, Image.GetPixelIDValue())  
            
            
            
            
    if Method == 'NotCorrect':
        """ 
        Use the 3rd method listed in the SimpleITK Transforms and Resampling 
        tutorial (explicitly define the new Size, Spacing, Origin and 
        Direction):
            
        https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/blob/master/Python/21_Transforms_and_Resampling.ipynb
        """
        
        ExtremePts = GetExtremePoints(RefImage)
        
        Affine = sitk.Euler3DTransform(RefImage.TransformContinuousIndexToPhysicalPoint([size/2 for size in RefImage.GetSize()]),
                                       RefImage.GetAngleX(), 
                                       RefImage.GetAngleY(), 
                                       RefImage.GetAngleZ(), 
                                       RefImage.GetTranslation())
        
        InvAffine = Affine.GetInverse()
        
        # Transformed ExtremePts:
        TxExtremePts = [InvAffine.TransformPoint(pt) for pt in ExtremePts]
        
        min_x = min(TxExtremePts)[0]
        min_y = min(TxExtremePts, key=lambda p: p[1])[1]
        min_z = min(TxExtremePts, key=lambda p: p[2])[2]
        max_x = max(TxExtremePts)[0]
        max_y = max(TxExtremePts, key=lambda p: p[1])[1]
        max_z = max(TxExtremePts, key=lambda p: p[2])[2]
        
        NewSpacing = RefImage.GetSpacing()
        #NewDirection = np.eye(3).flatten()
        NewDirection = RefImage.GetDirection()
        #NewOrigin = [min_x, min_y, min_z]
        NewOrigin = RefImage.GetOrigin()
        
        #NewSize = [math.ceil((max_x - min_x)/NewSpacing[0]), 
        #           math.ceil((max_y - min_y)/NewSpacing[1]),
        #           math.ceil((max_z - min_z)/NewSpacing[2])]
        NewSize = RefImage.GetSize()
        
        ResImage = sitk.Resample(Image, NewSize, Affine, Interpolator, 
                                 NewOrigin, NewSpacing, NewDirection)
    
    
    #sitk.Show(ResImage)

    return ResImage







def MappedCopySegmentAcrossSeries(SrcDcmDir, SrcSegFpath, FromSliceNum, 
                                  TrgDcmDir, TrgSegFpath, Method,
                                  Interpolation, LogToConsole=False):
    """
    Make a relationship-preserving copy of a single segment on a given slice to  
    a different DICOM series.  Since the relationship is preserved, the voxels 
    corresponding to the voxels copied to the Target ROI volume spatially
    relate to the voxels corresponding to the voxels copied from the Source ROI
    volume.
    
    There are four possible cases that will need to be accommodated*:
        
        2b. The Source and Target images have the same FOR, IOP, IPP, PS and ST 
        
        3b. The Source and Target images have the same FOR and IOP but have
           different PS and/or ST (if different ST they will likely have 
           different IPP)
        
        4. The Source and Target images have the same FOR but have different
           IOP and IPP, and possibly different PS and/or ST
           
        5. The Source and Target images have different FOR (hence different IPP
           and IOP), and possibly different ST and/or PS
        
    FOR = FrameOfReferenceUID, IPP = ImagePositionPatient, 
    IOP = ImageOrientationPatient, ST = SliceThickness, PS = PixelSpacing
    
    * The numbering deliberately starts at 2b for consistency with the 5 
    overall cases.  Cases 1, 2a and 3a (=Direct copies) are covered by other 
    functions (CopySegmentWithinSeries for Case 1, and 
    DirectCopySegmentAcrossSeries for Cases 2a and 3a).
    
    
    Inputs:
        SrcDcmDir    - (String) Directory containing the Source DICOMs
                            
        SrcSegFpath  - (String) Full path of the Source DICOM SEG file
                             
        FromSliceNum - (Integer) Slice index of the Source DICOM stack 
                       corresponding to the contour/segment to be copied 
                       (counting from 0)
                       
        TrgDcmDir    - (String) Directory containing the Target DICOMs
                            
        TrgSegFpath  - (String) Full path of the Target DICOM SEG file;
                       May also be empty string ('') if there is no DICOM SEG
                       for the Target Series
                            
        LogToConsole - (Boolean) Denotes whether or not some intermediate
                       results will be logged to the console
                            
    Returns:
        NewTrgSeg    - Modified Target ROI object 
    
    """
    
    # Import the Source and Target SEG ROI:
    SrcSeg = pydicom.dcmread(SrcSegFpath)
    if TrgSegFpath: # if TrgSegFpath is not empty
        TrgSeg = pydicom.dcmread(TrgSegFpath)
    
    # Get the modality of the ROIs:
    SrcModality = SrcSeg.Modality
    if TrgSegFpath:
        TrgModality = TrgSeg.Modality
    
    # Both modalities should be SEG.  Return if not:
    if TrgSegFpath:
        if SrcModality != 'SEG' or TrgModality != 'SEG':
            print(f'\nThe Source ({SrcModality}) and Target ({TrgModality})',
                  'modalities are different.')
            
            return
    
    # Import the Source and Target DICOMs:
    SrcDicoms = ImportDicoms(DicomDir=SrcDcmDir)
    TrgDicoms = ImportDicoms(DicomDir=TrgDcmDir)
    
    # Get the Source and Target FrameOfReferenceUID:
    SrcFOR = SrcDicoms[0].FrameOfReferenceUID
    TrgFOR = TrgDicoms[0].FrameOfReferenceUID
    
    # Get the image attributes using Pydicom:
    SrcPydiSize, SrcPydiSpacing, \
    SrcPydiIPP, SrcPydiDir = GetImageAttributes(SrcDcmDir)
    
    TrgPydiSize, TrgPydiSpacing, \
    TrgPydiIPP, TrgPydiDir = GetImageAttributes(TrgDcmDir)
    
    # Get the Image Attributes for Source and Target using SimpleITK:
    SrcSitkSize, SrcSitkSpacing,\
    SrcSitkIPP, SrcSitkDir = GetImageAttributes(DicomDir=SrcDcmDir,
                                                Package='sitk')
    
    TrgSitkSize, TrgSitkSpacing,\
    TrgSitkIPP, TrgSitkDir = GetImageAttributes(DicomDir=TrgDcmDir,
                                                Package='sitk')
    
    if LogToConsole:
        title = 'Select image attributes for *Source* DICOMs from Pydicom and SimpleITK:'
        ul = '*' * len(title)
        
        print('\n' + title)
        print(ul + '\n')
        print(f'Pydi Size    = {SrcPydiSize}')
        print(f'Sitk Size    = {list(SrcSitkSize)}\n')
        print(f'Pydi Spacing = {SrcPydiSpacing}')
        print(f'Sitk Spacing = {list(SrcSitkSpacing)}\n')
        print(f'Pydi Origin  = {SrcPydiIPP[0]}')
        print(f'Sitk Origin  = {list(SrcSitkIPP[0])}\n\n')
        
        title = 'Select image attributes for *Target* DICOMs from Pydicom and SimpleITK:'
        ul = '*' * len(title)
        
        print('\n' + title)
        print(ul + '\n')
        print(f'Pydi Size    = {TrgPydiSize}')
        print(f'Sitk Size    = {list(TrgSitkSize)}\n')
        print(f'Pydi Spacing = {TrgPydiSpacing}')
        print(f'Sitk Spacing = {list(TrgSitkSpacing)}\n')
        print(f'Pydi Origin  = {TrgPydiIPP[0]}')
        print(f'Sitk Origin  = {list(TrgSitkIPP[0])}\n\n')
    
    # Get the Source and Target DICOM SOP UIDs:
    SrcSOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    TrgSOPuids = GetDicomSOPuids(DicomDir=TrgDcmDir)
    
    # Get the ReferencedImageSequence-to-DICOM slice indices and 
    # PerFrameFunctionalGroupsSequence-to-DICOM slice indices for Source and 
    # Target:
    SrcRIStoDcmInds = GetRIStoDcmInds(SrcSeg, SrcSOPuids)

    SrcPFFGStoDcmInds = GetPFFGStoDcmInds(SrcSeg, SrcSOPuids)
    
    if TrgSegFpath:
        TrgRIStoDcmInds = GetRIStoDcmInds(TrgSeg, TrgSOPuids)
        
        TrgPFFGStoDcmInds = GetPFFGStoDcmInds(TrgSeg, TrgSOPuids)
        
        if LogToConsole:
            print('Segments exist for the Source series on slices',
                  f'{SrcPFFGStoDcmInds}, \nand for the Target series on',
                  f'slices {TrgPFFGStoDcmInds}')
    
    else:
        if LogToConsole:
            print('Segments exist for the Source series on slices',
                  f'{SrcPFFGStoDcmInds}')
            
    
    # Verify that a segment exists for FromSliceNum (this check won't be 
    # necessary in the OHIF-Viewer but a bad input could occur here):
    if not FromSliceNum in SrcPFFGStoDcmInds:
        print('\nA segment does not exist for the Source series on slice',
              f'{FromSliceNum}')
        
        return
    
    
    # The 3D pixel array:
    #SrcSegPixArr = SrcSeg.pixel_array
    #TrgSegPixArr = TrgSeg.pixel_array
    
    # Create 3D labelmaps (= pixel arrays in same frame position as 
    # corresponding DICOM slices, with 2D zero masks in between):
    SrcLabMap = PixArr2LabMap(PixelArray=SrcSeg.pixel_array,
                              NumOfSlices=SrcPydiSize[2],
                              FrameToSliceInds=SrcPFFGStoDcmInds)
    
    if TrgSegFpath:
        TrgLabMap = PixArr2LabMap(PixelArray=TrgSeg.pixel_array,
                                  NumOfSlices=TrgPydiSize[2],
                                  FrameToSliceInds=TrgPFFGStoDcmInds)
    else:
        # Initialise the Target LabelMap:
        TrgLabMap = np.zeros((TrgPydiSize[2], TrgPydiSize[1], TrgPydiSize[0]), 
                             dtype='uint')
    
    """ More useful to convert Pixel Array to sitk image.. """
    
    # Read in the Source and Target SimpleITK 3D images:
    SrcImage = ImportImage(SrcDcmDir)
    TrgImage = ImportImage(TrgDcmDir)
    
    # Create SimpleITK images of the 3D labelmaps (= pixel arrays in same frame 
    # position as corresponding DICOM slices, with 2D zero masks in between):
    SrcLabMapIm = PixArr2Image(PixelArray=SrcSeg.pixel_array,
                               Image=SrcImage,
                               NumOfSlices=SrcPydiSize[2],
                               FrameToSliceInds=SrcPFFGStoDcmInds)
    
    if TrgSegFpath:
        TrgLabMapIm = PixArr2Image(PixelArray=TrgSeg.pixel_array,
                                   Image=TrgImage,
                                   NumOfSlices=TrgPydiSize[2],
                                   FrameToSliceInds=TrgPFFGStoDcmInds)
        
    else:
        # Initialise the Target LabelMap:
        TrgLabMap = np.zeros((TrgPydiSize[2], TrgPydiSize[1], TrgPydiSize[0]), 
                             dtype='uint')
        
        TrgLabMapIm = sitk.GetImageFromArray(TrgLabMap)
        
        # Set the Origin, Spacing and Direction of TrgLabMapIm to that of 
        # TrgImage:
        TrgLabMapIm.SetOrigin(TrgImage.GetOrigin())
        TrgLabMapIm.SetSpacing(TrgImage.GetSpacing())
        TrgLabMapIm.SetDirection(TrgImage.GetDirection())
    
    
    # Check which case follows:
    if SrcFOR == TrgFOR:
        print('\nThe Source and Target FrameOfReferenceUID are the same')
        
        # Compare the Source and Target directions. Get the maximum value of 
        # their absolute differences:
        AbsDiffs = abs(np.array(SrcPydiDir) - np.array(TrgPydiDir))
        MaxAbsDiff = max(AbsDiffs)
        
        # Consider the directions different if any of the vector differences 
        # are greater than epsilon:
        epsilon = 1e-06
        
        #if SrcDirs == TrgDirs: 
        """ The line above will result in insignificant differences (e.g. due
        to quantisation/pixelation) resulting in False, so instead consider
        MaxAbsDiff and epsilon. 
        """
        if MaxAbsDiff < epsilon:
            print('\nThe Source and Target directions are the same')
            
            if SrcPydiSpacing == TrgPydiSpacing:
                print('\nThe Source and Target voxel sizes are the same')
                
                CaseNum = '2b'
                
            else:
                print('\nThe Source and Target voxel sizes are different:\n',
                      f'\n   Source: {SrcPydiSpacing} \n',
                      f'\n   Target: {TrgPydiSpacing}')
                
                CaseNum = '3b'
            
        else:
            print('\nThe Source and Target directions are different:\n',
                  f'\n   Source: [{SrcPydiDir[0]}, {SrcPydiDir[1]}, {SrcPydiDir[2]},',
                  f'\n            {SrcPydiDir[3]}, {SrcPydiDir[4]}, {SrcPydiDir[5]},',
                  f'\n            {SrcPydiDir[6]}, {SrcPydiDir[7]}, {SrcPydiDir[8]}]\n',
                  f'\n   Target: [{TrgPydiDir[0]}, {TrgPydiDir[1]}, {TrgPydiDir[2]},',
                  f'\n            {TrgPydiDir[3]}, {TrgPydiDir[4]}, {TrgPydiDir[5]},',
                  f'\n            {TrgPydiDir[6]}, {TrgPydiDir[7]}, {TrgPydiDir[8]}]')
            
            print(f'\nAbsDiffs = {AbsDiffs}')
            
            
            
            CaseNum = '4'
    
    else:
        print('\nThe Source and Target FrameOfReferenceUID are different')
        
        CaseNum = '5'
        
        
    print('\nThe Source and Target origins:\n',
                      f'\n   Source: {SrcPydiIPP[0]} \n',
                      f'\n   Target: {TrgPydiIPP[0]}')
    
    print('\nThe Source and Target image dims:\n',
                      f'\n   Source: {SrcPydiSize} \n',
                      f'\n   Target: {TrgPydiSize}')
    
    
    
    if LogToConsole:
        print(f'\nCase {CaseNum} applies.')
    
    
    if CaseNum == '2b':
        """
        The origins for Source and Target are the same since they have the same
        FrameOfReferenceUID.  And since the PixelSpacing and SliceThickness are
        also the same, ToSliceNum = FromSliceNum, and the relationships will be
        preserved.
        
        26/10: It's seems that having the same FOR does not guarantee the same
        origin.  Series 9 and 6 for Subject 011, MR4 have different origins!
        """
        
        print('\nApplying Case 2b..\n\n')
    
        ToSliceNum = copy.deepcopy(FromSliceNum)
        
        if LogToConsole:
            print(f'\nCopying slice {FromSliceNum} from Source SEG to slice',
                  f'{ToSliceNum} in Target SEG..')
    
        # Check if ToSliceNum already has a segment:
        """
        Note:
            If slice number ToSliceNum already has a segment, it will be 
            over-written with the segment data of slice number FromSliceNum.
            If it doesn't have a segment, ReferencedImageSequence and 
            PerFrameFunctionalGroupsSequence need to be extended by one.
        """
        if ToSliceNum in TrgRIStoDcmInds:
            # Use TrgSeg as a template for NewTrgSegRoi:
            NewTrgSeg = copy.deepcopy(TrgSeg)
            
            # Create a new list of TrgRIStoDcmInds: <-- not needed?
            #NewTrgRIStoDcmInds = copy.deepcopy(TrgRIStoDcmInds)
            
            # Create a new list of PFFGStoDcmInds:
            NewTrgPFFGStoDcmInds = copy.deepcopy(TrgPFFGStoDcmInds)
            
        else:
            # Increase the length of the sequences:
            NewTrgSeg = AddToSegSequences(TrgSeg)
            
            # Create a new list of TrgRIStoDcmInds by adding the index  
            # ToSliceNum (representing the contour to be added to 
            # ReferencedImageSequence) to TrgRIStoDcmInds: <-- not needed?
            #NewTrgRIStoDcmInds = AddIndToIndsAndSort(TrgRIStoDcmInds, 
            #                                         ToSliceNum)
            
            # Create a new list of TrgPFFGStoDcmInds by adding the index 
            # ToSliceNum (representing the segment to be added to 
            # PerFrameFunctionalGroupsSequence) to TrgPFFGStoDcmInds:
            NewTrgPFFGStoDcmInds = AddIndToIndsAndSort(TrgPFFGStoDcmInds, 
                                                       ToSliceNum)
            
        
        if LogToConsole:
            print('\nTrgPFFGStoDcmInds    =', TrgPFFGStoDcmInds)
            print('\nNewTrgPFFGStoDcmInds =', NewTrgPFFGStoDcmInds)
        
        # Modify select tags in NewTrgSeg:
        #NewTrgSeg = ModifySegTagVals(TrgSeg, NewTrgSeg, FromSliceNum, 
        #                             ToSliceNum, TrgDicoms, 
        #                             #TrgPFFGStoDcmInds, NewTrgPFFGStoDcmInds,
        #                             SrcPFFGStoDcmInds, NewTrgPFFGStoDcmInds,
        #                             LogToConsole)
        
        NewTrgSeg = ModifySegTagVals(SrcSeg, SrcDicoms, FromSliceNum, 
                                     TrgSeg, NewTrgSeg, TrgDicoms, ToSliceNum, 
                                     SrcPFFGStoDcmInds, TrgPFFGStoDcmInds, 
                                     NewTrgPFFGStoDcmInds, LogToConsole)
        
        """
        23/10:  Still need to verify that Case 2 provides the expected results.
        
        26/10:  Resampling will need to be performed if the origins are not the
        same...
        """
        
        
    if CaseNum == '3b':
        print(f'\nApplying Case 3b..\n\n')
        
        # Read in the Source and Target SimpleITK 3D images:
        #SrcImage = ImportImage(SrcDcmDir)
        #TrgImage = ImportImage(TrgDcmDir)
        
        #SrcSitkOrigin = SrcSitkIm.GetOrigin() 
        #TrgSitkOrigin = SrcSitkIm.GetOrigin() 
        #
        #SrcSitkDirs = SrcSitkIm.GetDirection() 
        #
        #SrcSitkSpacings = SrcSitkIm.GetSpacing() 
        #
        #SrcSitkDims = SrcSitkIm.GetSize() 
        
        
        # Get the Image Attributes for Source and Target using SimpleITK:
        #SrcSitkSize, SrcSitkSpacing,\
        #SrcSitkIPPs, SrcSitkDirs = GetImageAttributes(DicomDir=SrcDcmDir,
        #                                              Package='sitk')
        #
        #TrgSitkSize, TrgSitkSpacing,\
        #TrgSitkIPPs, TrgSitkDirs = GetImageAttributes(DicomDir=TrgDcmDir,
        #                                              Package='sitk')
        
        
        """
        Although it's the Source Labelmap that needs to be resampled, first
        prove that I can resample the image.
        """
        
        """
        # Resample the Source image:
        ResSrcImage = ResampleImage(Image=SrcImage, RefImage=TrgImage, 
                                    Method=Method, Interpolation=Interpolation)#,
                                    #RefImageSpacings=RefImageSpacings)
                                    
        print('\n\nResults after resampling Source image:\n\n')
        
        print('\nThe Source and Target image size:\n',
                      f'\n   Original Source:  {SrcImage.GetSize()} \n',
                      f'\n   Resampled Source: {ResSrcImage.GetSize()} \n',
                      f'\n   Target:           {TrgImage.GetSize()}')
            
        print('\nThe Source and Target voxel spacings:\n',
                      f'\n   Original Source:  {SrcImage.GetSpacing()} \n',
                      f'\n   Resampled Source: {ResSrcImage.GetSpacing()} \n',
                      f'\n   Target:           {TrgImage.GetSpacing()}')
            
        print('\nThe Source and Target Origin:\n',
                      f'\n   Original Source:  {SrcImage.GetOrigin()} \n',
                      f'\n   Resampled Source: {ResSrcImage.GetOrigin()} \n',
                      f'\n   Target:           {TrgImage.GetOrigin()}')
            
        print('\nThe Source and Target Direction:\n',
                      f'\n   Original Source:  {SrcImage.GetDirection()} \n',
                      f'\n   Resampled Source: {ResSrcImage.GetDirection()} \n',
                      f'\n   Target:           {TrgImage.GetDirection()}')
        """                            
                                    
        # Resample the Source labelmap:
        ResSrcLabMapIm = ResampleImage(Image=SrcLabMapIm, RefImage=TrgImage, 
                                       Method=Method, 
                                       Interpolation=Interpolation)
        
        
        print('\n\n')
        title = 'Results after resampling Source LabelMap image:'
        ul = '*' * len(title)
        
        print('\n' + title)
        print(ul)
        
        print('\n*The Source and Target image size:*\n',
                      f'\n   Original Source:  {SrcLabMapIm.GetSize()} \n',
                      f'\n   Resampled Source: {ResSrcLabMapIm.GetSize()} \n',
                      f'\n   Target:           {TrgLabMapIm.GetSize()}')
            
        print('\n*The Source and Target voxel spacings:*\n',
                      f'\n   Original Source:  {SrcLabMapIm.GetSpacing()} \n',
                      f'\n   Resampled Source: {ResSrcLabMapIm.GetSpacing()} \n',
                      f'\n   Target:           {TrgLabMapIm.GetSpacing()}')
            
        print('\n*The Source and Target Origin:*\n',
                      f'\n   Original Source:  {SrcLabMapIm.GetOrigin()} \n',
                      f'\n   Resampled Source: {ResSrcLabMapIm.GetOrigin()} \n',
                      f'\n   Target:           {TrgLabMapIm.GetOrigin()}')
            
        print('\n*The Source and Target Direction:*\n',
                      f'\n   Original Source:  {SrcLabMapIm.GetDirection()} \n',
                      f'\n   Resampled Source: {ResSrcLabMapIm.GetDirection()} \n',
                      f'\n   Target:           {TrgLabMapIm.GetDirection()}')
        
        
        # Use MinimumMaximumImageFilter to get image maximum:
        ImMaxFilt = sitk.MinimumMaximumImageFilter()
        
        #SrcLabMapImMax = ImMaxFilt.Execute(SrcLabMapIm).GetMaximum()
        #ResSrcLabMapImMax = ImMaxFilt.Execute(ResSrcLabMapIm).GetMaximum()
        #TrgLabMapImMax = ImMaxFilt.Execute(TrgLabMapIm).GetMaximum()
        
        """
        For some reason I can't nest the commands as in the above commented 
        lines:
            
            AttributeError: 'NoneType' object has no attribute 'GetMaximum'
        """
        
        SrcLabMapImMaxFilt = sitk.MinimumMaximumImageFilter()
        SrcLabMapImMaxFilt.Execute(SrcLabMapIm)
        SrcLabMapImMax = SrcLabMapImMaxFilt.GetMaximum()
        
        ResSrcLabMapImMaxFilt = sitk.MinimumMaximumImageFilter()
        ResSrcLabMapImMaxFilt.Execute(ResSrcLabMapIm)
        ResSrcLabMapImMax = ResSrcLabMapImMaxFilt.GetMaximum()
        
        TrgLabMapImMaxFilt = sitk.MinimumMaximumImageFilter()
        TrgLabMapImMaxFilt.Execute(TrgLabMapIm)
        TrgLabMapImMax = TrgLabMapImMaxFilt.GetMaximum()
        
        print('\n*The Source and Target image maximum:*\n',
                      f'\n   Original Source:  {SrcLabMapImMax} \n',
                      f'\n   Resampled Source: {ResSrcLabMapImMax} \n',
                      f'\n   Target:           {TrgLabMapImMax}')
        
        
        
        
        
        # Plot results:
        #PlotSitkImages_Src_ResSrc_Trg(SrcIm=SrcImage, 
        #                              ResSrcIm=ResSrcImage, 
        #                              TrgIm=TrgImage, 
        #                              LogToConsole=False)
        
        
        #return SrcImage, ResSrcImage, TrgImage
        return SrcLabMapIm, ResSrcLabMapIm, TrgLabMapIm
         
         
        
        
    if CaseNum == '4':
        print(f'\nApplying Case 4..\n\n')
        
        
        
    if CaseNum == '5':
        print(f'\nApplying Case 5..\n\n')
        
        
    
        
        
    
    # Check if NewTrgSeg exists (temporary check):
    if 'NewTrgSeg' in locals():
    
        # Generate a new SOP Instance UID:
        NewTrgSeg.SOPInstanceUID = pydicom.uid.generate_uid()
        
        # Generate a new Series Instance UID:
        NewTrgSeg.SeriesInstanceUID = pydicom.uid.generate_uid()
        
        
        return NewTrgSeg
    
    #else:
        #return []
        #return ResSrcImage








def ExportSegRoi(TrgSegRoi, SrcSegFpath, NamePrefix, ExportDir):
    """
    Export contour ROI Object to disc.
    
    
    Inputs:
        TrgSegRoi   - Target SEG ROI object to be exported
        
        SrcSegFpath - (String) Full path of the Source DICOM SEG file (used to
                      generate the filename of the new SEG file)
        
        NamePrefix  - (String) Prefix to be added to the assigned filename and
                      Content Label (e.g. 'MR4_S9_s23_to_MR4_S9_s22') 
                            
        ExportDir   - (String) Directory where the SEG is to be exported
                           
    
                            
    Returns:
        TrgSegFpath - (String) Full path of the exported Target DICOM SEG file
    
    """
    
    """
    The following was moved into the main function CopySegmentWithinSeries:
    # Generate a new SOP Instance UID:
    SegRoi.SOPInstanceUID = pydicom.uid.generate_uid()
    
    # Generate a new Series Instance UID:
    SegRoi.SeriesInstanceUID = pydicom.uid.generate_uid()
    """
    
    # Get the filename of the original SEG file:
    SrcSegFname = os.path.split(SrcSegFpath)[1]
    
    # Modify the Content Date and Time to the present:
    NewDate = time.strftime("%Y%m%d", time.gmtime())
    NewTime = time.strftime("%H%M%S", time.gmtime())
    
    TrgSegRoi.ContentDate = NewDate
    TrgSegRoi.ContentTime = NewTime
    
    FnamePrefix = NewDate + '_' + NewTime + '_' + NamePrefix + '_from_' 
    ContentLabelPrefix = NamePrefix + '_from_'
    
    # Modify the Content Label (this appears under Name in XNAT):
    #TrgSegRoi.ContentLabel = 'Copy_of_' + TrgSegRoi.ContentLabel
    TrgSegRoi.ContentLabel = ContentLabelPrefix + TrgSegRoi.ContentLabel
    
    # Modify Content Description:
    TrgSegRoi.ContentDescription = ContentLabelPrefix \
                                   + TrgSegRoi.ContentDescription
                                   
    # Modify the Series Description as with the Content Label:
    TrgSegRoi.SeriesDescription = ContentLabelPrefix \
                                  + TrgSegRoi.SeriesDescription
    
    
    
    # Create a new filename (this will appear under Label in XNAT):
    #TrgRoiFname = 'New_' + SrcSegFname + '_' + NewDate + '_' + NewTime
    #TrgRoiFname = FnamePrefix + '_SEG_' + NewDate + '_' + NewTime + '_' \
    #              + SrcSegFname
    TrgSegFname = FnamePrefix + SrcSegFname
    
    TrgSegFpath = os.path.join(ExportDir, TrgSegFname)
    
    TrgSegRoi.save_as(TrgSegFpath)
        
    print('\nSEG ROI exported to:\n\n', TrgSegFpath)
    
    return TrgSegFpath




def CropNonZerosIn2dMask(Orig2dMask):
    
    #print('\nShape of Orig2dMask =', Orig2dMask.shape)
    
    # The non-zero elements in the Orig2dMask:
    non0 = np.nonzero(Orig2dMask)
    
    # If there are non-zero elements:
    if non0[0].size:
    
        a = non0[0][0]
        b = non0[0][-1]
        
        c = non0[1][0]
        d = non0[1][-1]
    
        # The non-zero (cropped) array:
        Cropped2dMask = Orig2dMask[a:b, c:d]
        
        #print('\nShape of Cropped2dMask =', Cropped2dMask.shape)
        
        return Cropped2dMask
    
    else:
        #print('There were no non-zero elements in the 2D mask.')
        
        return non0[0]
    




def Compare2dMasksFrom3dMasksOLD(OrigSegRoi, NewSegRoi, OrigSliceNum, NewSliceNum,
                              OrigDicomDir, NewDicomDir):
    """ Compare cropped masks of non-zero elements only. """ 
    
    # Get the DICOM SOP UIDs:
    OrigSOPuids = GetDicomSOPuids(DicomDir=OrigDicomDir)
    NewSOPuids = GetDicomSOPuids(DicomDir=NewDicomDir)
    
    # Get the Per-frameFunctionalGroupsSequence-to-DICOM slice indices:
    OrigPFFGStoDcmInds = GetPFFGStoDcmInds(OrigSegRoi, OrigSOPuids)
    NewPFFGStoDcmInds = GetPFFGStoDcmInds(NewSegRoi, NewSOPuids)
    
    # Get the 3D SEG masks:
    Orig3dMask = OrigSegRoi.pixel_array
    New3dMask = NewSegRoi.pixel_array
    
    OrigShape = Orig3dMask.shape
    NewShape = New3dMask.shape
    
    print(f'Segments exist in OrigSegRoi on slices {OrigPFFGStoDcmInds}')
    print(f'Shape of Orig3dMask = {OrigShape}')
    print(f'\nSegments exist in NewSegRoi on slices {NewPFFGStoDcmInds}')
    print(f'Shape of New3dMask = {NewShape}\n')
    
    
    # Initialise Orig2dMaskCropped and New2dMaskCropped:
    Orig2dMaskCropped = np.zeros((1, 1))
    New2dMaskCropped = np.zeros((1, 1))
    
    
    # Does slice OrigSliceNum in OrigSegRoi have a segment?
    if OrigSliceNum in OrigPFFGStoDcmInds:
        # A segment frame exists for OrigSliceNum:
        OrigFrame = True
        
        # Get the frame number for this slice number:
        OrigFrameNum = OrigPFFGStoDcmInds.index(OrigSliceNum)
        
        Orig2dMask = OrigSegRoi.pixel_array[OrigFrameNum]
        
        print(f'Shape of Orig2dMask = Orig3dMask[{OrigFrameNum}] = {Orig2dMask.shape}')
    
        #print('Cropping Orig2dMask to array of non-zero elements..')
    
        Orig2dMaskCropped = CropNonZerosIn2dMask(Orig2dMask)
        #Orig2dMaskCropped = CropNonZerosIn2dMask(Orig3dMask[OrigFrameNum])
        
    else:
        OrigFrame = False
        
        print(f'A segment does not exist on slice {OrigSliceNum} in OrigSegRoi.')
        
    
    # Does slice NewSliceNum in NewSegRoi have a segment?
    if NewSliceNum in NewPFFGStoDcmInds:
        # A segment frame exists for NewSliceNum:
        NewFrame = True
        
        # Get the frame number for this slice number:
        NewFrameNum = NewPFFGStoDcmInds.index(NewSliceNum)
        
        New2dMask = NewSegRoi.pixel_array[NewFrameNum]
    
        print(f'Shape of New2dMask = New3dMask[{NewFrameNum}]  = {New2dMask.shape}')
    
        #print('Cropping New2dMask to array of non-zero elements..')
        
        New2dMaskCropped = CropNonZerosIn2dMask(New2dMask)
        #New2dMaskCropped = CropNonZerosIn2dMask(New3dMask[FrameNum])
        
        
    else:
        NewFrame = False
        
        print(f'A segment does not exist on slice {NewSliceNum} in NewSegRoi.')
    
    
    # Proceed only if either cropped arrays are not empty (i.e. if at least one
    # of the 2D masks had non-zero elements):
    if Orig2dMaskCropped.any() or New2dMaskCropped.any():
    
        print('')
        
        fig, ax = plt.subplots(1, 2)
        
        if Orig2dMaskCropped.any():
            print('Shape of Orig2dMaskCropped =', Orig2dMaskCropped.shape)
            
            ax = plt.subplot(1, 2, 1, aspect='equal')
            ax.imshow(Orig2dMaskCropped)
        
        else:
            if OrigFrame:
                print(f'Frame {OrigFrameNum} in OrigSegRoi does not have any',
                      'non-zero elements.')
        
        if New2dMaskCropped.any():
            print('Shape of New2dMaskCropped  =', New2dMaskCropped.shape)
        
            ax = plt.subplot(1, 2, 2, aspect='equal')
            ax.imshow(New2dMaskCropped)
        
        else:
            if NewFrame:
                print(f'Frame {NewFrameNum} in NewSegRoi does not have any',
                      'non-zero elements.')
            
    else:
        if OrigFrame and NewFrame:
            print(f'Frame {OrigFrameNum} and {NewFrameNum} does not have any',
                  'non-zero elements in OrigSegRoi and NewSegRoi.')
    
    return
    
    


def Compare2dMasksFrom3dMasks(OrigSegRoi, NewSegRoi, OrigDicomDir, NewDicomDir):
    """ Compare cropped masks of non-zero elements only. """ 
    
    # Get the DICOM SOP UIDs:
    OrigSOPuids = GetDicomSOPuids(DicomDir=OrigDicomDir)
    NewSOPuids = GetDicomSOPuids(DicomDir=NewDicomDir)
    
    # Get the Per-frameFunctionalGroupsSequence-to-DICOM slice indices:
    OrigPFFGStoDcmInds = GetPFFGStoDcmInds(OrigSegRoi, OrigSOPuids)
    NewPFFGStoDcmInds = GetPFFGStoDcmInds(NewSegRoi, NewSOPuids)
    
    # Combined indices from OrigPFFGStoDcmInds and NewPFFGStoDcmInds:
    AllInds = OrigPFFGStoDcmInds + NewPFFGStoDcmInds
    
    # Remove duplicates:
    AllInds = list(set(AllInds))
    
    
    # Get the 3D SEG masks:
    Orig3dMask = OrigSegRoi.pixel_array
    New3dMask = NewSegRoi.pixel_array
    
    OrigShape = Orig3dMask.shape
    NewShape = New3dMask.shape
    
    print(f'Segments exist in OrigSegRoi on slices {OrigPFFGStoDcmInds}')
    print(f'Shape of Orig3dMask = {OrigShape}')
    print(f'\nSegments exist in NewSegRoi on slices {NewPFFGStoDcmInds}')
    print(f'Shape of New3dMask = {NewShape}\n')
    
    # Initialise the 3D cropped SEG masks:
    Orig3dMaskCropped = []
    New3dMaskCropped = []
    
    for i in range(OrigShape[0]):
        cropped = CropNonZerosIn2dMask(Orig3dMask[i])
        
        Orig3dMaskCropped.append(cropped)
        
    for i in range(NewShape[0]):
        cropped = CropNonZerosIn2dMask(New3dMask[i])
        
        New3dMaskCropped.append(cropped)
    
    
    Nrows = len(AllInds)
    
    Ncols = 2
    
    n = 1 # initialised sub-plot number
    
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows))
    
    for i in range(len(AllInds)):
        SliceNum = AllInds[i]
        
        # Does slice SliceNum have a segment in OrigSegRoi or NewSegRoi?
        if SliceNum in OrigPFFGStoDcmInds:
            OrigFrameNum = OrigPFFGStoDcmInds.index(SliceNum)
        
            ax = plt.subplot(Nrows, Ncols, n, aspect='equal')
            ax.imshow(Orig3dMaskCropped[OrigFrameNum])
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'Orig slice {SliceNum}')
            
        n += 1 # increment sub-plot number
        
        if SliceNum in NewPFFGStoDcmInds:
            NewFrameNum = NewPFFGStoDcmInds.index(SliceNum)
    
            ax = plt.subplot(Nrows, Ncols, n, aspect='equal')
            ax.imshow(New3dMaskCropped[NewFrameNum])
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'New slice {SliceNum}')
            
        n += 1 # increment sub-plot number
    
    return




def PlotDicomsAndSegments(DicomDir, SegFpath, ExportPlot, ExportDir, 
                          LogToConsole):
    
    
    
    # Import the DICOMs:
    Dicoms = ImportDicoms(DicomDir=DicomDir)
    
    # Get the DICOM SOP UIDs:
    SOPuids = GetDicomSOPuids(DicomDir=DicomDir)
    
    # Import the SEG ROI:
    SegRoi = pydicom.dcmread(SegFpath)
    
    # Get the Per-frameFunctionalGroupsSequence-to-DICOM slice indices:
    PFFGStoDcmInds = GetPFFGStoDcmInds(SegRoi, SOPuids)
    
    # The 3D labelmap:
    SegNpa = SegRoi.pixel_array
    
    if LogToConsole:
        print(f'Segments exist on slices {PFFGStoDcmInds}')
        print(f'Shape of PixelData = {SegNpa.shape}\n')

    
    
    # Prepare the figure.
    
    # All DICOM slices that have segmentations will be plotted. The number of
    # slices to plot (= number of segments):
    #Nslices = int(SegRoi.NumberOfFrames)
    Nslices = len(PFFGStoDcmInds)
    
    # Set the number of subplot rows and columns:
    Ncols = np.int8(np.ceil(np.sqrt(Nslices)))
    
    # Limit the number of rows to 5 otherwise it's difficult to make sense of
    # the images:
    if Ncols > 5:
        Ncols = 5
    
    Nrows = np.int8(np.ceil(Nslices/Ncols))
    
    # Create a figure with two subplots and the specified size:
    if ExportPlot:
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows), dpi=300)
        fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows), dpi=300)
    else:
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows))
        fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows))
        
    
    n = 1 # initialised sub-plot number
    
    # Loop through each slice: 
    for i in range(Nslices):
        if LogToConsole:
                print('\ni =', i)
                
        # The DICOM slice number is:
        s = PFFGStoDcmInds[i]
        
        #plt.subplot(Nrows, Ncols, n)
        #plt.axis('off')
        ax = plt.subplot(Nrows, Ncols, n)

        #ax = plt.subplot(Nrows, Ncols, n, aspect=AR)
          
        # Plot the DICOM pixel array:
        ax.imshow(Dicoms[s].pixel_array, cmap=plt.cm.Greys_r)
        #ax.set_aspect(ar)
        
        if LogToConsole:
            print(f'\nShape of Dicoms[{s}] = {Dicoms[s].pixel_array.shape}')
            print(f'\nShape of SegNpa[{i}] = {SegNpa[i].shape}')
        
        # Plot the segment pixel array:
        #ax.imshow(SegNpa[i], cmap='red', alpha=0.1)
        ax.imshow(SegNpa[i], alpha=0.2)
        
        ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
        
        ax.set_title(f'Slice {s}')
        #plt.axis('off')
        
        n += 1 # increment sub-plot number
        
            
            
    if ExportPlot:
        SegFullFname = os.path.split(SegFpath)[1]
        
        SegFname = os.path.splitext(SegFullFname)[0]
        
        ExportFname = 'Plot_' + SegFname
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
        
    #print(f'PixAR = {PixAR}')
    #print(f'AxisAR = {AxisAR}')
        
    return






def DELETE_THIS_AddToRIStoDcmInds(RIStoDcmInds, ToSliceNum):
    """
    Append the DICOM slice number (ToSliceNum) representing the segmentation to 
    be added to the Referenced Instance Sequence to RIStoDcmInds (the 
    ReferencedInstanceSequence-to-DICOM slice indeces), and sort the list of 
    indeces.
    
    Inputs:
        RIStoDcmInds    - List of integers of the DICOM slice numbers that 
                          correspond to each Referenced Instance Sequence
        
        ToSliceNum      - (Integer) Slice index in the Target DICOM stack where
                          the segmentation will be copied to (counting from 0)
        
    Returns:
        NewRIStoDcmInds - Modified and sorted list of RIStoDcmInds with the  
                          slice index to be copied
    """
    
    NewRIStoDcmInds = copy.deepcopy(RIStoDcmInds)

    NewRIStoDcmInds.append(ToSliceNum)
    
    NewRIStoDcmInds.sort()
    
    return NewRIStoDcmInds




def DELETE_THIS_AddToPFFGStoDcmInds(PFFGStoDcmInds, ToSliceNum):
    """
    Append the DICOM slice number (ToSliceNum) representing the segmentation to 
    be added to the Per-frame Functional Groups Sequence to PFFGStoDcmInds (the 
    PerFrameFunctionalGroupsSequence-to-DICOM slice indeces), and sort the list 
    of indeces.
    
    Inputs:
        PFFGStoDcmInds    - List of integers of the DICOM slice numbers that 
                            correspond to each Per-frame Functional Groups 
                            Sequence
        
        ToSliceNum        - (Integer) Slice index in the Target DICOM stack 
                            where the segmentation will be copied to (counting 
                            from 0)
        
    Returns:
        NewPFFGStoDcmInds - Modified and sorted list of PFFGStoDcmInds with the 
                            slice index to be copied
    """
    
    NewPFFGStoDcmInds = copy.deepcopy(PFFGStoDcmInds)

    NewPFFGStoDcmInds.append(ToSliceNum)
    
    NewPFFGStoDcmInds.sort()
    
    return NewPFFGStoDcmInds




