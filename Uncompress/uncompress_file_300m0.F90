IMPLICIT NONE

integer*4,parameter :: ncol=43200, nlin=16800
integer*2,dimension(ncol*3) :: lread
integer*4,dimension(ncol*3) :: lread2
integer*1,dimension(ncol*3) :: lwrite
integer*1,dimension(ncol) :: lread_verif
integer*4 :: j, j2, i, k, icnt0, ideb
integer*4 :: icpt
integer*4,dimension(nlin*3) :: icpt2

open(11,file='filein',form='unformatted',access='stream')              
open(13,file='filein_2',form='unformatted',access='direct',recl=ncol*3)        

read(11) icpt2

! boucle sur les lignes
do j=1,nlin

  do j2 = 1,3

    ! lecture du lai
    lread(:) = 0
    read(11) lread(1:icpt2((j-1)*3+j2))
    lread2(:) = lread(:)
    do k = 1,icpt2((j-1)*3+j2)
      if (lread2(k)<0) lread2(k) = 32768*2 + lread2(k)
    enddo

    icpt = 0

    i = 1

    ! boucle sur les colonnes
    do 
   
      ! si on a dépassé la dernière colonne, on sort de la boucle
      if (icpt>=ncol*3) exit

      ! si la valeur est valide
      if (lread2(i)<4000) then

        ! on la met dans lwrite à l'indice icpt
        icpt = icpt + 1
        lwrite(icpt) = lread2(i)-floor(lread2(i)/100.)*100.
        ! on incrémente i
        i = i+1

      else

        do k = 1,lread2(i)-4000
          icpt = icpt + 1
          if (icpt>ncol*3) exit
          lwrite(icpt) = 0
        enddo

        i = i+1

      endif

    enddo

    write(13,rec=(j-1)*3+j2) lwrite(:)

  enddo

enddo

close(11)
close(13)
  

END
