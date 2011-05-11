import os
import cgi
import urllib, urllib2
import base64
import time
import Cookie
import hashlib
import hmac
import email.utils
import datetime
import logging

import facebook

from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.ext.webapp import template

class Client(db.Model):
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    created = db.DateTimeProperty(required=True, auto_now_add=True)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)
    domain = db.LinkProperty(required=True)
    
class Client_User(db.Model):
    # A client may have many users using different Facebook apps developed by the client
    client = db.ReferenceProperty(Client, collection_name='client_users')
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    email = db.EmailProperty()
    created = db.DateTimeProperty(required=True, auto_now_add=True)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)
    password = db.StringProperty(required=True)
    
class App(db.Model):
    client = db.ReferenceProperty(Client, collection_name='apps')
    app_id = db.StringProperty(required=True)
    api_key = db.StringProperty(required=True)
    app_secret = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    domain = db.LinkProperty(required=True)

class App_User(db.Model):
    app_id = db.StringProperty(required=True)#reference property, should fix here. A workaround.
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    email = db.EmailProperty()
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    token_status = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class MonitoredUser(db.Model):
    id = db.StringProperty(required=True)
    app_id = db.StringProperty(required=True)
    last_online_presence = db.StringProperty(required=True, default="error")
    message = db.StringProperty()
    access_token = db.StringProperty(required=True)
    time_to_post = db.DateTimeProperty(default=None)

class BaseClientHandler(webapp.RequestHandler):
    def render(self, name, **data):
        """Render a template in the 'templates' folder."""
        self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), 'templates', name + '.html'), data))

    
class Client1Handler(BaseClientHandler):
    def get(self):
        # The populating should run only once
        #self.populate_datastore() 
        admin2 = Client_User.get_by_key_name('admin06')
        apps = admin2.client.apps
        self.render(u'app_mngt', admin=admin2, admin_key=admin2.key().id_or_name(), apps=apps)
        
    def populate_datastore(self):
        client_key_name1='client01'
        client1 = Client(key_name=client_key_name1, id='12345678', name='Organic Oranges LLC', domain=db.Link("http://client1.click-in.appspot.com"))
        client1.put()
        
        admin_key_name1='admin001'
        admin1 = Client_User(key_name=admin_key_name1, client=client1, id='001002', name='David Administrator', 
                             email='dave@client1.com.au', password='SesameOil')
        admin1.put()
        
        admin_key_name2='admin002'
        admin2 = Client_User(key_name=admin_key_name2, client=client1, id='001005', name='John Admin', 
                             email='johnny@client1.com.au', password='Coconut')
        admin2.put()
        
        client_key_name2='client02'
        client2 = Client(key_name=client_key_name2, id='87654321', name='Green Trees Inc.', domain=db.Link("http://client2.click-in.appspot.com"))
        client2.put()

        admin_key_name5='admin05'
        admin5 = Client_User(key_name=admin_key_name5, client=client2, id='0010011', name='Joe Admin', 
                             email='joe@client2.com.au', password='dragon123')
        admin5.put()
        
        admin_key_name6='admin06'
        admin6 = Client_User(key_name=admin_key_name6, client=client2, id='0010016', name='Tom Admin', 
                             email='tommy@client2.com.au', password='dragonflies')
        admin6.put()

        
        #ClickIn People Search
        app_key_name1='app1'
        app1 = App(key_name=app_key_name1, client=client1, app_id='163185560402939', 
                   api_key='807c2277abe596cfe542927858105306', 
                   app_secret='aae6abb4d6bf0b41f066c387ab36e486',
                   name = 'ClickIn People Search', 
                   domain=db.Link("http://app1.client1.click-in.appspot.com/"))
        app1.put()
        
        #Click In People Search 2
        app_key_name2='app2'
        app2 = App(key_name=app_key_name2, client=client1, app_id='114549068628127', 
                   api_key='7f15ffb2b72ff6c4a6d08daebca21a52', 
                   app_secret='61545bcd8a3d9fc6a8107eaed5cbe4de',
                   name = 'ClickIn People Search 2', 
                   domain=db.Link("http://app2.client1.click-in.appspot.com/"))
        app2.put()
        
        #Cool Running App
        app_key_name3='app3'
        app3 = App(key_name=app_key_name3, client=client2, app_id='107411582680918', 
                   api_key='7a55f39fb4e0371aad78e1bd8dd517af', 
                   app_secret='c12b89b5f815cebe27636cd8c50a6264',
                   name = 'Cool Running App', 
                   domain=db.Link("http://app1.client2.click-in.appspot.com/"))

        app3.put()      
        

