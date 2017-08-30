#!/usr/bin/env python

import sys
import os
import logging

from unipath.path import Path as path

def _getlogger(name='laworks'):
    return logging.getLogger(name)

def _getformatter():
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s " +
        "[%(process)d] [%(thread)d] (%(filename)s:%(lineno)d) %(message)s") 

    return formatter

def getapplogger(name=None, debug=False):
    logger = None
    if not name:
        logger = _getlogger()
    else:
        logger = _getlogger('laworks.' + name)

    formatter = _getformatter()
    
    logfile = path("/var/log/laworks/")
    if not logfile.exists():
        logfile.mkdir()
    
    if debug:
        logger.setLevel(logging.DEBUG)

    loghandler = logging.FileHandler("/var/log/laworks/" + name, 'a')

    loghandler.setFormatter(formatter)

    logger.addHandler(loghandler)
    return logger
