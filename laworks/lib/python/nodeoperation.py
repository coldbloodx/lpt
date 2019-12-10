#!/usr/bin/env python

import os

from Cheetah.Template import Template

from IPy import IP
from ipfun import ipsort, get_available_ips, onnet
from dbhelper import *
from utils import *
from dbitem import *
from makeconfig import makehosts
from dbman import ConnManager as DBConnManager

def updatenode(dbconn, dictnode):

    if (not dictnode) or (not dictnode.has_key('nid')) and (not dictnode.has_key('nodename')):
        return 1, "invalid input node info"

    node = get_node_byid(dbconn, dictnode['nid'])

    if not node:
        return 1, "cannot find specified node"

        

    return 0, ""

def get_available_num(numbers, maxnum):
    counter = 0
    for i in numbers:
        if i != counter:
            return counter
        counter = counter + 1

    if counter < maxnum:
        return counter

    return 'zzz'

def importnodes(dbconn, deffile, nodegroup, updatehosts=True):
    if not os.path.isfile(deffile):
        return False, "Cannot find specified file: %s" % deffile

    ng = get_ng_byname(dbconn, nodegroup)
    if not ng :
        return False, "Can not find such nodegroup: %s" % nodegroup

    fp = open(deffile, "r")
    content = fp.readlines()
    fp.close()

    todonodes = {}

    netmap = get_net_map(dbconn)
    netnames = netmap.keys()
    node_bootnic_map =  {}
    
    for lineno, line in enumerate(content):
        #remove heading and tailing spaces
        if line: line = line.strip()
        #remove tailing "\n"
        if line: line = line.strip("\n")

        # for empty line
        if not line:
            continue

        # for line starts with a "#"
        if line.startswith("#"):
            continue

        mac, nodename, nodenicinfo = line.split(";")

        #print "lineno: %s, nodename: %s, mac: %s, nics: %s" % (lineno, nodename, mac, nodenicinfo)
        
        #check duplicate entry in deffile.
        if todonodes.has_key(nodename):
            errout("line: %s, node: %s duplicate with: %s, ignore" % todonodes[nodename]['lineno'])
            continue
        
        nodenics = {  } 
        if nodenicinfo:
            # nicname1@netname1,nicname2@netname2...
            nicinfolist = nodenicinfo.split(',')
            
            badnicinfo = False
            for nicinfo in nicinfolist:
                # no nic info
                if(nicinfo.find('@') < 0):
                    badnicinfo = True
                    break

                nicip, nicname= nicinfo.split("@")

                if (not onnet(nicip, netmap['provision'].network, netmap['provision'].netmask)) and \
                (not onnet(nicip, netmap['public'].network, netmap['public'].netmask)):
                    errout("IP: %s is on neither public network nor private network" % nicip)
                    badnicinfo = True
                    break

                if onnet(nicip, netmap['provision'].network, netmap['provision'].netmask):
                    provnic = Nic(nicname, mac, nicip, 'dummynid', netmap['provision'].netid, NICTYPE_BOOT) 
                    nodenics['provision'] = provnic

                    # fill the map for pxe file creation
                    node_bootnic_map[nodename] = provnic

                if onnet(nicip, netmap['public'].network, netmap['public'].netmask):
                    pubnic = Nic(nicname, None, nicip, 'dummynid', netmap['public'].netid, NICTYPE_PUBLIC) 
                    nodenics['public'] = pubnic

            if badnicinfo:
                continue

        else:
            #TODO: empty nodenicinfo line
            pass
        
        todonodes[nodename] = { }
        todonodes[nodename]['mac'] = mac
        todonodes[nodename]['lineno'] = lineno

        todonodes[nodename]['nics'] = nodenics
    
    if not len(todonodes):
        sys.exit(1)
    
    for nodename,attrdict in todonodes.iteritems():
        node = Node(nodename, ng.ngid, STATUS_IMPORTED)
        dbconn.add(node)
        dbconn.commit()
        for nic in attrdict['nics'].values():
            nic.nid = node.nid
            dbconn.add(nic)
        dbconn.commit()

    #print todonodes;

    #generate pxe file
    masterip = get_master_ip(dbconn)
    
    for node,bootnic in node_bootnic_map.iteritems():
        # gengerate file content
        pxetmpl = Template(file=NETBOOT_TMPL, searchList=[{'parentip': masterip, 'ip':bootnic.ip, 'netmask': bootnic.network.netmask}])
        content = str(pxetmpl)

        # generate pxe file
        macfilename = "01-%s" % (bootnic.mac.replace(":", "-"))
        macfile = "%s/%s" % (PXEFILE_DIR, macfilename.lower())
        target = file(macfile, 'w')
        target.writelines(content)
        target.close()
        os.chmod(macfile, 0666)

    #generate /etc/hosts
    if updatehosts:
        hosts = makehosts(dbconn)
        hostsfp = open("/etc/hosts", 'w')
        hostsfp.writelines(hosts)
        hostsfp.writelines("\n")
        hostsfp.close()

    return True, None

