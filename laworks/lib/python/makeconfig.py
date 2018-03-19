#!/usr/bin/env python

from Cheetah.Template import Template
from IPy import IP

from dbhelper import *
from dbitem import *
from constant import *
from utils import errout
from dbman import ConnManager as DBConnManager

def makedhcpd(dbconn):
    provip = get_master_ip(dbconn)
    domain = get_domain_name(dbconn)
    dns = get_dnsserver(dbconn)

    provnet = dbconn.query(Network).filter_by(nwtype=NETTYPE_PROV).first()
    startip, endip = provnet.drange.split("-")

    dhcptmpl = Template(file=CONF_TMPL_DHCPD, searchList={
        "dns": dns, "domain": domain, "startip": startip, "endip": endip,
        "networks" : [ provnet ]})

    return str(dhcptmpl)

def maketftp(dbconn):
    tftptmpl = Template(file=CONF_TMPL_TFTP)
    return str(tftptmpl)

def makehttpd(dbconn):
    httptmpl = Template(file=CONF_TMPL_HTTPD)
    return str(httptmpl)

def makenfs(dbconn):
    return "nfs"

def makehosts(dbconn):
    nodes = dbconn.query(Node).all()

    if not nodes or not len(nodes):
        return

    orighosts = []

    fp = open('/etc/hosts', 'r')
    hosts = fp.readlines()
    hosts = [ line.strip() for line in hosts ]

    newhosts = []
    
    nics = dbconn.query(Nic).all()
    ips = [ nic.ip for nic in nics ]
    ips.sort()

    for hostline in hosts:
        hostline = hostline.strip()

        if not hostline: continue

        hostip = hostline.split()[0]
        if hostip not in ips:
            newhosts.append(hostline)
        
    ipnamemap = {} 

    for node in nodes:
        for nic in node.nics:
            if nic.network.nwtype == "provision":
                ipnamemap[nic.ip] = "%s %s %s-%s" % (nic.ip, node.nodename, node.nodename, nic.nicname)
            else:
                ipnamemap[nic.ip] = "%s %s-%s" %(nic.ip, node.nodename, nic.nicname)

    for ip in ips:
        newhosts.append(ipnamemap[ip])

    if not newhosts:
        return ""

    return "\n".join(newhosts)
    
def makenamed(dbconn):
    domain = get_domain_name(dbconn)
    dnsserver = get_dnsserver(dbconn)

    provnetworks = get_prov_networks(dbconn)

    revfiles = []
    for network in provnetworks:
        segments = network.network.split(".")
        segments.reverse()
        revfile = "%s.in-addr.arpa" % (".".join(segments[1:4]))
        revfiles.append(revfile)

    namedtmpl = Template(file=CONF_TMPL_NAMED, searchList={"dnsserver" : dnsserver,
        "domain": domain, "revfiles": revfiles})

    return namedtmpl

def makeresolv(dbconn):
    return "resolv"

def makezone(dbconn):
    return "zone"

def makerevzone(dbconn):
    return "revzone"
