#!/bin/bash

echo "Master: $master"

if [ "x$master" == "x" ]; then
    echo "Master is null, use 192.168.7.100"
    master=192.168.7.100
fi

dest=/opt/local/
mpt=`mktemp -d`
nfsloc=$master:/software/linux

init() 
{
    mkdir -p $dest $mpt
    mount $nfsloc $mpt
}

clean()
{
    umount  -f $mpt
}

install_eclipse()
{
    javapkg=`ls $mpt/jdk*`
    epkg=`ls $mpt/eclipse*`
    
    ls -d $dest/jdk* $dest/eclipse* 
    if [ "x$?" == "x0" ]; then
        echo "The JAVA_HOME and Eclipse home exists, exit"
        return 0
    fi

    tar xf $javapkg -C $dest
    tar xf $epkg -C $dest

    jhome="`ls -d $dest/jdk*`"
    ehome="`ls -d $dest/eclipse*`"
    cat << _EOF > /etc/environment
PATH=$PATH:$jhome/bin/
JAVA_HOME=$jhome
CLASSPATH=$jhome/lib/dt.jar:$jhome/lib/tools.jar:.
_EOF

    cat << _EOF > /usr/share/applications/eclipse.desktop
[Desktop Entry]
Name=Eclipse
GenericName=Eclipse
Comment=Eclipse IDE
Exec=$ehome/eclipse
Terminal=false
Type=Application
StartupNotify=true
Icon=$ehome/icon.xpm
Categories=Development
Actions=new-window;new-document;
Keywords=Java;IDE;Eclipse
_EOF

}

installpkgs()
{
    install_eclipse
}

#################################
######### Main   Entry ##########
#################################

init

installpkgs

clean
