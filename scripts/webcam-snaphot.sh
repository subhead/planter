#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")

fswebcam -r 1280x720 --no-banner -d /dev/video0 /media/motion/Snap-$DATE.jpg