#!/bin/bash

apt install uvcdynctrl

# https://raspberrypi.stackexchange.com/questions/43118/turning-off-the-blue-status-led-on-the-logitech-c920-usb-camera
uvcdynctrl -i /usr/share/uvcdynctrl/data/046d/logitech.xml

# LED off
uvcdynctrl -s 'LED1 Mode' 0
# LED on
#uvcdynctrl -s 'LED1 Mode' 1
# LED blinking
#uvcdynctrl -s 'LED1 Mode' 2
# LED auto mode
#uvcdynctrl -s 'LED1 Mode' 3