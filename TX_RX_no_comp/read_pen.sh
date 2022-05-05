#!/bin/bash

pen_path=/media/usb
destination_path=.

pen_name=`ls -l /dev/disk/by-uuid/ | grep -o sda.*`
sudo mount /dev/$pen_name /media/usb -o uid=pi,gid=pi
file_name=$(ls /media/usb | grep .*.txt)
cp $pen_path/$file_name $destination_path/$1
sudo umount /media/usb

