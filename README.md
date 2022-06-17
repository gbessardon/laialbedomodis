# laialbedomodis

# 0 Download the ECO-SG LAI albedo and land cover map if needed
Follow the instruction from https://opensource.umr-cnrm.fr/projects/ecoclimap-sg/wiki in the Compress folder 
 ## 1. Uncompress ECOCLIMAP-SG files
  ### 1.1 uncompress all the .gz file
```
$ gzip -d *.gz
```
This will lead to XX_MMJJ_c.dir XX_MMJJ_c.hdr (XX depending on the file you are working on
   ### 1.2 Copy run make_uncompress.sh and uncompress_file_300m0.F90 in the folder containing LAI_MMJJ_c.dir LAI_MMJJ_c.hdr couples
   
   ### 1.3 run make_uncompress.sh
this will create LAI_MMJJ_c.dir_2 file a file that can be read outside surfex0
  ## 2. Download nasa scripts
