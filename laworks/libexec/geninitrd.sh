#!/bin/bash

if [ "x$LAROOT" == "x" ]; then
    echo "LAROOT is not set, ensure the environment has been set up"
    exit 1
fi

LAHOME=$LAROOT
SCRIPTSDIR=$LAHOME/etc/mkinitrd/
SCRIPT=laworks.hook
HOOKDIR=/usr/share/initramfs-tools/hooks
DESTDIR=/var/lib/tftpboot/
INITRD=initrd.gz

cp $SCRIPTSDIR/$SCRIPT $HOOKDIR

mkinitramfs -o  $DESTDIR/$INITRD

rm -fr $HOOKDIR/$SCRIPT
