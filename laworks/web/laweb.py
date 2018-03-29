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
        ret = {'code' : 400, 'msg': 'test msg'}
        data = request.get_json()

        app.logger.info("post json: %s, file: %s, form: %s" % (data, request.files, request.form))

        if (not request.files) or (not request.form):
            ret['msg'] = 'Node group or node definition file is not valid'
            return jsonify(ret)

        ifile = request.files['filename']
        macfile = os.path.join(app.config['UPLOAD_FOLDER'], ifile.filename)
        ifile.save(macfile)

        ngname = request.form['ngname']
        app.logger.info("post node group name: %s" % ngname)

        dbconn = DBConnManager.get_session()

        if not ngexist(dbconn, ngname):
            ret['msg'] = 'Node group: %s does not exist' % ngname
            return jsonify(ret)

        rcode = False
        errmsg = ''
        try:
            rcode, errmsg = importnodes(dbconn, macfile, ngname, updatehosts=False)
        except Exception, e:
            msg =  "Error import nodes into node group: %s, err: %s" % (ngname, str(e))
            app.logger.error(msg)
            ret['msg'] = msg

            return jsonify(ret)

        if rcode: 
            ret['code'] = 200
            ret['msg'] = 'Node import success'
        else:
            ret['msg'] = errmsg

        return jsonify(ret)

    def delete(self):
        """ update info about all specified nodes"""
        ret = {'code' : 403, 'msg': 'Method not allowed' }

        data = request.get_json()
        nodelist = data
        app.logger.info("delete json: %s, file: %s, form: %s" % (data, request.files, request.form))

        dbconn = DBConnManager.get_session()

        if not nodelist:
            ret['code'] = 400
            ret['msg'] = "Specified node name are not valid"
            return jsonify(ret)
        
        donelist = []
        undonelist = []

        try:
            (donelist, undonelist) = removenodes(dbconn, nodelist, updatehosts=False)
        except Exception, e:
            ret['code'] = 400
            ret['msg'] = "Error delete node %s, err: %s" % ( ','.join(nodelist), str(e))
            return jsonify(ret)

        app.logger.info("done list: %s, undone list %s" % (donelist, undonelist))
        
        if (len(undonelist) == 0) and (len(donelist) != 0):
            ret['code'] = 200
            ret['msg'] = "Node delete success"
            return jsonify(ret)

        if (len(undonelist) != 0) and (len(donelist) == 0):
            ret['code'] = 200
            ret['msg'] = "Node delete failed, %s can not be deleted" % ','.join(undonelist)
            return jsonify(ret)

        if (len(undonelist) != 0) and (len(donelist) != 0):
            ret['code'] = 200
            ret['msg'] = "Node delete partial success, %s deleted, %s not deleted" % (','.join(donelist), ','.join(undonelist))
            ret['deleted'] = donelist
            ret['undeleted'] = undonelist
            return jsonify(ret)

        if (len(undonelist) == 0) and (len(donelist) == 0):
            ret['code'] = 200
            ret['msg'] = "Node delete failed" 
            ret['deleted'] = donelist
            ret['undeleted'] = undonelist
            return jsonify(ret)

    def put(self):
        ret = {'code' : 403, 'msg': 'Method not allowed' }
        return jsonify(ret)

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

api.add_resource(Nodes, '/nodes/', methods = ['GET', 'POST', 'DELETE', 'PUT'])
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
