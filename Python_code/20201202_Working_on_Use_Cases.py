#!/usr/bin/env python
# coding: utf-8

# ## Use case scenarios:
# 
# 1) Same DICOM Series/XNAT Scan, FoR, IPP, IOP, ST, PS (= Direct copy)
# 
# 2) Different DICOM Series/XNAT Scans; Same DICOM Study/XNAT Session, FoR, IPP, IOP, ST and PS
# 
#     a) Direct copy
#     
#     b) Relationship-preserving copy
# 
# 3) Different Series, PS and/or ST (if different ST they will likely have different IPP); Same Study, FoR, IOP 
# 
#     a) Direct copy
#     
#     b) Relationship-preserving copy
# 
# 4) Different Series, IOP, IPP, possibly different ST and PS; Same Study (= Relationship-preserving copy)
# 
# 5) Different or Same* Study, Different FoR (hence different IPP and IOP), and possibly different ST and/or PS (= Relationship-preserving copy)
# 

# In[1]:


import os
from copy import deepcopy
import numpy as np
import importlib
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


DicomRootDir = r"C:\Data\Cancer imaging archive\ACRIN-FMISO-Brain\ACRIN-FMISO-Brain-011"

MR4Dir = r"04-10-1960-MRI Brain wwo Contrast-69626"
MR12Dir = r"06-11-1961-MRI Brain wwo Contrast-79433"

MR4_S3_DicomDir = os.path.join(DicomRootDir, MR4Dir,
                               r"3-T2 TSE AXIAL-07507") # 

MR4_S4_DicomDir = os.path.join(DicomRootDir, MR4Dir,
                              r"4-T2 AXIAL FLAIR DARK FL-48830") # 416x512x21 .449x.449x5 mm

MR4_S5_DicomDir = os.path.join(DicomRootDir, MR4Dir,
                               r"5-T1 SE AXIAL 3MM-81246")        # 208x256x50 .898x.898x3 mm

MR4_S6_DicomDir = os.path.join(DicomRootDir, MR4Dir, 
                               r"6-ep2ddiff3scantracep2-55446") # 192x192x63 1.302x1.302x5 mm

MR4_S7_DicomDir = os.path.join(DicomRootDir, MR4Dir, 
                               r"7-ep2ddiff3scantracep2ADC-22197") # 

MR4_S8_DicomDir = os.path.join(DicomRootDir, MR4Dir, 
                               r"8-T1 SE AXIAL POST FS FC-59362") # 212x256x30 .898x.898x5 mm

MR4_S9_DicomDir = os.path.join(DicomRootDir, MR4Dir,
                               r"9-T1 SE AXIAL POST 3MM 5 MIN DELAY-07268") # 208x256x50 .898x.898x3 mm

MR12_S8_DicomDir = os.path.join(DicomRootDir, MR12Dir,
                                r"8-T1 SE AXIAL POST FS FC-81428") # 256x192x35 .938x.938x5 mm

RoiRootDir = r"C:\Data\Data copied to Google Drive\ACRIN-FMISO-Brain-011"
RtsRootDir = os.path.join(RoiRootDir, "Fixed_RTS_Collections")
SegRootDir = os.path.join(RoiRootDir, "Fixed_SEG_Collections")

MR4_S8_RtsFpath = os.path.join(RtsRootDir, "MR4_S8_tumour_RTS_AIM_20200511_073405.dcm") # tumour

MR4_S8_SegFpath = os.path.join(SegRootDir, "Seg_from_MR4_S8_tumour_RTS_AIM_20200511_073405.dcm") # tumour

MR4_S9_RtsFpath = os.path.join(RtsRootDir, "MR4_S9_tumour_RTS_AIM_20201014_163721.dcm") # tumour drawn on S9 stack
MR4_S9_RtsFpath = os.path.join(RtsRootDir, "MR4_S9_brain_RTS_AIM_20201112_142559.dcm")
MR4_S9_RtsFpath = os.path.join(RtsRootDir, "MR4_S9_tumour_and_brain_RTS_AIM_20201116_122858.dcm")

MR4_S9_SegFpath = os.path.join(SegRootDir, "Seg_from_MR4_S9_tumour_RTS_AIM_20201014_163721.dcm") # tumour drawn on S9 stack
MR4_S9_SegFpath = os.path.join(SegRootDir, "MR4_S9_tumour_SEG_20201105_115408.dcm")
MR4_S9_SegFpath = os.path.join(SegRootDir, "MR4_S9_tumour_and_brain_SEG_20201105_115939.dcm")

MR4_S5_RtsFpath = os.path.join(RtsRootDir, "MR4_S5_tumour_RTS_AIM_20201021_151904.dcm") # tumour drawn on S5 stack
#MR4_S5_SegFpath = os.path.join(SegRootDir, "Seg_from_MR4_S5_tumour_RTS_AIM_20201021_151904.dcm") # tumour drawn on S5 stack
MR4_S5_SegFpath = os.path.join(SegRootDir, "MR4_S5_tumour_SEG_20201216_084441.dcm") # single frame on slice 24 or 26

#MR4_S3_RtsFpath = os.path.join(RtsRootDir, "MR4_S3_tumour_and_brain_RTS_AIM_20201112_162427.dcm") # <-- WARNING: tumour & brain are not separate ROIs!
MR4_S3_RtsFpath = os.path.join(RtsRootDir, "MR4_S3_tumour_and_brain_RTS_AIM_20201125_133250.dcm") # separate ROIs

MR4_S3_SegFpath = os.path.join(SegRootDir, "MR4_S3_brain_SEG_20201030_133110.dcm")
#MR4_S3_SegFpath = os.path.join(SegRootDir, "MR4_S3_tumour_and_brain_SEG_20201105_090359.dcm") # one ROI!
#MR4_S3_SegFpath = os.path.join(SegRootDir, "MR4_S3_tumour_and_brain_RTS_AIM_20201125_133250.dcm") # two ROIs
MR4_S3_SegFpath = os.path.join(SegRootDir, "MR4_S3_tumour_and_brain_SEG_20201105_090359.dcm") # two ROIs
#MR4_S3_SegFpath = os.path.join(SegRootDir, "MR4_S3_tumour_SEG_20201216_085421.dcm") # single frame on slice 10

RoiExportDir = os.path.join(RoiRootDir, "New_ROI_Collections")

PlotExportDir = r'C:\Data\Data copied to Google Drive\ACRIN-FMISO-Brain-011\Results_of_Copy_ROI_use_cases'


# In[13]:


import RoiCopyTools
importlib.reload(RoiCopyTools)
#from RoiCopyTools import CopyRts

from RoiCopyTools import WhichUseCase
from GeneralTools import PrintTitle

# Which case to run?
RunCase = '1a' 
#RunCase = '1b'
#RunCase = '2a' # ok
#RunCase = '2b' # ok
#RunCase = '3a-i' # ok
#RunCase = '3a-ii' # ok
#RunCase = '3b-i' # ok
#RunCase = '3b-ii' # ok
#RunCase = '5' # ok


RunCases = ['1a', '1b', '2a', '2b', '3a-i', '3a-ii', '3b-i', '3b-ii', '5']

for RunCase in RunCases:

    """
    ****************************************************
    Case 1a/b
    ****************************************************
    """
    if '1' in RunCase:
        # Use Case 1a/b:
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        #SrcSegFpath = deepcopy(MR4_S9_TandB_SegFpath)
        SrcRtsFpath = deepcopy(MR4_S9_RtsFpath)

        FromSliceNum = 26
        #FromSegLabel = 'tumour'
        FromRtsLabel = 'tumour' #?

        TrgDcmDir = deepcopy(SrcDcmDir)
        #TrgSegFpath = deepcopy(SrcSegFpath)
        #TrgSegFpath = ''
        TrgRtsFpath = deepcopy(SrcRtsFpath)
        #TrgRtsFpath = ''

        SrcLabel = 'S9'
        TrgLabel = 'S9'
    """
    ****************************************************
    """

    """
    ****************************************************
    Case 2a/b
    ****************************************************
    """
    if '2' in RunCase:
        # Use Case 2a/b:
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        #SrcSegFpath = deepcopy(MR4_S9_TandB_SegFpath)
        SrcRtsFpath = deepcopy(MR4_S9_RtsFpath)

        FromSliceNum = 26
        #FromSegLabel = 'tumour'
        FromRtsLabel = 'tumour' #?

        TrgDcmDir = deepcopy(MR4_S5_DicomDir)
        #TrgSegFpath = deepcopy(MR4_S5_SegFpath)
        #TrgSegFpath = ''
        TrgRtsFpath = deepcopy(MR4_S5_RtsFpath)
        #TrgRtsFpath = ''

        SrcLabel = 'S9'
        TrgLabel = 'S5'
    """
    ****************************************************
    """


    """
    ****************************************************
    Case 3a/b-i/ii
    ****************************************************
    """
    if '3' in RunCase:
        if 'ii' in RunCase:
            # Use Case 3a/b-ii.
            SrcDcmDir = deepcopy(MR4_S3_DicomDir)
            SrcSegFpath = deepcopy(MR4_S3_SegFpath)
            SrcRtsFpath = deepcopy(MR4_S3_RtsFpath)

            FromSliceNum = 11
            #FromSegLabel = 'tumour'
            FromRtsLabel = 'tumour' #?

            TrgDcmDir = deepcopy(MR4_S9_DicomDir)
            #TrgSegFpath = deepcopy(MR4_S9_TandB_SegFpath)
            #TrgSegFpath = ''
            TrgRtsFpath = deepcopy(MR4_S9_RtsFpath)
            #TrgRtsFpath = ''

            SrcLabel = 'S3'
            TrgLabel = 'S9'
        else:
            # Use Case 3a/b-i.
            SrcDcmDir = deepcopy(MR4_S9_DicomDir)
            #SrcSegFpath = deepcopy(MR4_S9_TandB_SegFpath)
            SrcRtsFpath = deepcopy(MR4_S9_RtsFpath)

            FromSliceNum = 25
            #FromSegLabel = 'tumour'
            FromRtsLabel = 'tumour' #?

            TrgDcmDir = deepcopy(MR4_S3_DicomDir)
            #TrgSegFpath = deepcopy(MR4_S3_TandB_SegFpath)
            #TrgSegFpath = ''

            SrcLabel = 'S9'
            TrgLabel = 'S3'
    """
    ****************************************************
    """

    """
    ****************************************************
    Case 5
    ****************************************************
    """
    if '5' in RunCase:
        # Use Case 3a/b-ii.
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        SrcSegFpath = deepcopy(MR4_S9_SegFpath)
        SrcRtsFpath = deepcopy(MR4_S9_RtsFpath)

        FromSliceNum = 23
        FromSegLabel = 'tumour'
        FromRtsLabel = 'tumour' #?

        TrgDcmDir = deepcopy(MR12_S8_DicomDir)
        TrgSegFpath = ''
        TrgRtsFpath = ''

        SrcLabel = 'MR4_S9'
        TrgLabel = 'MR12_S8'

    """
    ****************************************************
    """

    # If making a Direct copy, always copy to frame number 0:
    if 'a' in RunCase:
        # Direct copy.  Always copy to the first slice in Target:
        ToSliceNum = 0
    else:
        # Relationship-preserving copy.
        ToSliceNum = None



    LogToConsole = True
    LogToConsole = False

    PrintTitle(f'\n\nTesting UseCase {RunCase}:\n')
    
    if isinstance(ToSliceNum, int):
        print(f'Copying the Source contour on slice {FromSliceNum} in',
              f'segment "{FromRtsLabel}" to slice {ToSliceNum} in Target..')
    else:
        print(f'Copying the Source contour on slice {FromSliceNum} in',
              f'segment "{FromRtsLabel}" to Target..')

    if True:
        WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, True)



# # Run on case at a time:

# In[226]:


import RoiCopyTools
importlib.reload(RoiCopyTools)
from RoiCopyTools import CopyRts
from RoiCopyTools import CopySeg

