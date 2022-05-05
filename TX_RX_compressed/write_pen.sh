#!/bin/bash

pen_path=/media/usb
origin_path=.

pen_name=`ls -l /dev/disk/by-uuid/ | grep -o sda.*`
sudo mount /dev/$pen_name /media/usb -o uid=pi,gid=pi
cp $origin_path/$1 $pen_path/$1
sudo umount /media/usb
