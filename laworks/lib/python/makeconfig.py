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


def ipexists(ip, hostlist):
    for hostline in hostlist:
        if hostline.startswith(ip):
            return True

    return False;

def makehosts(dbconn):
    nodes = dbconn.query(Node).all()

    if not nodes or not len(nodes):
        return

    orighosts = []

    fp = open('/etc/hosts', 'r')
    hosts = fp.readlines()
    hosts = [ line.strip() for line in hosts ]

    content = []

    for node in nodes:
        for nic in node.nics:

            if ipexists(nic.ip, hosts):
                continue

            if nic.network.nwtype == "provision":
                content.append("%s %s %s-%s" % (nic.ip, node.nodename, node.nodename, nic.nicname))
            else:
                content.append("%s %s-%s" %(nic.ip, node.nodename, nic.nicname))
    
    hosts.extend(content)

    if not hosts:
        return ""

    return "\n".join(hosts)
    
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
