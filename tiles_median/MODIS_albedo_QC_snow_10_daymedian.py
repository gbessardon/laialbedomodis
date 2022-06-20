#!/usr/bin/env python
# coding: utf-8

# In[1]:


import gdal
from matplotlib import pyplot as plt
import numpy as np
import os
import re
import pandas as pd


# # Declare the MCD43A3 folder

# In[2]:


"""
Collection dir is assumed to contain a folder of each year of the product

"""
OUTPUTDIR='tilesDIR'
DATADIR='/home/gbessardon/DATA'
SHORTNAME='MCD43A3'
COLLECTION='061'
collectiondir=os.path.join(DATADIR,SHORTNAME,COLLECTION)
years=['2020', '2021', '2018', '2019','2017']


# # Function to read the hdf file metadata

# In[3]:


def extract_metadata(ds):
    geoT = ds.GetGeoTransform()
    projT = ds.GetProjection()
    w=ds.RasterXSize
    h=ds.RasterYSize
    offset=0
    scale_factor=1
    fillvalue=9999
    for item,value in ds.GetMetadata_Dict().items():
        if item=='add_offset':
            offset=int(value)
        if item=='scale_factor':
            scale_factor=float(value)
        if item=='_FillValue':
            fillvalue=int(value)
    return(offset,scale_factor,fillvalue,geoT,projT,w,h)


# # Function to clean the data

# In[4]:


def clean_data(ds,dsQC,add_offset=0,scale_factor=1,fillvalue=9999,fillQC=9999,maxQC=1,ECOSGscale_factor=100):
    # apply the desired QC value
    QC_np=dsQC.ReadAsArray()
    if fillQC<maxQC:
        QC_np[QC_np==fillQC]=maxQC+1
    B_np=ds.ReadAsArray()
    B_np[QC_np>maxQC]=fillvalue
    QC_np=None
    # apply the offset and the scale factor and set it to ECOSG
    B_np = scale_factor * (B_np - add_offset)*ECOSGscale_factor
    new_fill=scale_factor*(fillvalue- add_offset)*ECOSGscale_factor
    return (B_np,new_fill)
    


# In[5]:


def snow_free(data_ar,dssnow,fillv=9999,fillsnow=9999,maxsnow=0):
    Arsnow=dssnow.ReadAsArray()
    datasnow=fillv+0*data_ar
    if fillsnow<maxsnow:
        Arsnow[Arsnow==fillsnow]=maxsnow+1
    datasnow[Arsnow<=maxsnow]=data_ar[Arsnow<=maxsnow]
    return datasnow
        


# In[6]:


