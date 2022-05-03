#!/bin/bash

pen_path=/media/usb
destination_path=.

sudo mount /dev/sda1 /media/usb -o uid=pi,gid=pi
cp $pen_path/$1 $destination_path/$1 
sudo umount /media/usb
