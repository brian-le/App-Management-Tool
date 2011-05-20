'''
Created on May 20, 2011

@author: Brian
'''
from utils.base import BaseClientHandler

from google.appengine.ext import db
from google.appengine.api import users
from models import Client_User


class Client1Handler(BaseClientHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            query = db.Query(Client_User)
            query.filter('email =', user.email())
            admin = query.get()
            if admin:
                admin.put()
                apps = admin.client.apps
                self.render(u'select_app_to_search', admin=admin, apps=apps)
                return
            else:
                greeting = ("Welcome, %s (v2)! (<a href=\"%s\">Sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/search"))

        self.response.out.write("<html><body>%s</body></html>" % greeting)
                
class Client1SearchHandler(BaseClientHandler):
    def get(self):
        user = users.get_current_user()
        query = db.Query(Client_User)
        query.filter('email =', user.email())
        admin = query.get()
        if admin:
            #admin = Client_User.get_by_key_name('admin05')
            admin.put()
            apps = admin.client.apps
            self.render(u'select_app_to_search', admin=admin, apps=apps)
        else:
            self.response.out.write("<b>HTTP Error 401.1 - Unauthorized:</b> Access is denied due to invalid credentials.<br/>")
            self.response.out.write("Your account is not authorized to access <b>Facebook Apps Management Tool.</b><p><p>")
            self.response.out.write("<a href=\"%s\">Sign out</a>" % users.create_logout_url("/"))        
