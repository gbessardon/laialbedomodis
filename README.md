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
:q

```
example for vissible albedo files
```
$ vi make_uncompress.sh
$i 
$for file in AL-BH-VI*
:q

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
