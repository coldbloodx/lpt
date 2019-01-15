#!/usr/bin/env python
#

import string
import os

from utils import runcmd
from dbitem import Network, Nic
from constant import NETTYPE_PROV
from IPy import IP

def getnicinfo(nicname):
    nic = nicname.strip()
    if not nic:
        return None

    out, err, ret = runcmd("ifconfig %s |grep -w inet" % (nic)) 

    if ret:
        return None

    #out could be:
    #ubuntu 18.04: ['inet 9.111.250.86  netmask 255.255.255.0  broadcast 9.111.250.255', ' ']
    #ubuntu 16.04: ['inet addr:9.111.250.85  Bcast:9.111.250.255  Mask:255.255.255.0', ' ']

    ip = ''
    broadcast = ''
    mask = ''
    mac = ''
    
    if(out[0].find(":") > 0):
        ip, broadcast, mask = [ i.split(":")[1] for i in outlist[1:] ]
    else:
        strlist = out[0].split()
        ip = strlist[1]
        broadcast = strlist[3]
        mask = strlist[5]


    out, err, ret = runcmd("ifconfig %s |grep -w HWaddr" % (nic))
    if ret:
        out, err, ret = runcmd("ifconfig %s|grep -w ether" % (nic))
        if ret:
            return None
        mac = out[0].strip().split()[1]
    else:
        mac = out[0].strip().split()[-1]
    
    #get lines like below
    #0.0.0.0         9.111.251.2     0.0.0.0         UG    0      0        0 ens160
    out, err, ret = runcmd("route -n |grep 'UG.*%s'" % (nic))
    gateway = ''
    if ret:
        gateway = ip
    else:
        gateway = out[0].strip().split()[1]

    return [ip, broadcast, mask, mac, gateway]

def get_available_ips(dbconn):
    provnet = dbconn.query(Network).filter_by(nwtype=NETTYPE_PROV).first()
    startip, endip = provnet.srange.split('-')

    allips = [ str(ip) for ip in IP(provnet.network).make_net(provnet.netmask) ]

    ippool = allips[allips.index(startip): allips.index(endip)+1]

    nics = dbconn.query(Nic.ip).filter_by(netid=provnet.netid).all()
    usedips = [ nic.ip for nic in nics ]

    ips = list(set(ippool) - set(usedips))
    ips.sort(ipsort)

    return ips

def onnet(ipaddr, netaddr, netmask):
    ipnet = IP(ipaddr).make_net(netmask)
    net = IP(netaddr).make_net(netmask)

    return ipnet == net

def ipsort(ipa, ipb):
    if ipa == ipb:
        return 0;

    aa = ipa.split(".")
    ab = ipb.split(".")

    for i in range(0,4):
        ai = int(aa[i])
        bi = int(ab[i])
        if ai > bi:
            return 1
        elif ai == bi:
            continue
        else:
            return -1
