'''
Created on May 20, 2011

@author: Brian
'''
import urllib, urllib2
from django.utils import simplejson as json

def check_online_presence(user):
    format="JSON"
    query="SELECT online_presence FROM user WHERE uid=" + user.id
    access_token=user.access_token
    query_url="https://api.facebook.com/method/fql.query?"
    full_thing = query_url + urllib.urlencode(dict(query=query, format=format, access_token=access_token))
    result = json.load(urllib2.urlopen(full_thing))
    online_presence=None
    if len(result)==1:
        online_presence=result[0]['online_presence']            
    return online_presence

