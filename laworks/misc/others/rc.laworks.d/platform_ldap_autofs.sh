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
    echo "install pkgs"
    ostype=`lsb_release -is`
    case $ostype in
        CentOS | RedHatEnterpriseServer)
            pkgs="nss-pam-ldapd openldap autofs authconfig nfs-utils csh"
            yum -y install $pkgs
            ;;
        Ubuntu)
            preseed=/tmp/preseed.txt 
            cat > $preseed << _EOF
ldap-auth-config ldap-auth-config/ldapns/ldap-server     string    $ldapurl
ldap-auth-config ldap-auth-config/ldapns/base-dn         string    $basedn
ldap-auth-config ldap-auth-config/ldapns/ldap_version    select    3 
ldap-auth-config ldap-auth-config/dbrootlogin            boolean   false 
ldap-auth-config ldap-auth-config/dblogin                boolean   false 
nslcd            nslcd/ldap-uris                         string    $ldapurl 
nslcd            nslcd/ldap-base                         string    $basedn
_EOF
            cat $preseed | debconf-set-selections
            pkgs="autofs-ldap ldap-auth-client ldap-auth-config ldap-utils libnss-ldap libpam-ldap csh"
            apt -y install $pkgs
            ;;
        *)
            errexit "Unknown OS or lsb_release is not installed"
            ;;
    esac

    if [ "x$?" != "x0" ]; then
        errexit "can not install packages: $pkgs"
    fi
}

function setupldap()
{
    echo "setup ldap"
    ostype=`lsb_release -is`
    case $ostype in
        CentOS | RedHatEnterpriseServer)
            authconfig --enableldap --enableldapauth --ldapserver=$ldapurl --ldapbasedn=$basedn --disableldaptls --disablecache  --disablelocauthorize --update
            #restart nslcd when enabled ldap cache
            #echo "restart nslcd ..."
            #systemctl enable nslcd
            #systemctl stop nslcd
            #systemctl start nslcd
            # in rhel/centos 7 the nslcd can not be restarted, so disable cache
            ;;
        Ubuntu)
            auth-client-config -t nss -p lac_ldap
            ;;
        *)
            errexit "Unknown OS or lsb_release is not installed"
            ;;
    esac

}

function setupautofs()
{
    echo "setup autofs:"
    ostype=`lsb_release -is`
    case $ostype in
        CentOS | RedHatEnterpriseServer)
            # set default nfs mount version = 3
            echo "Defaultvers=3" >>  /etc/nfsmount.conf

            # set up /etc/idmap.conf 
            echo "Domain = eng.platformlab.ibm.com" >> /etc/idmapd.conf
            ;;
        Ubuntu)
            # add ldap_uri in autofs.conf
            sed -i "s/^#ldap_uri\ =\ \"\"/ldap_uri=\"ldap:\/\/$ldapserver\"/g" /etc/autofs.conf
            ;;
        *)
            errexit "Unknown OS or lsb_release is not installed"
            ;;
    esac
    cat >> /etc/auto.master << _EOF
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
ldapserver="xa1ldap2.eng.platformlab.ibm.com"
ldapurl="ldap://$ldapserver"
basedn='dc=platformlab,dc=ibm,dc=com'

installpkgs

setupldap 

setupautofs
