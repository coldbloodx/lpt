from flask import Flask,request
from flask.ext.restful import Api, Resource

import sys
sys.path.insert(0, '/opt/laworks/lib/python/')

from dbman import ConnManager as DBConnManager
from dbitem import *
from dbhelper import *
from constant import *
from nodeoperation import *
from utils import *


app = Flask(__name__)
api = Api(app)

class Nodes(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        nodes = dbconn.query(Node).all()
        nodemap = objs2dict(nodes, 'nid')

        return nodemap

    def post(self):
        node_id = len(nodemap)
        return nodemap['ccn001']


class NodeGroups(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        ngs = dbconn.query(NodeGroup).all()
        ngmap = objs2dict(ngs, 'ngid')

        return ngmap

class OSes(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        oses = dbconn.query(OS).all()
        osmap = objs2dict(oses, 'osid')

        return osmap

class Nets(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        nets = dbconn.query(Network).all()
        netmap = objs2dict(nets, 'netid')

        return netmap

class Nets(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        nets = dbconn.query(Network).all()
        netmap = objs2dict(nets, 'netid')

        return netmap

class Nics(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        nics = dbconn.query(Nic).all()
        nicmap = objs2dict(nics, 'nicid')

        return nicmap

class Globals(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        glbs = dbconn.query(Global).all()
        glbmap = objs2dict(glbs, 'key')

        return glbmap

class PartSchemas(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        pses = dbconn.query(PartSchema).all()
        psmap = objs2dict(pses, 'schemaid')

        return psmap

class Scripts(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        scripts = dbconn.query(Script).all()
        smap = objs2dict(scripts, 'scriptid')

        return smap

api.add_resource(Nodes, '/nodes')
api.add_resource(NodeGroups, '/ngs')
api.add_resource(OSes, '/oses')
api.add_resource(Nets, '/nets')
api.add_resource(Nics, '/nics')
api.add_resource(Globals, '/globals')
api.add_resource(PartSchemas, '/partschemas')
api.add_resource(Scripts, '/scripts')

if __name__ == '__main__':
    app.run(debug=True)