from RoiCopyTools import WhichUseCase
from GeneralTools import PrintTitle
from pydicom import dcmread

# Which case to run?
RunCase = '1a' 
RunCase = '1b'
#RunCase = '2a' # ok
#RunCase = '2b' # ok
#RunCase = '3a-i' # ok
#RunCase = '3a-ii' # ok
#RunCase = '3b-i' # ok
#RunCase = '3b-ii' # ok
#RunCase = '5' # ok

# Copy contour or segmentation?
Copy = 'contour'
Copy = 'segmentation'



"""
****************************************************
Case 1a/b
****************************************************
"""
if '1' in RunCase:
    # Use Case 1a/b:
    
    SrcDcmDir = deepcopy(MR4_S9_DicomDir)
    TrgDcmDir = deepcopy(MR4_S9_DicomDir)
    
    FromSliceNum = 26
    
    if Copy == 'contour':
        SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
        FromRoiLabel = 'tumour' #?
        
        TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
        #TrgRoiFpath = ''
    else:
        SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
        FromRoiLabel = 'tumour'
    
        TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
        #TrgRoiFpath = ''
    
    SrcLabel = 'S9'
    TrgLabel = 'S9'
"""
****************************************************
"""


"""
****************************************************
Case 2a/b
****************************************************
"""
if '2' in RunCase:
    # Use Case 2a/b:
    
    SrcDcmDir = deepcopy(MR4_S9_DicomDir)
    TrgDcmDir = deepcopy(MR4_S5_DicomDir)
    
    FromSliceNum = 26
    
    if Copy == 'contour':
        SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
        FromRoiLabel = 'tumour' #?
        
        TrgRoiFpath = deepcopy(MR4_S5_RtsFpath)
        #TrgRoiFpath = ''
    else:
        SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
        FromRoiLabel = 'tumour'
    
        TrgRoiFpath = deepcopy(MR4_S5_SegFpath)
        #TrgRoiFpath = ''
    
    SrcLabel = 'S9'
    TrgLabel = 'S5'
"""
****************************************************
"""


"""
****************************************************
Case 3a/b-i/ii
****************************************************
"""
if '3' in RunCase:
    if 'ii' in RunCase:
        # Use Case 3a/b-ii.
        
        SrcDcmDir = deepcopy(MR4_S3_DicomDir)
        TrgDcmDir = deepcopy(MR4_S9_DicomDir)
        
        FromSliceNum = 11
        
        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S3_RtsFpath)
            FromRoiLabel = 'tumour' #?
            
            TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
            #TrgRoiFpath = ''
            
        else:
            SrcRoiFpath = deepcopy(MR4_S3_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
            #TrgRoiFpath = ''
            
        SrcLabel = 'S3'
        TrgLabel = 'S9'
        
    else:
        # Use Case 3a/b-i.
        
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S3_DicomDir)
        
        FromSliceNum = 25
        
        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            FromRoiLabel = 'tumour' #?
            
            TrgRoiFpath = deepcopy(MR4_S3_RtsFpath)
            #TrgRoiFpath = ''
            
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = deepcopy(MR4_S3_SegFpath)
            TrgRoiFpath = ''

        SrcLabel = 'S9'
        TrgLabel = 'S3'
"""
****************************************************
"""


"""
****************************************************
Case 5
****************************************************
"""
if '5' in RunCase:
    # Use Case 3a/b-ii.
    
    SrcDcmDir = deepcopy(MR4_S9_DicomDir)
    TrgDcmDir = deepcopy(MR12_S8_DicomDir)
    
    FromSliceNum = 23
    
    if Copy == 'contour':
        SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
        FromRoiLabel = 'tumour' #?
        
        TrgRoiFpath = ''
    else:
        SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
        FromRoiLabel = 'tumour'
        
        TrgRoiFpath = ''

    SrcLabel = 'MR4_S9'
    TrgLabel = 'MR12_S8'

"""
****************************************************
"""

# If making a Direct copy, always copy to frame number 0:
if 'a' in RunCase:
    # Direct copy.  Always copy to the first slice in Target:
    ToSliceNum = 0
else:
    # Relationship-preserving copy.
    ToSliceNum = None



LogToConsole = True
LogToConsole = False

PrintTitle(f'\n\nRunning UseCase {RunCase}:\n')

if isinstance(ToSliceNum, int):
    if Copy == 'contour':
        roi = 'ROI'
    else:
        roi = 'segment'
        
    print(f'Copying the Source {Copy} on slice {FromSliceNum} in',
          f'{roi} "{FromRoiLabel}" to slice {ToSliceNum} in Target..')
else:
    print(f'Copying the Source {Copy} on slice {FromSliceNum} in',
          f'{roi} "{FromRoiLabel}" to Target..')

if True:
    WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, True)


# Import the RTS or SEGs:
SrcRoi = dcmread(SrcRoiFpath)
#SrcRoi = dcmread(MR4_S3_SegFpath)
if TrgRoiFpath:
    TrgRoi = dcmread(TrgRoiFpath)
else:
    TrgRoi = None
    
    if Copy == 'contour':
        print('\nA Target RTS was not provided so the Source RTS will',
              'be used as a template.')
    else:
        print('\nA Target SEG was not provided so the Source SEG will',
              'be used as a template.')

if Copy == 'contour':
    NewTrgRoi = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
                        TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)
    
    ##ListOfLabmapIms, ListOfPixArrs, ListOfFrameToSliceInds,\
    ##ListOfPlotTitles = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
    ##                           TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)
    
    #LabmapImToCopy,\
    #RegImFilt = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
    #                    TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)

else:
    NewTrgRoi = CopySeg(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
                        TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)


# In[24]:


### Timings for Case:

1a RTS = 2.2 s
1a SEG = 2.1 s
1b RTS = 1.9 s
1b SEG = 2.3 s
2a RTS = 2.5 s
2a SEG = 3.7 s
2b RTS = 2.1 s
2b SEG = 2.9 s
3a-i RTS = 2.6 s
3a-i SEG = 1.8 s
3a-ii RTS = 2.7 s
3a-ii SEG = 2.4 s
3b-i RTS = 2.4 s
3b-i SEG = 1.9 s
3b-ii RTS = 2.5 s
3b-ii SEG = 2.2 s
5 RTS = 12.8 s
5 SEG = 12.4 s


# # Plot pixel arrays:

# In[205]:


import ImageTools
importlib.reload(ImageTools)

from ImageTools import TransformImage
from ImageTools import BinaryThresholdImage
from ConversionTools import Image2PixArr

import PlottingTools
importlib.reload(PlottingTools)
from PlottingTools import PlotPixelArrays

Thresh = 1E-6
#Thresh = 0.0005
#Thresh = 0.1
#Thresh = 0.25
#Thresh = 0.5

ExportPlot=False
ExportPlot=True

if ExportPlot:
    dpi = 120


#Threshs = [1E-6, 0.0005, 0.1, 0.25, 0.5]

#for Thresh in Threshs:

# Transform LabmapImToCopy using RegImFilt:
TxLabmapImToCopyPreBinary = TransformImage(Im=LabmapImToCopy, 
                                           RegImFilt=RegImFilt)

# Binary threshold TxLabmapImToCopyPreBinary:
TxLabmapImToCopyPostBinary = BinaryThresholdImage(Im=TxLabmapImToCopyPreBinary,
                                                  Thresh=Thresh)

# Convert LabmapImToCopy, TxLabmapImToCopyPreBinary
# and TxLabmapImToCopyPostBinary to pixel arrays:
PixArrPreTx,F2Sinds = Image2PixArr(LabmapIm=LabmapImToCopy)

TxPixArrPreBinary,F2SindsPreBinary = Image2PixArr(LabmapIm=TxLabmapImToCopyPreBinary)

TxPixArrPostBinary,F2SindsPostBinary = Image2PixArr(LabmapIm=TxLabmapImToCopyPostBinary)

ListOfLabmapIms = [LabmapImToCopy, TxLabmapImToCopyPreBinary, TxLabmapImToCopyPostBinary]

ListOfPixArrs = [PixArrPreTx, TxPixArrPreBinary, TxPixArrPostBinary]

ListOfFrameToSliceInds = [F2Sinds, F2SindsPreBinary, F2SindsPostBinary]

ListOfPlotTitles = ['PreTx', 'TxPreBinary', 'TxBinary']

PlotPixelArrays(ListOfPixArrs=ListOfPixArrs, 
                 ListOfFrameToSliceInds=ListOfFrameToSliceInds, 
                 ListOfPlotTitles=ListOfPlotTitles,
                 AddTxt=f'Thresh = {Thresh}',
                 ExportPlot=ExportPlot, ExportDir=PlotExportDir, 
                 dpi=dpi)


# In[ ]:





# In[197]:


import GeneralTools
importlib.reload(GeneralTools)
from GeneralTools import UniqueItems

#UniqueItems(np.array([23, 24, 25, 26, 27, 28, 29, 26]))

#print('\n', TxPixArrPreBinary.shape)

#print('\n', TxPixArrPreBinary.flatten().shape)

PreTxUnique = UniqueItems(PixArrPreTx.flatten())

TxPreBinaryUnique = UniqueItems(TxPixArrPreBinary.flatten())

TxPostBinaryUnique = UniqueItems(TxPixArrPostBinary.flatten())

print(f'\nUnique items in PixArrPreTx (N = {len(PreTxUnique)}) = {PreTxUnique}')
print(f'min = {np.min(PreTxUnique)}, max = {np.max(PreTxUnique)}, mean = {np.mean(PreTxUnique)}')

print(f'\nUnique items in TxPixArrPreBinary (N = {len(TxPreBinaryUnique)}) = {TxPreBinaryUnique}')
print(f'min = {np.min(TxPreBinaryUnique)}, max = {np.max(TxPreBinaryUnique)}, mean = {np.mean(TxPreBinaryUnique)}')

print(f'\nUnique items in TxPixArrPostBinary (N = {len(TxPostBinaryUnique)}) = {TxPostBinaryUnique}')
print(f'min = {np.min(TxPixArrPostBinary)}, max = {np.max(TxPixArrPostBinary)}, mean = {np.mean(TxPixArrPostBinary)}')


# In[64]:


enumerate(['a', 'b', 'c', 'd'])


# In[67]:


from DicomTools import GetRoiLabels

labels = GetRoiLabels(dcmread(SrcRoiFpath))
labels


# In[70]:


for i,label in enumerate(labels):
    print(i, label)


# In[72]:


[i for i, label in enumerate(labels) if 'tumour' in label]


# In[114]:


for i, mask in enumerate(np.zeros((1, 5, 5))):
    print(i)
    print(mask)


# In[115]:


for i, mask in enumerate(np.zeros((3, 5, 5))):
    print(i)
    print(mask)


# # Plot pixel arrays from SEGs:

# In[231]:


import PlottingTools
importlib.reload(PlottingTools)
from PlottingTools import PlotPixelArraysFromSegs

ExportPlot=False
ExportPlot=True

LogToConsole = False
LogToConsole = True

if ExportPlot:
    dpi = 120
    
    

if TrgRoi:
    ListOfSegs = [SrcRoi, TrgRoi, NewTrgRoi]
    
    ListOfDicomDirs = [SrcDcmDir, TrgDcmDir, TrgDcmDir]
    
    ListOfPlotTitles = ['Source', 'Target', 'New Target']
else:
    ListOfSegs = [SrcRoi, NewTrgRoi]
    
    ListOfDicomDirs = [SrcDcmDir, TrgDcmDir]
    
    ListOfPlotTitles = ['Source', 'New Target']
    

TxtToAdd = f'(RunCase = {RunCase}, \nFromSliceNum = {FromSliceNum}, \nToSliceNum = {ToSliceNum})'
    
PlotPixelArraysFromSegs(ListOfSegs, ListOfDicomDirs, ListOfPlotTitles,
                        SegLabel=FromRoiLabel, AddTxt=TxtToAdd, 
                        ExportPlot=ExportPlot, ExportDir=PlotExportDir,
                        dpi=dpi, LogToConsole=LogToConsole)


