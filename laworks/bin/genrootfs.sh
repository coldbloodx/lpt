#!/bin/bash

# by Leo.C.Wu 2013 copyright by LAWorks

#if [ -d $rootfsdir ]; then
#    echo "$fsdir exists, all contents in it should be removed. "
#fi

password=letmein
apturl=http://mirrors.163.com/ubuntu/
#apturl=http://itaas:itaas@9.111.113.25/ubuntu/

ipkgs="linux-image-generic openssh-server vim bash-completion tree subversion build-essential git-core nfs-common ctags cscope  libc6-dev"
rpkgs="thunderbird-gnome-support thunderbird libreoffice-avmedia-backend-gstreamer libreoffice-base-core libreoffice-calc libreoffice-common libreoffice-core libreoffice-draw libreoffice-gnome libreoffice-gtk libreoffice-impress libreoffice-math libreoffice-ogltrans libreoffice-pdfimport libreoffice-style-breeze libreoffice-style-elementary libreoffice-style-galaxy libreoffice-writer"

which ngls > /dev/null 2>&1
if [ "$?" != "0" ]; then
    echo "Can not find ngls"
    exit 1
fi

if [ "x$1" = "x" -o "x$1" = "x-h" ]; then
    echo "Usage: $0 ngname"
    exit 1
fi


ngname=$1
ngls $ngname > /dev/null 2>&1
if [ "x$?" != "x0" ]; then
    exit 1
fi

uitype=`ngls -g $ngname -c uitype --valueonly`
if [ "x$uitype" = "x" ]; then
    echo "Can not get uitype for $ngname"
    exit 1
fi

fsdir=/tmp/${uitype}rootfs
srclist=$fsdir/etc/apt/sources.list

if [ "x$uitype" = "xgui" ]; then
    ipkgs="$ipkgs ubuntu-desktop"
fi

distro=`ngls -g $ngname -c distro --valueonly`
if [ "x$distro" = "x" ]; then
    echo "Can not get distro for $ngname"
    exit 1
fi

###########################
#    Main starts here     # 
###########################

debootstrap --verbose --no-check-gpg `lsb_release -cs` $fsdir $apturl

#prepare new source list file

cp /etc/apt/sources.list $srclist

#some runtime information
mount -o bind /dev $fsdir/dev
mount -o bind /sys $fsdir/sys
mount -t proc proc $fsdir/proc

#change root and do some thing

# <------ command for chroot start

cat <<_EOF > $fsdir/env.sh
#!/bin/bash

#change root password
echo -e "$password\n$password" |passwd


#environment variable to disable interactive prompt
export DEBIAN_FRONTEND=noninteractive

#install some necessary packages
apt -y clean
apt -y update
apt -o Dpkg::Options::="--force-confdef" -fuy install -y --allow-unauthenticated $ipkgs

#remove useless pkgs
apt -y purge $rpkgs
apt -y autoremove

#clean again for the installed packages
apt -y clean

#unset environment variable
unset DEBIAN_FRONTEND

#configure locales
#/usr/share/locales/install-language-pack en.US
locale-gen en_US.UTF-8

cat << __LAEOF >> /etc/default/locale
LANG="en_US.UTF-8"
LANGUAGE="en_US.UTF-8"
__LAEOF

#fix grub menu
sed -i 's/GRUB_HIDDEN_TIMEOUT=0/#GRUB_HIDDEN_TIMEOUT=0/g' /etc/default/grub

#fix ssh root login
sed -ie 's/PermitRoot.*/PermitRootLogin yes/g; s/StrictModes.*/StrictModes No/g' /etc/ssh/sshd_config

#did not show all files for alias ll
sed -i 's/alF/hlF/g' /root/.bashrc

_EOF

# <------ command for chroot end

chroot $fsdir /bin/bash -c "/bin/bash env.sh"

sleep 3
umount --force $fsdir{/dev,/sys,/proc}

sleep 3
umount --force $fsdir{/dev,/sys,/proc}


# make some config changes
LAHOME=/opt/laworks
#add customed vimrcs
cp -fr $LAHOME/etc/config/vim/{.vimrc,.vim}  $fsdir/root/

#fix .profile issue when gui login 
if [ "x$uitype" = "xgui" ]; then
    sed -i 's/mesg/tty -s \&\& mesg n/g' $fsdir/root/.profile
    echo "greeter-show-manual-login=true" >> $fsdir/usr/share/lightdm/lightdm.conf.d/50-ubuntu.conf
fi

#make rootfs
exclude_list=/tmp/exclude_list

cat << _EOF > $exclude_list
proc/*
dev/*
tmp/*
_EOF

ln -sf $LAHOME/rootfs /var/www/

cd $fsdir
tar -czf /var/www/rootfs/$distro/${uitype}rootfs.tar.gz . -X $exclude_list
cd - > /dev/null 2>&1
