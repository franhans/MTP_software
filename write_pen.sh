#!/bin/bash

pen_path=/media/usb
origin_path=.

sudo mount /dev/sda1 /media/usb -o uid=pi,gid=pi
cp $origin_path/$1 $pen_path/$1
sudo umount /media/usb
