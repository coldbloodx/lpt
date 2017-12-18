#!/usr/bin/env python
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from IPy import IP

from utils import runcmd, parseconf, errout, getmyos
from dbitem import *
from constant import *
from ipfun import getnicinfo

class DatabaseManager:
    
    def __init__(self, username='root',dbname='laworks', 
            host='localhost', port='3306',driver='mysql'):
        self.username = username
        self.dbname   = dbname
        self.host     = host
        self.port     = port
        self.driver   = driver
        conf = parseconf()
        if not conf.has_key('dbpass') and conf['dbpass']:
            errout('Cannot create database laworks, the db pass is not set')
            sys.exit(1)

        self.password = conf['dbpass']

    def create_database(self):
        db_create_cmd = ''

        if self.driver == 'mysql':
            # mysql 
            db_create_cmd = 'mysql --no-defaults -u %s -p%s -h %s -P %s -e "create database %s;"' % \
                  (self.username, self.password, self.host, self.port, self.dbname)
        elif self.driver == 'postgres':
            # postgres
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            cmd = 'psql -p %s  postgres %s -c "create database %s with owner = %s;"'\
                  % (self.port, self.username, self.dbname, self.username)
        else:
            raise Exception, "unknown database driver"

        out, err, ret = runcmd(db_create_cmd)
        if ret:
            raise Exception, "database create error %s, %s" %(err)

        return ret
        
    def remove_database(self, database='laworks'):
        db_remove_cmd = ''

        if self.driver == 'mysql':
            # mysql 
            db_remove_cmd = 'mysql --no-defaults -u %s -p%s -h %s -P %s -e "drop database %s;"' \
                  %(self.username, self.password, self.host, self.port, self.dbname)
        elif self.driver == 'postgres':
            # postgres
            password = self.password
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            db_remove_cmd = 'psql -p %s  postgres %s   -c "drop database %s;"'\
                  %(self.port, self.username, self.dbname)
        else:
            raise Exception, "unknown database driver"

        out, err, ret = runcmd(db_remove_cmd)
        if ret:
            raise Exception, "database remove error: %s" %(err)

        return ret

class ConnManager:
    @classmethod
    def getdbpass(self):
        conf = parseconf()
        if not conf.has_key('dbpass') and not conf['dbpass']:
            errout('Cannot create database laworks, the db pass is not set')
            sys.exit(1)
        return conf['dbpass']
    
    @classmethod
    def get_mysql_session(self, dbname='laworks', host='localhost', username='root', 
            password='letmein', port='3306', debug=False):
        driver = 'mysql'
        password = self.getdbpass()
        connect_string = "%s://%s:%s@%s:%s/%s" % (driver, username, password, host, port, dbname)
        engine =  create_engine(connect_string, echo=debug)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session 

    @classmethod
    def get_session(self, mysql=True):
        if mysql:
            return ConnManager.get_mysql_session()
        else:
            return ConnManager.get_psql_session()

    @classmethod
    def get_psql_session(self, dbname='laworks',host='localhost',username='root',
            password='letmein', port='5432'):
        driver = 'postgres'
        connect_string = "%s://%s:%s@%s:%s/%s" % (driver, username, password, host, port, dbname)
        engine = create_engine(connect_string, debug)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session 

