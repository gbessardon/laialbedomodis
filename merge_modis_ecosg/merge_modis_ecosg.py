#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import gdal
from matplotlib import pyplot as plt
import os
import re
import rasterio
from rasterio.merge import merge
from rasterio.plot import show


# In[2]:


ecodir='/home/gbessardon/DATA/LAI_treatement/Uncompress/'
modisdir='/home/gbessardon/DATA/laialebdomodis/'
outputdir='/home/gbessardon/DATA/laialebdomodis/MODISECOSG'


# In[3]:


if not os.path.isdir(outputdir):
    os.mkdir(outputdir)


# In[4]:


def merge_eco_mos(fneco,fnmodis,out_fp,h=54000,w=129600):
    src=rasterio.open(fneco)
    src2=rasterio.open(fnmodis)
    src_files_to_mosaic=[src,src2]
    mosaic, out_trans = merge(src_files_to_mosaic)
    mosaic[mosaic==255]=0
    out_meta = src2.meta.copy()    
    # Update the metadata
    out_meta.update({"driver": out_meta.get('driver'),
                  "height": h,
                  "width": w,
                  "transform": out_trans,
                  "nodata":0,
                 }
                )
    with rasterio.open(out_fp, "w", **out_meta) as dest:
        dest.write(mosaic)
    return 


# In[5]:


listecosg=[os.path.join(ecodir,f) for f in os.listdir(ecodir) if (f.startswith('AL-BH-VI') and f.endswith('c.dir_2'))]
listmodis=[os.path.join(modisdir,f) for f in os.listdir(modisdir) if (f.startswith('mosaic') and f.endswith('ecosg.tif'))]


# In[6]:


dayspattern='mosaic\d\d\d\d'
dayslist= [re.search(dayspattern,f).group().split('mosaic')[1] for f in listmodis]
testlist=[le for d in dayslist for le in listecosg if d in le]
Resultlist=[os.path.join(outputdir,t.split(ecodir)[1]).replace('dir_2','tif') for t in testlist]


# In[7]:


data={'ECOSGfiles':testlist, 'MODISfiles':listmodis, 'days':dayslist, 'outputlist': Resultlist}
df=pd.DataFrame(data) 


# In[8]:


for ind in range(0,len(df)):
    merge_eco_mos(df.ECOSGfiles[ind],df.MODISfiles[ind],df.outputlist[ind])


# In[9]:


gdal.Info(df.outputlist[ind])


# In[14]:


src=rasterio.open(df.outputlist[ind-4])
show(src)


# In[15]:


src=rasterio.open(df.ECOSGfiles[ind-4])
show(src)


# In[ ]:




