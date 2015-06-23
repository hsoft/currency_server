#!/usr/bin/env python
# Unit Name: currency_server.db
# Created By: Virgil Dupras
# Created On: 2008-04-20
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date, datetime, timedelta
import xml.etree.cElementTree as ET
import xml.parsers.expat
import re

from .hscommon.currency import Currency, RatesDB as RatesDBBase
from .hscommon import sqlite


DB_PATH = '/var/sqlite/currency.db'
# DB_PATH = '/Users/hsoft/Desktop/currency.db'
RE_ENDS_WITH_PARENS = re.compile(r"\([^(]+\)$")

class RatesDB(RatesDBBase):
    """The RatesDB on the server side automatically updates itself using Bank of Canada's rates
    
    Bank of Canada uses n/a values for week-ends, holidays and future dates. We want to ignore those
    values when importing.
    """
    def __init__(self, dbpath=DB_PATH):
        RatesDBBase.__init__(self, sqlite.ThreadedConn(dbpath, False))
    
    def get_CAD_values(self, start, end, currency_code):
        """Returns [(date, value)] for each CAD value the DB has for 'currency'.
        
        The values are in date order.
        """
        str_start = '%d%02d%02d' % (start.year, start.month, start.day)
        str_end = '%d%02d%02d' % (end.year, end.month, end.day)
        sql = "select date, rate from rates where date >= ? and date <= ? and currency = ?"
        cur = self.con.execute(sql, [str_start, str_end, currency_code])
        return [(datetime.strptime(date, '%Y%m%d').date(), rate) for (date, rate) in cur]
    
    def import_bank_of_canada_rates(self, source):
        """Import rates from a Bank of Canada lookup xml file"""
        root = ET.fromstring(source.read().strip())
        for observation in root.getiterator('Observation'):
            currency_element = observation.find('Currency_name')
            name = currency_element.text.strip()
            # Some currency names have (), some not, but if we can't find it, try without the ()
            if name not in Currency.by_name:
                name = RE_ENDS_WITH_PARENS.sub('', name).strip() # remove the parens at the end of the name
            currency_code = Currency(name=name).code
            date_element = currency_element.find('Observation_date')
            rate_element = currency_element.find('Observation_data')
            try:
                rate = float(rate_element.text.strip())
            except (ValueError, AttributeError): # probably n/a
                continue
            year, month, day = date_element.text.strip().split('-')
            self.set_CAD_value(date(int(year), int(month), int(day)), currency_code, rate)
