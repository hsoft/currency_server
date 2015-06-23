# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-10-10
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import logging
from datetime import datetime
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import DateTime

from . import db

LOGFILE = '/var/log/currency/access.log'

logging.basicConfig(filename=LOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')

server = SimpleXMLRPCServer(("localhost", 8081), encoding='utf-8')
server.register_introspection_functions()

# Test method

def hello():
    return sys.version
server.register_function(hello, 'hello')

# Wrapper around the get_rates() method

def convert_date(d):
    return DateTime(datetime(d.year, d.month, d.day))

RATES_DB = db.RatesDB(db.DB_PATH)
def get_CAD_values(start, end, currency):
    logging.info('%s %s %s' % (start, end, currency))
    start = datetime.strptime(start.value, "%Y%m%dT%H:%M:%S")
    end = datetime.strptime(end.value, "%Y%m%dT%H:%M:%S")
    rates = RATES_DB.get_CAD_values(start, end, currency)
    return [(convert_date(d), r) for d, r in rates]
server.register_function(get_CAD_values, 'get_CAD_values')

server.serve_forever()