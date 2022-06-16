for file in AL-BH-VI_09*
do

  echo $file
  sed -e "s/filein/$file/g" uncompress_file_300m0.F90 > uncompress_file_300m.F90
  gfortran uncompress_file_300m.F90 
  ./a.out

done
