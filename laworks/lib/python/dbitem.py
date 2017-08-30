#!/usr/bin/env python

from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from constant import *

Base = declarative_base()

class PartSchema(Base):

    __tablename__ = "partschema"

    schemaid   = Column(Integer, primary_key=True)
    schemaname = Column(String(32))
    schemafile = Column(String(32))

    def __init__(self, name, schemafile):
        self.schemaname = name
        self.schemafile = schemafile

    def __repr__(self):
        return "<PartSchema('%s', '%s', '%s')>" % (self.schemaid,
                self.schemaname, self.schemafile)

class Global(Base):
    __tablename__ = "global"

    key   = Column(String(16), unique=True, nullable=False)
    value = Column(String(64), nullable=False)
    extra = Column(String(64), default=None)
    keyid = Column(Integer(), primary_key=True)
    
    def __init__(self, key, value, extra=None):
        self.key   = key
        self.value = value
        self.extra = extra

    def __repr__(self):
        return "<Global('%s', '%s', '%s', '%s')>" % (self.keyid,
                self.key, self.value, self.extra)

class Nic(Base):
    __tablename__ = "nic"

    nicid   = Column(Integer(), primary_key=True)
    nicname = Column(String(8), nullable=False)
    mac     = Column(String(20), unique=True, nullable=False)
    ip      = Column(String(20), unique=True, nullable=False)
    nid  = Column(Integer(), ForeignKey("node.nid"))
    netid   = Column(Integer(), ForeignKey("network.netid"))
    nictype = Column(String(8), default=NICTYPE_OTHER)

    node = relationship("Node", backref=backref("node", order_by=nicid))
    network = relationship("Network", backref=backref("net", order_by=nicid))

    def __init__(self, nicname, mac, ip, nid, netid, nictype=NICTYPE_OTHER):

        self.nicname = nicname
        self.mac     = mac
        self.ip      = ip
        self.nid  = nid
        self.netid   = netid
        self.nictype = nictype

    def __repr__(self):
        return "<Nic('%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.nicid, 
                self.nicname, self.mac, self.ip, self.nid, self.netid, self.nictype)

class Network(Base):
    __tablename__ = "network"

    netid   = Column(Integer(), primary_key=True)
    netname = Column(String(20), unique=True, nullable=False)
    network = Column(String(20), nullable=False)
    netmask = Column(String(20), nullable=False)
    broadcast = Column(String(20), nullable=False)
    gateway = Column(String(20))
    dns     = Column(String(20))
    drange  = Column(String(40))
    srange  = Column(String(40))
    tftpsrv = Column(String(20), default="")
    nwtype  = Column(String(16), nullable=False)
    
    def __init__(self, netname, network, netmask, broadcast, drange="", srange="",
            nwtype=NETTYPE_PROV, gateway="", dns="",  tftpsrv=""):
        self.netname = netname
        self.network = network
        self.netmask = netmask
        self.broadcast = broadcast
        self.nwtype = nwtype
        self.gateway = gateway
        self.drange = drange
        self.srange = srange
        self.tftpsrv = tftpsrv
        self.dns     = dns

    def __repr__(self):
        return "<Network('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.netid,
                self.netname, self.network, self.netmask, self.broadcast, self.nwtype, self.gateway,
                self.drange, self.srange, self.tftpsrv, self.dns)

class Script(Base):
    __tablename__ = "script"
    
    scriptid   = Column(Integer(), primary_key=True)
    scriptname = Column(String(32))

    def __init__(self, scriptname):
        self.scriptname = scriptname

    def __repr__(self):
        return "<Script('%s', '%s')>" % (self.scriptid, self.scriptname)

class OS(Base):
    __tablename__ = "os"

    osid   = Column(Integer(), primary_key=True)
    osname = Column(String(32), nullable=False)
    major  = Column(String(8), nullable=False)
    minor  = Column(String(8), nullable=False)
    ostype   = Column(String(8), nullable=False)
    isoname = Column(String(32), nullable=True)

    def __init__(self, osname, major, minor, ostype, isoname):
        self.osname = osname.lower()
        self.major  = major
        self.minor  = minor
        self.ostype = ostype
        self.isoname = isoname

    def __repr__(self):
        return "<OS('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.osid,
                self.osname, self.major, self.minor, self.ostype, self.isoname)

def makeos(vallist):
    """return an OS object from a given list or tuple"""
    return OS(vallist[0], vallist[1], vallist[2], vallist[3], vallist[4])

class Node(Base):
    __tablename__ = "node"

    nid      = Column(Integer(), primary_key=True)
    nodename = Column(String(32), unique=False, nullable=False)
    ngid     = Column(Integer(), ForeignKey("nodegroup.ngid"))
    status = Column(String(32), nullable=False)


    nodegroup = relationship("NodeGroup", backref=backref("node", order_by=nid))

    #when delete node we must delete the nic associate to the node
    nics = relationship("Nic", backref=backref("nic.nid", order_by=Nic.nicid),
            cascade="all, delete, delete-orphan")

    def __init__(self, nodename, ngid, status):
        self.nodename = nodename
        self.ngid     = ngid
        self.status = status

    def __repr__(self):
        return "<Node('%s', '%s', '%s', '%s')>" % (self.nid, self.nodename, self.ngid, self.status) 

ngscript = Table('ngscript', Base.metadata,
        Column('ngid', Integer(), ForeignKey('nodegroup.ngid')),
        Column('scriptid', Integer(), ForeignKey('script.scriptid')))

ngnet = Table('ngnet', Base.metadata,
   Column('ngid', Integer(), ForeignKey("nodegroup.ngid")),
   Column('netid', Integer(), ForeignKey("network.netid")))

class NodeGroup(Base):
    __tablename__ = "nodegroup"

    ngid   = Column(Integer(), primary_key=True)
    ngname = Column(String(32), unique=True, nullable=False)
    provtype = Column(String(16), nullable=False)
    uitype = Column(String(8), nullable=False)
    namerule = Column(String(32), nullable=False, default="node###")
    osid   = Column(Integer(), ForeignKey("os.osid"))
    partid = Column(Integer(), ForeignKey("partschema.schemaid"))

    os = relationship("OS", backref=backref("os.osid", order_by=ngid))
    partschema = relationship("PartSchema", backref=backref("partschema.schemaid", order_by=ngid))

    nodes = relationship("Node", backref=backref("node.nid", order_by=Node.nid))
    networks = relationship("Network", secondary=ngnet, backref=backref("ngnet.ngid", order_by=Network.netid))
    scripts = relationship("Script", secondary=ngscript, backref=backref("ngscript.ngid", order_by=Script.scriptid))

    def __init__(self, ngname, osid, partid, provtype, uitype, namerule="node-###"):
        self.ngname = ngname
        self.osid = osid
        self.partid = partid
        self.provtype = provtype
        self.uitype = uitype
        self.namerule = namerule 

    def __repr__(self):
        return "<NodeGroup('%s', '%s', '%s', '%s', '%s', '%s', '%s')>" %(self.ngid,
                self.ngname, self.osid, self.partid, self.provtype, self.uitype, self.namerule)

