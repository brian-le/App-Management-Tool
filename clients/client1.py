'''
Created on May 20, 2011

@author: Brian Le
'''
from utils.base import BaseClientHandler

from google.appengine.ext import db
from google.appengine.api import users
from models import Client_User
import logging

class Client1Handler(BaseClientHandler):
    def get(self):
        self.render(u'client1_login_button')
        
    def post(self):
        '''The signed_request is sent here once the user allows the app
        In order to create a personalized user experience, Facebook sends your app information about the user.
        This information is passed to your Canvas URL using HTTP POST within a single signed_request parameter 
        which contains a base64url encoded JSON object.
        '''
        logging.info("Canvas Page 2: Another Facebook user allows Client1 app ClickIn People Search.")

class Client1SearchHandler(BaseClientHandler):
    def get(self):
        user = users.get_current_user()
        query = db.Query(Client_User)
        query.filter('email =', user.email())
        admin = query.get()
        if admin:
            admin.put()
            apps = admin.client.apps
            self.render(u'select_app_to_search', admin=admin, apps=apps)
        else:
            self.response.out.write("<b>HTTP Error 401.1 - Unauthorized:</b> Access is denied due to invalid credentials.<br/>")
            self.response.out.write("Your account is not authorized to access <b>Facebook Apps Management Tool.</b><p><p>")
            self.response.out.write("<a href=\"%s\">Sign out</a>" % users.create_logout_url("/"))        

