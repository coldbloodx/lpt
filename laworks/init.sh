

errexit()
{
    echo "$1" 1>&2
    exit 1
}

initenv()
{
    LAPWD=`pwd`
    LAROOT=/opt/laworks
    LAMISC=$LAROOT/misc
    LACGI=$LAROOT/cgi
    LAWEB=$LAROOT/web
    INSTCONF=$LAROOT/etc/install.conf

    if [ ! -f "$LAPWD/init.sh" ]; then 
        errexit "Cannot init environment in other directory, enter code root directory first" 
    fi

    #create root directory 
    ln -sf $LAPWD /opt/

    #unalias cp in case the cp is alias of cp -i
    unalias cp > /dev/null 2>&1
}

installpkgs()
{
    pkgfilepath=$LAROOT/etc/packages 
    if [ ! -f $pkgfilepath ];  then
        errexit "Cannot find $LAROOT/etc/packages" 
    fi

    pkgs=`cat $pkgfilepath |xargs`
    apt -y install $pkgs 
    if [ "x$?" != "x0" ]; then
        errexit "Cannot install $pkgs, check the pkgs and restart the script"
    fi

}

buildenv()
{
    #now we have environment
    cp $LAROOT/bin/laworks.profile /etc/profile.d
    source /etc/profile.d/laworks.profile
    touch /etc/.master

    chmod 755 $LAROOT/libexec/initdb.py
    $LAROOT/libexec/initdb.py
    
    echo "Generating RAM disk..."
    $LAROOT/libexec/geninitrd.sh

    echo "Generating rootfs..."
    #genrootfs.sh ubuntu-Disked-GUI
    #genrootfs.sh ubuntu-Disked-CLI
    
    if [ ! -f $LAROOT/bak ]; then
        mkdir -p $LAROOT/etc/bak
    fi

    cp /etc/default/tftpd-hpa $LAROOT/etc/bak
    cp /etc/dhcp/dhcpd.conf $LAROOT/etc/bak
    
    #tftpd
    mkconfig -t tftp > /etc/default/tftpd-hpa

    mkconfig -t httpd > /etc/apache2/sites-enabled/001-lpt.conf
   
    #dhcpd
    mkconfig -t dhcpd > /etc/dhcp/dhcpd.conf
    provnic=`grep 'provnic.*".*"' $INSTCONF|sed 's/"provnic".*:.*"\(.*\)".*,/\1/' |tr -d " "`
    pubnic=`grep 'pubnic.*".*"' $INSTCONF|sed 's/"pubnic".*:.*"\(.*\)".*,/\1/' |tr -d " "`

    cat > /etc/default/isc-dhcp-server <<_EOF  
INTERFACES="$provnic"
_EOF

    #httpd related staff

    #enable cgi
    ln -sf /etc/apache2/mods-available/cgi.load /etc/apache2/mods-enabled/

    #create part schema links
    for ngid in `ngls --valueonly -c ngid`; do 
        ln -sf $LAMISC/profiles/default $LAMISC/profiles/$ngid
    done
    
    #add kernel
    cp -f /vmlinuz /tftpboot/linux
    chmod 644 /tftpboot/linux
    
    #gen ssh keys
    if [ ! -f /root/.ssh/id_rsa.pub ]; then
        ssh-keygen -t rsa -b 1024 -f /root/.ssh/id_rsa -N ""
    fi
    cp /root/.ssh/id_rsa.pub $LAMISC/others/.id_rsa.pub

    systemctl enable apache2.service tftpd-hpa.service isc-dhcp-server
    systemctl stop apache2.service tftpd-hpa.service isc-dhcp-server
    sleep 3
    systemctl start apache2.service tftpd-hpa.service isc-dhcp-server

    #config proxy
    if ! grep "net\.ipv4\.ip_forward=1" /etc/sysctl.conf  > /dev/null 2>&1  ; then
        echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    fi
    sysctl -p

    nwstr=`netls -t provision -c network,netmask --valueonly`
    provnet=`echo $nwstr |tr " " "/"`
    iptables -F
    iptables -F -t nat
    iptables -P FORWARD ACCEPT
    iptables -t nat -A POSTROUTING -s $provnet -o $pubnic -j MASQUERADE
}

initpxeroot()
{
    #create tftp boot 
    ln -sf /var/lib/tftpboot /
    mkdir -p /tftpboot/pxelinux.cfg
    cp -f /usr/lib/PXELINUX/pxelinux.0 /tftpboot
    cp -f /usr/lib/syslinux/modules/bios/ldlinux.c32 /tftpboot
}

confignfs()
{
    echo "config nfs"
}

configsamba()
{
    echo "config samba"
}

configwin()
{
    echo "config win"
}

################### Main #################
##########################################


#init environment
initenv

#install packages
installpkgs

#init pxe root
initpxeroot

#update environment
buildenv

#config services
confignfs
configsamba

#config windows provision
configwin
