#!/bin/bash




#main

bash -x proxy.sh
sleep 3
bash -x platform_ldap_autofs.sh

if [ -f /bak/configs/hosts ]; then 
    cat  /bak/configs/hosts  >> /etc/hosts
fi
sleep 3
bash -x nfs.sh
