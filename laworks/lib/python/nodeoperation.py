#!/usr/bin/env python

import os

from Cheetah.Template import Template

from IPy import IP
from ipfun import ipsort, get_available_ips
from dbhelper import *
from dbitem import *
from makeconfig import makehosts
from dbman import ConnManager as DBConnManager

def get_available_num(numbers, maxnum):
    counter = 0
    for i in numbers:
        if i != counter:
            return counter
        counter = counter + 1

    if counter < maxnum:
        return counter

    return 'zzz'

def importnode(dbconn, mac, nodegroup, iface='eth0'):
    ng = get_ng_byname(dbconn, nodegroup)
    if not ng :
        return False, "Can not find such nodegroup"

    nic = get_nic_bymac(dbconn, mac)
    if nic:
        return False, "The nic has been already used by another node"

    network = None
    for n in ng.networks:
        if n.nwtype == NETTYPE_PROV:
            network = n
            break

    nodename = getnext_nodename(dbconn, ng.ngid)
    node = Node(nodename, ng.ngid, STATUS_IMPORTED)
    dbconn.add(node)
    dbconn.commit()
    
    ips = get_available_ips(dbconn)
    if not ips:
        return False, "No ip available on the network"

    nic = Nic(iface, mac, ips[0], node.nid, network.netid, NICTYPE_BOOT)
    dbconn.add(nic)
    dbconn.commit()
    
    sambadir = get_samba_dir(dbconn)

    if ng.os.ostype == 'windows':
        genwincmd(sambadir, nic)
        genwinnbpxe(nic) 
    elif ng.os.ostype == 'linux':
        genlnxnbpxe(nic)
    else:
        pass

    hosts = makehosts(dbconn)
    hostsfp = open("/etc/hosts", 'w')
    hostsfp.writelines(hosts)
    hostsfp.writelines("\n")
    hostsfp.close()
    
    return True, None


    
def getnext_nodename(dbconn, ngid):
    nodegroup = get_ng_byid(dbconn, ngid)

    if not nodegroup:
        return False

    nodes = get_nodes_byngid(dbconn, nodegroup.ngid)

    stub = '#'
    nodename = None
    
    index = nodegroup.namerule.find(stub)
    prefix = nodegroup.namerule[0:index]
    placeholder = nodegroup.namerule[index-1:-1]

    holderlen = len(placeholder)

    nextnum = 0
    if not nodes:
        nextnum = '{num:{fill}{width}}'.format(num=0, fill='0', width=holderlen)
    else:
        numbers = []
        separator = '-'
        for node in nodes:
            strarray = node.nodename.split(separator)
            numbers.append(int(strarray[-1], 10))

        num = get_available_num(numbers, pow(10, 2))
        nextnum = '{n:{fill}{width}}'.format(n=num, fill='0', width=holderlen)

    return "%s-%s" % (prefix, nextnum)


def gennodeinfo(node):
    nodeinfo = '#!/bin/sh\n'
    nid = node.nid
    nodename = node.nodename
    ngid = node.nodegroup.ngid
    provtype = node.nodegroup.provtype
    uitype = node.nodegroup.uitype
    distro = node.nodegroup.os.osname.lower()
    bootnic = ''
    nicstrs = []
    for nic in node.nics:
        #nicname1:network1:ip1:netmask1:broadcast1:gateway1:dns1
        tempstr = "%s:%s:%s:%s:%s:%s:%s" % (nic.nicname, nic.network.network, nic.ip,
                nic.network.netmask, nic.network.broadcast, nic.network.gateway, nic.network.dns)
        if nic.nictype == NICTYPE_BOOT:
            bootnic = nic.nicname
        nicstrs.append(tempstr)

    nicinfo = ";".join(nicstrs)

    dualboot = node.nodegroup == PROVTYPE_DUALBOOT

    #add all content
    infotmpl = Template(file=NODEINFO_TMPL,
            searchList=[{'NID': nid, 'NODENAME':nodename, 'NGID': ngid, 
                'NICINFO': nicinfo, 'DUALBOOT': dualboot, 'BOOTNIC': bootnic,
                'PROVTYPE': provtype, 'UITYPE': uitype, 'DISTRO': distro}])

    content = str(infotmpl)
    nodeinfo = nodeinfo + content
    return nodeinfo

