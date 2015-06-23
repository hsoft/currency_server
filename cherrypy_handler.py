# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-10-08
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import datetime
from xmlrpc.client import DateTime

import cherrypy
from cherrypy._cptools import XMLRPCController
from . import db

RATES_DB = db.RatesDB(db.DB_PATH)

def convert_date(d):
    return DateTime(datetime(d.year, d.month, d.day))

class Root(XMLRPCController):
    @cherrypy.expose
    def hello(self):
        return 'hello!'
    
    @cherrypy.expose
    def get_CAD_values(self, start, end, currency):
        start = datetime.strptime(start.value, "%Y%m%dT%H:%M:%S")
        end = datetime.strptime(end.value, "%Y%m%dT%H:%M:%S")
        rates = RATES_DB.get_CAD_values(start, end, currency)
        return [(convert_date(d), r) for d, r in rates]
    

config = {
    '/': {
        'tools.xmlrpc.encoding': 'utf-8',
        'tools.xmlrpc.allow_none': False,
    }
}

app = cherrypy.tree.mount(root=Root(), config=config)