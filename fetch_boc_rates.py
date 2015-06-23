# This script fetches today's rates from the Bank of Canada website
# Created By: Eric Mc Sween
# Created On: 2008-05-19
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

import sys
import re
from datetime import date
from urllib.parse import urlencode
from urllib.request import urlopen

from currency_server.db import RatesDB

def main():
    # Open the db
    db = RatesDB()

    # Make the first query

    db_min, db_max = db.date_range('USD')
    start = db_max # We'll always refetch yesterday's data in case there was some missing.
    end = date.today()

    form_data = {
        # Hidden
        'lookupPage': 'lookup_daily_exchange_rates.php',
        'startRange': '2001-07-07',
        'dFrom': start.strftime('%Y-%m-%d'),
        'dTo': end.strftime('%Y-%m-%d'),

        # Select currencies
        'series[]': [
            'LOOKUPS_IEXE0101',  # U.S. dollar (close)
            'LOOKUPS_IEXE2702',  # Argentine peso (floating rate)
            'LOOKUPS_IEXE1601',  # Australian dollar
            'LOOKUPS_IEXE6001',  # Bahamian dollar
            'LOOKUPS_IEXE2801',  # Brazilian real
            'LOOKUPS_IEXE4501',  # CFA franc
            'LOOKUPS_IEXE4601',  # CFP franc
            'LOOKUPS_IEXE2901',  # Chilean peso
            'LOOKUPS_IEXE2201',  # Chinese renminbi (yuan)
            'LOOKUPS_IEXE3901',  # Colombian peso
            'LOOKUPS_IEXE6101',  # Croatian kuna
            'LOOKUPS_IEXE2301',  # Czech Republic koruna
            'LOOKUPS_IEXE0301',  # Danish krone
            'LOOKUPS_IEXE4001',  # East Caribbean dollar
            'LOOKUPS_EUROCAE01', # European Euro
            'LOOKUPS_IEXE4101',  # Fiji dollar
            'LOOKUPS_IEXE4702',  # Ghanaian cedi
            'LOOKUPS_IEXE6501',  # Guatemalan quetzal
            'LOOKUPS_IEXE4301',  # Honduran lempira
            'LOOKUPS_IEXE1401',  # Hong Kong dollar
            'LOOKUPS_IEXE2501',  # Hungarian forint
            'LOOKUPS_IEXE4401',  # Icelandic krona
            'LOOKUPS_IEXE3001',  # Indian rupee
            'LOOKUPS_IEXE2601',  # Indonesian rupiah
            'LOOKUPS_IEXE5301',  # Israeli new shekel
            'LOOKUPS_IEXE6401',  # Jamaican dollar
            'LOOKUPS_IEXE0701',  # Japanese yen
            'LOOKUPS_IEXE3201',  # Malaysian ringgit
            'LOOKUPS_IEXE2001',  # Mexican peso
            'LOOKUPS_IEXE4801',  # Moroccan dirham
            'LOOKUPS_IEXE3801',  # Myanmar (Burma) kyat
            'LOOKUPS_IEXE1901',  # New Zealand dollar
            'LOOKUPS_IEXE0901',  # Norwegian krone
            'LOOKUPS_IEXE5001',  # Pakistan rupee
            'LOOKUPS_IEXE5101',  # Panamanian balboa
            'LOOKUPS_IEXE5201',  # Peruvian new sol
            'LOOKUPS_IEXE3301',  # Philippine peso
            'LOOKUPS_IEXE2401',  # Polish zloty
            'LOOKUPS_IEXE6505',  # Romanian new leu
            'LOOKUPS_IEXE2101',  # Russian rouble
            'LOOKUPS_IEXE6504',  # Serbian dinar
            'LOOKUPS_IEXE3701',  # Singapore dollar
            'LOOKUPS_IEXE6201',  # Slovak koruna
            'LOOKUPS_IEXE3401',  # South African rand
            'LOOKUPS_IEXE3101',  # South Korean won
            'LOOKUPS_IEXE5501',  # Sri Lanka rupee
            'LOOKUPS_IEXE1001',  # Swedish krona
            'LOOKUPS_IEXE1101',  # Swiss franc
            'LOOKUPS_IEXE3501',  # Taiwanese new dollar
            'LOOKUPS_IEXE3601',  # Thai baht
            'LOOKUPS_IEXE5701',  # Tunisian dinar
            'LOOKUPS_IEXE6506',  # U.A.E. dirham
            'LOOKUPS_IEXE1201',  # U.K. pound sterling
            'LOOKUPS_IEXE5902',  # Venezuelan bolivar fuerte
            'LOOKUPS_IEXE6503',  # Vietnamese dong
        ],
    }

    with urlopen('http://www.bankofcanada.ca/rates/exchange/10-year-lookup/', urlencode(form_data, True).encode('ascii')) as response:
        contents = response.read().decode('latin-1')

    # search for a link to XML data
    match = re.search(r'(?<=")http://www\.bankofcanada\.ca/stats/results/p_xml.*?(?=")', contents)

    if not match:
        print('Invalid response')
        sys.exit(1)

    # Fetch the XML file
    xml_url = contents[match.start():match.end()]
    with urlopen(xml_url) as xml_file:
        # print(repr(xml_file.read()))
        db.import_bank_of_canada_rates(xml_file)

if __name__ == '__main__':
    main()