def genwincmd(sambadir, nic):
    wintmpl = Template(file=AUTO_INSTALL_CMD_TMPL)

    content = str(wintmpl)
    mac = nic.mac.replace(":", "-")
    cmdfile = "%s/autoinstall/%s.cmd" % (sambadir, mac)
    fp = open(cmdfile, 'w+')
    fp.write(content)
    fp.close()

def genwinnbpxe(nic):
    macfilename = "01-%s" % (nic.mac.replace(":", "-"))
    macfile = "%s/%s" % (PXEFILE_DIR, macfilename.lower())
    content = """LABEL install
default install
kernel Boot/pxeboot.0
"""

    target = file(macfile, 'w')
    target.writelines(content)
    target.close()

    os.chmod(macfile, 0666)

def genlnxnbpxe(nic):
    # necessary information
    dbconn = DBConnManager.get_session()
    masterip = get_master_ip(dbconn)
   
    # gengerate file content
    pxetmpl = Template(file=NETBOOT_TMPL, searchList=[{'parentip': masterip, 'ip':nic.ip, 'netmask': nic.network.netmask}])
    content = str(pxetmpl)

    # generate pxe file
    macfilename = "01-%s" % (nic.mac.replace(":", "-"))
    macfile = "%s/%s" % (PXEFILE_DIR, macfilename.lower())
    target = file(macfile, 'w')
    target.writelines(content)
    target.close()
    os.chmod(macfile, 0666)

def genlocalbootpxe(nic):
    pxetmpl = file(LOCALBOOT_TMPL, 'r')
    content = pxetmpl.readlines()
    pxetmpl.close()

    macfilename = "01-%s" % (nic.mac.replace(":", "-"))
    macfile = "%s/%s" % (PXEFILE_DIR, macfilename.lower())
    target = file(macfile, 'w')
    target.writelines(content)
    target.close()

    os.chmod(macfile, 0666)

def removenodes(namelist):

    dbconn = DBConnManager.get_session()

    nodes = dbconn.query(Node).filter(Node.nodename.in_(namelist)).all()
    if not nodes:
        return None, None

    valid_node_names = [ node.nodename for node in nodes ]
    invalid_node_names = list(set(namelist) - set(valid_node_names))

    nidlist = [ node.nid for node in nodes ]
    nics = dbconn.query(Nic).filter(Nic.nid.in_(nidlist)).filter(Nic.nictype==NICTYPE_BOOT).all()
    ips = [ nic.ip for nic in nics ]


    macfiles = [ "01-%s" % nic.mac.replace(':', "-") for nic in nics ] 
    rmcmd = "cd %s; rm -fr %s" % (PXEFILE_DIR, " ".join(macfiles))
    os.system(rmcmd) 

    maccmds = [ "%s.cmd" % nic.mac.replace(":", "-") for nic in nics ]
    cmddir = "%s/autoinstall/" % (get_samba_dir(dbconn))
    rmcmd = "cd %s; rm -fr %s " % (cmddir, " ".join(maccmds))
    os.system(rmcmd) 
    
    for node in nodes:
        dbconn.delete(node)

    dbconn.commit()
    dbconn.close()

    hostsfp = open('/etc/hosts', 'r')
    content = hostsfp.readlines()
    hostsfp.close()
    
    newcontent = []
    for line in content:
        # handle empty lines
        if not line.strip():
            newcontent.append(line)
            continue

        ip = line.split()[0]

        if ip not in ips:
            newcontent.append(line)

    hostsfp = open('/etc/hosts', 'w')
    content = hostsfp.writelines(newcontent)
    hostsfp.close()

    return valid_node_names, invalid_node_names