# # Run several SEG cases and plot pixel arrays sequentially:

# In[243]:


import RoiCopyTools
importlib.reload(RoiCopyTools)

import PlottingTools
importlib.reload(PlottingTools)

from RoiCopyTools import CopyRts
from RoiCopyTools import CopySeg
from PlottingTools import PlotPixelArraysFromSegs

from RoiCopyTools import WhichUseCase
from GeneralTools import PrintTitle
from pydicom import dcmread

# Which case to run?
RunCase = '1a' 
RunCase = '1b'
#RunCase = '2a' # ok
#RunCase = '2b' # ok
#RunCase = '3a-i' # ok
#RunCase = '3a-ii' # ok
#RunCase = '3b-i' # ok
#RunCase = '3b-ii' # ok
#RunCase = '5' # ok

# Copy contour or segmentation?
Copy = 'contour'
Copy = 'segmentation'


RunCases = ['1a', '1b', '2a', '2b', '3a-i', '3a-ii', '3b-i', '3b-ii', '5']
#RunCases = ['3a-ii', '3b-i', '3b-ii', '5']
#RunCases = ['3a-ii']

for RunCase in RunCases:


    """
    ****************************************************
    Case 1a/b
    ****************************************************
    """
    if '1' in RunCase:
        # Use Case 1a/b:

        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S9_DicomDir)

        FromSliceNum = 26

        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            FromRoiLabel = 'tumour' #?

            TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
            #TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
            #TrgRoiFpath = ''

        SrcLabel = 'S9'
        TrgLabel = 'S9'
    """
    ****************************************************
    """


    """
    ****************************************************
    Case 2a/b
    ****************************************************
    """
    if '2' in RunCase:
        # Use Case 2a/b:

        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S5_DicomDir)

        FromSliceNum = 26

        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            FromRoiLabel = 'tumour' #?

            TrgRoiFpath = deepcopy(MR4_S5_RtsFpath)
            #TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = deepcopy(MR4_S5_SegFpath)
            #TrgRoiFpath = ''

        SrcLabel = 'S9'
        TrgLabel = 'S5'
    """
    ****************************************************
    """


    """
    ****************************************************
    Case 3a/b-i/ii
    ****************************************************
    """
    if '3' in RunCase:
        if 'ii' in RunCase:
            # Use Case 3a/b-ii.

            SrcDcmDir = deepcopy(MR4_S3_DicomDir)
            TrgDcmDir = deepcopy(MR4_S9_DicomDir)

            FromSliceNum = 11

            if Copy == 'contour':
                SrcRoiFpath = deepcopy(MR4_S3_RtsFpath)
                FromRoiLabel = 'tumour' #?

                TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
                #TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S3_SegFpath)
                FromRoiLabel = 'tumour'

                TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
                #TrgRoiFpath = ''

            SrcLabel = 'S3'
            TrgLabel = 'S9'

        else:
            # Use Case 3a/b-i.

            SrcDcmDir = deepcopy(MR4_S9_DicomDir)
            TrgDcmDir = deepcopy(MR4_S3_DicomDir)

            FromSliceNum = 25

            if Copy == 'contour':
                SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
                FromRoiLabel = 'tumour' #?

                TrgRoiFpath = deepcopy(MR4_S3_RtsFpath)
                #TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
                FromRoiLabel = 'tumour'

                TrgRoiFpath = deepcopy(MR4_S3_SegFpath)
                TrgRoiFpath = ''

            SrcLabel = 'S9'
            TrgLabel = 'S3'
    """
    ****************************************************
    """


    """
    ****************************************************
    Case 5
    ****************************************************
    """
    if '5' in RunCase:
        # Use Case 3a/b-ii.

        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR12_S8_DicomDir)

        FromSliceNum = 23

        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            FromRoiLabel = 'tumour' #?

            TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = ''

        SrcLabel = 'MR4_S9'
        TrgLabel = 'MR12_S8'

    """
    ****************************************************
    """

    # If making a Direct copy, always copy to frame number 0:
    if 'a' in RunCase:
        # Direct copy.  Always copy to the first slice in Target:
        ToSliceNum = 0
    else:
        # Relationship-preserving copy.
        ToSliceNum = None



    LogToConsole = True
    LogToConsole = False

    PrintTitle(f'\n\nRunning UseCase {RunCase}:\n')

    if isinstance(ToSliceNum, int):
        if Copy == 'contour':
            roi = 'ROI'
        else:
            roi = 'segment'

        print(f'Copying the Source {Copy} on slice {FromSliceNum} in',
              f'{roi} "{FromRoiLabel}" to slice {ToSliceNum} in Target..')
    else:
        print(f'Copying the Source {Copy} on slice {FromSliceNum} in',
              f'{roi} "{FromRoiLabel}" to Target..')

    if True:
        WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, True)


    # Import the RTS or SEGs:
    SrcRoi = dcmread(SrcRoiFpath)
    #SrcRoi = dcmread(MR4_S3_SegFpath)
    if TrgRoiFpath:
        TrgRoi = dcmread(TrgRoiFpath)
    else:
        TrgRoi = None

        if Copy == 'contour':
            print('\nA Target RTS was not provided so the Source RTS will',
                  'be used as a template.')
        else:
            print('\nA Target SEG was not provided so the Source SEG will',
                  'be used as a template.')

    if Copy == 'contour':
        NewTrgRoi = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
                            TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)

        ##ListOfLabmapIms, ListOfPixArrs, ListOfFrameToSliceInds,\
        ##ListOfPlotTitles = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
        ##                           TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)

        #LabmapImToCopy,\
        #RegImFilt = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
        #                    TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)

    else:
        NewTrgRoi = CopySeg(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
                            TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)
        
        
        
        
    """ Plot Pixel arrays """

    ExportPlot=False
    ExportPlot=True

    LogToConsole = False
    LogToConsole = True

    if ExportPlot:
        dpi = 120



    if TrgRoi:
        ListOfRois = [SrcRoi, TrgRoi, NewTrgRoi]

        ListOfDicomDirs = [SrcDcmDir, TrgDcmDir, TrgDcmDir]

        ListOfPlotTitles = ['Source', 'Target', 'New Target']
    else:
        ListOfRois = [SrcRoi, NewTrgRoi]

        ListOfDicomDirs = [SrcDcmDir, TrgDcmDir]

        ListOfPlotTitles = ['Source', 'New Target']


    TxtToAdd = f'(RunCase = {RunCase}, \nFromSliceNum = {FromSliceNum}, \nToSliceNum = {ToSliceNum})'

    PlotPixelArraysFromSegs(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                            SegLabel=FromRoiLabel, AddTxt=TxtToAdd, 
                            ExportPlot=ExportPlot, ExportDir=PlotExportDir,
                            dpi=dpi, LogToConsole=LogToConsole)
    
    
print('\nAll iterations complete.')


# In[236]:


NewTrgRoi


# In[237]:


TrgRoi


# # 04/12:
# 
# # Problem with SEG Case 1b, 2b, 3b

# In[ ]:





# # Run several RTS cases and plot contours sequentially:

# In[41]:


import RoiCopyTools
importlib.reload(RoiCopyTools)

import PlottingTools
importlib.reload(PlottingTools)

from RoiCopyTools import CopyRts
from RoiCopyTools import CopySeg
from PlottingTools import PlotContoursFromRtss
from PlottingTools import PlotPixelArraysFromSegs

from RoiCopyTools import WhichUseCase
from GeneralTools import PrintTitle
from pydicom import dcmread

# Which case to run?
RunCase = '1a' 
RunCase = '1b'
#RunCase = '2a' # ok
#RunCase = '2b' # ok
#RunCase = '3a-i' # ok
#RunCase = '3a-ii' # ok
#RunCase = '3b-i' # ok
#RunCase = '3b-ii' # ok
#RunCase = '5' # ok

# Copy contour or segmentation?
Copy = 'contour'
#Copy = 'segmentation'


#RunCases = ['1a', '1b', '2a', '2b', '3a-i', '3a-ii', '3b-i', '3b-ii', '5']
#RunCases = ['3a-ii', '3b-i', '3b-ii', '5']
#RunCases = ['3a-ii']
#RunCases = ['1b']
#RunCases = ['1a']
RunCases = ['3a-i', '3a-ii', '3b-i', '3b-ii', '5']
RunCases = ['3b-i']

LogToConsoleForRoiCopy = False
#LogToConsoleForRoiCopy = True

LogToConsoleForPlot = False
#LogToConsoleForPlot = True

PlotAllSlices = False # only plot slices that contain a ROI in at least one of the datasets
#PlotAllSlices = True

ExportPlot=False
ExportPlot=True

if Copy == 'contour':
    roi = 'ROI'
else:
    roi = 'segment'
    