def importnode(dbconn, mac, nodegroup, iface='eth0'):
    ng = get_ng_byname(dbconn, nodegroup)
    if not ng :
        return False, "Can not find such nodegroup: %s" % nodegroup

    nic = get_nic_bymac(dbconn, mac)
    if nic:
        return False, "The mac: %s has been already used by another node" % mac

    network = None
    for n in ng.networks:
        if n.nwtype == NETTYPE_PROV:
            network = n
            break

    nodename = getnext_nodename(dbconn, ng.ngid)
    node = Node(nodename, ng.ngid, STATUS_IMPORTED)
    dbconn.add(node)
    
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


def gennodeinfo(dbconn, node):
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
        #nicname1:network1:ip1:netmask1:broadcast1:gateway1
        tempstr = "%s:%s:%s:%s:%s:%s" % (nic.nicname, nic.network.network, nic.ip,
                nic.network.netmask, nic.network.broadcast, nic.network.gateway)

        if nic.nictype == NICTYPE_BOOT:
            bootnic = nic.nicname

        nicstrs.append(tempstr)

    nicinfo = ";".join(nicstrs)

    dualboot = node.nodegroup == PROVTYPE_DUALBOOT

    gkeys = ['dns1', 'dns2', 'gateway', 'miscport']
    vmap = get_global_records(dbconn, gkeys)

    if len(vmap['miss']) > 0:
        raise Exception("can not get values for key: %s" % ",".join(vmap['miss']))

    gvmap = vmap['found']

    #add all content
    infotmpl = Template(file=NODEINFO_TMPL,
            searchList=[{'NID': nid, 'NODENAME':nodename, 
                'NGID'      : ngid, 
                'NICINFO'   : nicinfo, 
                'DUALBOOT'  : dualboot, 
                'BOOTNIC'   : bootnic,
                'PROVTYPE'  : provtype, 
                'UITYPE'    : uitype, 
                'DISTRO'    : distro, 
                'GATEWAY'   : gvmap['gateway'], 
                'DNS1'      : gvmap['dns1'],
                'DNS2'      : gvmap['dns2'],
                'MISCPORT'  : gvmap['miscport'],
                }])

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

def removenodes(dbconn, namelist, updatehosts=True):

    nodes = dbconn.query(Node).filter(Node.nodename.in_(namelist)).all()
    if not nodes:
        return [], namelist

    valid_node_names = [ node.nodename for node in nodes ]
    invalid_node_names = (list(set(namelist) - set(valid_node_names))) 

    nidlist = [ node.nid for node in nodes ]
    nics = dbconn.query(Nic).filter(Nic.nid.in_(nidlist)).filter(Nic.nictype==NICTYPE_BOOT).all()
    ips = [ nic.ip for nic in nics ]

    macfiles = [ "01-%s" % nic.mac.replace(':', "-") for nic in nics ] 
    rmcmd = "cd %s; rm -fr %s" % (PXEFILE_DIR, " ".join(macfiles))
    os.system(rmcmd) 

    maccmds = [ "%s.cmd" % nic.mac.replace(":", "-") for nic in nics ]
    cmddir = "%s/autoinstall/" % (get_samba_dir(dbconn))
    rmcmd = "cd %s > /dev/null 2>&1; rm -fr %s " % (cmddir, " ".join(maccmds))
    os.system(rmcmd) 
    
    for node in nodes:
        dbconn.delete(node)

    dbconn.commit()
    dbconn.close()

    if updatehosts:
        hosts = makehosts(dbconn)
        hostsfp = open("/etc/hosts", 'w')
        hostsfp.writelines(hosts)
        hostsfp.writelines("\n")
        hostsfp.close()

    return valid_node_names or [], invalid_node_names or []
