#!/bin/bash


function errexit()
{
    echo "$1" > /dev/null 2>&1
    exit 1
}

function init()
{
    if [ -f /etc/profile.d/nodeinfo ]; then
        . /etc/profile.d/nodeinfo
    else
        errexit "Cannot get node info"
    fi

    if [ "x$proxy" = "x" ]; then
        errexit "No proxy configured"
    fi
}

function setup_pkgmgr_proxy()
{
    ostype=`lsb_release -is`
    case $ostype in
        CentOS | RedHatEnterpriseServer)
            errexit "Not implement yet..."
            echo "proxy=$proxy" >> /etc/yum.conf
            ;;
        Ubuntu)
            proxyconf=/etc/apt/apt.conf.d/00proxy
            cat > $proxyconf << _EOF
Acquire::http::proxy "$proxy";
Acquire::https::proxy "$proxy";
_EOF
            ;;
        *)
            errexit "Unknown OS or lsb_release is not installed"
            ;;
    esac

    if [ "x$?" != "x0" ]; then
        errexit "can not install packages: $pkgs"
    fi
}


#main starts here:
init

setup_pkgmgr_proxy