for RunCase in RunCases:

    """
    ****************************************************
    Case 1a/b
    ****************************************************
    """
    if '1' in RunCase:
        # Use Case 1a/b:

        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S9_DicomDir)

        #FromSliceNum = 26
        #FromSliceNum = 29
        #FromSliceNum = 23
        
        if 'a' in RunCase:
            FromSliceNum = 23
            ToSliceNum = 29
        else:
            FromSliceNum = 24
            ToSliceNum = None

        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            FromRoiLabel = 'tumour' #?

            TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
            #TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
            #TrgRoiFpath = ''

        SrcLabel = 'S9'
        TrgLabel = 'S9'
    """
    ****************************************************
    """


    """
    ****************************************************
    Case 2a/b
    ****************************************************
    """
    if '2' in RunCase:
        # Use Case 2a/b:

        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S5_DicomDir)

        #FromSliceNum = 26
        #FromSliceNum = 29
        #FromSliceNum = 23
        
        if 'a' in RunCase:
            FromSliceNum = 23
            ToSliceNum = 22
        else:
            FromSliceNum = 27
            ToSliceNum = None

        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            FromRoiLabel = 'tumour' #?

            TrgRoiFpath = deepcopy(MR4_S5_RtsFpath)
            #TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = deepcopy(MR4_S5_SegFpath)
            #TrgRoiFpath = ''

        SrcLabel = 'S9'
        TrgLabel = 'S5'
    """
    ****************************************************
    """


    """
    ****************************************************
    Case 3a/b-i/ii
    ****************************************************
    """
    if '3' in RunCase:
        if 'ii' in RunCase:
            # Use Case 3a/b-ii.

            SrcDcmDir = deepcopy(MR4_S3_DicomDir)
            TrgDcmDir = deepcopy(MR4_S9_DicomDir)

            #FromSliceNum = 11
            
            if 'a' in RunCase:
                FromSliceNum = 11
                ToSliceNum = 26
            else:
                FromSliceNum = 10 # ROI copied to slices 24-25
                FromSliceNum = 11 # ROI copied to slices 26-28
                ToSliceNum = None

            if Copy == 'contour':
                SrcRoiFpath = deepcopy(MR4_S3_RtsFpath)
                FromRoiLabel = 'tumour' #?

                TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
                #TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S3_SegFpath)
                FromRoiLabel = 'tumour'

                TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
                #TrgRoiFpath = ''

            SrcLabel = 'S3'
            TrgLabel = 'S9'

        else:
            # Use Case 3a/b-i.

            SrcDcmDir = deepcopy(MR4_S9_DicomDir)
            TrgDcmDir = deepcopy(MR4_S3_DicomDir)

            #FromSliceNum = 25
            
            if 'a' in RunCase:
                FromSliceNum = 25
                ToSliceNum = 20
            else:
                FromSliceNum = 23 # no ROI copied
                FromSliceNum = 24 # no ROI copied
                FromSliceNum = 25 # contour copied to slice 10
                FromSliceNum = 26 # no ROI copied
                FromSliceNum = 27 # ROI copied to slice 11
                FromSliceNum = 28 # no ROI copied
                FromSliceNum = 29 # no ROI copied
                ToSliceNum = None

            if Copy == 'contour':
                SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
                FromRoiLabel = 'tumour' #?

                TrgRoiFpath = deepcopy(MR4_S3_RtsFpath)
                #TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
                FromRoiLabel = 'tumour'

                TrgRoiFpath = deepcopy(MR4_S3_SegFpath)
                TrgRoiFpath = ''

            SrcLabel = 'S9'
            TrgLabel = 'S3'
    """
    ****************************************************
    """


    """
    ****************************************************
    Case 5
    ****************************************************
    """
    if '5' in RunCase:
        # Use Case 3a/b-ii.

        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR12_S8_DicomDir)

        FromSliceNum = 23 # contour copied to slices 12-14

        if Copy == 'contour':
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            FromRoiLabel = 'tumour' #?

            TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            FromRoiLabel = 'tumour'

            TrgRoiFpath = ''

        SrcLabel = 'MR4_S9'
        TrgLabel = 'MR12_S8'

    """
    ****************************************************
    """

    ## If making a Direct copy, always copy to frame number 0:
    #if 'a' in RunCase:
    #    # Direct copy.  Always copy to the first slice in Target:
    #    #ToSliceNum = 0
    #    ToSliceNum = 22
    #else:
    #    # Relationship-preserving copy.
    #    ToSliceNum = None


    PrintTitle(f'\n\nRunning UseCase {RunCase}:\n')

    if isinstance(ToSliceNum, int):
        print(f'Copying the Source {Copy} on slice {FromSliceNum} in',
              f'{roi} "{FromRoiLabel}" to slice {ToSliceNum} in Target..')
    else:
        print(f'Copying the Source {Copy} on slice {FromSliceNum} in',
              f'{roi} "{FromRoiLabel}" to Target..')

    if True:
        WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, True)


    # Import the RTS or SEGs:
    SrcRoi = dcmread(SrcRoiFpath)
    #SrcRoi = dcmread(MR4_S3_SegFpath)
    if TrgRoiFpath:
        TrgRoi = dcmread(TrgRoiFpath)
    else:
        TrgRoi = None

        if Copy == 'contour':
            print('\nA Target RTS was not provided so the Source RTS will',
                  'be used as a template.')
        else:
            print('\nA Target SEG was not provided so the Source SEG will',
                  'be used as a template.')

    if Copy == 'contour':
        print(f'\n\nInputs to CopyRts:\n FromRoiLabel = {FromRoiLabel}\n',
              f'FromSliceNum = {FromSliceNum}\n ToSliceNum = {ToSliceNum}')
        
        NewTrgRoi = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
                            TrgDcmDir, TrgRoi, ToSliceNum, LogToConsoleForRoiCopy)

        ##ListOfLabmapIms, ListOfPixArrs, ListOfFrameToSliceInds,\
        ##ListOfPlotTitles = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
        ##                           TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)

        #LabmapImToCopy,\
        #RegImFilt = CopyRts(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
        #                    TrgDcmDir, TrgRoi, ToSliceNum, LogToConsole)

    else:
        NewTrgRoi = CopySeg(SrcRoi, FromRoiLabel, SrcDcmDir, FromSliceNum, 
                            TrgDcmDir, TrgRoi, ToSliceNum, LogToConsoleForRoiCopy)
        
        
        
        
    """ Plot Contours """

    if ExportPlot:
        dpi = 120
    else:
        dpi = 80



    if TrgRoi:
        ListOfRois = [SrcRoi, TrgRoi, NewTrgRoi]

        ListOfDicomDirs = [SrcDcmDir, TrgDcmDir, TrgDcmDir]

        ListOfPlotTitles = ['Source', 'Original Target', 'New Target']
    else:
        ListOfRois = [SrcRoi, NewTrgRoi]

        ListOfDicomDirs = [SrcDcmDir, TrgDcmDir]

        ListOfPlotTitles = ['Source', 'New Target']


    TxtToAdd = f'(RunCase = {RunCase}, \nFromSliceNum = {FromSliceNum}, \nToSliceNum = {ToSliceNum})'
    
    if Copy == 'contour':
        PlotContoursFromRtss(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                             RoiLabel=FromRoiLabel, PlotAllSlices=PlotAllSlices,
                             AddTxt=TxtToAdd, ExportPlot=ExportPlot, 
                             ExportDir=PlotExportDir, dpi=dpi, 
                             LogToConsole=LogToConsoleForPlot)
        
    else:
        PlotPixelArraysFromSegs(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                                SegLabel=FromRoiLabel, PlotAllSlices=PlotAllSlices, 
                                AddTxt=AddTxt, ExportPlot=ExportPlot, 
                                ExportDir=PlotExportDir, dpi=dpi, 
                                LogToConsole=LogToConsoleForPlot)
    
    
print('\nAll iterations complete.')


# In[66]:


CSs = NewTrgRoi.ROIContourSequence[0].ContourSequence

for CS in CSs:
    print(f'{int(len(CS.ContourImageSequence[0].ContourData)/3)}')


# In[75]:


CSs = NewTrgRoi.ROIContourSequence[0].ContourSequence

for i in len(CSs):
    print(f'{int(len(NewTrgRoi.ROIContourSequence[0].ContourSequence[i].ContourImageSequence[0].ContourData)/3)}')


# In[67]:


CSs = NewTrgRoi.ROIContourSequence[0].ContourSequence

for CS in CSs:
    print(f'{int(len(CS.ContourData)/3)}')


# # RTS:
# 
# # 1b doesn't work

# In[76]:


import RtsTools
importlib.reload(RtsTools)
from RtsTools import GetPtsByRoi

PtsByRoi, C2SindsByRoi = GetPtsByRoi(NewTrgRoi, TrgDcmDir)

len(PtsByRoi)


# In[57]:


from DicomTools import GetRoiNum

RoiNum = GetRoiNum(NewTrgRoi, 'tumour')
RoiNum


# In[58]:


C2SindsByRoi[RoiNum]


# In[60]:


for contour in PtsByRoi[RoiNum]:
    print(len(contour))


# In[64]:


TrgRoi


# In[69]:


SrcRoi


# In[74]:


SrcRoi.ROIContourSequence[0].ContourSequence[0].ContourImageSequence[0].ContourData


# In[103]:


import ConversionTools
importlib.reload(ConversionTools)
from ImageTools import GetImageAttributes
from ConversionTools import Contour2Indices
from ConversionTools import Indices2Points

SrcSize, SrcSpacings, SrcST,SrcIPPs, SrcDirs = GetImageAttributes(DicomDir=SrcDcmDir)

#pts = [[10,3,5], [11,4,5], [14,2,5]]

pts = [[7.19289933575097, 13.2608461299651, 1.01866843393437], 
       [6.64416507522526, 14.3224640990391, 0.72596709348039], 
       [6.09543081469955, 15.3840820681132, 0.43326575302642], 
       [5.27232942370588, 15.9271410276028, 0.32569477260944], 
       [4.72359516312892, 16.7264169981465, 0.11586368972146], 
       [3.90049377213528, 17.2694759576362, 0.00829270930447]]

inds = Contour2Indices(pts, SrcIPPs[0], SrcDirs, SrcSpacings)

inds


# In[104]:


Indices2Points(inds, SrcIPPs[0], SrcDirs, SrcSpacings)


# In[ ]:





# # Run several RTS/SEG cases and plot segmentations sequentially:

# In[175]:


import RoiCopyTools
importlib.reload(RoiCopyTools)

import PlottingTools
importlib.reload(PlottingTools)

from RoiCopyTools import CopyRoi
from RoiCopyTools import ExportTrgRoi
from RoiCopyTools import ErrorCheckRoi
from PlottingTools import PlotContoursFromListOfRtss_v1
from PlottingTools import PlotPixArrsFromListOfSegs_v1

from RoiCopyTools import WhichUseCase
from GeneralTools import PrintTitle
from pydicom import dcmread

# Which cases to run?
#RunCases = ['1a', 2a', '2b', '3a-i', '3a-ii', '3b-i', '3b-ii', '5']
#RunCases = ['3a-ii', '3b-i', '3b-ii', '5']
#RunCases = ['3a-ii']
#RunCases = ['1a']
#RunCases = ['3a-i', '3a-ii', '3b-i', '3b-ii', '5']
#RunCases = ['3b-i'] # <-- problems due to lack of segmentations when resampling to lower res (09/12/20)
#RunCases = ['3b-ii']

# Previously problemmatic cases as of 10/12:
######RunCases = ['Case1A_RTS'] # RTS - Right half of contour appears cropped - ISSUE RESOLVED
#####RunCases = ['Case2a_RTS'] # RTS - ROI import gets stuck - ISSUE RESOLVED
#####RunCases = ['Case2B_RTS'] # RTS - ROI import gets stuck - ISSUE RESOLVED
#####RunCases = ['Case3A-i_RTS'] # RTS - Bottom half of contour appears cropped - ISSUE RESOLVED
#####RunCases = ['Case3B-i_RTS'] # RTS - Bottom (angled) half of contour appears cropped (TrgRoi was None) - ISSUE RESOLVED
#####RunCases = ['Case5_RTS'] # RTS - RUA tool reports “missing dependencies" - ISSUE RESOLVED
#####RunCases = ['Case3A-i_SEG'] # SEG - RUA tool reports “missing dependencies" - ISSUE RESOLVED (but get "missing
# dependencies" if no TrgSeg used...)
#####RunCases = ['Case5_SEG'] # SEG - RUA tool reports “missing dependencies" - ISSUE RESOLVED
#####RunCases = ['Case3B-ii_SEG'] # SEG - 2-3 pixels seem to be missing (also in plot) - THE MISSING PIXELS ARE IN THE
# SOURCE SEG!  CHANGED TO FromSliceNum 11 (which doesn't have missing pixels)

# Problemmatic cases as of 15/12:
RunCases = ['Case2B_SEG'] # SEG - No segmentations visible in viewer if TrgSeg is used (which is a RTS-to-SEG 
# conversion) OR if no TrgSeg is used.
RunCases = ['Case3B-i_SEG'] # SEG - No segmentations visible in viewer if TrgSeg is used (which is a RTS-to-SEG 
# conversion) OR if no TrgSeg is used.

#RunCases = ['Case5_SEG']
#RunCases = ['Case3A-i_SEG']

IsOrigTrg = True # use available Target RTS/SEG
#IsOrigTrg = False # assume that Target RTS/SEG doesn't yet exist

LogToConsoleForRoiCopy = False
#LogToConsoleForRoiCopy = True

ExportRoi = False
ExportRoi = True

PlotResults = False
PlotResults = True

LogToConsoleForPlot = False
#LogToConsoleForPlot = True

PlotAllSlices = False # only plot slices that contain a ROI in at least one of the datasets
#PlotAllSlices = True

ExportPlot=False
#ExportPlot=True


FromSearchString = 'tumour'
    