class Client2Handler(BaseClientHandler):
    def get(self):
        self.response.out.write("You are Client 02!") 
        
class StartHandler(BaseClientHandler):
    def post(self):
        self.response.out.write("Admin ID: " + self.request.get("admin") + "<br />\n")
        self.response.out.write("Admin's App ID: " + self.request.get("app") + "<br />\n")
        app_id = self.request.get("app")
        apps = App.all()
        apps.filter('app_id =', app_id)
        app = apps.get()
        self.render(u'permissions', app=app)
        
class PermissionsHandler(BaseClientHandler):
    def post(self):
        #self.response.out.write("Permissions handler is coming...")
        arguments = self.request.arguments()
        scope = set()
        for argument in arguments:
            if argument != 'app_id':
                value = cgi.escape(self.request.get(argument))
                if value:
                    scope.add(value)
                
        scope.add('offline_access')
        app_id=cgi.escape(self.request.get("app_id"))
        args = dict(scope=','.join(scope), app_id=app_id)
        self.redirect("/gettoken?" + urllib.urlencode(args))
            
class GetAccessTokenHandler(BaseClientHandler):
    def get(self):
        app_id=self.request.get("app_id")
        app_id_args = dict(app_id=app_id)
        redirect_uri = self.request.path_url + "?" + urllib.urlencode(app_id_args)
        args = dict(client_id=app_id, redirect_uri=redirect_uri)
        
        if self.request.get("code"):
            self.response.out.write("OAuth Dance Step 2 for App ID '" + app_id + "'.<br>\n")            
            
            query = db.Query(App)
            query.filter('app_id =', app_id)
            app = query.fetch(limit=1)[0]
           
            app_secret = app.app_secret
            args["client_secret"] = app_secret
            args["client_id"] = app_id
            args["code"] = self.request.get("code")    
            response = cgi.parse_qs(urllib2.urlopen("https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)).read())
            access_token = response["access_token"][-1]
            
            # Download the user profile and cache a local instance of the basic profile info
            profile = json.load(urllib.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(dict(access_token=access_token))))        
            user_id = str(profile["id"])
            key_name = app_id + "_" + user_id
            user = App_User(key_name=key_name, id=user_id, app_id=app_id,
                        name=profile["name"], access_token=access_token,
                        profile_url=profile["link"], token_status="Active")
            user.put()
            set_cookie(self.response, "fb_user", str(profile["id"]),
                       expires=time.time() + 30 * 86400, secret=app_secret)
            
            self.redirect("/show_users?app_id="+app_id)
        else:
            scope = cgi.escape(self.request.get("scope"))
            custom_scope = "&scope=" + scope
            custom_request_url="https://www.facebook.com/dialog/oauth?" + urllib.urlencode(args) + custom_scope
            self.redirect(custom_request_url)
        
class ShowSelectedUsersHandler(BaseClientHandler):
    def get(self):
        app_id=self.request.get("app_id")
        selected_users = db.Query(App_User).filter('app_id =', app_id)
        app = db.Query(App).filter("app_id =", app_id).get()                    
        self.render(u'message_form', app=app, users=selected_users, date_range=range(1, 32), year_range=range(2011, 2021), 
                    hour_range=range(24), minute_range=range(60))
        
class PostMessagesHandler(BaseClientHandler):
    def post(self):
        app_id = self.request.get("app_id")
        message = cgi.escape(self.request.get("message"))
        selected_user_ids = self.request.get_all("selected_users")
        selected_users = db.Query(App_User).filter("app_id =", app_id).filter("id IN ", selected_user_ids)
        
        """
        self.response.out.write("App ID: " + app_id + "<br />")
        self.response.out.write("Selected users: ")
        self.response.out.write(selected_users)
        self.response.out.write("<br />Message: " + message)
        """
        
        schedule = self.request.get_all("schedule")
        time_to_post=None
        if "later" in schedule:
            month=int(cgi.escape(self.request.get("month")))
            date=int(cgi.escape(self.request.get("date")))
            year=int(cgi.escape(self.request.get("year")))
            hour=int(cgi.escape(self.request.get("hour")))
            minute=int(cgi.escape(self.request.get("minute")))
            time_to_post=datetime.datetime(year, month, date, hour, minute)
           
            if len(schedule)==1: #if only scheduled posting was chosen
                self.schedule_a_post(app_id, selected_users, time_to_post, message)             
            
        if ("gets_online" in schedule):
            self.monitor_users(app_id, selected_users, message, time_to_post)
            
        self.render(u'confirmation', users=selected_users, message=message)

    def monitor_users(self, app_id, users, message, time_to_post=None):
        for user in users:
            online_presence=check_online_presence(user)
            if online_presence is None:
                online_presence="error" #cannot determine online presence
            monitor_user = MonitoredUser(app_id=app_id, id=user.id, 
                                         last_online_presence=online_presence, 
                                         message=message, access_token=user.access_token,
                                         time_to_post=time_to_post)
            monitor_user.put()

    def schedule_a_post(self, app_id, users, time_to_post, message): 
        deferred_queue = taskqueue.Queue(name="deferred-queue")
        for user in users:
            task = taskqueue.Task(eta=time_to_post, url="/post_a_message", 
                                  params={'app_id':app_id, 'user_id':user.id, 
                                          'access_token':user.access_token,
                                          'message':message})
            deferred_queue.add(task)

# A really simple handler which just posts a message on a user's wall,
# given a correct access token.
class Post_A_Message(webapp.RequestHandler):
    def post(self):
        access_token = cgi.escape(self.request.get("access_token"))
        user_id = cgi.escape(self.request.get("user_id"))
        app_id = cgi.escape(self.request.get("app_id"))
        message = cgi.escape(self.request.get("message"))        
        graph = facebook.GraphAPI(access_token)
        graph.put_wall_post(message=message, profile_id=user_id)
        logging.debug("App ID " + app_id + " | Scheduled posting | User ID " 
                      + user_id + " | Message: " + message)

class OnlinePresenceMonitor(webapp.RequestHandler):
    def get(self):
        monitored_users=MonitoredUser.all()
        for user in monitored_users:
            logging.debug("Serving user " + user.id + " | Message: " + user.message)
    
        monitored_users=MonitoredUser.all()
       
        for user in monitored_users:
            message=user.message
            access_token=user.access_token
            current_online_status=check_online_presence(user)
            
            if (current_online_status=='active'): #active, idle, offline, or error
                graph = facebook.GraphAPI(access_token)
                if user.time_to_post:
                    now = datetime.datetime.now()
                    if now > user.time_to_post:
                        graph.put_wall_post(message=message, profile_id=user.id)
                        user.delete() #remove this user's pending post from the cron list
                        logging.debug("Online presence + scheduled posting User ID " + user.id 
                                      + " | Message: " + message)
                else:
                    graph.put_wall_post(message=message, profile_id=user.id)
                    logging.debug("Online posting User ID " + user.id + " | Message: " + message)
                    user.delete() #remove this user's pending post from the cron list
clients = {
  'client1.click-in.appspot.com': webapp.WSGIApplication([
    ('/', Client1Handler),
    ('/(.*)', Client1Handler)]),
           
  'client2.click-in.appspot.com': webapp.WSGIApplication([
    ('/', Client2Handler),
    ('/(.*)', Client2Handler)]),
           
  'click-in.appspot.com': webapp.WSGIApplication([
    (r"/start", StartHandler),
    (r"/permissions", PermissionsHandler),
    (r"/gettoken", GetAccessTokenHandler),
    (r"/show_users", ShowSelectedUsersHandler),
    (r"/post_messages", PostMessagesHandler),
    (r"/post_a_message", Post_A_Message), 
    (r"/tasks/monitor", OnlinePresenceMonitor)])
}

def main():
    run_wsgi_app(clients[os.environ['HTTP_HOST']])

if __name__ == "__main__":
    main()

"""    
def main():
    application = webapp.WSGIApplication([
    ('/', Client1Handler),
    (r"/start", StartHandler),
    (r"/permissions", PermissionsHandler),
    (r"/gettoken", GetAccessTokenHandler),
    (r"/show_users", ShowSelectedUsersHandler),
    (r"/post_messages", PostMessagesHandler),
    (r"/post_a_message", Post_A_Message),
    (r"/tasks/monitor", OnlinePresenceMonitor),
    ('/(.*)', Client1Handler)], debug=True)

                                     
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

"""

def set_cookie(response, name, value, domain=None, path="/", expires=None, secret=""):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(secret, value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[name] = "|".join([value, timestamp, signature])
    cookie[name]["path"] = path
    if domain: cookie[name]["domain"] = domain
    if expires:
        cookie[name]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
    response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))

def cookie_signature(secret, *parts):
    """Generates a cookie signature.

    We use the Facebook app 'secret' since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(secret, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()

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
