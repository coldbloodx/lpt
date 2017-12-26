#!/bin/bash

#The script is used to setup ldap and autofs in intranet environment in IBM Platform Xi'an branch
#By Leo.C.Wu

function errexit()
{
    echo "$1" > /dev/null 2>&1
    exit 1
}

function installpkgs()
{
    pkgs="nss-pam-ldapd openldap autofs authconfig nfs-utils csh"
    yum -y install $pkgs

    if [ "x$?" != "x0" ]; then
        errexit "can not install packages: $pkgs"
    fi
}

function setupldap()
{
    ldapurl='ldap://xa1ldap2.eng.platformlab.ibm.com'
    basedn='dc=platformlab,dc=ibm,dc=com'
    authconfig --enableldap --enableldapauth --ldapserver=$ldapurl --ldapbasedn=$basedn --disableldaptls --disablecache  --disablelocauthorize --update

    #enable and restart nslcd
    #echo "restart nslcd ..."
    #systemctl enable nslcd
    #systemctl stop nslcd
    #systemctl start nslcd
}

function setupautofs()
{
    # set default nfs mount version = 3
    echo "Defaultvers=3" >>  /etc/nfsmount.conf

    # set up /etc/idmap.conf 
    echo "Domain = eng.platformlab.ibm.com" >> /etc/idmapd.conf

    cat >> /etc/autofs.master << _EOF
/home    ldap:nisMapName=auto.home,ou=linux,ou=xa,ou=autofs,dc=platformlab,dc=ibm,dc=com vers=3
/pcc    ldap:nisMapName=auto.pcc,ou=linux,ou=xa,ou=autofs,dc=platformlab,dc=ibm,dc=com vers=3
/scratch    ldap:nisMapName=auto.scratch,ou=linux,ou=xa,ou=autofs,dc=platformlab,dc=ibm,dc=com vers=3
_EOF

    systemctl enable autofs
    systemctl stop autofs
    systemctl start autofs
}


#####################
#        Main       #
#####################

installpkgs

setupldap 

setupautofs