for RunCase in RunCases:
    #if 'RTS' in RunCase:
    #    RoiType = 'ROI'
    #else:
    #    RoiType = 'segment'
    
    
    if '1' in RunCase:
        """
        ***********************************************
        Run Case 1A
        ***********************************************
        """
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S9_DicomDir)
        
        if 'RTS' in RunCase:
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
            else:
                TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
            else:
                TrgRoiFpath = ''
                
        FromSliceNum = 23
        ToSliceNum = 29
        
        SrcLabel = 'S9'
        TrgLabel = 'S9'

    
    elif '2' in RunCase:
        """
        ***********************************************
        Run Case 2A/B
        ***********************************************
        """
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S5_DicomDir)

        if 'RTS' in RunCase:
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S5_RtsFpath)
            else:
                TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S5_SegFpath)
            else:
                TrgRoiFpath = ''
            
        if 'A' in RunCase:
            FromSliceNum = 23
            ToSliceNum = 22
        else:
            FromSliceNum = 27 # no segmentations visible in OHIF
            #FromSliceNum = 23 # 15/12 no segmentations visible in OHIF
            ToSliceNum = None

        SrcLabel = 'S9'
        TrgLabel = 'S5'

    
    elif '3' in RunCase:
        """
        ***********************************************
        Run Case 3A/B-i/ii
        ***********************************************
        """
        if 'ii' in RunCase:
            # Run Case 3A/B-ii.

            SrcDcmDir = deepcopy(MR4_S3_DicomDir)
            TrgDcmDir = deepcopy(MR4_S9_DicomDir)

            if 'RTS' in RunCase:
                SrcRoiFpath = deepcopy(MR4_S3_RtsFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
                else:
                    TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S3_SegFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
                else:
                    TrgRoiFpath = ''
            
            if 'A' in RunCase:
                FromSliceNum = 11
                ToSliceNum = 26
            else:
                if 'RTS' in RunCase:
                    FromSliceNum = 10 # ROI copied to slices 24-25
                    #FromSliceNum = 11 # ROI copied to slices 26-28
                else:
                    #FromSliceNum = 10 # segmentation copied to slice 24-25 - some pixels missing in SEG for S3 
                    # (i.e. in Source that get copied to NewTarget)
                    FromSliceNum = 11 # segmentation copied to slices 26-28
                
                ToSliceNum = None
                
            SrcLabel = 'S3'
            TrgLabel = 'S9'

        else:
            # Run Case 3A/B-i.

            SrcDcmDir = deepcopy(MR4_S9_DicomDir)
            TrgDcmDir = deepcopy(MR4_S3_DicomDir)

            if 'RTS' in RunCase:
                SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S3_RtsFpath)
                else:
                    TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S3_SegFpath)
                else:
                    TrgRoiFpath = ''
                
            if 'A' in RunCase:
                FromSliceNum = 25
                ToSliceNum = 20
            else:
                if 'RTS' in RunCase:
                    #FromSliceNum = 23 # no ROI copied - workaround 2 
                    # results in copy to slice 9 (21/12/20)
                    #FromSliceNum = 24 # no ROI copied - workaround 2 
                    # results in copy to slice 10 (21/12/20)
                    FromSliceNum = 25 # contour copied to slice 10
                    #FromSliceNum = 26 # no ROI copied - workaround 2 
                    # results in copy to slice 11 (21/12/20)
                    #FromSliceNum = 27 # ROI copied to slice 11
                    #FromSliceNum = 28 # no ROI copied - workaround 2 
                    # results in copy to slice 11 (21/12/20)
                    #FromSliceNum = 29 # no ROI copied - workaround 2 
                    # results in copy to slice 12 (21/12/20)
                else:
                    #FromSliceNum = 23 # TrgPFFGStoSliceInds = [] - workaround 2 
                    # results in copy to slice 9 (21/12/20)
                    #FromSliceNum = 24 # TrgPFFGStoSliceInds = [] - workaround 2 
                    # results in copy to slice 10 (21/12/20)
                    FromSliceNum = 25 # segmentation copied to slice 10 in plot but 
                    # no segmentation visible in OHIF-Viewer
                    #FromSliceNum = 26 # TrgPFFGStoSliceInds = [] - workaround 2 
                    # results in copy to slice 11 (19/12/20)
                    #FromSliceNum = 27 # segmentation copied to slice 11 in plot but 
                    # no segmentation visible in OHIF-Viewer
                
                ToSliceNum = None

            SrcLabel = 'S9'
            TrgLabel = 'S3'


    
    elif '5' in RunCase:
        """
        ***********************************************
        Run Case 5
        ***********************************************
        """
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR12_S8_DicomDir)
    
        if 'RTS' in RunCase:
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            
            if IsOrigTrg:
                raise Exception('A RTS does not yet exist for this Target.')
            else:
                TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            
            if IsOrigTrg:
                raise Exception('A SEG does not yet exist for this Target.')
            else:
                TrgRoiFpath = ''
            
        FromSliceNum = 23 # contour/segmentation copied to slices 12-14
        
        SrcLabel = 'MR4_S9'
        TrgLabel = 'MR12_S8'
    
    
    else:
        raise Exception('"RunCase" must have a 1, 2, 3, 4 or 5 in the string.')



    PrintTitle(f'\n\nRunning UseCase {RunCase}:\n')

    if isinstance(ToSliceNum, int):
        print(f'Copying the Source ({SrcLabel}) RTS/SEG on slice {FromSliceNum} in the ROI/segment',
              f'matching "{FromSearchString}" to slice {ToSliceNum} in Target ({TrgLabel})..')
    else:
        print(f'Copying the Source ({SrcLabel}) RTS/SEG on slice {FromSliceNum} in the ROI/segment',
              f'matching "{FromSearchString}" to Target ({TrgLabel})..')

    if not LogToConsoleForRoiCopy:
        WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, True)


    # Import the RTS or SEGs:
    SrcRoi = dcmread(SrcRoiFpath)

    if TrgRoiFpath:
        TrgRoi = dcmread(TrgRoiFpath)
    else:
        TrgRoi = None

        if 'RTS' in RunCase:
            print('\nA Target RTS was not provided so the Source RTS will',
                  'be used as a template.')
        else:
            print('\nA Target SEG was not provided so the Source SEG will',
                  'be used as a template.')
    
    
    print(f'\n\nInputs to CopyRoi:\n FromSearchString = {FromSearchString}\n',
              f'FromSliceNum = {FromSliceNum}\n ToSliceNum = {ToSliceNum}')
    
    # NamePrefix for RTS StructureSetLabel / SEG Series Description and RTS/SEG filename:
    NamePrefix = f'{RunCase}_from_s{FromSliceNum}_in_{SrcLabel}_to_s{ToSliceNum}_in_{TrgLabel}'
        
    NewTrgRoi = CopyRoi(SrcRoi, FromSearchString, SrcDcmDir, FromSliceNum, 
                        TrgDcmDir, TrgRoi, ToSliceNum, NamePrefix, 
                        LogToConsoleForRoiCopy)
    
    #LabmapImToCopy,\
    #ResLabmapImToCopy = CopyRoi(SrcRoi, FromSearchString, SrcDcmDir, FromSliceNum, 
    #                    TrgDcmDir, TrgRoi, ToSliceNum, NamePrefix, 
    #                    LogToConsoleForRoiCopy)
        
    
    
    """ Error check RTS/SEG """
    
    ErrorList = ErrorCheckRoi(NewTrgRoi, TrgDcmDir, LogToConsole)
    
    
    """ Export RTS/SEG """
    
    if ExportRoi and not ErrorList:
        
        
        if 'RTS' in RunCase:
            ExportDir = os.path.join(RoiExportDir, 'RTS')
        else:
            ExportDir = os.path.join(RoiExportDir, 'SEG')
        
        NewTrgRoiFpath = ExportTrgRoi(NewTrgRoi, SrcRoiFpath, ExportDir, NamePrefix)

            
            
        
    """ Plot Contours """
    
    if PlotResults:
        if ExportPlot:
            dpi = 120
        else:
            dpi = 80



        if TrgRoi:
            ListOfRois = [SrcRoi, TrgRoi, NewTrgRoi]

            ListOfDicomDirs = [SrcDcmDir, TrgDcmDir, TrgDcmDir]

            ListOfPlotTitles = ['Source', 'Original Target', 'New Target']
        else:
            ListOfRois = [SrcRoi, NewTrgRoi]

            ListOfDicomDirs = [SrcDcmDir, TrgDcmDir]

            ListOfPlotTitles = ['Source', 'New Target']


        TxtToAdd = f'(RunCase = {RunCase}, \nFromSliceNum = {FromSliceNum}, '                   + f'\nToSliceNum = {ToSliceNum})'

        if 'RTS' in RunCase:
            PlotContoursFromListOfRtss_v1(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                                          SearchString=FromSearchString, 
                                          PlotAllSlices=PlotAllSlices,
                                          AddTxt=TxtToAdd, ExportPlot=ExportPlot, 
                                          ExportDir=PlotExportDir, dpi=dpi, 
                                          LogToConsole=LogToConsoleForPlot)

        else:
            PlotPixArrsFromListOfSegs_v1(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                                         SearchString=FromSearchString, 
                                         PlotAllSlices=PlotAllSlices, 
                                         AddTxt=TxtToAdd, ExportPlot=ExportPlot, 
                                         ExportDir=PlotExportDir, dpi=dpi, 
                                         LogToConsole=LogToConsoleForPlot)

    
print('\nAll iterations complete.')


# # 18/12/20 What to do next:
# 
# ## 1. Verify if workaround 2 works for slices other than slice number 26.
# ## 2. If it works for others, copy the workaround to CopyRts
# ## 3. Continue trying to update XNAT and OHIF-Viewer

# In[115]:


TrgRoiFpath


# # Verify that the exported SEG contains expected frames:

# In[43]:


# Verify that the exported SEG contains expected frames:

SrcRoi = dcmread(SrcRoiFpath)

TrgRoi = dcmread(TrgRoiFpath)
        
NewTrgRoiFromFile = dcmread(os.path.join(ExportDir, "20201217_181959_Case3B-i_SEG_from_s25_in_S9_to_sNone_in_S3.dcm"))

#ListOfRois = [SrcRoi, TrgRoi, NewTrgRoi] # <-- shown in plot
ListOfRois = [SrcRoi, TrgRoi, NewTrgRoiFromFile] # <-- shown in plot, but not in OHIF-Viewer

ListOfDicomDirs = [SrcDcmDir, TrgDcmDir, TrgDcmDir]

#ListOfPlotTitles = ['Source', 'Original Target', 'New Target'] 
ListOfPlotTitles = ['Source', 'Original Target', 'New Target from SEG file']
        
PlotPixArrsFromListOfSegs_v1(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                             SearchString=FromSearchString, 
                             PlotAllSlices=PlotAllSlices, 
                             AddTxt=TxtToAdd, ExportPlot=ExportPlot, 
                             ExportDir=PlotExportDir, dpi=dpi, 
                             LogToConsole=True)


# In[45]:


SrcRoi


# In[73]:


TrgRoi


# In[74]:


NewTrgRoi


# In[170]:


from ImageTools import GetImageAttributes


#print(NewTrgRoi.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SliceThickness)

#print(type(NewTrgRoi.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SliceThickness))

#st = str(deepcopy(NewTrgRoi.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SliceThickness))

Size, Spacings, ST,IPPs, Dirs = GetImageAttributes(DicomDir=dicomdir, Package='sitk')

spacing_str = f"{Spacings[0]}"

print(spacing_str)

print(len(spacing_str))

print(spacing_str[:16])


# In[76]:


NewTrgRoi[0x0b, 0x62]


# In[144]:


os.path.join(RoiExportDir, "SEG", "MR4_S3_tumour_and_brain_SEG_20201105_090359.dcm")

os.path.join(r"C:\Users\ctorti\Dropbox\DICOMs", "MR4_S3_tumour_and_brain_SEG_20201105_090359.dcm")


# In[154]:


dicomdir = deepcopy(MR4_S3_DicomDir)
#dicomdir = deepcopy(MR4_S9_DicomDir)

segfname = "MR4_S3_tumour_and_brain_SEG_20201105_090359.dcm"
segfname = "MR4_S9_tumour_and_brain_SEG_20201105_115939.dcm"
segfname = "20201215_164639_Case3A-i_SEG_from_s25_in_S9_to_s20_in_S3.dcm"
segfname = "20201216_100543_Case3B-i_SEG_from_s25_in_S9_to_sNone_in_S3.dcm"
segfname = "20201222_103947_Case3A-i_SEG_from_s25_in_S9_to_s20_in_S3.dcm"
segfname = "20201222_104005_Case3B-i_SEG_from_s25_in_S9_to_sNone_in_S3.dcm"

segfpath = os.path.join(r"C:\Users\ctorti\Dropbox\DICOMs", segfname)

dicom = ImportDicom(dicomdir)
seg = dcmread(segfpath)

print(dicom.SOPInstanceUID)
print(dicom.file_meta.MediaStorageSOPInstanceUID)
print('')
print(seg.SOPInstanceUID)
print(seg.file_meta.MediaStorageSOPInstanceUID)


# In[173]:


WorkingSeg = dcmread(os.path.join(r"C:\Users\ctorti\Dropbox\DICOMs", 
                                  "20201222_103947_Case3A-i_SEG_from_s25_in_S9_to_s20_in_S3.dcm"))

