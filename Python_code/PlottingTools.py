# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 11:52:36 2020

@author: ctorti
"""



# Import packages and functions:
#import os
#import time
#from pydicom import dcmread
#import SimpleITK as sitk
#import numpy as np
#import matplotlib.pyplot as plt

##import importlib
##import GeneralTools
##importlib.reload(GeneralTools)
#from GeneralTools import Unpack

#from ConversionTools import GetIndsInRois
#from ConversionTools import ConvertContourDataToIcsPoints

#from DicomTools import ImportDicoms
#from DicomTools import GetDicomSOPuids
#from DicomTools import GetRoiLabels

#from ImageTools import InitialiseImage
#from ImageTools import AddImages
#from ImageTools import SumAllLabmapIms

#from RtsTools import GetCIStoSliceInds
#from RtsTools import GetCStoSliceInds

#from SegTools import GetPFFGStoSliceInds



"""
******************************************************************************
******************************************************************************
PLOTTING FUNCTIONS
******************************************************************************
******************************************************************************
"""       





def PlotImagesAndContours(Image, ImageType, DicomDir, RtsFpath,
                          ExportPlot, ExportDir, Label='', dpi=80,
                          LogToConsole=False):
    """
    Image can either be a 3D DICOM image, or 3D labelmap, or a list of 3D 
    labelmaps.
    """
    
    import SimpleITK as sitk
    from pydicom import dcmread
    import matplotlib.pyplot as plt
    from ConversionTools import GetIndsInRois
    from DicomTools import GetDicomSOPuids
    from RtsTools import GetCStoSliceInds
    from DicomTools import GetRoiLabels
    from ConversionTools import ConvertContourDataToIndices
    from GeneralTools import Unpack
    import time
    import os
    
    # Convert Image to a list of Numpy arrays (even if only one 3D 
    # DICOM/labelmap):
    Ndas = []
    
    if isinstance(Image, list):
        for r in range(len(Image)):
            Ndas.append(sitk.GetArrayFromImage(Image[r]))
            
    elif isinstance(Image, sitk.SimpleITK.Image):
        Ndas.append(sitk.GetArrayFromImage(Image))
        
    else:
        msg = "Image is type " + str(type(Image)) + ". It must either be a " \
              + "SimpleITK Image or a list of SimpleITK Images"
                        
        raise Exception(msg)
    
    # Import the RTS object:
    Rts = dcmread(RtsFpath)
    
    
    IndsInRois = GetIndsInRois(RtsFpath, DicomDir)
    
    Nrois = len(IndsInRois)
    
    
    ContourToSliceNumsByRoi = GetCStoSliceInds(Rts, GetDicomSOPuids(DicomDir))
    
    print(f'ContourToSliceNumsByRoi = {ContourToSliceNumsByRoi}')
    
    # The slices to plot are all slice numbers in ContourToSliceNums and all
    # non-zero masks in Image if ImageType is 'Labelmap':
    #SliceNums = []
    #SliceNums.extend(ContourToSliceNums)
    
    # Get all the slice numbers in ContourToSliceNumsByRoi:
    SliceNums = []
    
    for nums in ContourToSliceNumsByRoi:
        SliceNums.extend(nums)
        
    # If ImageType is 'Labelmap' append the slice numbers of any non-zero 
    # frames:
    
    if ImageType in ['Labelmap', 'labelmap', 'LabelMap']:
        Non0inds = []
        
        for r in range(len(Ndas)):
            # Get the indices of non-zero arrays in Ndas[r]: 
            for i in range(Ndas[r].shape[0]):
                if Ndas[r][i].sum() > 0:
                    Non0inds.append(i)
            
            #Nnon0s = len(Non0inds)
            
            SliceNums.extend(Non0inds)
        
        print(f'Non0inds = {Non0inds}')
        
    
    # Get the list of unique slice numbers:
    SliceNums = list(set(SliceNums))
    
    print(f'SliceNums = {SliceNums}')
    
    #Nslices = len(SliceNums)
    
    # Set the number of subplot rows and columns:
    #Ncols = np.int8(np.ceil(np.sqrt(Nnon0s)))
    Ncols = Nrois
    
    # Limit the number of rows to 5 otherwise it's difficult to make sense of
    # the images:
    #if Ncols > 5:
    #    Ncols = 5
    
    #Nrows = np.int8(np.ceil(Nnon0s/Ncols))
    Nrows = len(SliceNums)
    
    # Create a figure with two subplots and the specified size:
    if ExportPlot:
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows), dpi=300)
        fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7*Nrows), dpi=300)
    else:
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows))
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows))
        #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15*Ncols, 6*Nrows), dpi=dpi)
        fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7*Nrows), dpi=dpi)
        
    
    n = 0 # sub-plot number
    
    # List of colours for multiple ROIs per slice (limited to 5 for now):
    colours = ['r', 'c', 'm', 'y', 'g']
    
    # Get ROI labels:
    RoiLabels = GetRoiLabels(Rts)
    
    # Loop through each slice number in SliceNums: 
    for s in SliceNums:
        
        if LogToConsole:
                print('\ns =', s)
                
        
        # Only plot if Nda[s] is not empty (i.e. if it is a DICOM 2D image or
        # a non-empty mask):
        #if Nda[s].sum() > 0:
        
        #n += 1 # increment sub-plot number
        
        ##plt.subplot(Nrows, Ncols, n)
        ##plt.axis('off')
        #ax = plt.subplot(Nrows, Ncols, n)

        #ax = plt.subplot(Nrows, Ncols, n, aspect=AR)
          
        # Plot the image:
        #ax.imshow(Nda[s], cmap=plt.cm.Greys_r)
        ##ax.set_aspect(ar)
        
        
        # Loop through all ROIs:
        for r in range(Nrois):
            n += 1 # increment sub-plot number
            
            ax = plt.subplot(Nrows, Ncols, n)
            
            # Plot the image:
            if len(Ndas) > 1:
                ax.imshow(Ndas[r][s], cmap=plt.cm.Greys_r)
                
            else:
                ax.imshow(Ndas[0][s], cmap=plt.cm.Greys_r)
            
            
            ContourToSliceNums = ContourToSliceNumsByRoi[r]
            
            # Does this slice have a contour?
            if s in ContourToSliceNums:
                #ind = ContourToSliceNums.index(s)
                
                # Find all occurances of slice s in ContourToSliceNums:
                inds = [i for i, val in enumerate(ContourToSliceNums) if val==s]
                
                for i in range(len(inds)):
                    if ImageType in ['DICOM', 'Dicom', 'dicom']:
                        Points = IndsInRois[r][inds[i]]
                        
                        # Convert contour data from Patient Coordinate System to  
                        # Image Coordinate System:
                        Indices = ConvertContourDataToIndices(Points, DicomDir)
                        
                    else:
                        # ImageType in ['Labelmap', 'labelmap']
                        Indices = IndsInRois[r][inds[i]]
                    
                    
                    # Unpack the indices:
                    X, Y, Z = Unpack(Indices)
                    
                    # Plot the contour points:
                    plt.plot(X, Y, linewidth=0.5, c=colours[i]);
                    
                ax.set_title(f'Slice {s} \n' + RoiLabels[r])
                
            else:
                ax.set_title(f'Slice {s}')
                
            
            
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            
            #ax.set_title(f'Slice {s}')
            #plt.axis('off')
        
            
            
    if ExportPlot:
        CDT = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        
        ExportFname = CDT + '_' + ImageType + '_' + Label
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
        
    #print(f'PixAR = {PixAR}')
    #print(f'AxisAR = {AxisAR}')
        
    return





def PlotDicomsAndSegments(DicomDir, SegFpath, ExportPlot, ExportDir, 
                          LogToConsole):
    
    from pydicom import dcmread
    import numpy as np
    import os
    import matplotlib.pyplot as plt
    from DicomTools import ImportDicoms
    from DicomTools import GetDicomSOPuids
    from SegTools import GetPFFGStoSliceInds
    
    # Import the DICOMs:
    Dicoms = ImportDicoms(DicomDir=DicomDir)
    
    # Get the DICOM SOP UIDs:
    SOPuids = GetDicomSOPuids(DicomDir=DicomDir)
    
    # Import the SEG ROI:
    SegRoi = dcmread(SegFpath)
    
    # Get the Per-frameFunctionalGroupsSequence-to-slice indices:
    PFFGStoSliceInds = GetPFFGStoSliceInds(SegRoi, SOPuids)
    
    # The 3D labelmap:
    SegNpa = SegRoi.pixel_array
    
    if LogToConsole:
        print(f'Segments exist on slices {PFFGStoSliceInds}')
        print(f'Shape of PixelData = {SegNpa.shape}\n')

    
    
    # Prepare the figure.
    
    # All DICOM slices that have segmentations will be plotted. The number of
    # slices to plot (= number of segments):
    #Nslices = int(SegRoi.NumberOfFrames)
    Nslices = len(PFFGStoSliceInds)
    
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
        s = PFFGStoSliceInds[i]
        
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






def Plot_Src_ResSrc_Trg_Images(SrcIm, ResSrcIm, TrgIm, SrcLabel, TrgLabel, 
                               Case, ImageType, ExportPlot, ExportDir, 
                               LogToConsole=False, dpi=80):
    
    """ 
    SrcIm/ResSrcIm/TrgIm could either be a SimpleITK image,
    i.e. type(SrcIm).__name__ == 'Image', or a list of SimpleITK images,
    i.e. type(SrcIm).__name__ == 'list'.
    
    e.g. SrcIm can be a list of sitk images of the labelmaps for each of 
    multiple ROIs.
    """
    
    import SimpleITK as sitk
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    import time
    
    # If ___Im is an Image (i.e. not a list), redefine it as a list with one 
    # item:  
    if type(SrcIm).__name__ == 'Image':
        SrcIm = [SrcIm]
        
    if type(ResSrcIm).__name__ == 'Image':
        ResSrcIm = [ResSrcIm]
        
    if type(TrgIm).__name__ == 'Image':
        TrgIm = [TrgIm]
        
        
    if Case == '5':
        ResOrReg = 'Registered'
        ResOrReg_short = '_Reg'
        #print('\nCase = 5 -->', ResOrReg)
    else:
        ResOrReg = 'Resampled'
        ResOrReg_short = '_Resamp'
        
    
    if LogToConsole:
        print('\nThe Source and Target image size:\n',
                      f'\n   Original Source:  {SrcIm[0].GetSize()} \n',
                      '\n  ', ResOrReg, f'Source: {ResSrcIm[0].GetSize()} \n',
                      f'\n   Target:           {TrgIm[0].GetSize()}')
            
        print('\nThe Source and Target voxel spacings:\n',
                      f'\n   Original Source:  {SrcIm[0].GetSpacing()} \n',
                      '\n  ', ResOrReg, f'Source: {ResSrcIm[0].GetSpacing()} \n',
                      f'\n   Target:           {TrgIm[0].GetSpacing()}')
            
        print('\nThe Source and Target Origin:\n',
                      f'\n   Original Source:  {SrcIm[0].GetOrigin()} \n',
                      '\n  ', ResOrReg, f'Source: {ResSrcIm[0].GetOrigin()} \n',
                      f'\n   Target:           {TrgIm[0].GetOrigin()}')
            
        print('\nThe Source and Target Direction:\n',
                      f'\n   Original Source:  {SrcIm[0].GetDirection()} \n',
                      '\n  ', ResOrReg, f'Source: {ResSrcIm[0].GetDirection()} \n',
                      f'\n   Target:           {TrgIm[0].GetDirection()}')

    
    # Convert from SimpleITK image to Numpy arrays, assigning different values
    # for each ROI (i.e. 1, 2, 3, ...):
    SrcNpas = []
    ResSrcNpas = []
    TrgNpas = []
    
    # Loop through all ROIs:
    for r in range(len(SrcIm)):
        SrcNpas.append(sitk.GetArrayFromImage(SrcIm[r]))
        #SrcNpas.append((r + 1)*sitk.GetArrayFromImage(SrcIm[r]))
        
    for r in range(len(ResSrcIm)):
        ResSrcNpas.append(sitk.GetArrayFromImage(ResSrcIm[r]))
        #ResSrcNpas.append((r + 1)*sitk.GetArrayFromImage(ResSrcIm[r]))
        
    for r in range(len(TrgIm)):
        TrgNpas.append(sitk.GetArrayFromImage(TrgIm[r]))
        #TrgNpas.append((r + 1)*sitk.GetArrayFromImage(TrgIm[r]))
            
    
    # Find the maxima for all labelmaps:
    if 'Labelmaps' in ImageType:
        maxima = []
        
        for r in range(len(SrcNpas)):
            maxima.append(np.amax(SrcNpas[r]))
            
        for r in range(len(ResSrcNpas)):
            maxima.append(np.amax(ResSrcNpas[r]))
            
        for r in range(len(TrgNpas)):
            maxima.append(np.amax(TrgNpas[r]))
        
        MaxVal = max(maxima)

    
    # Prepare the figure:
    #Nslices = max(SrcIm.GetSize()[2], TrgIm.GetSize()[2])
    SrcNslices = SrcNpas[0].shape[0]
    ResSrcNslices = ResSrcNpas[0].shape[0]
    TrgNslices = TrgNpas[0].shape[0]
    Nslices = max(SrcNslices, TrgNslices)
    
    # Set the number of subplot rows and columns:
    Ncols = 3
    
    Nrows = Nslices
    
    
    # Create a figure with two subplots and the specified size:
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows))
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Define the colourmaps to use for each ROI:
    #cmaps = [plt.cm.spring, plt.cm.cool, plt.cm.autumn, plt.cm.winter, 
    #         plt.cm.hsv, plt.cm.jet]
    
    # Loop through each slice: 
    for s in range(Nslices):
         
        # Plot the Original Source slice:
        if s < SrcNslices:
            ax = plt.subplot(Nrows, Ncols, n)
            
            # Loop through all ROIs:
            #maxima = []
            for r in range(len(SrcNpas)):
                im = ax.imshow(SrcNpas[r][s], cmap=plt.cm.Greys_r)
                #im = ax.imshow(SrcNpas[r][s], cmap=cmaps[r])
                #maxima.append(np.amax(SrcNpas[r][s]))
                
            if 'Labelmaps' in ImageType:
                cbar = fig.colorbar(im, ax=ax)
                cbar.mappable.set_clim(0, MaxVal)
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'Original Source ({SrcLabel}) slice {s}')
            
        n += 1 # increment sub-plot number
            
        # Plot the Resampled Source slice:
        if s < ResSrcNslices:
            ax = plt.subplot(Nrows, Ncols, n)
            
            #maxima = []
            for r in range(len(ResSrcNpas)):
                im = ax.imshow(ResSrcNpas[r][s], cmap=plt.cm.Greys_r)
                #im = ax.imshow(ResSrcNpas[r][s], cmap=cmaps[r])
                #maxima.append(np.amax(ResSrcNpas[r][s]))
                
            if 'Labelmaps' in ImageType:
                cbar = fig.colorbar(im, ax=ax)
                cbar.mappable.set_clim(0, MaxVal)
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(ResOrReg + f' Source ({SrcLabel}) slice {s}')
            
        n += 1 # increment sub-plot number
        
        # Plot the Target slice:
        if s < TrgNslices:
            ax = plt.subplot(Nrows, Ncols, n)
            
            #maxima = []
            for r in range(len(TrgNpas)):
                im = ax.imshow(TrgNpas[r][s], cmap=plt.cm.Greys_r)
                #im = ax.imshow(TrgNpas[r][s], cmap=cmaps[r])
                #maxima.append(np.amax(TrgNpas[r][s]))
                
            if 'Labelmaps' in ImageType:
                cbar = fig.colorbar(im, ax=ax)
                cbar.mappable.set_clim(0, MaxVal)
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'Target ({TrgLabel}) slice {s}')
            
        n += 1 # increment sub-plot number
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
                      
        ExportFname = CurrentDateTime + '_Case' + Case + '_Orig' + SrcLabel \
                      + ResOrReg_short + SrcLabel + '_' + TrgLabel + '_' \
                      + ImageType + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return





def Plot_Src_ResSrc_Trg_NewTrg_Images(SrcIm, ResSrcIm, TrgIm, 
                                      SrcLMIms, ResSrcLMIms, 
                                      TrgLMIms, NewTrgLMIms,
                                      SrcLabel, TrgLabel, Case,
                                      ImageType, ExportPlot, ExportDir, 
                                      LogToConsole=False, dpi=80):
    """ 
    Note:
    
    ResSrcIm = Resampled Source image could instead be a Registered Source
    image.
    
    
    ___Im is a 3D SimpleITK image from DICOMs.
    
    ___LMIms is either be a 3D labelmap as a SimpleITK image, or a list
    of 3D labelmaps as a SimpleITK image for each segment for ___Im.
    
    i.e. type(___LMIms).__name__ == 'Image', or
    i.e. type(___LMIms).__name__ == 'list'.
    
    """
    
    if Case == '5':
        ResOrReg = 'Registered'
        ResOrReg_short = '_Reg'
        #print('\nCase = 5 -->', ResOrReg)
    else:
        ResOrReg = 'Resampled'
        ResOrReg_short = '_Resamp'
        #print('\nCase != 5 -->', ResOrReg)
    
    if LogToConsole:
        print('\nThe Source and Target image size:\n',
                      f'   Original Source:  {SrcIm.GetSize()} \n',
                      '  ', ResOrReg, f'Source: {ResSrcIm.GetSize()} \n',
                      f'   Original Target:  {TrgIm.GetSize()}')#,
                      #f'   New Target:       {NewTrgIm[0].GetSize()}')
            
        print('\nThe Source and Target voxel spacings:\n',
                      f'   Original Source:  {SrcIm.GetSpacing()} \n',
                      '  ', ResOrReg, f'Source: {ResSrcIm.GetSpacing()} \n',
                      f'   Original Target:  {TrgIm.GetSpacing()}')#,
                      #f'   New Target:       {NewTrgIm[0].GetSpacing()}')
        
        """
        print('\nThe Source and Target Origin:\n',
                      f'   Original Source:  {SrcIm.GetOrigin()} \n',
                      f'   Resampled Source: {ResSrcIm.GetOrigin()} \n',
                      f'   Original Target:  {TrgIm.GetOrigin()}')#,
                      #f'   New Target:       {NewTrgIm[0].GetOrigin()}')
            
        print('\nThe Source and Target Direction:\n',
                      f'   Original Source:  {SrcIm.GetDirection()} \n',
                      f'   Resampled Source: {ResSrcIm.GetDirection()} \n',
                      f'   Original Target:  {TrgIm.GetDirection()}')#,
                      #f'   New Target:       {NewTrgIm[0].GetDirection()}')
        """
    
    
    import SimpleITK as sitk
    import numpy as np
    import matplotlib.pyplot as plt
    from ImageTools import SumAllLabmapIms
    import os
    import time
    
    if 'Images' in ImageType:
        # Convert from sitk to numpy array:
        SrcImNpa = sitk.GetArrayFromImage(SrcIm)
        ResSrcImNpa = sitk.GetArrayFromImage(ResSrcIm)
        TrgImNpa = sitk.GetArrayFromImage(TrgIm)
        
        
        
    
    if 'Labelmaps' in ImageType:
        # If ___Im is an Image (i.e. not a list), redefine it as a list with  
        # one item:  
        if SrcLMIms:
            if type(SrcLMIms).__name__ == 'Image':
                SrcLMIms = [SrcLMIms]
            
            if LogToConsole:
                print(f'\nScrIm has {len(SrcLMIms)} segments')
        
            # Add all segments pixel-by-pixel:
            SrcLMImsSumNpa = SumAllLabmapIms(SrcLMIms)
            
            SrcNslices = SrcLMImsSumNpa.shape[0]
    
    
            
        if ResSrcLMIms:
            if type(ResSrcLMIms).__name__ == 'Image':
                ResSrcLMIms = [ResSrcLMIms]
            
            if LogToConsole:
                print(f'ResScrIm has {len(ResSrcLMIms)} segments')
                
            # Add all segments pixel-by-pixel:
            ResSrcLMImsSumNpa = SumAllLabmapIms(ResSrcLMIms)
            
            ResSrcNslices = ResSrcLMImsSumNpa.shape[0]
        
        
            
        if TrgLMIms:
            if type(TrgLMIms).__name__ == 'Image':
                TrgLMIms = [TrgLMIms]
            
            if LogToConsole:
                print(f'TrgIm has {len(TrgLMIms)} segments')
                
            # Add all segments pixel-by-pixel:
            TrgLMImsSumNpa = SumAllLabmapIms(TrgLMIms)
            
            TrgNslices = TrgLMImsSumNpa.shape[0]
        
        
            
        if NewTrgLMIms:
            if type(NewTrgLMIms).__name__ == 'Image':
                NewTrgLMIms = [NewTrgLMIms]
        
            if LogToConsole:
                print(f'NewTrgIm has {len(NewTrgLMIms)} segments')
                
            # Add all segments pixel-by-pixel:
            NewTrgLMImsSumNpa = SumAllLabmapIms(NewTrgLMIms)
            
            NewTrgNslices = NewTrgLMImsSumNpa.shape[0]
            
            # Convert only the last segment (last labelmap image):
            NewTrgOnlyNewLM = sitk.GetArrayFromImage(NewTrgLMIms[-1])
            
            
        print('\nThe Source and Target labelmap image size:\n',
              f'   Original Source:  {SrcLMIms[0].GetSize()} \n',
              ResOrReg, f'Source: {ResSrcLMIms[0].GetSize()} \n',
              f'   Original Target:  {TrgLMIms[0].GetSize()}')
            
            
    else:
        SrcNslices = SrcIm.GetSize()[2]
        ResSrcNslices = ResSrcIm.GetSize()[2]
        TrgNslices = TrgIm.GetSize()[2]
        NewTrgNslices = TrgNslices
    
    
    
    Nslices = max(SrcNslices, TrgNslices)

    
    # Get the maxima for all slices for all labelmaps along x (axis=2) and
    # y (axis=1):
    if 'Labelmaps' in ImageType:
        SrcMaximaBySlice = np.amax(SrcLMImsSumNpa, axis=(1,2))
        
        ResSrcMaximaBySlice = np.amax(ResSrcLMImsSumNpa, axis=(1,2))
            
        TrgMaximaBySlice = np.amax(TrgLMImsSumNpa, axis=(1,2))
        
        NewTrgMaximaBySlice = np.amax(NewTrgLMImsSumNpa, axis=(1,2))
        
        NewTrgOnlyNewLmMaximaBySlice = np.amax(NewTrgOnlyNewLM, axis=(1,2))
           
        if LogToConsole:
            print(f'\nSrcMaximaBySlice   = {SrcMaximaBySlice}')
            print(f'ResSrcMaximaBySlice = {ResSrcMaximaBySlice}')
            print(f'TrgMaximaBySlice    = {TrgMaximaBySlice}')
            print(f'NewTrgMaximaBySlice = {NewTrgMaximaBySlice}')
            print(f'NewTrgOnlyNewLmMaximaBySlice = {NewTrgOnlyNewLmMaximaBySlice}')
        
        
        #AllMaxima = [max(SrcMaximaBySlice), max(ResSrcMaximaBySlice),
        #             max(TrgMaximaBySlice), max(NewTrgMaximaBySlice)]
            
        
        # Determine which slices have at least one non-zero labelmap across all
        # labelmaps:
        SumOfMaximaBySlice = []
        
        for s in range(Nslices):
            count = 0
            
            if s < SrcNslices:
                count += SrcMaximaBySlice[s]
                
            if s < ResSrcNslices:
                count += ResSrcMaximaBySlice[s]
                
            if s < TrgNslices:
                count += TrgMaximaBySlice[s]
                
            if s < NewTrgNslices:
                count += NewTrgMaximaBySlice[s]
                
            SumOfMaximaBySlice.append(count)
        
        
        #print(f'\nSumOfMaximaBySlice = {SumOfMaximaBySlice}')
        
    
    # Prepare the figure.
    
    # Set the number of subplot rows and columns:
    #Ncols = 4
    Ncols = 5 # 19/11: Add New Target new segment only in 5th column
    
    if 'Labelmaps' in ImageType:
        NonZeroSlices = np.nonzero(SumOfMaximaBySlice)
        SliceNums = NonZeroSlices[0]
        
        #print(f'\nNonZeroSlices = {NonZeroSlices}')
        
        #Nrows = np.count_nonzero(np.array(SumOfMaximaBySlice))
        Nrows = len(SliceNums)
    else:
        SliceNums = list(range(Nslices))
        
        Nrows = Nslices
        
    
    #if ExportPlot:
    #    dpi = 120
    
    
    # Create a figure with two subplots and the specified size:
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(15, 9*Nrows))
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    alpha = 0.2
    alpha = 0.5
    
    # Define the colormap to use for labelmaps overlaid over DICOMs:
    #cmap = plt.cm.Reds
    #cmap = plt.cm.cool
    #cmap = plt.cm.hsv
    cmap = plt.cm.nipy_spectral
    
    
    # Loop through each SliceNums: 
    for s in SliceNums:
        #print(f's = {s}')
        
        # Only proceed if labelmaps are not to be displayed or (if they are) at 
        # least one of the labelmaps is non-zero for this slice number:
        if not 'Labelmaps' in ImageType or SumOfMaximaBySlice[s]:
            
            if s < SrcNslices:
                ax = plt.subplot(Nrows, Ncols, n)
                
                if 'Images' in ImageType:
                    # Plot the Original Source DICOM image:
                    im = ax.imshow(SrcImNpa[s], cmap=plt.cm.Greys_r)
                    
                    if 'Labelmaps' in ImageType:
                        # Plot the labelmap with tranparency:
                        im = ax.imshow(SrcLMImsSumNpa[s], cmap=cmap,
                                       alpha=alpha)
                        
                        m = 1 if SrcMaximaBySlice[s] < 1 else SrcMaximaBySlice[s]
                        cbar = fig.colorbar(im, ax=ax)
                        cbar.mappable.set_clim(0, m)
                    
                elif 'Labelmaps' in ImageType:
                    # Plot the labelmap only:
                    im = ax.imshow(SrcLMImsSumNpa[s], cmap=plt.cm.Greys_r)
                    
                    m = 1 if SrcMaximaBySlice[s] < 1 else SrcMaximaBySlice[s]
                    cbar = fig.colorbar(im, ax=ax)
                    cbar.mappable.set_clim(0, m)
                        
                ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                if len(SrcLMIms) == 1:
                    ax.set_title(f'Original Source ({SrcLabel}) slice {s}'\
                                 + '\n(only segmentation to be copied)')
                else:
                    ax.set_title(f'Original Source ({SrcLabel}) slice {s}'\
                                 + '\n(sum of all segments)')
                 
                
            n += 1 # increment sub-plot number
            
            if s < ResSrcNslices:
                ax = plt.subplot(Nrows, Ncols, n)
                
                if 'Images' in ImageType:
                    # Plot the Resampled Source DICOM image:
                    im = ax.imshow(ResSrcImNpa[s], cmap=plt.cm.Greys_r)
                    
                    if 'Labelmaps' in ImageType:
                        im = ax.imshow(ResSrcLMImsSumNpa[s], cmap=cmap,
                                       alpha=alpha)
                        
                        m = 1 if ResSrcMaximaBySlice[s] < 1 else ResSrcMaximaBySlice[s]
                        cbar = fig.colorbar(im, ax=ax)
                        cbar.mappable.set_clim(0, m)
                    
                elif 'Labelmaps' in ImageType:
                    im = ax.imshow(ResSrcLMImsSumNpa[s], cmap=plt.cm.Greys_r)
                    
                    m = 1 if ResSrcMaximaBySlice[s] < 1 else ResSrcMaximaBySlice[s]
                    cbar = fig.colorbar(im, ax=ax)
                    cbar.mappable.set_clim(0, m)
                        
                ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                if len(ResSrcLMIms) == 1:
                    ax.set_title(ResOrReg + f' Source ({SrcLabel}) slice {s}'\
                                 + '\n(only segmentation to be copied)')
                else:
                    ax.set_title(ResOrReg + f' Source ({SrcLabel}) slice {s}'\
                                 + '\n(sum of all segments)')
                
                
            n += 1 # increment sub-plot number
                
            if s < TrgNslices:
                ax = plt.subplot(Nrows, Ncols, n)
               
                if 'Images' in ImageType:
                    # Plot the Target slice:
                    im = ax.imshow(TrgImNpa[s], cmap=plt.cm.Greys_r)
                    
                    if 'Labelmaps' in ImageType:
                        im = ax.imshow(TrgLMImsSumNpa[s], cmap=cmap,
                                       alpha=alpha)
                        
                        m = 1 if TrgMaximaBySlice[s] < 1 else TrgMaximaBySlice[s]
                        cbar = fig.colorbar(im, ax=ax)
                        cbar.mappable.set_clim(0, m)
                    
                elif 'Labelmaps' in ImageType:
                    im = ax.imshow(TrgLMImsSumNpa[s], cmap=plt.cm.Greys_r)
                    
                    m = 1 if TrgMaximaBySlice[s] < 1 else TrgMaximaBySlice[s]
                    cbar = fig.colorbar(im, ax=ax)
                    cbar.mappable.set_clim(0, m)
                    
                ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                ax.set_title(f'Original Target ({TrgLabel}) slice {s}'\
                             + '\n(sum of all segments)')
                
            n += 1 # increment sub-plot number
                
            
            if s < NewTrgNslices:
                ax = plt.subplot(Nrows, Ncols, n)
                    
                if 'Images' in ImageType:      
                    # Plot the New Target slice:
                    im = ax.imshow(TrgImNpa[s], cmap=plt.cm.Greys_r)
                    
                    if 'Labelmaps' in ImageType:
                        im = ax.imshow(NewTrgLMImsSumNpa[s], cmap=cmap,
                                       alpha=alpha)
                        
                        m = 1 if NewTrgMaximaBySlice[s] < 1 else NewTrgMaximaBySlice[s]
                        cbar = fig.colorbar(im, ax=ax)
                        cbar.mappable.set_clim(0, m)
                    
                elif 'Labelmaps' in ImageType:
                    im = ax.imshow(NewTrgLMImsSumNpa[s], cmap=plt.cm.Greys_r)
                    
                    m = 1 if NewTrgMaximaBySlice[s] < 1 else NewTrgMaximaBySlice[s]
                    cbar = fig.colorbar(im, ax=ax)
                    cbar.mappable.set_clim(0, m)
                    
                ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                ax.set_title(f'New Target ({TrgLabel}) slice {s}'\
                             + '\n(sum of all segments)')
                
            n += 1 # increment sub-plot number
            
                
            
            if s < NewTrgNslices:
                # Plot the new segment of New Target only:
                ax = plt.subplot(Nrows, Ncols, n)
                    
                if 'Images' in ImageType:      
                    # Plot the New Target slice:
                    im = ax.imshow(TrgImNpa[s], cmap=plt.cm.Greys_r)
                    
                    if 'Labelmaps' in ImageType:
                        im = ax.imshow(NewTrgOnlyNewLM[s], cmap=cmap,
                                       alpha=alpha)
                        
                        m = 1 if NewTrgMaximaBySlice[s] < 1 else NewTrgMaximaBySlice[s]
                        cbar = fig.colorbar(im, ax=ax)
                        cbar.mappable.set_clim(0, m)
                    
                elif 'Labelmaps' in ImageType:
                    im = ax.imshow(NewTrgOnlyNewLM[s], cmap=plt.cm.Greys_r)
                    
                    m = 1 if NewTrgOnlyNewLmMaximaBySlice[s] < 1 else NewTrgOnlyNewLmMaximaBySlice[s]
                    cbar = fig.colorbar(im, ax=ax)
                    cbar.mappable.set_clim(0, m)
                    
                ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                ax.set_title(f'New Target ({TrgLabel}) slice {s}'\
                             + '\n(only new segment)')
                
            n += 1 # increment sub-plot number
        
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
                      
        ExportFname = CurrentDateTime + '_Case' + Case + '_Orig' + SrcLabel \
                      + ResOrReg_short + SrcLabel + '_' + TrgLabel + '_New' \
                      + TrgLabel + '_' + ImageType + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return







def PlotPixelArrays(ListOfPixArrs, ListOfFrameToSliceInds, ListOfPlotTitles, 
                    AddTxt=None, ExportPlot=False, ExportDir=None, dpi=80, 
                    LogToConsole=False):
    """ 
    Note:
    
    ListOfPixArrs is a list (which could be of length 1) of pixel arrays.
    
    ListOfFrameToSliceInds is a list (which could be of length 1) of 
    FrameToSliceInds.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    """
    
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    import time
    from copy import deepcopy
    
    for i in range(len(ListOfFrameToSliceInds)):
        print(f'\nListOfPlotTitles[{i}] = {ListOfPlotTitles[i]}')
        
        print(f'\nListOfFrameToSliceInds[{i}] = {ListOfFrameToSliceInds[i]}')
        
        print(f'\nListOfPixArrs[{i}].shape = {ListOfPixArrs[i].shape}')
    
    
    if len(ListOfFrameToSliceInds) > 1:
        # Get the slice numbers that cover all FrameToSliceInds in 
        # ListOfFrameToSliceInds:
        AllSliceNums = []
        
        for FrameToSliceInds in ListOfFrameToSliceInds:
            for SliceInd in FrameToSliceInds:
                AllSliceNums.append(SliceInd)
        
        # Reduce to unique slice numbers:
        AllSliceNums = list(set(AllSliceNums))    
    else:
        AllSliceNums = deepcopy(ListOfFrameToSliceInds[0])
    
        
    # Get the maxima for all frames for all pixel arrays along x (axis=2) and
    # y (axis=1):
    ListOfMaximaByFrame = []
    
    for PixArr in ListOfPixArrs:
    
        ListOfMaximaByFrame.append(np.amax(PixArr, axis=(1,2)))
    
    
    if LogToConsole:
        print(f'\nListOfMaximaByFrame = {ListOfMaximaByFrame}')
    
    
    
    # Prepare the figure.
    
    # Set the number of subplot rows and columns:
    Ncols = len(ListOfPixArrs)
    Nrows = len(AllSliceNums)
    
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Loop through each AllSliceNums: 
    for SliceNum in AllSliceNums:
        #print(f's = {SliceNum}')
        
        # Loop through each pixel array:
        for p in range(len(ListOfPixArrs)):
            PixArr = ListOfPixArrs[p]
            
            Frame2SliceInds = ListOfFrameToSliceInds[p]
            
            PlotTitle = ListOfPlotTitles[p]
            
            #MaximaByFrame = ListOfMaximaByFrame[p]
            
            if SliceNum in Frame2SliceInds:
                FrameNum = Frame2SliceInds.index(SliceNum)
                
                Frame = PixArr[FrameNum]
                
                ax = plt.subplot(Nrows, Ncols, n)
                
                im = ax.imshow(Frame, cmap=plt.cm.Greys_r)
                
                #m = 1 if MaximaByFrame[FrameNum] < 1 else MaximaByFrame[FrameNum]
                #cbar = fig.colorbar(im, ax=ax)
                #cbar.mappable.set_clim(0, m)
                fig.colorbar(im, ax=ax)
                        
                ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                if AddTxt:
                    plotTitle = PlotTitle\
                                + f' Slice {SliceNum} Frame {FrameNum} \n'\
                                + AddTxt
                else:
                    plotTitle = PlotTitle\
                                + f' Slice {SliceNum} Frame {FrameNum}'
                ax.set_title(plotTitle)
                
            n += 1 # increment sub-plot number
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
    
        if AddTxt:
            AddTxt = AddTxt.replace(' = ', '_').replace(' ', '_')
            AddTxt = AddTxt.replace(',', '').replace('(', '').replace(')', '')
            AddTxt = AddTxt.replace('\n', '')
        else:
            AddTxt = ''
            
        ExportFname = CurrentDateTime + '_PixArrs_' + AddTxt + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return








def GetPixArrsFromListOfSegs(ListOfSegs, ListOfDicomDirs, SearchString, 
                             LogToConsole=False):
    """ 
    Note:
    
    ListOfSegs is a list (which could be of length 1) of SEG (Pydicom) objects.
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each SEG.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    """
    
    import importlib
    import SegTools
    importlib.reload(SegTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    import numpy as np
    from SegTools import GetPFFGStoSliceIndsBySeg
    from DicomTools import GetDicomFpaths
    from DicomTools import GetDicomSOPuids
    from DicomTools import GetRoiNum
    from SegTools import GetFramesFromPixArr
    
    ListOfPixArrs = []
    ListOfF2Sinds = []
    ListOfSegNums = []
    ListOfDcmFpaths = []
    
    for i in range(len(ListOfSegs)):
        if LogToConsole:
            print(f'\n\nListOfSegs[{i}]:')
        
        DcmFpaths = GetDicomFpaths(ListOfDicomDirs[i])
        
        ListOfDcmFpaths.append(DcmFpaths)
        
        """
        11/12/20:  
            There should only be one segment so perhaps this should be checked
            and raise exception if the number of segments is greater than one.
            And if not, SegNum will always be = 0 (no need to GetRoiNum).
        """
        
        if ListOfSegs[i]:
            SegNum = GetRoiNum(ListOfSegs[i], SearchString)
            
            SOPuids = GetDicomSOPuids(ListOfDicomDirs[i])
        
            PFFGS2SindsBySeg = GetPFFGStoSliceIndsBySeg(ListOfSegs[i], 
                                                        SOPuids)
            
            ListOfF2Sinds.append(PFFGS2SindsBySeg[SegNum])
            
            if LogToConsole:
                print(f'\nListOfF2Sinds[{i}] = {ListOfF2Sinds[i]}')
            
            
            
            #PixArr = ListOfSegs[i].pixel_array # this contains all segments!
            PixArr = GetFramesFromPixArr(ListOfSegs[i], ListOfDicomDirs[i], 
                                         SearchString, LogToConsole)
            
            if LogToConsole:      
                print(f'\nPixArr.shape = {PixArr.shape}')
                [print(f'np.amax(PixArr[{i}]) = {np.amax(PixArr[i])}') for i in range(PixArr.shape[0])]
                
            """
            If PixArr has a single frame it will have shape (NumOfRows, NumOfCols).
            For compatibility with multi-framed pixel arrays, convert single-framed
            pixel arrays to shape (1, NumOfRows, NumOfCols).
            """
            if len(PixArr.shape) < 3:
                R, C = PixArr.shape
                
                PixArr = np.reshape(PixArr, (1, R, C))
                
                if LogToConsole:      
                    print(f'\nPixArr was a single frame so reshaped to {PixArr.shape}')
                    
        else:
            SegNum = None
            ListOfF2Sinds.append(None)
            PixArr = None
        
        ListOfSegNums.append(SegNum)
        
        ListOfPixArrs.append(PixArr)
        
        #if LogToConsole: 
        #    print('')
        #    print(f'\nListOfPixArrs[{i}].shape = {ListOfPixArrs[i].shape}')
        
    
    return ListOfPixArrs, ListOfF2Sinds, ListOfSegNums, ListOfDcmFpaths








def PlotPixArrsFromListOfSegs_v1(ListOfSegs, ListOfDicomDirs, ListOfPlotTitles,
                                 SearchString, PlotAllSlices=False, AddTxt=None, 
                                 ExportPlot=False, ExportDir=None, dpi=80, 
                                 LogToConsole=False):
    """ 
    Note:
    
    ListOfSegs is a list (which could be of length 1) of SEG (Pydicom) objects.
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each SEG.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    import importlib
    import SegTools
    importlib.reload(SegTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    import matplotlib.pyplot as plt
    import os
    import time
    from copy import deepcopy
    from pydicom import dcmread
    from DicomTools import GetDicomFpaths
    
    ListOfPixArrs, ListOfF2Sinds, ListOfSegNums,\
    ListOfDcmFpaths = GetPixArrsFromListOfSegs(ListOfSegs, ListOfDicomDirs, 
                                               SearchString, LogToConsole)
    
    # Get the list of slice numbers to be plotted:
    if PlotAllSlices:
        NumOfSlices = []
        
        for i in range(len(ListOfDcmFpaths)):
            NumOfSlices.append(len(ListOfDcmFpaths[i]))
            
        AllSliceNums = list(range(max(NumOfSlices)))
            
        
    else:
        if len(ListOfF2Sinds) > 1:
            # Get the slice numbers that cover all FrameToSliceInds in 
            # ListOfFrameToSliceInds:
            AllSliceNums = []
            
            for F2Sinds in ListOfF2Sinds:
                if F2Sinds:
                    for SliceInd in F2Sinds:
                        AllSliceNums.append(SliceInd)
            
            # Reduce to unique slice numbers:
            AllSliceNums = list(set(AllSliceNums))    
        else:
            AllSliceNums = deepcopy(ListOfF2Sinds[0])
    
        
    # Get the maxima for all frames for all pixel arrays along x (axis=2) and
    # y (axis=1):
    #ListOfMaximaByFrame = []
    #
    #for PixArr in ListOfPixArrs:
    #
    #    ListOfMaximaByFrame.append(np.amax(PixArr, axis=(1,2)))
    #
    #
    #if LogToConsole:
    #    print(f'\nListOfMaximaByFrame = {ListOfMaximaByFrame}')
    
    
    
    # Prepare the figure.
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    #alpha = 0.2
    alpha = 0.5
    
    # Set the number of subplot rows and columns:
    Ncols = len(ListOfPixArrs)
    Nrows = len(AllSliceNums)
    
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7*Nrows), dpi=dpi)
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 8*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Loop through each AllSliceNums: 
    for SliceNum in AllSliceNums:
        #print(f's = {SliceNum}')
        
        # Loop through each data set:
        for i in range(len(ListOfPixArrs)):
            PixArr = ListOfPixArrs[i]
            
            F2Sinds = ListOfF2Sinds[i]
            
            DcmFpaths = GetDicomFpaths(ListOfDicomDirs[i])
            
            PlotTitle = ListOfPlotTitles[i]
            
            #MaximaByFrame = ListOfMaximaByFrame[i]
            
            ax = plt.subplot(Nrows, Ncols, n)
            
            
            if SliceNum < len(DcmFpaths):
                DcmPixArr = dcmread(DcmFpaths[SliceNum]).pixel_array
            
                #im = ax.imshow(DicomPixArr, cmap=plt.cm.Greys_r)
                ax.imshow(DcmPixArr, cmap=plt.cm.Greys_r, alpha=alpha)
                
                if SliceNum in F2Sinds:
                    FrameNum = F2Sinds.index(SliceNum)
                    
                    Frame = PixArr[FrameNum]
                    
                    #ax = plt.subplot(Nrows, Ncols, n)
                    
                    #im = ax.imshow(Frame, cmap=plt.cm.nipy_spectral, 
                    #               alpha=alpha)
                    ax.imshow(Frame, cmap=plt.cm.nipy_spectral, alpha=alpha)
                    
                    #m = 1 if MaximaByFrame[FrameNum] < 1 else MaximaByFrame[FrameNum]
                    #cbar = fig.colorbar(im, ax=ax)
                    #cbar.mappable.set_clim(0, m)
                    
                    #fig.colorbar(im, ax=ax)
                    #fig.colorbar(ax=ax)
                    ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                    if AddTxt:
                        plotTitle = PlotTitle\
                                    + f' Slice {SliceNum}, Frame {FrameNum}\n'\
                                    + AddTxt
                    else:
                        plotTitle = PlotTitle\
                                    + f' Slice {SliceNum}, Frame {FrameNum}'
                    ax.set_title(plotTitle)
                
            n += 1 # increment sub-plot number
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
    
        if AddTxt:
            AddTxt = AddTxt.replace(' = ', '_').replace(' ', '_')
            AddTxt = AddTxt.replace(',', '').replace('(', '').replace(')', '')
            AddTxt = AddTxt.replace('\n', '')
        else:
            AddTxt = ''
            
        ExportFname = CurrentDateTime + '_PixArrs_' + AddTxt + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return





def PlotPixArrsFromListOfSegs_v2(ListOfSegs, ListOfDicomDirs, ListOfPlotTitles,
                                 SearchString, PlotAllSlices=False, AddTxt=None, 
                                 ExportPlot=False, ExportDir=None, dpi=80, 
                                 LogToConsole=False):
    """ 
    Note:
    
    ListOfSegs is a list (which could be of length 1) of SEG (Pydicom) objects.
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each SEG.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    
    Plot has different DATASETS ALONG ROWS and different SLICES ALONG COLUMNS. 
    """
    
    import importlib
    import SegTools
    importlib.reload(SegTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    import matplotlib.pyplot as plt
    import os
    import time
    from copy import deepcopy
    from pydicom import dcmread
    from DicomTools import GetDicomFpaths
    
    ListOfPixArrs, ListOfF2Sinds, ListOfSegNums,\
    ListOfDcmFpaths = GetPixArrsFromListOfSegs(ListOfSegs, ListOfDicomDirs, 
                                               SearchString, LogToConsole)
    
    # Get the list of slice numbers to be plotted:
    if PlotAllSlices:
        NumOfSlices = []
        
        for i in range(len(ListOfDcmFpaths)):
            NumOfSlices.append(len(ListOfDcmFpaths[i]))
            
        AllSliceNums = list(range(max(NumOfSlices)))
            
        
    else:
        if len(ListOfF2Sinds) > 1:
            # Get the slice numbers that cover all FrameToSliceInds in 
            # ListOfFrameToSliceInds:
            AllSliceNums = []
            
            for F2Sinds in ListOfF2Sinds:
                if F2Sinds:
                    for SliceInd in F2Sinds:
                        AllSliceNums.append(SliceInd)
            
            # Reduce to unique slice numbers:
            AllSliceNums = list(set(AllSliceNums))    
        else:
            AllSliceNums = deepcopy(ListOfF2Sinds[0])
    
    
    if True:#LogToConsole:
        print(f'\nAllSliceNums = {AllSliceNums}')
        
    # Get the maxima for all frames for all pixel arrays along x (axis=2) and
    # y (axis=1):
    #ListOfMaximaByFrame = []
    #
    #for PixArr in ListOfPixArrs:
    #
    #    ListOfMaximaByFrame.append(np.amax(PixArr, axis=(1,2)))
    #
    #
    #if LogToConsole:
    #    print(f'\nListOfMaximaByFrame = {ListOfMaximaByFrame}')
    
    
    
    # Prepare the figure.
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    #alpha = 0.2
    alpha = 0.5
    
    # Set the number of subplot rows and columns:
    Nrows = len(ListOfPixArrs)
    Ncols = len(AllSliceNums)
    
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7*Nrows), dpi=dpi)
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 8*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Loop through each data set:
    for i in range(len(ListOfPixArrs)):
        PixArr = ListOfPixArrs[i]
        
        F2Sinds = ListOfF2Sinds[i]
        
        DcmFpaths = GetDicomFpaths(ListOfDicomDirs[i])
        
        PlotTitle = ListOfPlotTitles[i]
        
        #MaximaByFrame = ListOfMaximaByFrame[i]
        
        #print(f'\n\nDataset {i + 1}, len(DcmFpaths) = {len(DcmFpaths)}')
        
        # Loop through each AllSliceNums: 
        for SliceNum in AllSliceNums:
            #print(f's = {SliceNum}')
            
            ax = plt.subplot(Nrows, Ncols, n)
            
            if SliceNum < len(DcmFpaths):
                DcmPixArr = dcmread(DcmFpaths[SliceNum]).pixel_array
            
                #im = ax.imshow(DicomPixArr, cmap=plt.cm.Greys_r)
                ax.imshow(DcmPixArr, cmap=plt.cm.Greys_r)#, alpha=alpha)
                
                if F2Sinds:
                    if SliceNum in F2Sinds:
                        FrameNum = F2Sinds.index(SliceNum)
                        
                        Frame = PixArr[FrameNum]
                        
                        #ax = plt.subplot(Nrows, Ncols, n)
                        
                        #im = ax.imshow(Frame, cmap=plt.cm.nipy_spectral, 
                        #               alpha=alpha)
                        ax.imshow(Frame, cmap=plt.cm.nipy_spectral, alpha=alpha)
                        
                        FrameTxt = f'Frame {FrameNum}'
                    else:
                        FrameTxt = 'No frame'
                else:
                    FrameTxt = 'No frame'
                    
                 
                SliceTxt = f'Slice {SliceNum + 1}'
                SliceTxt = ''
                
                ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                
                if AddTxt:
                    plotTitle = PlotTitle\
                                + f'\n' + SliceTxt + '\n'\
                                + f'\n' + FrameTxt + '\n'\
                                + AddTxt
                else:
                    plotTitle = PlotTitle\
                                + f'\n' + SliceTxt + '\n'\
                                + f'\n' + FrameTxt
                                
                ax.set_title(plotTitle)
                
            n += 1 # increment sub-plot number
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
    
        if AddTxt:
            AddTxt = AddTxt.replace(' = ', '_').replace(' ', '_')
            AddTxt = AddTxt.replace(',', '').replace('(', '').replace(')', '')
            AddTxt = AddTxt.replace('\n', '')
        else:
            AddTxt = ''
            
        ExportFname = CurrentDateTime + '_PixArrs_' + AddTxt + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return






