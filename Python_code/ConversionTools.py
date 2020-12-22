# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 12:38:31 2020

@author: ctorti

Modified from:
    https://programtalk.com/vs2/python/7636/sima/sima/ROI.py/
    
"""



# Import packages and functions:
#import numpy as np
#import SimpleITK as sitk
#from pydicom import dcmread
#from itertools import product
#from scipy.sparse import lil_matrix, issparse
#from skimage.measure import find_contours
#from shapely.geometry import MultiPolygon, Polygon, Point
##from warnings import warn

#from GeneralTools import UnpackPoints
#from GeneralTools import UniqueItems

##from DicomTools import ImportDicoms
#from DicomTools import GetDicomSOPuids

#from ImageTools import GetImageAttributes
##from ImageTools import InitialiseImage
##from ImageTools import AddImages

##from RtsTools import GetCIStoSliceInds
#from RtsTools import GetCStoSliceInds

##from SegTools import GetPFFGStoSliceInds





"""
******************************************************************************
******************************************************************************
CONVERSION FUNCTIONS
******************************************************************************
******************************************************************************
"""       


"""
Note function Point2Index is somewhat redundant since a point can be converted
to an index with a single line of code using SimpleITK:
    
    SitkIm.TransformPhysicalPointToIndex(Point)
"""


def Point2Index(Point, Origin, Directions, Spacings, Rounding=True):
    """
    Convert a physical point (in Patient Coordinate System (PCS)) to an index
    (in Image Coordinate System (ICS).
    
    Inputs:
    ------
    
    Point : list of floats
        A list (for each dimension) of a point in PCS, e.g. [x, y, z].
        
    Origin : list of floats
        A list (for each dimension) of the 3D image origin 
        (= ImagePositionPatient of the first slice in the DICOM series), 
        e.g. [x0, y0, z0].
        
    Directions : list of floats 
        List of the direction cosines along x (rows), y (columns) and z 
        (slices) (= the cross product of the x and y direction cosines from 
        ImageOrientationPatient appended to ImageOrientationPatient),
        e.g. [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz].
        
    Spacings : list of floats 
        List (for each dimension) of the pixel spacings along x, y and z, 
        e.g. [di, dj, dk].  The x and y spacings come from PixelSpacing.  The 
        z spacing is not the SliceThickness but instead is determined from 
        ImagePositionPatient and ImageOrientationPatient.
        
    Rounding : boolean (optional; True by default)
        If True, the integers in Index will be rounded to the nearest integers.
    
        
    Ouputs:
    ------
    
    Index : list of integers
        List (for each dimension) of the index (i.e. in ICS) of Point, 
        e.g. [i, j, k].
        
    
    Equations:
    ---------
    
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
    
    # The indices of the largest direction cosines along rows, columns and 
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
    Vx = Point[0] - S[0]
    Vy = Point[1] - S[1]
    Vz = Point[2] - S[2]
    
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
    
    if Rounding: # 8/12/20
        # Convert fractional indices to integers:
        i = int(round(i))
        j = int(round(j))
        k = int(round(k))
    
    return [i, j, k]






def Contour2Indices(Points, Origin, Directions, Spacings, Rounding=True):
    """
    Convert a list of physical point (in Patient Coordinate System (PCS)) to a
    list of indeces (in Image Coordinate System (ICS).
    
    Inputs:
    ------
    
    Points : list of a list of floats
        List (for each point) of a list (for each dimension) of points in the
        PCS, e.g. [[x0, y0, z0], [x1, y1, z1], ...].
        
    Origin : list of floats
        A list (for each dimension) of the 3D image origin 
        (= ImagePositionPatient of the first slice in the DICOM series), 
        e.g. [x0, y0, z0].
        
    Directions : list of floats 
        List of the direction cosines along x (rows), y (columns) and z 
        (slices) (= the cross product of the x and y direction cosines from 
        ImageOrientationPatient appended to ImageOrientationPatient),
        e.g. [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz].
        
    Spacings : list of floats 
        List (for each dimension) of the pixel spacings along x, y and z, 
        e.g. [di, dj, dk].  The x and y spacings come from PixelSpacing.  The 
        z spacing is not the SliceThickness but instead is determined from 
        ImagePositionPatient and ImageOrientationPatient.
    
    Rounding : boolean (optional; True by default)
        If True, the integers in Index will be rounded to the nearest integers.
    
        
    Ouputs:
    ------
    
    Indices : list of a list of integers
        List (for each point) of a list (for each dimension) of the indices 
        (in ICS) of Points, e.g. [[i0, j0, k0], [i1, j1, k1], ...].
    """
    
    Indices = []
    
    for Point in Points:
        Indices.append(Point2Index(Point, Origin, Directions, Spacings, 
                                   Rounding))
        
    return Indices




    
    
    
    
def ConvertContourDataToIndices(ContourData, DicomDir):
    """
    Not useful?..
    
    Convert contour data from a flat list of points in the Patient Coordinate
    System (PCS) to a list of [i, j, k] indices in the Image Coordinate System. 
    
    Inputs:
        ContourData - (List of floats) Flat list of points in the PCS,
                      e.g. [x0, y0, z0, x1, y1, z1, ...]
        
        DicomDir    - (String) Directory containing DICOMs
        
        
    Returns:
        Indices   - (List of floats) List of a list of [i, j, k] coordinates
                      of each point in ContourData converted to the ICS,
                      e.g. [[i0, j0, k0], [i1, j1, k1], ...]
    """
    
    from ImageTools import GetImageAttributes
    
    # Get the image attributes:
    Size, Spacings, ST, IPPs, Dirs = GetImageAttributes(DicomDir)
    
    # Initialise the array of contour points:
    Indices = []
    
    # Iterate for all contour points in threes:
    for p in range(0, len(ContourData), 3):
        # The point in Patient Coordinate System:
        pt = [ContourData[p], ContourData[p+1], ContourData[p+2]]
        
        # Convert pt to Image Coordinate System:
        ind = Point2Index(pt, IPPs[0], Dirs, Spacings)
        
        Indices.append(ind)
        
    return Indices








def Index2Point(Index, Origin, Directions, Spacings):
    """
    Convert an index (in Image Coordinate System (ICS)) to a physical point 
    (in Patient Coordinate System (PCS)).
    
    Inputs:
    ------
    
    Index : list of integers
        List (for each dimension) of the indices (in ICS) of a point, 
        e.g. [i, j, k].
        
    Origin : list of floats
        A list (for each dimension) of the 3D image origin 
        (= ImagePositionPatient of the first slice in the DICOM series), 
        e.g. [x0, y0, z0].
        
    Directions : list of floats 
        List of the direction cosines along x (rows), y (columns) and z 
        (slices) (= the cross product of the x and y direction cosines from 
        ImageOrientationPatient appended to ImageOrientationPatient),
        e.g. [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz].
        
    Spacings : list of floats 
        List (for each dimension) of the pixel spacings along x, y and z, 
        e.g. [di, dj, dk].  The x and y spacings come from PixelSpacing.  The 
        z spacing is not the SliceThickness but instead is determined from 
        ImagePositionPatient and ImageOrientationPatient.
    
        
    Ouputs:
    ------
    
    Point : list of floats
        List (for each dimension) of the coordinates of a point, 
        e.g. [x, y, z].
        
        
    Equations:
    ---------
    
    P = S + (di*i).X + (dj*j).Y + (dk*k).Z
    
    where P = (Px, Py, Pz) is the point in the Patient Coordinate System
    
          S = (Sx, Sy, Sz) is the origin in the Patient Coordinate System (i.e.
          the ImagePositionPatient)
          
          X = (Xx, Xy, Xz) is the direction cosine vector along rows (x) 
          
          Y = (Yx, Yy, Yz) is the direction cosine vector along columns (y)
          
          Z = (Zx, Zy, Zz) is the direction cosine vector along slices (z)
          
          di, dj and dk are the pixel spacings along x, y and z
          
          i, j, and k are the row (x), column (y) and slice (z) indices
    """
    
    if False: # 08/12/20
        x = Origin[0] + Index[0]*Spacings[0]*Directions[0] \
                      + Index[0]*Spacings[0]*Directions[1] \
                      + Index[0]*Spacings[0]*Directions[2] \
        
        y = Origin[1] + Index[1]*Spacings[1]*Directions[3] \
                      + Index[1]*Spacings[1]*Directions[4] \
                      + Index[1]*Spacings[1]*Directions[5] \
            
        z = Origin[2] + Index[2]*Spacings[2]*Directions[6] \
                      + Index[2]*Spacings[2]*Directions[7] \
                      + Index[2]*Spacings[2]*Directions[8] \
                  
    x = Origin[0] + Index[0]*Spacings[0]*Directions[0] \
                  + Index[1]*Spacings[1]*Directions[3] \
                  + Index[2]*Spacings[2]*Directions[6] \
    
    y = Origin[1] + Index[0]*Spacings[0]*Directions[1] \
                  + Index[1]*Spacings[1]*Directions[4] \
                  + Index[2]*Spacings[2]*Directions[7] \
        
    z = Origin[2] + Index[0]*Spacings[0]*Directions[2] \
                  + Index[1]*Spacings[1]*Directions[5] \
                  + Index[2]*Spacings[2]*Directions[8] \
        
    return [x, y, z]







def Indices2Points(Indices, Origin, Directions, Spacings):
    """
    Convert a list of indices (in Image Coordinate System (ICS)) to a list of
    physical points (in Patient Coordinate System (PCS)).
    
    Inputs:
    ------
    
    Indices : list of a list of integers
        List (for each point) of a list (for each dimension) of the indices 
        (in ICS) of Points, e.g. [[i0, j0, k0], [i1, j1, k1], ...].
        
    Origin : list of floats
        A list (for each dimension) of the 3D image origin 
        (= ImagePositionPatient of the first slice in the DICOM series), 
        e.g. [x0, y0, z0].
        
    Directions : list of floats 
        List of the direction cosines along x (rows), y (columns) and z 
        (slices) (= the cross product of the x and y direction cosines from 
        ImageOrientationPatient appended to ImageOrientationPatient),
        e.g. [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz].
        
    Spacings : list of floats 
        List (for each dimension) of the pixel spacings along x, y and z, 
        e.g. [di, dj, dk].  The x and y spacings come from PixelSpacing.  The 
        z spacing is not the SliceThickness but instead is determined from 
        ImagePositionPatient and ImageOrientationPatient.
    
        
    Ouputs:
    ------
    
    Points : list of a list of floats
        List (for each point) of a list (for each dimension) of points in the
        PCS, e.g. [[x0, y0, z0], [x1, y1, z1], ...].
    """
    
    Points = []
    
    for index in Indices:
        Points.append(Index2Point(index, Origin, Directions, Spacings))
        
    return Points









def ContourData2Points(ContourData):
    """
    Re-format a flat list of coordinates to a list of a list of [x, y, z]
    coordinates.
    
    Inputs:
    ------
    
    ContourData : list of strings
        Flat list of [x, y, z] coordinates as strings.
    
        
    Outputs:
    -------
    
    Points : list of a list of floats
        List (for each point) of a list (for each dimension) of points,
        e.g. [[x0, y0, z0], [x1, y1, z1], ...].
    """
    
    ContourData = [float(item) for item in ContourData]
    
    Points = []
            
    # Iterate for all points in threes:
    for p in range(0, len(ContourData), 3):
        point = [ContourData[p], ContourData[p+1], ContourData[p+2]]
        
        Points.append(point)
        
    return Points








def Points2ContourData(Points):
    """
    Re-format a list of points to a flat list as required for ContourData.
    
    Inputs:
    ------
    
    Points : list of a list of floats
        List (for each point) of a list (for each dimension) of points,
        e.g. [[x0, y0, z0], [x1, y1, z1], ...].
        
        
    Outputs:
    -------
    
    ContourData : list of strings
        Flat list of coordinates in Points converted from floats to strings.
    """
    
    ContourData = []
    
    for point in Points:
        point = [str(item) for item in point]
        
        ContourData.extend(point)
        
    return ContourData







def IndsByContour2PixArr(IndsByContour, RefImage):
    """
    Convert a list of indices grouped by contour to a pixel array.
       
    Adapted from https://programtalk.com/vs2/python/7636/sima/sima/ROI.py/
    
    Inputs:
    ------
    
    IndsByContour : list of lists of lists of integers
        A list (for each contour) of a list (for all polygons) of a list (for 
        each dimension) of indices.
                     
    RefImage : SimpleITK image
        Reference image whose size will be used to define the shape of the 
        pixel array.
        
        
    Outputs:
    -------
    
    PixArr : Numpy data array
        A list of 2D masks of the indices - one mask per contour.
    """
    
    import numpy as np
    from shapely.geometry import Polygon, Point
    from itertools import product
    
    ImSize = RefImage.GetSize()
    
    Ncontours = len(IndsByContour)
    
    PixArr = np.zeros((Ncontours, ImSize[1], ImSize[0]))
    
    # Note that IndsByContour are a list of indices for each contour:
    for c in range(Ncontours):
        Indices = IndsByContour[c]
        
        # Only proceed if there are at least 3 indices in this contour (the 
        # minimum number required to define a closed contour):
        if len(Indices) > 2:
            # Convert list Indices to a Shapely Polygon:
            Poly = Polygon(Indices)
                
            xMin, yMin, xMax, yMax = Poly.bounds
         
            points = [Point(x, y) for x, y in
                      product(np.arange(int(xMin), np.ceil(xMax)),
                              np.arange(int(yMin), np.ceil(yMax)))]
                      
            PointsInPoly = list(filter(Poly.contains, points))
            
            for point in PointsInPoly:
                xx, yy = point.xy
                
                x = int(xx[0])
                y = int(yy[0])
                
                if 0 <= y < ImSize[1] and 0 <= x < ImSize[0]:
                    PixArr[c, y, x] = 1
    
        
    return PixArr








def GetLabmapImsByRoi(Rts, DicomDir, CStoSliceIndsByRoi, RefIm):
    """
    Get a list of 3D labelmap (SimpleITK) images - one per ROI.  
    
    Inputs:
    ------
    
    Rts : Pydicom object
        RTS object.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
    CStoSliceIndsByRoi : list of a list of integers
        List (for each ROI) of a list (for each contour) of slice numbers that 
        correspond to each Referenced SOP instance UID in the Contour Sequence.
    
    RefIm : SimpleITK image
        The 3D image that PixArr relates to.
    
        
    Outputs:
    -------
        
    LabmapIms : List of SimpleITK images
        A list of 3D zero-padded labelmap (SimpleITK) images - one per ROI.
    """
    
    from RtsTools import GetIndsByRoi
    
    LabmapIms = []
    
    IndsByRoi = GetIndsByRoi(Rts, DicomDir)
    
    for RoiNum in range(len(IndsByRoi)):
        PixArr = IndsByContour2PixArr(IndsByContour=IndsByRoi[RoiNum], 
                                      RefImage=RefIm)
    
        LabmapIm = PixArr2Labmap(PixArr=PixArr, 
                                 NumOfSlices=RefIm.GetSize()[2], 
                                 FrameToSliceInds=CStoSliceIndsByRoi[RoiNum])
        
        LabmapIms.append(LabmapIm)
    
    return LabmapIms








def PixArr2Labmap(PixArr, NumOfSlices, FrameToSliceInds):
    """
    Convert a 3D SEG pixel array to a 3D SEG labelmap.  The labelmap will 
    contain the 2D pixel arrays at the same frame position as the slice
    position of the corresponding DICOM series (with 2D zero masks in-between).
    
    Inputs:
    ------
    
    PixArr : Numpy array
        SEG PixelData as a Numpy array.
        
    NumOfSlices : integer
        The total number of frames in the labelmap (e.g. the number of slices 
        in a image series).
        
    FrameToSliceInds : List of integers
        The DICOM slice numbers that correspond to each frame in PixArr,
        e.g. PFFGStoSliceInds = PerFrameFunctionalGroupsSequence-to-slice
        number.
        
    Outputs:
    -------
    
    Labmap : Numpy array
        Zero-padded version of PixArr.
    """
    
    import numpy as np
    
    NumOfFrames, NumOfRows, NumOfCols = PixArr.shape
    
    # Initialise Labmap:
    #Labmap = np.zeros((NumOfSlices, NumOfRows, NumOfCols), dtype='bool')
    Labmap = np.zeros((NumOfSlices, NumOfRows, NumOfCols), dtype='uint')
    
    #print(f'\nPixArr.shape = {PixArr.shape}')
    ##print(f'\n\nThe maximum value in PixArr is {PixArr.max()}')
    #print(f'FrameToSliceInds = {FrameToSliceInds}')
    #print(f'Labmap.shape = {Labmap.shape}')
    
    # Over-write all frames in Labmap with non-zero 2D masks from PixArr:
    for i in range(len(FrameToSliceInds)):
        # The slice number for the i^th frame:
        s = FrameToSliceInds[i]
        
        #print(f'\nThe slice number for the {i}^th frame is {s}')
        
        Labmap[s] = PixArr[i]
        
    
    #print(f'\n\nThe maximum value in Labmap is {Labmap.max()}')
    
    return Labmap





def PixArr2Image(PixArr, FrameToSliceInds, RefIm):
    """
    Convert a 3D pixel array to a 3D SimpleITK image.  
    
    Inputs:
    ------
    
    PixArr : Numpy array
        SEG PixelData as a Numpy array.
    
    FrameToSliceInds : List of integers
        The DICOM slice numbers that correspond to each frame in PixArr,
        e.g. PFFGStoSliceInds = PerFrameFunctionalGroupsSequence-to-slice
        number
    
    RefIm : SimpleITK image
        The 3D image that PixArr relates to.
    
        
    Outputs:
    -------
        
    LabmapIm : SimpleITK image
        A zero-padded version of PixArr.
    """
    
    import SimpleITK as sitk
    
    ImSize = RefIm.GetSize()
    
    #print(f'\nImSize = {ImSize}')
    #print(f'PixArr.shape = {PixArr.shape}')
    #print(f'ImSize[2] = {ImSize[2]}')
    #print(f'FrameToSliceInds = {FrameToSliceInds}')
    
    nda = PixArr2Labmap(PixArr, ImSize[2], FrameToSliceInds)
    
    LabmapIm = sitk.GetImageFromArray(nda)
    
    # Set the Origin, Spacing and Direction of LabmapIm to that of RefIm:
    LabmapIm.SetOrigin(RefIm.GetOrigin())
    LabmapIm.SetSpacing(RefIm.GetSpacing())
    LabmapIm.SetDirection(RefIm.GetDirection())
    
    #print(f'\n\nThe maximum value in nda is {nda.max()}')
    #print(f'\n\nThe maximum value in LabmapIm is {ImageMax(LabmapIm)}')
        
    return LabmapIm






def PixArr2ImagesBySeg(PixArr, FrameToSliceIndsBySeg, FrameNumsBySeg, RefIm):
    """
    Convert a 3D pixel array to a list of 3D SimpleITK images - one per
    segment.  
    
    Inputs:
    ------
    
    PixArr : Numpy array
        SEG PixelData as a Numpy array.
    
    FrameToSliceIndsBySeg : List of list of integers
        List of the DICOM slice numbers that correspond to each frame in PixArr 
        (e.g. PFFGStoSliceInds = PerFrameFunctionalGroupsSequence-to-slice
        number) - a list for each segment.
    
    FrameNumsBySeg : List of list of integers
        List of the frame numbers that belong to each segment - one list per
        segment.
    
    RefIm : SimpleITK image
        The 3D image that PixArr relates to.
    
        
    Outputs:
    -------
        
    LabmapIms : List of SimpleITK images
        A list of 3D zero-padded labelaps - one per segment.
    """
    
    LabmapIms = []
    
    #print(f'\nFrameToSliceIndsBySeg = {FrameToSliceIndsBySeg}\n')
    #print(f'FrameNumsBySeg = {FrameNumsBySeg}')
    
    for i in range(len(FrameNumsBySeg)):
        # The starting (= a) and ending (= b) frame numbers:
        a = FrameNumsBySeg[i][0]
        b = FrameNumsBySeg[i][-1]
        
        
        #print(f'a = {a}, b = {b}')
        #print(f'PixArr.shape = {PixArr.shape}')
        #print(f'PixArr[{a}:{b+1}].shape = {PixArr[a:b+1].shape}')
        
        LabmapIm = PixArr2Image(PixArr=PixArr[a:b+1],
                                RefIm=RefIm,
                                FrameToSliceInds=FrameToSliceIndsBySeg[i])
        
        LabmapIms.append(LabmapIm)
        
    return LabmapIms






def Image2PixArr(LabmapIm, Non0FrameInds=None):
    """
    Convert a 3D SimpleITK image to a 3D SEG pixel array.  
    
    Inputs:
    ------
    
    LabelmapIm : SimpleITK image
        A zero-padded version of PixelData.
        
    Non0FrameInds : List of integers (optional; None by default)  
        Use PerFrameFunctionalGroupsSequence-to-slice indices 
        (PFFGStoSliceInds) if they are known. If this input is not specified a 
        list of the frame numbers that are non-zero will be determined.
        
        
    Outputs:
    -------
        
    PixArr : Numpy array
        The non-zero frames in LabmapIm as a Numpy array.
                           
    Non0FrameInds : List of integers
        List of the indices of non-zero frames in LabelmapIm.  This should be
        equivalent to the PerFrameFunctionalGroupsSequence-to-slice 
        indices (PFFGStoSliceInds).
    """
    
    import SimpleITK as sitk
    import numpy as np
    
    # Convert from SimpleITK image to a Numpy array:
    Nda = sitk.GetArrayFromImage(LabmapIm)
    
    if not Non0FrameInds:
        Non0FrameInds = []
        
        #print('')
        
        # Loop through all frames in Nda and get the sum of all pixels:
        for i in range(Nda.shape[0]):
            Sum = np.amax(Nda[i])
            
            #print(f'i = {i}, Sum = {Sum}')
            
            if Sum:
                # This is a non-zero frame:
                Non0FrameInds.append(i)
    
    # Initialise PixArr:
    PixArr = np.zeros((len(Non0FrameInds), Nda.shape[1], Nda.shape[2]))
        
    # Use Non0FrameInds to index the non-zero frames in Nda:
    for i in range(len(Non0FrameInds)):
        PixArr[i] = Nda[Non0FrameInds[i]]
        
    
    return PixArr, Non0FrameInds
        










def PixArr2IndsByFrame(PixArr, FrameToSliceInds, Thresh=0.5):
    """
    Convert a 3D pixel array to a list (for each frame) of a list of indices
    that define the equivalent contour for the mask in each frame.
    
    Adapted from https://programtalk.com/vs2/python/7636/sima/sima/ROI.py/
 
    Inputs:
    ------
    
    PixArr : Numpy array
        A FxRxC (frames x rows x cols) Numpy array containing F RxC masks in 
        PixArr.
    
    FrameToSliceInds : List of list of integers
        A list (for each frame) of the slice numbers that correspond to each 
        frame in PixArr.  This is equivalent to a list of Per-Frame Functional 
        Groups Sequence-to-slice inds (PFFGStoSliceInds). 
        
    Thresh : float (optional; 0.5 by default)
        Threshold value used to binarise the labels in PixArr.
 
    
    Outputs:
    -------
    
    IndicesByFrame : list of floats
        A list (for each contour/frame) of a flat list of [x, y, z] coordinates
        of the polygons that define each frame in PixArr.
        
    PtsByCnt : list of a list of floats
        A list (for each contour/frame) of a list (for each dimension) of the 
        polygons that define each frame in PixArr.
        
    #CntToSliceInds : list of integers
    #    List of slice numbers that correspond to each contour.
    """
    
    import numpy as np
    from scipy.sparse import issparse
    from skimage.measure import find_contours
    
    IndsByFrame = []
    
    for FrameNum, Mask in enumerate(PixArr):
        if issparse(Mask):
            Mask = np.array(Mask.astype('byte').todense())
 
        if (Mask != 0).sum() == 0:
            # If Mask is empty, just skip it
            continue
 
        # Add an empty row and column at both sides of the mask to ensure that
        # any masks near the edge are found:
        ExpandedDims = (Mask.shape[0] + 2, Mask.shape[1] + 2)
        
        ExpandedMask = np.zeros(ExpandedDims, dtype=float)
        
        ExpandedMask[1:Mask.shape[0] + 1, 1:Mask.shape[1] + 1] = Mask
 
        # Get the indices that define contours in ExpandedMask:
        """
        I'm not sure how this will behave if there is more than one label (i.e.
        more than one closed mask on any given frame).  Since the returned
        item is a list of length 1, presummably a frame with multiple masks 
        will result in a list of length > 1 for each mask.  This needs to be
        tested and confirmed.
        """
        IndsByObj_2D = find_contours(ExpandedMask.T, Thresh)
        
        #print(f'\n\n\nFrameNum = {FrameNum}')
        #print(f'\nlen(IndsByObj_2D) = {len(IndsByObj_2D)}')
        #print(f'\nIndsByObj_2D = {IndsByObj_2D}')
 
        # Remove on row and column to shift the indices back to their original
        # locations:
        IndsByObj_2D = [np.subtract(x, 1).tolist() for x in IndsByObj_2D]
        
        if len(IndsByObj_2D) > 1:
            print(f'\nWarning: {len(IndsByObj_2D)} objects were found in',
                  f'frame {FrameNum} in PixArr.')
            
            print(f'\nIndsByObj_2D = {IndsByObj_2D}')
            
            """
            Consider what else needs to be done. 
            e.g.
            
            for IndsThisObj_2D in IndsByObj_2D:
                ...
            """
            
        else:
            """
            Only one object was found. Reduce the level of nested lists to one
            list of 2D indices.
            """
            Inds_2D = IndsByObj_2D[0]
        
        #print(f'\n\n\nFrameNum = {FrameNum}')
        #print(f'\nlen(Inds_2D) = {len(Inds_2D)}')
        #print(f'\nInds_2D = {Inds_2D}')
        
        SliceNum = FrameToSliceInds[FrameNum]
            
        # Add the index for the 3rd dimension:
        Inds_3D = [Ind_2D + [SliceNum] for Ind_2D in Inds_2D]
        
        #print(f'\nlen(Inds_3D) = {len(Inds_3D)}')
        #print(f'\nInds_3D = {Inds_3D}')
        
        IndsByFrame.append(Inds_3D)
        
        
    #print(f'\n\n\n\nlen(IndsByFrame) = {len(IndsByFrame)}')
    #print(f'\nIndsByFrame = {IndsByFrame}')
 
    return IndsByFrame








def PixArr2PtsByContour(PixArr, FrameToSliceInds, DicomDir, Thresh=0.5):
    """
    Convert a 3D pixel array to a list (for each frame/contour) of a list (for 
    each point) of a list (for each dimension) of physical coordinates.
 
    Inputs:
    ------
    
    PixArr : Numpy array
        A FxRxC (frames x rows x cols) Numpy array containing F RxC masks in 
        PixArr.
    
    FrameToSliceInds : List of list of integers
        A list (for each frame) of the slice numbers that correspond to each 
        frame in PixArr.  This is equivalent to a list of Per-Frame Functional 
        Groups Sequence-to-slice inds (PFFGStoSliceInds). 
    
    DicomDir : string
        Directory containing the DICOMs that relate to PixArr.
        
    Thresh : float (optional; 0.5 by default)
        Threshold value used to binarise the labels in PixArr.
 
    
    Outputs:
    -------
    
    PtsByCnt : list of a list of floats
        A list (for each contour/frame) of a list (for each dimension) of the 
        physical coordinates that define the mask in each frame in PixArr.
        
    CntDataByCnt : list of a list of strings
        A list (for each contour/frame) of a flattened list of [x, y, z]
        physical coordinates that define the mask in each frame in PixArr as
        strings (format of ContourData tag in RTS).
    """
    
    from ImageTools import GetImageAttributes
    
    # Convert the pixel array to a list of indices-by-frame:
    IndsByFrame = PixArr2IndsByFrame(PixArr, FrameToSliceInds, Thresh=0.5)
    
    Size, Spacings, ST,\
    IPPs, Dirs = GetImageAttributes(DicomDir, Package='pydicom')
    
    PtsByCnt = []
    CntDataByCnt = []
    
    for Inds in IndsByFrame:
        Pts = Indices2Points(Indices=Inds, Origin=IPPs[0], Directions=Dirs, 
                             Spacings=Spacings)
        
        PtsByCnt.append(Pts)
        
        CntDataByCnt.append(Points2ContourData(Points=Pts))
    
    
    #print(f'\n\n\nlen(PtsByCnt) = {len(PtsByCnt)}')
    #print(f'\nlen(CntDataByCnt) = {len(CntDataByCnt)}')
    #print(f'\nPtsByCnt = {PtsByCnt}')
    #print(f'\nCntDataByCnt = {CntDataByCnt}')
 
    return PtsByCnt, CntDataByCnt











def Indices2Mask(Inds, RefImage):
    """
    Convert a list of indices to a (filled) mask (pixel array).
       
    Adapted from https://programtalk.com/vs2/python/7636/sima/sima/ROI.py/
    
    Inputs:
    ------
    
    Inds : list of a list of integers
        A list (for all points) of a list (for each dimension) of indices.
                     
    RefImage : SimpleITK image
        Reference image whose size will be used to define the shape of the 
        pixel array.
        
        
    Outputs:
    -------
    
    Mask : Numpy data array
        A 2D mask of the indices.
    """
    
    import numpy as np
    from itertools import product
    from shapely.geometry import Polygon, Point
    
    # Only proceed if there are at least 3 indices in this contour (the 
    # minimum number required to define a closed contour):
    if len(Inds) < 3:
        raise Exception(f"There are only {len(Inds)} indices. A minimum of ",
                        "3 are required to define a closed contour.")
        
    
    C, R, S = RefImage.GetSize()
    
    Mask = np.zeros((1, R, C))
    
    #print(f'\nMask.shape = {Mask.shape}')
    
    # Convert Inds to a Shapely Polygon:
    Poly = Polygon(Inds)
        
    xMin, yMin, xMax, yMax = Poly.bounds
 
    points = [Point(x, y) for x, y in 
              product(np.arange(int(xMin), np.ceil(xMax)),
                      np.arange(int(yMin), np.ceil(yMax)))]
              
    PointsInPoly = list(filter(Poly.contains, points))
    
    for point in PointsInPoly:
        xx, yy = point.xy
        
        x = int(xx[0])
        y = int(yy[0])
        
        if 0 <= y < R and 0 <= x < C:
            #print(f'\n   Mask.shape = {Mask.shape}')
            
            Mask[0, y, x] = 1
    
        
    return Mask






def ConvertImagePixelType(Image, NewPixelType):
    """
    Convert a 3D SimpleITK image to a new pixel type.
    
    Inputs:
    ------                      
        
    Image : SimpleITK image
        The 3D image whose pixel type is to be converted.
        
    NewPixelType : string
        The pixel type to convert Image to.  Acceptable inputs are a subset of
        the SimpleITK pixel types 
        (https://simpleitk.org/SimpleITK-Notebooks/01_Image_Basics.html):
            
        - 'sitkUInt32' 	Unsigned 32 bit integer
        - 'sitkFloat32' 	32 bit float

    
    
    Outputs:
    -------
    
    Image : SimpleITK image
        The 3D image with modified pixel type.

    
    Note:
    ----
        While a linear (or BSpline) interpolator is appropriate for intensity 
        images, only a NearestNeighbor interpolator is appropriate for binary 
        images (e.g. segmentations) so that no new labels are introduced.
    """
    
    import SimpleITK as sitk
    
    if NewPixelType == 'sitkUInt32':
        OutputPixelType = sitk.sitkUInt32
        
    elif NewPixelType == 'sitkFloat32':
        OutputPixelType = sitk.sitkFloat32
    
    else:
        msg = '"NewPixelType" must be either "sitkUInt32" or "sitkFloat32".'
        
        raise Exception(msg)
        
    
    Caster = sitk.CastImageFilter()
    
    Caster.SetOutputPixelType(OutputPixelType)
    
    Image = Caster.Execute(Image)
    
    return Image
    