NonWorkingSeg = dcmread(os.path.join(r"C:\Users\ctorti\Dropbox\DICOMs", 
                                     "20201222_104005_Case3B-i_SEG_from_s25_in_S9_to_sNone_in_S3.dcm"))

WS_ST = str(deepcopy(WorkingSeg.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SliceThickness))
WS_SBS = str(deepcopy(WorkingSeg.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SpacingBetweenSlices))

NWS_ST = str(deepcopy(NonWorkingSeg.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SliceThickness))
NWS_SBS = str(deepcopy(NonWorkingSeg.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SpacingBetweenSlices))

#print(WorkingSeg.StudyID)
#print(NonWorkingSeg.StudyID)
print(len(WS_ST))
print(len(WS_SBS))
print(len(NWS_ST))
print(len(NWS_SBS))


# In[146]:


from DicomTools import ImportDicom

SrcDicom = ImportDicom(SrcDcmDir)
TrgDicom = ImportDicom(TrgDcmDir)


SrcDicom#.MediaStorageSOPInstanceUID

#print(SrcDicom[0x10,0x10])
#print(SrcDicom[0x10,0x10].value)

# (0002 0003)
#print(SrcDicom[0x02,0x03])

#print(SrcDicom.file_meta)

print(SrcDicom.SOPInstanceUID)
print(SrcDicom.file_meta.MediaStorageSOPInstanceUID)
print('')
print(TrgDicom.SOPInstanceUID)
print(TrgDicom.file_meta.MediaStorageSOPInstanceUID)
print('')
print(SrcSeg.SOPInstanceUID)
print(SrcSeg.file_meta.MediaStorageSOPInstanceUID)
print('')
print(TrgSeg.SOPInstanceUID)
print(TrgSeg.file_meta.MediaStorageSOPInstanceUID)
print('')
print(NewTrgRoi.SOPInstanceUID)
print(NewTrgRoi.file_meta.MediaStorageSOPInstanceUID)


# In[ ]:


import PlottingTools
importlib.reload(PlottingTools)
from PlottingTools import PlotPixArrsFromListOfImages

ListOfImages = [LabmapImToCopy, ResLabmapImToCopy]

ListOfDicomDirs = [TrgDcmDir, TrgDcmDir]

ListOfPlotTitles = ['LabmapImToCopy', 'ResLabmapImToCopy']

PlotPixArrsFromListOfImages(ListOfImages, ListOfDicomDirs, ListOfPlotTitles, LogToConsole=True)


# In[65]:


import RoiCopyTools
importlib.reload(RoiCopyTools)

from RoiCopyTools import ErrorCheckRoi

ErrorList = ErrorCheckRoi(NewTrgRoi, TrgDcmDir, LogToConsole)

for error in ErrorList:
    print('\n', error)


# In[505]:


NewTrgPixArr = deepcopy(NewTrgRoi.pixel_array)

print(NewTrgPixArr.shape)

print(np.amax(NewTrgPixArr))

IndsR, IndsC = np.where(NewTrgPixArr==1)

print([[IndsR[i], IndsC[i]] for i in range(0, len(IndsR), 100)])


# In[430]:


print(SrcRoi.SharedFunctionalGroupsSequence[0]            .PlaneOrientationSequence[0]            .ImageOrientationPatient)
print(TrgRoi.SharedFunctionalGroupsSequence[0]            .PlaneOrientationSequence[0]            .ImageOrientationPatient)
print(NewTrgRoi.SharedFunctionalGroupsSequence[0]               .PlaneOrientationSequence[0]               .ImageOrientationPatient)


# In[243]:


#SrcRoi


# In[252]:


if SrcRoi.Modality == 'RTSTRUCT':
    SrcRoi.StructureSetLabel
else:
    SrcRoi.SeriesDescription


# In[248]:


if SrcRoi.Modality == 'RTSTRUCT':
    TrgRoi.StructureSetLabel
else:
    TrgRoi.SeriesDescription


# In[253]:


if NewTrgRoi.Modality == 'RTSTRUCT':
    NewTrgRoi.StructureSetLabel
else:
    NewTrgRoi.SeriesDescription


# In[339]:


from DicomTools import ImportDicom

SrcDicom = ImportDicom(SrcDcmDir)

SrcDicom.SeriesInstanceUID


# In[480]:


SrcRoi


# In[482]:


SrcPFFGS = deepcopy(SrcRoi.PerFrameFunctionalGroupsSequence)

SrcPFFGS[0]


# In[453]:


TrgRoi


# In[496]:


NewTrgRoi


# In[483]:


NewTrgPFFGS = deepcopy(NewTrgRoi.PerFrameFunctionalGroupsSequence)

NewTrgPFFGS[0]


# In[477]:


# Check the ReferencedSOPInstanceUIDs from the ReferencedInstanceSequence:

from DicomTools import GetDicomSOPuids

TrgSOPuids = GetDicomSOPuids(TrgDcmDir)

N = len(TrgSOPuids)

print(f'\nThere are {N} Target DICOMs')

for i in range(N):
    RSOPuid = deepcopy(NewTrgRoi.ReferencedSeriesSequence[0].ReferencedInstanceSequence[i].ReferencedSOPInstanceUID)
    
    if RSOPuid != TrgSOPuids[i]:
        print('\nRSOPuid =', RSOPuid)
        print('SOPuid  =', TrgSOPuids[i])


# In[484]:


# Confirm the ReferencedSOPInstanceUIDs from the PerFrameFunctionalGroupsSequence:

from DicomTools import GetDicomSOPuids

TrgSOPuids = GetDicomSOPuids(TrgDcmDir)

S = len(NewTrgRoi.PerFrameFunctionalGroupsSequence)

RSOPuids = [NewTrgRoi.PerFrameFunctionalGroupsSequence[i]                     .DerivationImageSequence[0]                     .SourceImageSequence[0]                     .ReferencedSOPInstanceUID for i in range(S)]

for i in range(S):
    if not RSOPuids[i] in TrgSOPuids:
        print(f'\nRSOPuid[{i}] is not in TrgSOPuids')
        
        
    ind = int(NewTrgRoi.PerFrameFunctionalGroupsSequence[i]                       .FrameContentSequence[0]                       .DimensionIndexValues[1])
    
    RSOPuidFromRIS = deepcopy(NewTrgRoi.ReferencedSeriesSequence[0]                                       .ReferencedInstanceSequence[ind-1]                                       .ReferencedSOPInstanceUID)
    
    if RSOPuids[i] != RSOPuidFromRIS:
        print(f'\nRSOPuids[{i}] =', RSOPuids[i])
        print('RSOPuidFromRIS  =', RSOPuidFromRIS)
    


# ### The IPPs obtained using GetImageAttributes are in the same order as the IPPs obtained from ImportDicoms (as expected):

# In[443]:


from DicomTools import ImportDicoms
from ImageTools import GetImageAttributes

TrgSize, TrgSpacings, TrgST, TrgIPPs_1, TrgDirs = GetImageAttributes(TrgDcmDir)

TrgDicoms = ImportDicoms(TrgDcmDir)

TrgIPPs_2 = [[float(item) for item in IPP] for IPP in [TrgDicoms[i].ImagePositionPatient for i in range(len(TrgDicoms))]]

for i in range(len(TrgDicoms)):
    print(f'TrgIPPs_1 = {TrgIPPs_1[i]}')
    print(f'TrgIPPs_2 = {TrgIPPs_2[i]}\n')


# In[107]:


from DicomTools import GetRoiNum

GetRoiNum(SrcRoi, FromRoiLabel)


# In[265]:


from DicomTools import GetDicomSOPuids

SOPuids = GetDicomSOPuids(TrgDcmDir)

RIS = NewTrgRoi.ReferencedSeriesSequence[0].ReferencedInstanceSequence

RefSOPuids = [RIS[i].ReferencedSOPInstanceUID for i in range(len(RIS))]

matches = [RefSOPuid in SOPuids for RefSOPuid in RefSOPuids]

Inds = [i for i, x in enumerate(matches) if True]

[RefSOPuids[i] for i in Inds]


# In[331]:


# Datasets used:
Dataset1DcmDir = deepcopy(MR4_S9_DicomDir)
Dataset1RtsFpath = deepcopy(MR4_S9_RtsFpath)
Dataset1SegFpath = deepcopy(MR4_S9_SegFpath)

Dataset2DcmDir = deepcopy(MR4_S5_DicomDir)
Dataset2RtsFpath = deepcopy(MR4_S5_RtsFpath)
Dataset2SegFpath = deepcopy(MR4_S5_SegFpath)

Dataset3DcmDir = deepcopy(MR4_S3_DicomDir)
Dataset3RtsFpath = deepcopy(MR4_S3_RtsFpath)
Dataset3SegFpath = deepcopy(MR4_S3_SegFpath)

Dataset4DcmDir = deepcopy(MR12_S8_DicomDir)
Dataset4RtsFpath = None
Dataset4SegFpath = None


ListOfDcmDirs = [Dataset1DcmDir, Dataset2DcmDir, Dataset3DcmDir, Dataset4DcmDir]

ListOfRtsFpaths = [Dataset1RtsFpath, Dataset2RtsFpath, Dataset3RtsFpath, Dataset4RtsFpath]
ListOfSegFpaths = [Dataset1SegFpath, Dataset2SegFpath, Dataset3SegFpath, Dataset4SegFpath]

ListOfRtss = []
ListOfSegs = []

for RtsFpath in ListOfRtsFpaths:
    if RtsFpath:
        ListOfRtss.append(dcmread(RtsFpath))
    else:
        ListOfRtss.append(None)

for SegFpath in ListOfSegFpaths:
    if SegFpath:
        ListOfSegs.append(dcmread(SegFpath))
    else:
        ListOfSegs.append(None)

ListOfPlotTitles = ['Dataset 1', 'Dataset 2', 'Dataset 3', 'Dataset 4']
ListOfPlotTitles = ['', '', '', '']

[print(ListOfDcmDirs[i], '\n') for i in range(len(ListOfDcmDirs))]


# In[297]:


ListOfRtss[1]


# In[538]:


import PlottingTools
importlib.reload(PlottingTools)

from PlottingTools import GetContoursFromListOfRtss
from PlottingTools import PlotContoursFromListOfRtss_v2
from PlottingTools import GetPixArrsFromListOfSegs
from PlottingTools import PlotPixArrsFromListOfSegs_v2

DataToPlot = 'RTS'
DataToPlot = 'SEG'

SearchString = 'tumour'

TxtToAdd = f'(RunCase = {RunCase}, \nFromSliceNum = {FromSliceNum}, '           + '\nToSliceNum = {ToSliceNum})'
TxtToAdd = ''

LogToConsoleForPlot = False
#LogToConsoleForPlot = True

PlotAllSlices = False # only plot slices that contain a ROI in at least one of the datasets
#PlotAllSlices = True

ExportPlot=False
#ExportPlot=True

if PlotResults:
    if ExportPlot:
        dpi = 120
    else:
        dpi = 80


if DataToPlot == 'RTS':
    ListOfContours, ListOfC2Sinds, ListOfRoiNums,    ListOfDcmFpaths, ListOfOrigins, ListOfDirections,    ListOfSpacings = GetContoursFromListOfRtss(ListOfRtss, ListOfDcmDirs, 
                                               SearchString, LogToConsole)


    PlotContoursFromListOfRtss_v2(ListOfRtss, ListOfDcmDirs, ListOfPlotTitles,
                                  SearchString, PlotAllSlices, TxtToAdd, 
                                  ExportPlot, PlotExportDir, dpi, 
                                  LogToConsoleForPlot)

else:
    ListOfPixArrs, ListOfF2Sinds, ListOfSegNums,    ListOfDcmFpaths = GetPixArrsFromListOfSegs(ListOfSegs, ListOfDcmDirs, 
                                               SearchString, LogToConsole)
    
    PlotPixArrsFromListOfSegs_v2(ListOfSegs, ListOfDcmDirs, ListOfPlotTitles,
                                 SearchString, PlotAllSlices, TxtToAdd, 
                                 ExportPlot, PlotExportDir, dpi, 
                                 LogToConsoleForPlot)


