# laialbedomodis
 ## Required python libraires
os
earthdata
matplotlib
numpy
os
re
pandas
gdal
rasterio

 ## 0 Download the ECO-SG LAI albedo and land cover map if needed
Follow the instruction from https://opensource.umr-cnrm.fr/projects/ecoclimap-sg/wiki in the Compress folder 
```
$ cd Compress
$ ftp ftp.umr-cnrm.fr
...
...
```
 ## 1. Uncompress ECOCLIMAP-SG files
  ### 1.1 uncompress all the .gz file
```
$ gzip -d *.gz
```
This will lead to XX_MMJJ_c.dir XX_MMJJ_c.hdr (XX depending on the file you are working on)
   ### 1.2 Edit the first line of make_uncompress_files.sh according to your file names
example for LAI files
```
$ vi make_uncompress.sh
$i 
$for file in LAI*
$:wq

```
example for vissible albedo files
```
$ vi make_uncompress.sh
$i 
$for file in AL-BH-VI*
$:wq

```

   ### 1.3 run make_uncompress.sh
this will create XX_MMJJ_c.dir_2 file 
```
$ chmod +x make_uncompress.sh
$ ./run make_uncompress.sh 
```
  ### 1.4 run cat_hdr_files.sh
It overwrite every  XX_MMJJ_c.hdr file with the content of example.hdr

```
$ chmod +x cat_hdr_files.sh
$ ./run cat_hdr_files.sh
```
  ## 2. Download nasa data  
   ### 2.1 Install earthdata python library
This is a python library to access NASA data https://earthdata.readthedocs.io/en/latest/
```
python3 -m pip install earthdata
```
   ### 2.2 Register on NASA modis website and create a .netrc for authentification in earthdata
```
$ touch .netrc

$ echo "machine urs.earthdata.nasa.gov login USERNAME password PASSWORD " > .netrc

$ chmod 0600 .netrc

```
   ### 2.3 Run the script or the notebook to download the data
Currently it downloads the data only one product and year at a time the process can be long so I recommend to run the script
Don't forget to change the SHORTNAME, COLLECTION, YEAR etc in the file to the desired values before running the script

```
$ cd Download_nasa_data
$ vi Download_nasa_script.py
.....
$:wq
$ nohup python3 Download_nasa_script.py

```
## 3. Create 10 days median for each tiles
Go in the tiles_median directory and run the script or notebook "MODIS_albedo_QC_snow_10_daymedian"
Edit the DATADIR which is the directory where your MCD43A3 data have been downloaded (for future collection or different product it needs to be replaced
```
$ cd tiles_median

$ nohup python3 MODIS_albedo_QC_snow_10_daymedian.py
```
MODIS_albedo_QC_snow_10_daymedian lists all the MCD43A3 and MCD43A2 pairs presents in datadir
Proceed the MCD43A3 QC on the NIR and VIS band, identifies the snow data using MCD43A2 and produce 10days median following the ECOCLIMAP-SG dates
saves the 10days median in the OUTPUTDIR
## 4 Merge and reproject MODIS tiles
```
$ cd merge_tiles_reproject/
```
## 5 Merge MODIS to the rest of ECOSG data

```
$ cd merge_modis_ecosg 
```

## 6 Recompress the resulting files

```
$ cd Compress
```


