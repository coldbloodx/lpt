from flask import Flask,request,jsonify
from flask.ext.restful import Api, Resource, reqparse

from dbman import ConnManager as DBConnManager
from dbitem import *
from dbhelper import *
from constant import *
from nodeoperation import *
from utils import *

import os

app = Flask(__name__)
api = Api(app)
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

class Nodes(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        nodes = dbconn.query(Node).all()
        nodemap = objs2dict(nodes, 'nid')

        return jsonify(nodemap)

    def post(self):
        ret = {'code' : 400}
        data = request.get_json()
        app.logger.info("post json: %s" % data)

        ifile = request.files['filename']
        app.logger.info("post files: %s" % ifile)
        ifile.save(os.path.join(app.config['UPLOAD_FOLDER'], ifile.filename))

        #iform = request.form
        #app.logger.info("post form: %s" % iform)
        return jsonify(ret)

    def put(self):
        """ update info about all specified nodes"""
        data= {'code' : 200 }

        return jsonify(data)

    def delete(self):
        data= {'code' : 200 }

        return jsonify(data)

class RNode(Resource):
    def get(self, nid):
        dbconn = DBConnManager.get_session()
        node = get_node_byid(dbconn, nid)
        nodedict = obj2dict(node)
        return jsonify(nodedict)

    def post(self):
        """ update specified node"""
        data = {'code' : 403}
        return jsonify(data)

    def put(self):
        data= {'code' : 200 }
        return jsonify(data)

    def delete(self):
        data= {'code' : 200 }
        return jsonify(data)

class NodeGroups(Resource):
    def get(self):
        dbconn = DBConnManager.get_session()
        ngs = dbconn.query(NodeGroup).all()
        ngmap = objs2dict(ngs, 'ngid')

        return ngmap

class RNodeGroup(Resource):
    def get(self, ngid):
        return jsonify({ngid, ngid})

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

#R<classname> refers to wRapper<classname>
api.add_resource(OSes, '/oses/')
#api.add_resource(ROS, '/oses/<osid>')
api.add_resource(Nets, '/nets/')
#api.add_resource(RNet, '/nets/<netid>')
api.add_resource(Nics, '/nics/')
#api.add_resource(RNic, '/nics/<nicid>')

api.add_resource(Nodes, '/nodes/', methods = ['GET', 'POST'])
api.add_resource(RNode, '/nodes/<nid>')

api.add_resource(NodeGroups, '/ngs/')
#api.add_resource(RNodeGroup, '/ngs/<ngid>')
api.add_resource(Globals, '/globals/')
#api.add_resource(RGlobal, '/globals/<gkey>')
api.add_resource(Scripts, '/scripts/')
#api.add_resource(RScript, '/scripts/<scriptid>')
api.add_resource(PartSchemas, '/partschemas/')
#api.add_resource(RPartSchema, '/partschemas/<schemaid>')

if __name__ == '__main__':
    app.debug = True
    api.initlogger()
    app.run()
