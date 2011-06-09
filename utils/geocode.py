'''
Created on Jun 9, 2011

@author: Brian
'''
from django.utils import simplejson
import urllib

GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'

'''
Return the country of an address.
For example: 123 Amphitheatre Pkwy Mountain View, CA 94043
Returns: USA
'''
def get_country(address,sensor, **geo_args):
    geo_args.update({
        'address': address,
        'sensor': sensor  
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))

    address_list =  simplejson.dumps([s['formatted_address'] for s in result['results']])
    address = eval(address_list)[0]
    country = address.split(', ')[-1]
    return country

if __name__ == '__main__':
    print get_country(address="123 Amphitheatre Pkwy Mountain View, CA", sensor="false")
