#!/usr/bin/env python

from dbitem import *

def get_global_records(dbconn, keylist):

    recs = dbconn.query(Global).all()
    ret = { "found" : {} ,
            "miss" : [] }

    found = {} 
    fkeys = []

    for rec in recs:
        if rec.key in keylist:
            fkeys.append(rec.key)
            found[rec.key] = rec.value
    
    origkeyset = set(keylist)
    fkeyset = set(fkeys)

    misskeylist = list(origkeyset - fkeyset)

    ret['found'] = found
    ret['miss'] = misskeylist

    return ret

def get_net_map(dbconn):
    netmap = {} 
    networks = dbconn.query(Network).all()

    for network in networks:
        netmap[network.netname] = network

    return netmap

def ngexist(dbconn, ngname):
    ng = get_ng_byname(dbconn, ngname)

    if not ng: return False

    return True
    

def get_prov_networks(dbconn):
    provnetworks = dbconn.query(Network).filter_by(nwtype="prov").all()
    return provnetworks

def get_domain_name(dbconn):
    domain = dbconn.query(Global).filter_by(key="domain").first();
    return domain.value

def get_samba_dir(dbconn):
    sambadir = dbconn.query(Global).filter_by(key="sambashare").first();
    return sambadir.value

def get_dnsserver(dbconn):
    dnsserver = dbconn.query(Global).filter_by(key="dns1").first();
    return dnsserver.value

def get_master_ip(dbconn):
    ip = dbconn.query(Global).filter_by(key="master").first() 
    return ip.value

def get_ng_byname(dbconn, ngname):
    nodegroup = dbconn.query(NodeGroup).filter_by(ngname=ngname).first()
    return nodegroup

def get_ng_byid(dbconn, ngid):
    nodegroup = dbconn.query(NodeGroup).filter_by(ngid=ngid).first()
    return nodegroup

def get_node_byname(dbconn, nodename):
    node = dbconn.query(Node).filter_by(nodename=nodename).first()
    return node

def get_node_byid(dbconn, nid):
    node = dbconn.query(Node).filter_by(nid=nid).first()
    return node

def get_nic_bymac(dbconn, mac):
    nic = dbconn.query(Nic).filter_by(mac=mac).first()
    return nic

def get_node_bymac(dbconn, mac):
    nic = dbconn.query(Nic).filter_by(mac=mac).first()
    return nic.node

def get_nodes_byngid(dbconn, ngid):
    nodes = dbconn.query(Node).filter_by(ngid=ngid).all()
    return nodes

def get_bootnic_bynodename(dbconn, nodename):
    node = get_node_byname(dbconn, nodename)
    nic = dbconn.query(Nic).filter_by(nid=node.nid, nictype=NICTYPE_BOOT).first()
    return nic

