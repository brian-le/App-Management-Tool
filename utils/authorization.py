'''
Created on May 24, 2011

@author: Brian
'''
from google.appengine.api import users
from google.appengine.ext import db

from models import Client_User

def authorizedAdminClient():
    user = users.get_current_user()
    if user:
        query = db.Query(Client_User)
        email = user.nickname()
        if email.find("@") < 0:
            email = user.email()            
        query.filter('email =', email)
        #Executes the query, then returns the first result, or None if the query returned no results.
        return query.get()
    else:
        return None

    
