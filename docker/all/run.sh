#!/bin/bash -eu

source /dist

if [ "$DIST" = "archlinux" ]
then echo /opt/openrobots/lib/python2.7/site-packages/ > /usr/lib/python2.7/site-packages/robotpkg.pth
fi
if [ "$DIST" = "centos7" ]
then export LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}
fi

if [ "$DIST" != "20.04" ]
then python2 /run.py
fi
python3 /run.py
