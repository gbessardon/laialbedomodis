for file in *_c.hdr
do
  echo $file
  cat example.hdr>$file

done