def GetContoursFromListOfRtss(ListOfRtss, ListOfDicomDirs, SearchString, 
                              LogToConsole=False):
    """ 
    Note:
    
    ListOfRtss is a list (which could be of length 1) of RTS (Pydicom) objects.
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each RTS.
    """
    
    import importlib
    import RtsTools
    importlib.reload(RtsTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    from DicomTools import GetRoiNum
    from DicomTools import GetDicomFpaths
    from RtsTools import GetPtsInRoi
    from ImageTools import GetImageAttributes
    
    ListOfContours = []
    ListOfC2Sinds = []
    ListOfRoiNums = []
    ListOfDcmFpaths = []
    ListOfOrigins = []
    ListOfDirections = []
    ListOfSpacings = []
    
    for i in range(len(ListOfRtss)):
        if LogToConsole:
            print(f'\nListOfRtss[{i}]:')
        
        """
        11/12/20:  
            There should only be one ROI so perhaps this should be checked
            and raise exception if the number of ROIs is greater than one.
            And if not, RoiNum will always be = 0 (no need to GetRoiNum).
        """
        
        if ListOfRtss[i]:
            RoiNum = GetRoiNum(ListOfRtss[i], SearchString)
            
            Contours, C2Sinds = GetPtsInRoi(ListOfRtss[i], 
                                            ListOfDicomDirs[i], 
                                            SearchString)
            
            if LogToConsole:      
                print(f'len(Contours) in "{SearchString}" = {len(Contours)}')
                print(f'C2Sinds = {C2Sinds}')
                [print(f'len(Contours{i}) = {len(Contours[i])}') for i in range(len(Contours))]
            
        else:
            RoiNum = None
            Contours = None
            C2Sinds = None
            
            if LogToConsole:      
                print(f'No contours for this dataset')
        
        
        ListOfRoiNums.append(RoiNum)
        
        DcmFpaths = GetDicomFpaths(ListOfDicomDirs[i])
        
        Size, Spacings, ST, IPPs, Dirs = GetImageAttributes(ListOfDicomDirs[i])
        
        ListOfContours.append(Contours)
        ListOfC2Sinds.append(C2Sinds)
        ListOfDcmFpaths.append(DcmFpaths)
        ListOfOrigins.append(IPPs[0])
        ListOfDirections.append(Dirs)
        ListOfSpacings.append(Spacings)
        
        if LogToConsole:      
            #print(f'len(Contours) in "{SearchString}" = {len(Contours)}')
            print(f'len(ListOfContours) = {len(ListOfContours)}')
            #print(f'C2Sinds = {C2Sinds}')
            #[print(f'len(Contours{i}) = {len(Contours[i])}') for i in range(len(Contours))]
        
        
        #SOPuids = GetDicomSOPuids(ListOfDicomDirs[i])
        
        #CStoSliceIndsByRoi = GetCStoSliceIndsByRoi(ListOfRtss[i], SOPuids)
        
        #ListOfC2Sinds.append(CStoSliceIndsByRoi[RoiNum])
        
        #if LogToConsole:
        #    print(f'ListOfC2Sinds[{i}] = {ListOfC2Sinds[i]}')
    
            
    return ListOfContours, ListOfC2Sinds, ListOfRoiNums, ListOfDcmFpaths,\
           ListOfOrigins, ListOfDirections, ListOfSpacings






    
def PlotContoursFromListOfRtss_v1(ListOfRtss, ListOfDicomDirs, ListOfPlotTitles,
                                  SearchString, PlotAllSlices=False, AddTxt=None, 
                                  ExportPlot=False, ExportDir=None, dpi=80, 
                                  LogToConsole=False):
    """ 
    Note:
    
    ListOfRtss is a list (which could be of length 1) of RTS (Pydicom) objects.
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each RTS.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    import importlib
    import RtsTools
    importlib.reload(RtsTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    import matplotlib.pyplot as plt
    import os
    import time
    from copy import deepcopy
    from pydicom import dcmread
    from GeneralTools import Unpack
    from ConversionTools import Contour2Indices
    
    ListOfContours, ListOfC2Sinds, ListOfRoiNums,\
    ListOfDcmFpaths, ListOfOrigins, ListOfDirections,\
    ListOfSpacings = GetContoursFromListOfRtss(ListOfRtss, ListOfDicomDirs, 
                                               SearchString, LogToConsole)
    
    # Get the list of slice numbers that will be plotted:
    if PlotAllSlices:
        NumOfSlices = []
        
        for i in range(len(ListOfDcmFpaths)):
            NumOfSlices.append(len(ListOfDcmFpaths[i]))
            
        AllSliceNums = list(range(max(NumOfSlices)))
            
        
    else:
        if len(ListOfC2Sinds) > 1:
            # Get the slice numbers that cover all CSToSliceInds in 
            # ListOfSliceToSliceInds:
            AllSliceNums = []
            
            for C2Sinds in ListOfC2Sinds:
                if C2Sinds:
                    for SliceInd in C2Sinds:
                        AllSliceNums.append(SliceInd)
            
            # Reduce to unique slice numbers:
            AllSliceNums = list(set(AllSliceNums))    
        else:
            AllSliceNums = deepcopy(ListOfC2Sinds[0])
    
    if LogToConsole:
            print(f'\nAllSliceNums = {AllSliceNums}')
            
            
    # Prepare the figure.
    
    # Set the number of subplot rows and columns:
    Ncols = len(ListOfRtss)
    Nrows = len(AllSliceNums)
    
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7.5*Nrows), dpi=dpi)
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 8*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Loop through each AllSliceNums: 
    for SliceNum in AllSliceNums:
        if LogToConsole:
            print(f'\nSliceNum = {SliceNum}')
        
        # Loop through each list of contours:
        for i in range(len(ListOfContours)):
            Contours = ListOfContours[i]
            C2SInds = ListOfC2Sinds[i]
            
            DicomFpaths = ListOfDcmFpaths[i]
            Origin = ListOfOrigins[i]
            Directions = ListOfDirections[i]
            Spacings = ListOfSpacings[i]
            
            PlotTitle = ListOfPlotTitles[i]
            
            if LogToConsole:
                    print(f'\n   i = {i}')
                    print(f'   PlotTitle = {PlotTitle}')
                    print(f'   len(Contours) = {len(Contours)}')
                    print(f'   C2SInds = {C2SInds}')
                    
            ax = plt.subplot(Nrows, Ncols, n)
            
            if SliceNum < len(DicomFpaths):
                DicomPixArr = dcmread(DicomFpaths[SliceNum]).pixel_array
            
                ax.imshow(DicomPixArr, cmap=plt.cm.Greys_r)
            
            
                if SliceNum in C2SInds:
                    ContourNum = C2SInds.index(SliceNum)
                    
                    Contour = Contours[ContourNum]
                    
                    Indices = Contour2Indices(Points=Contour, Origin=Origin, 
                                              Directions=Directions, 
                                              Spacings=Spacings)
                    
                    if LogToConsole:
                        print(f'      SliceNum = {SliceNum} is in C2SInds')
                        print(f'      ContourNum = {ContourNum}')
                        print(f'      len(Contour) = {len(Contour)}')
                        #print(f'      Contour = {Contour}')
                    
                    #ax = plt.subplot(Nrows, Ncols, n)
                    
                    # Unpack the contour points' indices:
                    X, Y, Z = Unpack(Indices)
                    
                    # Plot the contour points:
                    #ax = plt.plot(X, Y, linewidth=0.5, c='r');
                    ax.plot(X, Y, linewidth=0.5, c='r');
                    
                    ContourTxt = f'Contour {ContourNum + 1}'
                    
                else:
                    ContourTxt = 'No contour'
                    
                    if LogToConsole:
                        print(f'      SliceNum = {SliceNum} is NOT in C2SInds')
                
                SliceTxt = f'Slice {SliceNum}'
                
                if AddTxt:
                    plotTitle = PlotTitle \
                                + f'\n' + SliceTxt + '\n'\
                                + f'\n' + ContourTxt + '\n'\
                                + AddTxt
                else:
                    plotTitle = PlotTitle \
                                + f'\n' + SliceTxt + '\n'\
                                + f'\n' + ContourTxt
                
                ax.set_xlabel('pixels'); ax.set_ylabel('pixels')
                ax.set_title(plotTitle)
                
            n += 1 # increment sub-plot number
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
    
        if AddTxt:
            AddTxt = AddTxt.replace(' = ', '_').replace(' ', '_')
            AddTxt = AddTxt.replace(',', '').replace('(', '').replace(')', '')
            AddTxt = AddTxt.replace('\n', '')
        else:
            AddTxt = ''
            
        ExportFname = CurrentDateTime + '_Contours_' + AddTxt + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return










def PlotContoursFromListOfRtss_v2(ListOfRtss, ListOfDicomDirs, ListOfPlotTitles,
                                  SearchString, PlotAllSlices=False, AddTxt=None, 
                                  ExportPlot=False, ExportDir=None, dpi=80, 
                                  LogToConsole=False):
    """ 
    Note:
    
    ListOfRtss is a list (which could be of length 1) of RTS (Pydicom) objects.
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each RTS.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    
    Plot has different DATASETS ALONG ROWS and different SLICES ALONG COLUMNS. 
    """
    
    import importlib
    import RtsTools
    importlib.reload(RtsTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    import matplotlib.pyplot as plt
    import os
    import time
    from copy import deepcopy
    from pydicom import dcmread
    from GeneralTools import Unpack
    from ConversionTools import Contour2Indices
    
    ListOfContours, ListOfC2Sinds, ListOfRoiNums,\
    ListOfDcmFpaths, ListOfOrigins, ListOfDirections,\
    ListOfSpacings = GetContoursFromListOfRtss(ListOfRtss, ListOfDicomDirs, 
                                               SearchString, LogToConsole)
    
    # Get the list of slice numbers that will be plotted:
    if PlotAllSlices:
        NumOfSlices = []
        
        for i in range(len(ListOfDcmFpaths)):
            NumOfSlices.append(len(ListOfDcmFpaths[i]))
            
        AllSliceNums = list(range(max(NumOfSlices)))
            
        
    else:
        if len(ListOfC2Sinds) > 1:
            # Get the slice numbers that cover all CSToSliceInds in 
            # ListOfSliceToSliceInds:
            AllSliceNums = []
            
            for C2Sinds in ListOfC2Sinds:
                if C2Sinds:
                    for SliceInd in C2Sinds:
                        AllSliceNums.append(SliceInd)
            
            # Reduce to unique slice numbers:
            AllSliceNums = list(set(AllSliceNums))    
        else:
            AllSliceNums = deepcopy(ListOfC2Sinds[0])
    
    if True:#LogToConsole:
            print(f'\nAllSliceNums = {AllSliceNums}')
            
            
    # Prepare the figure.
    
    # Set the number of subplot rows and columns:
    Nrows = len(ListOfRtss)
    Ncols = len(AllSliceNums)
    
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7.5*Nrows), dpi=dpi)
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 8*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
        
    # Loop through each dataset:
    for i in range(len(ListOfContours)):
        Contours = ListOfContours[i]
        C2Sinds = ListOfC2Sinds[i]
        
        DicomFpaths = ListOfDcmFpaths[i]
        Origin = ListOfOrigins[i]
        Directions = ListOfDirections[i]
        Spacings = ListOfSpacings[i]
        
        PlotTitle = ListOfPlotTitles[i]
        
        if LogToConsole:
                print(f'\ni = {i}')
                print(f'   PlotTitle = {PlotTitle}')
                print(f'   C2Sinds = {C2Sinds}')
                if C2Sinds:
                    print(f'   len(Contours) = {len(Contours)}')
        
        # Loop through each AllSliceNums: 
        for SliceNum in AllSliceNums:
            if LogToConsole:
                print(f'\n   SliceNum = {SliceNum}')
                
            ax = plt.subplot(Nrows, Ncols, n)
            
            if SliceNum < len(DicomFpaths):
                DicomPixArr = dcmread(DicomFpaths[SliceNum]).pixel_array
            
                ax.imshow(DicomPixArr, cmap=plt.cm.Greys_r)
            
                if C2Sinds:
                    if SliceNum in C2Sinds:
                        ContourNum = C2Sinds.index(SliceNum)
                        
                        Contour = Contours[ContourNum]
                        
                        Indices = Contour2Indices(Points=Contour, Origin=Origin, 
                                                  Directions=Directions, 
                                                  Spacings=Spacings)
                        
                        if LogToConsole:
                            print(f'   SliceNum = {SliceNum} is in C2Sinds')
                            print(f'   ContourNum = {ContourNum}')
                            print(f'   len(Contour) = {len(Contour)}')
                            #print(f'      Contour = {Contour}')
                        
                        #ax = plt.subplot(Nrows, Ncols, n)
                        
                        # Unpack the contour points' indices:
                        X, Y, Z = Unpack(Indices)
                        
                        # Plot the contour points:
                        #ax = plt.plot(X, Y, linewidth=0.5, c='r');
                        ax.plot(X, Y, linewidth=0.5, c='r');
                    
                        ContourTxt = f'Contour {ContourNum + 1}'
                    else:
                        ContourTxt = 'No contour'
                        
                        if LogToConsole:
                            print(f'   SliceNum = {SliceNum} is NOT in C2Sinds')
                else:
                    ContourTxt = 'No contour'
                
                SliceTxt = f'Slice {SliceNum}'
                SliceTxt = ''
                
                if AddTxt:
                    plotTitle = PlotTitle \
                                + f'\n' + SliceTxt + '\n'\
                                + f'\n' + ContourTxt + '\n'\
                                + AddTxt
                else:
                    plotTitle = PlotTitle \
                                + f'\n' + SliceTxt + '\n'\
                                + f'\n' + ContourTxt
                                        
                ax.set_xlabel('pixels'); ax.set_ylabel('pixels')
                ax.set_title(plotTitle)
                
            n += 1 # increment sub-plot number
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
    
        if AddTxt:
            AddTxt = AddTxt.replace(' = ', '_').replace(' ', '_')
            AddTxt = AddTxt.replace(',', '').replace('(', '').replace(')', '')
            AddTxt = AddTxt.replace('\n', '')
        else:
            AddTxt = ''
            
        ExportFname = CurrentDateTime + '_Contours_' + AddTxt + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return






def GetPixArrsFromListOfImages(ListOfImages, ListOfDicomDirs, 
                               LogToConsole=False):
    """ 
    Note:
    
    ListOfImages is a list (which could be of length 1) of SimpleITK images
    (e.g. labelmaps).
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each SEG.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    """
    
    import importlib
    import SegTools
    importlib.reload(SegTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    import numpy as np
    from DicomTools import GetDicomFpaths
    
    from ConversionTools import Image2PixArr
    
    ListOfPixArrs = []
    ListOfF2Sinds = []
    ListOfDcmFpaths = []
    
    for i in range(len(ListOfImages)):
        if LogToConsole:
            print(f'\n\nListOfSegs[{i}]:')
        
        DcmFpaths = GetDicomFpaths(ListOfDicomDirs[i])
        
        ListOfDcmFpaths.append(DcmFpaths)
        
        """
        11/12/20:  
            There should only be one segment so perhaps this should be checked
            and raise exception if the number of segments is greater than one.
            And if not, SegNum will always be = 0 (no need to GetRoiNum).
        """
        
        if ListOfImages[i]:
            PixArr, F2Sinds = Image2PixArr(ListOfImages[i])
            
            ListOfF2Sinds.append(F2Sinds)
            
            if LogToConsole:
                print(f'\nListOfF2Sinds[{i}] = {ListOfF2Sinds[i]}')
            
            
            if LogToConsole:      
                print(f'\nPixArr.shape = {PixArr.shape}')
                [print(f'np.amax(PixArr[{i}]) = {np.amax(PixArr[i])}') for i in range(PixArr.shape[0])]
                
            """
            If PixArr has a single frame it will have shape (NumOfRows, NumOfCols).
            For compatibility with multi-framed pixel arrays, convert single-framed
            pixel arrays to shape (1, NumOfRows, NumOfCols).
            """
            if len(PixArr.shape) < 3:
                R, C = PixArr.shape
                
                PixArr = np.reshape(PixArr, (1, R, C))
                
                if LogToConsole:      
                    print(f'\nPixArr was a single frame so reshaped to {PixArr.shape}')
                    
        else:
            ListOfF2Sinds.append(None)
            PixArr = None
        
        
        ListOfPixArrs.append(PixArr)
        
        #if LogToConsole: 
        #    print('')
        #    print(f'\nListOfPixArrs[{i}].shape = {ListOfPixArrs[i].shape}')
        
    
    return ListOfPixArrs, ListOfF2Sinds, ListOfDcmFpaths







def PlotPixArrsFromListOfImages(ListOfImages, ListOfDicomDirs, ListOfPlotTitles,
                                PlotAllSlices=False, AddTxt=None, 
                                ExportPlot=False, ExportDir=None, dpi=80, 
                                LogToConsole=False):
    """ 
    Note:
    
    ListOfSegs is a list (which could be of length 1) of SEG (Pydicom) objects.
    
    ListOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each SEG.
    
    ListOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    import importlib
    import SegTools
    importlib.reload(SegTools)
    import DicomTools
    importlib.reload(DicomTools)
    
    import matplotlib.pyplot as plt
    import os
    import time
    from copy import deepcopy
    from pydicom import dcmread
    from DicomTools import GetDicomFpaths
    
    ListOfPixArrs, ListOfF2Sinds,\
    ListOfDcmFpaths = GetPixArrsFromListOfImages(ListOfImages, ListOfDicomDirs, 
                                                 LogToConsole)
    
    print(f'\nlen(ListOfPixArrs) = {len(ListOfPixArrs)}')
    print(f'len(ListOfF2Sinds) = {len(ListOfF2Sinds)}')
    print(f'len(ListOfDcmFpaths) = {len(ListOfDcmFpaths)}')
    print(f'ListOfF2Sinds = {ListOfF2Sinds}')
    
    
    # Get the list of slice numbers to be plotted:
    if PlotAllSlices:
        NumOfSlices = []
        
        for i in range(len(ListOfDcmFpaths)):
            NumOfSlices.append(len(ListOfDcmFpaths[i]))
            
        AllSliceNums = list(range(max(NumOfSlices)))
            
        
    else:
        if len(ListOfF2Sinds) > 1:
            # Get the slice numbers that cover all FrameToSliceInds in 
            # ListOfFrameToSliceInds:
            AllSliceNums = []
            
            for F2Sinds in ListOfF2Sinds:
                if F2Sinds:
                    for SliceInd in F2Sinds:
                        AllSliceNums.append(SliceInd)
            
            print(f'\nAllSliceNums = {AllSliceNums}')
            
            # Reduce to unique slice numbers:
            AllSliceNums = list(set(AllSliceNums))
            
            print(f'\nAllSliceNums = {AllSliceNums}')
        else:
            AllSliceNums = deepcopy(ListOfF2Sinds[0])
    
    
    
    print(f'\nAllSliceNums = {AllSliceNums}')
    
    # Get the maxima for all frames for all pixel arrays along x (axis=2) and
    # y (axis=1):
    #ListOfMaximaByFrame = []
    #
    #for PixArr in ListOfPixArrs:
    #
    #    ListOfMaximaByFrame.append(np.amax(PixArr, axis=(1,2)))
    #
    #
    #if LogToConsole:
    #    print(f'\nListOfMaximaByFrame = {ListOfMaximaByFrame}')
    
    
    
    # Prepare the figure.
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    #alpha = 0.2
    alpha = 0.5
    
    # Set the number of subplot rows and columns:
    Ncols = len(ListOfPixArrs)
    Nrows = len(AllSliceNums)
    
    #fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 7*Nrows), dpi=dpi)
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 8*Nrows), dpi=dpi)
        
    
    n = 1 # initialised sub-plot number
    
    # Loop through each AllSliceNums: 
    for SliceNum in AllSliceNums:
        #print(f's = {SliceNum}')
        
        # Loop through each data set:
        for i in range(len(ListOfPixArrs)):
            PixArr = ListOfPixArrs[i]
            
            F2Sinds = ListOfF2Sinds[i]
            
            DcmFpaths = GetDicomFpaths(ListOfDicomDirs[i])
            
            PlotTitle = ListOfPlotTitles[i]
            
            #MaximaByFrame = ListOfMaximaByFrame[i]
            
            ax = plt.subplot(Nrows, Ncols, n)
            
            
            if SliceNum < len(DcmFpaths):
                DcmPixArr = dcmread(DcmFpaths[SliceNum]).pixel_array
            
                #im = ax.imshow(DicomPixArr, cmap=plt.cm.Greys_r)
                ax.imshow(DcmPixArr, cmap=plt.cm.Greys_r, alpha=alpha)
                
                if SliceNum in F2Sinds:
                    FrameNum = F2Sinds.index(SliceNum)
                    
                    Frame = PixArr[FrameNum]
                    
                    #ax = plt.subplot(Nrows, Ncols, n)
                    
                    #im = ax.imshow(Frame, cmap=plt.cm.nipy_spectral, 
                    #               alpha=alpha)
                    ax.imshow(Frame, cmap=plt.cm.nipy_spectral, alpha=alpha)
                    
                    #m = 1 if MaximaByFrame[FrameNum] < 1 else MaximaByFrame[FrameNum]
                    #cbar = fig.colorbar(im, ax=ax)
                    #cbar.mappable.set_clim(0, m)
                    
                    #fig.colorbar(im, ax=ax)
                    #fig.colorbar(ax=ax)
                    ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                    if AddTxt:
                        plotTitle = PlotTitle\
                                    + f' Slice {SliceNum}, Frame {FrameNum}\n'\
                                    + AddTxt
                    else:
                        plotTitle = PlotTitle\
                                    + f' Slice {SliceNum}, Frame {FrameNum}'
                    ax.set_title(plotTitle)
                
            n += 1 # increment sub-plot number
        
    
    if ExportPlot:
        CurrentDate = time.strftime("%Y%m%d", time.gmtime())
        CurrentTime = time.strftime("%H%M%S", time.gmtime())
        CurrentDateTime = CurrentDate + '_' + CurrentTime
    
        if AddTxt:
            AddTxt = AddTxt.replace(' = ', '_').replace(' ', '_')
            AddTxt = AddTxt.replace(',', '').replace('(', '').replace(')', '')
            AddTxt = AddTxt.replace('\n', '')
        else:
            AddTxt = ''
            
        ExportFname = CurrentDateTime + '_PixArrs_' + AddTxt + '.jpg'
        
        ExportFpath = os.path.join(ExportDir, ExportFname)
        
        plt.savefig(ExportFpath, bbox_inches='tight')
        
        print('\nPlot exported to:\n\n', ExportFpath)
        
    return