"""Quick and dirty script that downloads some regional poll averages."""

import json
import urllib2

def PrintDataPoint(data, party_name):
    row = [data['statdate'], data['region'], party_name, data[party_name]]
    print ','.join(str(x) for x in row)

def DoRegion(region_name):
    url = ('http://cbcnewsinteractives.com/canopy/poll_tracker_prod/np/' +
           'poll_averages/' + region_name + '?parseData=' +
           'jQuery2140210138985227179_1443503953058&_=1443503953061')
    response = urllib2.urlopen(url)
    raw = response.read()
    raw = raw.replace('parseData(', '').replace(');', '')
    parsed = json.loads(raw)
    for data_row in parsed['data']:
        for party_name in ['cpc', 'ndp', 'lpc', 'gpc', 'bq', 'oth']:
            PrintDataPoint(data_row, party_name)

for region in ['Canada', 'AB', 'ATL', 'BC', 'ON', 'QC', 'SK_MB']:
    DoRegion(region)
