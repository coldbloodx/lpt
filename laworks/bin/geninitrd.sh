#!/bin/bash

LAHOME=/opt/laworks
SCRIPTSDIR=$LAHOME/scripts
SCRIPT=laworks
HOOKDIR=/usr/share/initramfs-tools/hooks
DESTDIR=/var/lib/tftpboot/
INITRD=initrd.gz

cp $SCRIPTSDIR/$SCRIPT $HOOKDIR

mkinitramfs -o  $DESTDIR/$INITRD

rm -fr $HOOKDIR/$SCRIPT
