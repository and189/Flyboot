#!/bin/bash

# Parameter (ADB location, Device IP:Port)
ADBLOC=$1
DEVICELOC=$2

# ADB command to reboot
$ADBLOC connect $DEVICELOC:5555
$ADBLOC -s $DEVICELOC reboot
$ADBLOC disconnect $DEVICELOC
RETURNCODE=$?

# Returncode
exit $RETURNCODE