def onefilefilter_treatment(fn,maxdataQC,maxsnowQC,visband=28,visQCband=7,
                            nirband=29,nirQCband=8,snowA2band=0,ECOSGsf=100):
    """
    INPUTS:
    fn: the MCD43A3 file path
    maxdataQC: the maximum QC value in the MCD43A3 QC band allowed (same for nir and vis in this version)
    maxsnowQC: maximum QC value in the MCD43A2 band
    visband: visible band location in the MCD43A3 file
    visQCband: visible band quality control location in the MCD43A3 file
    nirband: near-infrared band location in the MCD43A3 file
    nirQCband: near-infrared band quality control location in the MCD43A3 file
    ECOSGsf: scale factor in ECOCLIMAP-SG files
    
    
    OUTPUTS:
    VIS_np: numpy array cleaned 
    fillv:  fill value of VIS_np
    VIS_Sfree_np: VIS_np with snow_filter applied
    
    NIR_np: numpy array cleaned 
    filln: fill value of NIR_np
    NIR_Sfree_np: NIR_np with snow_filter applied
    
    geoT: file geotransform details
    projT: file projection details
    w: width of the file array
    h: height of the file array
    """
    #get the snow filter data
    fnA2=fn.replace('MCD43A3','MCD43A2')
    sdsA2=gdal.Open(fnA2).GetSubDatasets()
    dssnow=gdal.Open(sdsA2[snowA2band][0])
    ofsnow,sfsnow,filsnow,geoTsnow,projsnow,wsnow,hsnow=extract_metadata(dssnow)
    
    # Open and filter the visible data
    sds=gdal.Open(fn).GetSubDatasets()
    dsBSAVIS=gdal.Open(sds[visband][0])
    dsVISQC=gdal.Open(sds[visQCband][0])
    offVIS,sfVIS,fillvis,geoT,projT,w,h=extract_metadata(dsBSAVIS)
    _,_,fillvisQC,geoT,projT,w,h=extract_metadata(dsVISQC)
    VIS_np,fillv=clean_data(dsBSAVIS,dsVISQC,offVIS,sfVIS,fillvis,fillvisQC,maxQC=maxdataQC,ECOSGscale_factor=ECOSGsf)

    # filter snow data in visible file
    VIS_Sfree_np=snow_free(VIS_np,dssnow,fillv,filsnow,maxsnowQC)
    # Clear the visible visible QC gdal datasets
    dsVISQC=None
    dsBSAVIS=None
    # Open and filter the nir data
    dsBSANIR=gdal.Open(sds[nirband][0])
    dsNIRQC=gdal.Open(sds[8][0] )
    offNIR,sfNIR,fillnir,_,_,_,_=extract_metadata(dsBSANIR)
    _,_,fillnirQC,_,_,_,_=extract_metadata(dsNIRQC)
    NIR_np,filln=clean_data(dsBSANIR,dsNIRQC,offNIR,sfNIR,fillnir,fillnirQC,maxQC=maxdataQC,ECOSGscale_factor=ECOSGsf)

    # filter snow data in nir file
    NIR_Sfree_np=snow_free(NIR_np,dssnow,filln,filsnow,maxsnowQC)
    dsBSANIR=None
    dsBSAVIS=None
    return (VIS_np,VIS_Sfree_np,fillv, NIR_np,NIR_Sfree_np,filln,geoT,projT,w,h)


# # Functions to Create raster from numpy array

# In[7]:


def create_raster(output_path,columns,rows,nband = 1,gdal_data_type = gdal.GDT_Int16, driver = r'GTiff'):
    ''' returns gdal data source raster object

    '''
    # create driver
    driver = gdal.GetDriverByName(driver)

    output_raster = driver.Create(output_path,
                                  int(columns),
                                  int(rows),
                                  nband,
                                  eType = gdal_data_type)    
    return output_raster


# In[8]:


def numpy_array_to_raster(output_path,
                          numpy_array,
                          geoTin,
                          projectionin,
                          nband = 1,
                          no_data = -9999,
                          gdal_data_type = gdal.GDT_Int16,
                          driver = r'GTiff'):
    ''' returns a gdal raster data source

    keyword arguments:

    output_path -- full path to the raster to be written to disk
    numpy_array -- numpy array containing data to write to raster
    geoTin -- geotransform input from ds.GetGetGeoTransform()
    projectionin -- projection input from ds.GetProjection()
    nband -- the band to write to in the output raster
    no_data -- value in numpy array that should be treated as no data
    gdal_data_type -- gdal data type of raster (see gdal documentation for list of values)
    driver -- string value of the gdal driver to use

    '''


    rows, columns = numpy_array.shape

    # create output raster
    output_raster = create_raster(output_path,
                                  int(columns),
                                  int(rows),
                                  nband,
                                  gdal_data_type) 

    geotransform = geoTin


    output_raster.SetProjection(projectionin)
    output_raster.SetGeoTransform(geotransform)
    output_band = output_raster.GetRasterBand(1)
    output_band.SetNoDataValue(no_data)
    output_band.WriteArray(numpy_array)          
    output_band.FlushCache()
    output_band.ComputeStatistics(False)

    if os.path.exists(output_path) == False:
        raise Exception('Failed to create raster: %s' % output_path)

    return  


# # Main part

# ## Create dataframe with the different files available and sort them by tile and 10days period

# In[9]:


filelistMCD43A3=[os.path.join(collectiondir,y,f) for y in years for f in os.listdir(os.path.join(collectiondir,y)) if os.path.isfile(os.path.join(collectiondir,y,f).replace('MCD43A3','MCD43A2'))]


# In[10]:


ECOSGdates=['0105', '0115', '0125', '0205', '0215', '0225', '0305', '0315',
            '0325', '0405', '0415', '0425', '0505', '0515', '0525', '0605',
            '0615', '0625', '0705', '0715', '0725', '0805', '0815', '0825',
            '0905', '0915', '0925', '1005', '1015', '1025', '1105', '1115',
            '1125', '1205', '1215', '1225',]


# In[11]:


tilepattern='.h\d\dv\d\d'
tilelist= [re.search(tilepattern,f).group() for f in filelistMCD43A3]
hlist=[int(t.split('h')[1].split('v')[0]) for t in tilelist]
vlist=[int(t.split('h')[1].split('v')[1]) for t in tilelist]
dayspattern='.A\d\d\d\d\d\d\d'
dayslist= [re.search(dayspattern,f).group() for f in filelistMCD43A3]
yearlist=[int(d[2:6]) for d in dayslist]
juliandays=[int(d[6:9]) for d in dayslist]
julian10daysclass=[int((j/365)*36) for j in juliandays]
ECOSG10days=[ECOSGdates[j10] for j10 in julian10daysclass]
data = {'filename':filelistMCD43A3, 'tile':tilelist,'htile':hlist,'vtile':vlist,
        'year':yearlist,'julianday':juliandays,'julian10days':julian10daysclass,
        'ecosg10':ECOSG10days}
df=pd.DataFrame(data)
groupeddftilejuliandays=df.groupby(['htile','vtile','ecosg10'])


# ## Loop over the group aplly quality filter and calculate the 10-day mean

# In[ ]:


outpath=os.path.join(os.getcwd(),OUTPUTDIR)
if not os.path.isdir(outpath):
    os.mkdir(outpath)

files_issuelist=[]
for name, group in groupeddftilejuliandays:
        VISlist=[]
        VISsnowfreelist=[]
        NIRlist=[]
        NIRsnowfreelist=[]
        print(name)
        for i,fn in enumerate(group.filename):
            try:
                VIS_np,VIS_Sfree_np,fillv, NIR_np,NIR_Sfree_np,filln,geoT,projT,w,h=onefilefilter_treatment(fn,1,0)
                VISlist.append(np.ma.masked_array(VIS_np,VIS_np==fillv))
                VISsnowfreelist.append(np.ma.masked_array(VIS_Sfree_np,VIS_Sfree_np==fillv))
                NIRlist.append(np.ma.masked_array(NIR_np,NIR_np==filln))
                NIRsnowfreelist.append(np.ma.masked_array(NIR_Sfree_np,NIR_Sfree_np==filln))
            except:
                files_issuelist.append(fn)
        VIS_median=np.ma.median(np.ma.stack(VISlist),axis=0,overwrite_input=True)
        numpy_array_to_raster(os.path.join(outpath,'vis_h'+str(name[0])+'v'+str(name[1])+'jd'+str(name[2])+'.tif'),
                              VIS_median,geoT,projT,nband = 1,no_data = fillv,gdal_data_type = gdal.GDT_Int16,driver = r'GTiff')
        VISsf_median=np.ma.median(np.ma.stack(VISsnowfreelist),axis=0,overwrite_input=True)
        numpy_array_to_raster(os.path.join(outpath,'vis_sf_h'+str(name[0])+'v'+str(name[1])+'jd'+str(name[2])+'.tif'),
                              VISsf_median,geoT,projT,nband = 1,no_data = fillv,gdal_data_type = gdal.GDT_Int16,driver = r'GTiff')
        NIR_median=np.ma.median(np.ma.stack(NIRlist),axis=0,overwrite_input=True)
        numpy_array_to_raster(os.path.join(outpath,'nir_h'+str(name[0])+'v'+str(name[1])+'jd'+str(name[2])+'.tif'),
                              NIR_median,geoT,projT,nband = 1,no_data = fillv,gdal_data_type = gdal.GDT_Int16,driver = r'GTiff')
        NIRsf_median=np.ma.median(np.ma.stack(NIRsnowfreelist),axis=0,overwrite_input=True)
        numpy_array_to_raster(os.path.join(outpath,'nir_h'+str(name[0])+'v'+str(name[1])+'jd'+str(name[2])+'.tif'),
                              NIRsf_median,geoT,projT,nband = 1,no_data = fillv,gdal_data_type = gdal.GDT_Int16,driver = r'GTiff')