class TableManager:
    def __init__(self, dbname='laworks', host='localhost', driver='mysql', 
            username='root', port='3306'):
        self.dbname = dbname
        self.host = host
        self.driver = driver
        self.username = username
        self.port = port
        self.conf = parseconf()
        if not self.conf.has_key('dbpass') and not self.conf['dbpass']:
            errout('Cannot create database laworks, the db pass is not set')
            sys.exit(1)

        self.password = self.conf['dbpass']
        connect_string = "%s://%s:%s@%s:%s/%s" % (self.driver, 
                self.username, self.password, self.host, self.port, self.dbname)
        self.engine = create_engine(connect_string, echo=True)

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        self.__init_record()

    def __init_record(self):
        
        #make a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        #nicfinfo: ip, broadcast, mask, mac 
        pubnicinfo = getnicinfo(self.conf['pubnic'])
        provnicinfo = getnicinfo(self.conf['provnic'])

        if not pubnicinfo or not provnicinfo:
            errout("Cannot get public or provision network info")
            sys.exit(1)

        pubnetwork  = IP(pubnicinfo[0]).make_net(pubnicinfo[2])
        provnetwork = IP(provnicinfo[0]).make_net(provnicinfo[2])

        provippool = []
        for ip in provnetwork:
            if ip == provnetwork.net() or ip == provnetwork.broadcast():
                continue
            provippool.append(ip)

        #1. global table
        pubip = pubnicinfo[0]
        provip = provnicinfo[0]

        #key, value, extra
        domain = "laworks.com"

        if self.conf.has_key("domain") and validate_domain(self.conf["domain"]):
            domain = self.conf['domain']

        session.add_all([
            Global("master", provip), 
            Global("provnic", self.conf['provnic']),
            Global("dnsserver", self.conf['dns']), 
            Global("tftpserver", provip),
            Global("gateway", provip), 
            Global("ntpserver", provip),
            Global("sambashare", "/share"),
            Global("domain", domain)])
        session.commit();

        #2. os table
        myos = getmyos()
        osnames = [ myos.osname ]
        osdict = { myos.osname: myos }

        session.add(myos)

        if self.conf.has_key('addonos'):
            for entry in self.conf['addonos']:
                os = [ "%s%s.%s" % (entry[0], entry[1], entry[2]) ]
                os.extend(list(entry))
                os = makeos(os)
                session.add(os)
                osnames.append(os.osname)
                osdict[os.osname] = os
        session.commit();

        #3. network table
        # netname, network, netmask, broadcast, drange="", srange="",
        # nwtype=NETTYPE_PROV, gateway="", dns="",  tftpsrv=""

        if not self.conf.has_key('drange'):
            errout("Dynamic range in config file not found")
            sys.exit(1)

        if not self.conf.has_key('srange'):
            errout("Static range in config file not found")
            sys.exit(1)
         
        provnet = Network("provison", str(provnetwork.net()), str(provnetwork.netmask()), 
                str(provnetwork.broadcast()), self.conf['drange'], self.conf['srange'],
                NETTYPE_PROV, provip, self.conf['dns'], provip)
        pubnet  = Network("public", str(pubnetwork.net()), str(pubnetwork.netmask()), str(pubnetwork.broadcast()), 
                '', '', NETTYPE_PUB)

        session.add_all([provnet, pubnet])
        session.commit();

        #4. partschema table
        #schemaname
        disked_schema = PartSchema("disked", "disked")
        diskless_schema = PartSchema("diskless", "diskless")
        win_schema = PartSchema("windows", "windows")
        dualboot_schema = PartSchema("dualboot", "dualboot")
        session.add_all([disked_schema, diskless_schema, win_schema, dualboot_schema])
        session.commit();
        
        #5. nodegroup table
        #ngname, osid, partid, provtype, uitype, namerule 
        uitypes = [ UITYPE_GUI, UITYPE_CLI ]
        provtypes = [ PROVTYPE_DISKED, PROVTYPE_DISKLESS ]

        if self.conf.has_key('uitypes'):
            invalid = False
            for uitype in self.conf['uitypes']:
                if uitype not in uitypes: 
                    invalid = True
                    break

            if invalid == False:
                uitypes = self.conf['uitypes']

        
        if self.conf.has_key('provtypes'):
            invalid = False
            for provtype in self.conf['provtypes']:
                if provtype not in provtypes:
                    invalid = True

            if invalid == False:
                provtypes = self.conf['provtypes']

        for osname in osnames:
            os = osdict[osname]
            if os.ostype == 'linux':
                for uitype in uitypes:
                    for provtype in provtypes:
                        #ignore diskless gui
                        if uitype == UITYPE_GUI and provtype == PROVTYPE_DISKLESS : continue

                        #ignore centos, rhel gui 
                        if uitype == UITYPE_GUI and os.distro.lower() in [ 'centos', 'rhel'] : continue

                        #if provtype == PROVTYPE_DISKLESS and (os.osname.lower() in [ 'centos', 'rhel', 'ubuntu' ]): 
                        #    continue

                        ngname = "%s-%s-%s" % (os.osname, provtype.capitalize(), uitype.upper())
                        ngrule = "%s-%s-%s-%s###" % (os.distro, os.major, os.minor, provtype) 
                        ng = NodeGroup(ngname, os.osid, disked_schema.schemaid, provtype, uitype, ngrule)
                        ng.networks.extend([provnet])
                        session.add(ng)

            elif os.ostype == 'windows':
                winng = NodeGroup(os.osname, os.osid, win_schema.schemaid, PROVTYPE_WIN, UITYPE_GUI, "%s###" % (os.osname)) 
                dualbootng = NodeGroup("%s-dualboot" % (os.osname), os.osid, dualboot_schema.schemaid, PROVTYPE_DUALBOOT, UITYPE_GUI, "dualboot###") 
                winng.networks.extend([provnet])
                dualbootng.networks.extend([provnet])
                session.add_all([ winng, dualbootng ])
            else:
                pass

        session.commit();

    def validate_domain(domain):
        if not domain:
            return False
       
        if not domain.isalnum():
           return False

        if not len(domain.split(".")) > 2:
            return False
        
        return True;

#if __name__ == '__main__':

#    dbmanager = DatabaseManager()
#    try:
#        dbmanager.remove_database()
#    except Exception, e:
#        print e.message

#    try:
#        dbmanager.create_database()
#    except Exception, e:
#        print e.message

#    tblmanager = TableManager()
#    tblmanager.create_tables()
