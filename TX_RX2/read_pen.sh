#!/bin/bash

pen_path=/media/usb
destination_path=.

pen_name=`ls -l /dev/disk/by-uuid/ | grep -o sda.*`
sudo mount /dev/$pen_name /media/usb -o uid=pi,gid=pi
cp $pen_path/$1 $destination_path/$1 
tar czvf  $1 $1 
sudo umount /media/usb