# from RtsTools import GetCStoSliceIndsByRoi
# from DicomTools import GetSOPuids
# 
# GetCStoSliceIndsByRoi(ListOfRtss[1], GetSOPuids())

# In[304]:


ListOfF2Sinds
ListOfC2Sinds


# In[290]:


print(len(ListOfDcmFpaths))
print('')
[print(len(ListOfDcmFpaths[i])) for i in range(len(ListOfDcmFpaths))]


# In[519]:


#S5_Seg = dcmread(MR4_S5_SegFpath)
#S5_Seg

S3_Seg = dcmread(os.path.join(SegRootDir, "MR4_S3_tumour_SEG_20201216_085421.dcm")) # single frame on slice 10
S3_Seg

# The RefSOP in PFFGS.DIS.SIS is the 10^th RefSOP in RIS


# In[518]:


NewTrgRoi # single frame on slice 10


# In[520]:


TrgRoi


# In[521]:


print(f'{S3_Seg.pixel_array.shape}')
print(f'{TrgRoi.pixel_array.shape}')
print(f'{NewTrgRoi.pixel_array.shape}')


# In[535]:


from SegTools import GetRSOPuidsInRIS
from SegTools import GetRSOPuidsInPFFGS
from DicomTools import GetDicomSOPuids
from ImageTools import GetImageAttributes

S3_RSOPsInCIS = GetRSOPuidsInRIS(S3_Seg)

S3_RSOPsInPFFGS = GetRSOPuidsInPFFGS(S3_Seg)

S3_RSOPind = S3Seg_RSOPsInCIS.index(S3_RSOPsInPFFGS[0])

S3_IPPinPFFGS = deepcopy(S3_Seg.PerFrameFunctionalGroupsSequence[0]                               .PlanePositionSequence[0]                               .ImagePositionPatient)
S3_IPPinPFFGS = [float(item) for item in S3_IPPinPFFGS]

#S3_RSOPsInPFFGS

S3_SOPs = GetDicomSOPuids(MR4_S3_DicomDir)

S3_SOPind = S3_SOPs.index(S3_RSOPsInPFFGS[0])

Size, Spacings, ST, S3_IPPs, Dirs = GetImageAttributes(MR4_S3_DicomDir)

S3_IPPind = S3_IPPs.index(S3_IPPinPFFGS)

print(f'The RefSOP in PFFGS is the {S3_RSOPind}th RefSOP in CIS')
print(f'The RefSOP in PFFGS is the {S3_SOPind}th SOP in S3_SOPs')
print(f'The IPP in PFFGS is the {S3_IPPind}th S3_IPPs')


# In[537]:


NewTrg_RSOPsInCIS = GetRSOPuidsInRIS(NewTrgRoi)

NewTrg_RSOPsInPFFGS = GetRSOPuidsInPFFGS(NewTrgRoi)

NewTrg_RSOPind = S3Seg_RSOPsInCIS.index(S3_RSOPsInPFFGS[0])

NewTrg_IPPinPFFGS = deepcopy(NewTrgRoi.PerFrameFunctionalGroupsSequence[0]                                      .PlanePositionSequence[0]                                      .ImagePositionPatient)
NewTrg_IPPinPFFGS = [float(item) for item in NewTrg_IPPinPFFGS]

NewTrg_SOPs = GetDicomSOPuids(TrgDcmDir)

NewTrg_SOPind = NewTrg_SOPs.index(NewTrg_RSOPsInPFFGS[0])

Size, Spacings, ST, NewTrg_IPPs, Dirs = GetImageAttributes(TrgDcmDir)

NewTrg_IPPind = NewTrg_IPPs.index(NewTrg_IPPinPFFGS)

print(f'The RefSOP in PFFGS is the {NewTrg_RSOPind}th RefSOP in CIS')
print(f'The RefSOP in PFFGS is the {NewTrg_SOPind}th SOP in NewTrg_SOPs')
print(f'The IPP in PFFGS is the {NewTrg_IPPind}th NewTrg_IPPs')


# In[539]:


ListOfRois = [S3_Seg, NewTrgRoi]

ListOfDicomDirs = [MR4_S3_DicomDir, TrgDcmDir]

ListOfPlotTitles = ['S3_Seg', 'New Target']


TxtToAdd = f'(RunCase = {RunCase}, \nFromSliceNum = {FromSliceNum}, '           + '\nToSliceNum = {ToSliceNum})'

if 'RTS' in RunCase:
    PlotContoursFromListOfRtss_v1(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                                  SearchString=FromSearchString, 
                                  PlotAllSlices=PlotAllSlices,
                                  AddTxt=TxtToAdd, ExportPlot=ExportPlot, 
                                  ExportDir=PlotExportDir, dpi=dpi, 
                                  LogToConsole=LogToConsoleForPlot)

else:
    PlotPixArrsFromListOfSegs_v1(ListOfRois, ListOfDicomDirs, ListOfPlotTitles,
                                 SearchString=FromSearchString, 
                                 PlotAllSlices=PlotAllSlices, 
                                 AddTxt=TxtToAdd, ExportPlot=ExportPlot, 
                                 ExportDir=PlotExportDir, dpi=dpi, 
                                 LogToConsole=LogToConsoleForPlot)


# In[544]:


RunCase


# # Start with a SEG created in the OHIF-Viewer for S3 and modify only the PixelData to that of NewTrgRoi for UseCase 3B=i_SEG:

# In[543]:


from pydicom.pixel_data_handlers.numpy_handler import pack_bits
from RoiCopyTools import ExportTrgRoi

NewS3_Seg = deepcopy(S3_Seg)

OldSD = deepcopy(S3_Seg.SeriesDescription)
NewSD = 'PixelData_from_NewTrgSeg_copied_to_' + OldSD

NewS3_Seg.SeriesDescription = NewSD

#NewS3_Seg.SeriesDescription

packed = pack_bits(NewTrgRoi.pixel_array.ravel())
    
NewS3_Seg.PixelData = packed + b'\x00' if len(packed) % 2 else packed

NewS3_SegFpath = ExportTrgRoi(NewS3_Seg, SrcRoiFpath, ExportDir, NewSD)


# # No segmentations appear in the OHIF Viewer for NewS3_Seg.
# 
# # This time start with NewTrgRoi and set the PixelData to that of S3 SEG (created in the OHIF-Viewer):

# In[545]:


NewNewTrgSeg = deepcopy(NewTrgRoi)

OldSD = deepcopy(NewTrgRoi.SeriesDescription)
NewSD = 'PixelData_from_S3_Seg_copied_to_' + OldSD

NewNewTrgSeg.SeriesDescription = NewSD

#NewNewTrgSeg.SeriesDescription

packed = pack_bits(S3_Seg.pixel_array.ravel())
    
NewNewTrgSeg.PixelData = packed + b'\x00' if len(packed) % 2 else packed

NewNewTrgSegFpath = ExportTrgRoi(NewNewTrgSeg, SrcRoiFpath, ExportDir, NewSD)


# # Still no segmentations visible in the OHIF-Viewer.
# 
# # I then imported the SEG that I created IN THE OHIF-VIEWER for S3 earlier this morning and no segmentations showed for that either!!!

# In[ ]:





# In[ ]:





# # Case 3b - Deal with issue of resampling resulting in no segmentations:

# In[34]:


import RoiCopyTools
importlib.reload(RoiCopyTools)

import PlottingTools
importlib.reload(PlottingTools)

import ImageTools
importlib.reload(ImageTools)

from RoiCopyTools import CopyRoi
from RoiCopyTools import ExportTrgRoi
from RoiCopyTools import ErrorCheckRoi
from PlottingTools import PlotContoursFromListOfRtss_v1
from PlottingTools import PlotPixArrsFromListOfSegs_v1

from RoiCopyTools import WhichUseCase
from GeneralTools import PrintTitle
from pydicom import dcmread


RunCases = ['Case3B-i_SEG'] # SEG - No segmentations visible in viewer if TrgSeg is used (which is a RTS-to-SEG 
# conversion) OR if no TrgSeg is used.
RunCases = ['Case3B-ii_SEG']

# Try S4 instead of S3 for problematic use cases:
UseS3orS4 = 'S3'
UseS3orS4 = 'S4'

IsOrigTrg = True # use available Target RTS/SEG
#IsOrigTrg = False # assume that Target RTS/SEG doesn't yet exist

LogToConsoleForRoiCopy = False
LogToConsoleForRoiCopy = True

ExportRoi = False
#ExportRoi = True

PlotResults = False
PlotResults = True

LogToConsoleForPlot = False
LogToConsoleForPlot = True

PlotAllSlices = False # only plot slices that contain a ROI in at least one of the datasets
#PlotAllSlices = True

ExportPlot=False
#ExportPlot=True


FromSearchString = 'tumour'
    
