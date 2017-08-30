#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("/opt/laworks/lib/python")
import cgi
import os

from unipath.path import Path as path
from Cheetah.Template import Template

from dbitem import *
from dbhelper import *
from constant import *
from nodeoperation import *
from app import LAApp
from dbman  import ConnManager as DBConnManager




class LANodeInfoApp(LAApp):
    def __init__(self):
        LAApp.__init__(self, debug=False, root=False, haslog=False)

    def parseargs(self):

        self.parser.add_option("-v", "--version", action="callback",
                callback=self.showversion, help="version")
        self.parser.add_option("-n", "--name", action="store", 
                dest="nodename", help="node name", metavar="node name")

        if len(sys.argv[1:]) < 1:
            self.parser.print_help()
            sys.exit(0)

        (self.options, self.args) = self.parser.parse_args(sys.argv[1:])

    def run(self):
        node = None
        dbconn = None
        
        #check whether the app is invoked via cgi or not

        if os.environ.has_key('REMOTE_ADDR'):
            iscgi = 1
            ip = os.environ['REMOTE_ADDR']
            print "Content-type: text/html;charset=utf-8\n"
            fields = cgi.FieldStorage()
            if not fields.has_key('mac'):
                sys.exit(-1)

            mac = fields['mac'].value
            # for windows case
            mac = mac.replace('-', ':')
            status=  fields['status'].value

            dbconn =  DBConnManager.get_session()

            node = get_node_bymac(dbconn, mac)
            nic = get_nic_bymac(dbconn, mac)
            node.status = status

            #update node status
            dbconn.commit()

            if status != STATUS_CREATINGFS:
                if status == STATUS_FIRSTBOOT:
                    genlocalbootpxe(nic)
                sys.exit(0)

        else:
        #not run as cgi but cmdline
            self.parseargs()
            dbconn =  DBConnManager.get_session()
            node = get_node_byname(dbconn, self.options.nodename)
        
        if not node:
            sys.exit(-1)

        nodeinfo = gennodeinfo(node)

        print nodeinfo

if __name__ == '__main__':
    nodeinfoapp = LANodeInfoApp()
    nodeinfoapp.run()
