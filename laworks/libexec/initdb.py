#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbitem import *
from dbman import *
from dbhelper import *
from constant import *

if __name__ == '__main__':
    dbmanager = DatabaseManager()
    try:
        dbmanager.remove_database()
    except Exception, e:
        print e.message

    try:
        dbmanager.create_database()
    except Exception, e:
        print e.message
    tblmanager = TableManager()
    tblmanager.create_tables()