for RunCase in RunCases:
    #if 'RTS' in RunCase:
    #    RoiType = 'ROI'
    #else:
    #    RoiType = 'segment'
    
    
    if '1' in RunCase:
        """
        ***********************************************
        Run Case 1A
        ***********************************************
        """
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S9_DicomDir)
        
        if 'RTS' in RunCase:
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
            else:
                TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
            else:
                TrgRoiFpath = ''
                
        FromSliceNum = 23
        ToSliceNum = 29
        
        SrcLabel = 'S9'
        TrgLabel = 'S9'

    
    elif '2' in RunCase:
        """
        ***********************************************
        Run Case 2A/B
        ***********************************************
        """
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR4_S5_DicomDir)

        if 'RTS' in RunCase:
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S5_RtsFpath)
            else:
                TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            
            if IsOrigTrg:
                TrgRoiFpath = deepcopy(MR4_S5_SegFpath)
            else:
                TrgRoiFpath = ''
            
        if 'A' in RunCase:
            FromSliceNum = 23
            ToSliceNum = 22
        else:
            FromSliceNum = 27 # no segmentations visible in OHIF
            #FromSliceNum = 23 # 15/12 no segmentations visible in OHIF
            ToSliceNum = None

        SrcLabel = 'S9'
        TrgLabel = 'S5'

    
    elif '3' in RunCase:
        """
        ***********************************************
        Run Case 3A/B-i/ii
        ***********************************************
        """
        if 'ii' in RunCase:
            # Run Case 3A/B-ii.

            SrcDcmDir = deepcopy(MR4_S3_DicomDir)
            TrgDcmDir = deepcopy(MR4_S9_DicomDir)

            if 'RTS' in RunCase:
                SrcRoiFpath = deepcopy(MR4_S3_RtsFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S9_RtsFpath)
                else:
                    TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S3_SegFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S9_SegFpath)
                else:
                    TrgRoiFpath = ''
            
            if 'A' in RunCase:
                FromSliceNum = 11
                ToSliceNum = 26
            else:
                if 'RTS' in RunCase:
                    FromSliceNum = 10 # ROI copied to slices 24-25
                    #FromSliceNum = 11 # ROI copied to slices 26-28
                else:
                    #FromSliceNum = 10 # segmentation copied to slice 24-25 - some pixels missing in SEG for S3 
                    # (i.e. in Source that get copied to NewTarget)
                    FromSliceNum = 11 # segmentation copied to slices 26-28
                
                ToSliceNum = None
                
            SrcLabel = 'S3'
            TrgLabel = 'S9'

        else:
            # Run Case 3A/B-i.

            SrcDcmDir = deepcopy(MR4_S9_DicomDir)
            TrgDcmDir = deepcopy(MR4_S3_DicomDir)

            if 'RTS' in RunCase:
                SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S3_RtsFpath)
                else:
                    TrgRoiFpath = ''

            else:
                SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
                
                if IsOrigTrg:
                    TrgRoiFpath = deepcopy(MR4_S3_SegFpath)
                else:
                    TrgRoiFpath = ''
                
            if 'A' in RunCase:
                FromSliceNum = 25
                ToSliceNum = 20
            else:
                if 'RTS' in RunCase:
                    #FromSliceNum = 23 # no ROI copied
                    #FromSliceNum = 24 # no ROI copied
                    FromSliceNum = 25 # contour copied to slice 10
                    #FromSliceNum = 26 # no ROI copied
                    #FromSliceNum = 27 # ROI copied to slice 11
                    #FromSliceNum = 28 # no ROI copied
                    #FromSliceNum = 29 # no ROI copied
                else:
                    #FromSliceNum = 23 # TrgPFFGStoSliceInds = []
                    #FromSliceNum = 24 # TrgPFFGStoSliceInds = []
                    FromSliceNum = 25 # segmentation copied to slice 10 in plot but 
                    # no segmentation visible in OHIF-Viewer
                    #FromSliceNum = 26 # TrgPFFGStoSliceInds = []
                    #FromSliceNum = 27 # segmentation copied to slice 11 in plot but 
                    # no segmentation visible in OHIF-Viewer
                
                ToSliceNum = None

            SrcLabel = 'S9'
            TrgLabel = 'S3'


    
    elif '5' in RunCase:
        """
        ***********************************************
        Run Case 5
        ***********************************************
        """
        SrcDcmDir = deepcopy(MR4_S9_DicomDir)
        TrgDcmDir = deepcopy(MR12_S8_DicomDir)
    
        if 'RTS' in RunCase:
            SrcRoiFpath = deepcopy(MR4_S9_RtsFpath)
            
            if IsOrigTrg:
                raise Exception('A RTS does not yet exist for this Target.')
            else:
                TrgRoiFpath = ''
        else:
            SrcRoiFpath = deepcopy(MR4_S9_SegFpath)
            
            if IsOrigTrg:
                raise Exception('A SEG does not yet exist for this Target.')
            else:
                TrgRoiFpath = ''
            
        FromSliceNum = 23 # contour/segmentation copied to slices 12-14
        
        SrcLabel = 'MR4_S9'
        TrgLabel = 'MR12_S8'
    
    
    else:
        raise Exception('"RunCase" must have a 1, 2, 3, 4 or 5 in the string.')



    PrintTitle(f'\n\nRunning UseCase {RunCase}:')

    if isinstance(ToSliceNum, int):
        print(f'Copying the Source RTS/SEG on slice {FromSliceNum} in the ROI/segment',
              f'matching "{FromSearchString}" to slice {ToSliceNum} in Target..')
    else:
        print(f'Copying the Source RTS/SEG on slice {FromSliceNum} in the ROI/segment',
              f'matching "{FromSearchString}" to Target..')

    if not LogToConsoleForRoiCopy:
        WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, True)


    # Import the RTS or SEGs:
    SrcRoi = dcmread(SrcRoiFpath)

    if TrgRoiFpath:
        TrgRoi = dcmread(TrgRoiFpath)
    else:
        TrgRoi = None

        if 'RTS' in RunCase:
            print('\nA Target RTS was not provided so the Source RTS will',
                  'be used as a template.')
        else:
            print('\nA Target SEG was not provided so the Source SEG will',
                  'be used as a template.')
    
    
    print(f'\n\nInputs to CopyRoi:\n FromSearchString = {FromSearchString}\n',
              f'FromSliceNum = {FromSliceNum}\n ToSliceNum = {ToSliceNum}')
    
    # NamePrefix for RTS StructureSetLabel / SEG Series Description and RTS/SEG filename:
    NamePrefix = f'{RunCase}_from_s{FromSliceNum}_in_{SrcLabel}_to_s{ToSliceNum}_in_{TrgLabel}'
        
    #NewTrgRoi = CopyRoi(SrcRoi, FromSearchString, SrcDcmDir, FromSliceNum, 
    #                    TrgDcmDir, TrgRoi, ToSliceNum, NamePrefix, 
    #                    LogToConsoleForRoiCopy)
    
    #LabmapImToCopy,\
    #ResLabmapImToCopy = CopyRoi(SrcRoi, FromSearchString, SrcDcmDir, FromSliceNum, 
    #                    TrgDcmDir, TrgRoi, ToSliceNum, NamePrefix, 
    #                    LogToConsoleForRoiCopy)
        
    
    """ Running the code within CopyRoi manually: """
    
    SrcSeg = deepcopy(SrcRoi)
    TrgSeg = deepcopy(TrgRoi)
    
    #SrcSeg = deepcopy(TrgRoi)
    #TrgSeg = deepcopy(SrcRoi)
    #SrcDcmDir = deepcopy(MR4_S3_DicomDir)
    #TrgDcmDir = deepcopy(MR4_S9_DicomDir)
    
    
    
    LogToConsole = False
    
    import importlib
    
    import SegTools
    importlib.reload(SegTools)
    import DicomTools
    importlib.reload(DicomTools)
    import ImageTools
    importlib.reload(ImageTools)
    
    from copy import deepcopy
    import numpy as np
    from DicomTools import GetRoiNum
    from SegTools import GetFrameFromPixArr
    from GeneralTools import PrintTitle
    from GeneralTools import UniqueItems
    from ImageTools import ImportImage
    from SegTools import InitialiseSeg
    from SegTools import ModifySeg
    
    from DicomTools import GetDicomSOPuids
    from SegTools import GetPFFGStoSliceIndsBySeg
    from ImageTools import ImageMax
    
    FromSegNum = GetRoiNum(Roi=SrcSeg, SearchString=FromSearchString)
    
    SegSOPuids = GetDicomSOPuids(DicomDir=SrcDcmDir)
    
    SegPFFGStoSliceIndsBySeg = GetPFFGStoSliceIndsBySeg(Seg=SrcSeg, 
                                                        SOPuids=SegSOPuids)
    
    SegPFFGStoSliceIndsInSeg = SegPFFGStoSliceIndsBySeg[FromSegNum]
    
    print(f'\nThe Source SEG matching "{FromSearchString}" has segmentations',
          f'on slices {SegPFFGStoSliceIndsInSeg}.')
    
    # The pixel array that only contains the frame to be copied:
    PixArrToCopy = GetFrameFromPixArr(Seg=SrcSeg, DicomDir=SrcDcmDir, 
                                      SearchString=FromSearchString, 
                                      SliceNum=FromSliceNum,
                                      LogToConsole=LogToConsole)
    
    unique = UniqueItems(Items=PixArrToCopy, NonZero=False)
    print(f'\nThere are {len(unique)} unique items in PixArrToCopy')
    if len(unique) < 50:
        print(f'Unique values: {unique}')
    
    
    # Determine which Use Case applies:
    UseCase = WhichUseCase(SrcDcmDir, TrgDcmDir, ToSliceNum, LogToConsole)
    
    if True:#LogToConsole:
        PrintTitle(f'\nCase {UseCase} applies.')
        
    if UseCase in ['3a', '3b', '4', '5']:
        from ConversionTools import PixArr2Image
        from ConversionTools import Image2PixArr
        
        # Import the 3D images:
        if not 'a' in UseCase:
            SrcIm = ImportImage(SrcDcmDir)
            TrgIm = ImportImage(TrgDcmDir)
        
        PrintTitle(f'\nConverting "PixArrToCopy" to a labelmap image:')
        
        # Convert PixArrToCopy to a labelmap image:
        LabmapImToCopy = PixArr2Image(PixArr=PixArrToCopy,
                                      FrameToSliceInds=[FromSliceNum],
                                      RefIm=SrcIm)
        
        print(f'LabmapImToCopy.GetSize() = {LabmapImToCopy.GetSize()}')
        print(f'Max of LabmapImToCopy = {ImageMax(LabmapImToCopy)}')
        
        
    if '3' in UseCase:
        from ImageTools import ResampleImage
        
        #print(f'\n\n\n***** LabmapImToCopy.GetSize() = {LabmapImToCopy.GetSize()}')
        
        
        
        """ 16/12:
            Instead of using NearestNeighbor, use a BSpline interpolation, then
            binary threshold the image using a low threshold (much lower than
            0.5).
        """
        interp = 'BSpline'
        interp = 'Linear'
        #interp = 'NearestNeighbor'
        
        PrintTitle(f'\nResampling "LabmapImToCopy" using {interp} interpolation:')
        
        # Resample LabmapImToCopy to the Target image's grid:
        ResLabmapImToCopy = ResampleImage(Image=LabmapImToCopy, 
                                          RefImage=TrgIm, 
                                          Interpolation=interp)
        
        print(f'ResLabmapImToCopy.GetSize() = {ResLabmapImToCopy.GetSize()}')
        print(f'Max of ResLabmapImToCopy = {ImageMax(ResLabmapImToCopy)}')
        
        
        # Convert ResLabmapImToCopy back to a pixel array:
        ResPixArrToCopy,        PFFGStoSliceIndsToCopy = Image2PixArr(LabmapIm=ResLabmapImToCopy)
        
        PrintTitle('\nConversion of ResLabmapImToCopy to a pixel array:')
        print(f'PFFGStoSliceIndsToCopy = {PFFGStoSliceIndsToCopy}')
        print(f'ResPixArrToCopy.shape = {ResPixArrToCopy.shape}')
        
        unique = UniqueItems(Items=ResPixArrToCopy, NonZero=False)
        print(f'\nThere are {len(unique)} unique items in ResPixArrToCopy')
        if len(unique) < 50:
            print(f'Unique values: {unique}')
            
        for i in range(ResPixArrToCopy.shape[0]):
            maxval = np.amax(ResPixArrToCopy[i])
            minval = np.amin(ResPixArrToCopy[i])

            print(f'Frame {i} has max = {maxval}, min = {minval}')

        
        
        if not 'earest' in interp:
            from ImageTools import BinaryThresholdImage
            
            PrintTitle(f'\nBinary thresholding of "ResLabmapImToCopy":')
            
            ResLabmapImToCopy = BinaryThresholdImage(ResLabmapImToCopy, 
                                                     Thresh=0.5)
        
            print(f'ResLabmapImToCopy.GetSize() = {ResLabmapImToCopy.GetSize()}')
            print(f'Max of ResLabmapImToCopy = {ImageMax(ResLabmapImToCopy)}')

            #print(f'***** ResLabmapImToCopy.GetSize() = {ResLabmapImToCopy.GetSize()}')

            # Convert ResLabmapImToCopy back to a pixel array:
            ResPixArrToCopy,            PFFGStoSliceIndsToCopy = Image2PixArr(LabmapIm=ResLabmapImToCopy)

            PrintTitle('\nConversion of binary thresholded ResLabmapImToCopy to a pixel array:')
            print(f'PFFGStoSliceIndsToCopy = {PFFGStoSliceIndsToCopy}')
            print(f'ResPixArrToCopy.shape = {ResPixArrToCopy.shape}')

            unique = UniqueItems(Items=ResPixArrToCopy, NonZero=False)
            print(f'\nThere are {len(unique)} unique items in ResPixArrToCopy')
            if len(unique) < 50:
                print(f'Unique values: {unique}')

            for i in range(ResPixArrToCopy.shape[0]):
                maxval = np.amax(ResPixArrToCopy[i])
                minval = np.amin(ResPixArrToCopy[i])

                print(f'Frame {i} has max = {maxval}, min = {minval}')
        
        
        

    
print('\nAll iterations complete.')


# import SimpleITK as sitk
# 
# sitk.Show(ResLabmapImToCopy)

# In[8]:


ResLabmapImToCopy[104,28,10]


# In[25]:


import PlottingTools
importlib.reload(PlottingTools)
from PlottingTools import PlotPixArrsFromListOfImages

ListOfImages = [LabmapImToCopy, ResLabmapImToCopy]

ListOfDicomDirs = [SrcDcmDir, TrgDcmDir]

ListOfPlotTitles = ['LabmapImToCopy', 'ResLabmapImToCopy']

PlotPixArrsFromListOfImages(ListOfImages, ListOfDicomDirs, ListOfPlotTitles, LogToConsole=True)


# In[ ]:




