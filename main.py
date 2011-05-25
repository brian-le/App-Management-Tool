import os, cgi
import urllib, urllib2, logging
import base64
import time, datetime

import facebook

from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.api import users

from utils.base import BaseClientHandler
from utils.cookies import set_cookie
from utils.facebook import check_online_presence
from utils.authorization import authorizedAdminClient

from models import App
from models import App_User
from models import MonitoredUser
from models import TimeZone
from clients.client1 import Client1Handler
from clients.client1 import Client1SearchHandler
from clients.client2 import Client2Handler

class MasterHandler(BaseClientHandler):
    def get(self):
        admin = authorizedAdminClient()
        if admin:
            self.render(u'admin_menu')
        else:
            self.render(u'unauthorized', user=users.get_current_user(), 
                        login_url=users.create_login_url("/"), 
                        logout_url=users.create_logout_url("/"))
        
class SelectAppHandler(BaseClientHandler):
    def get(self):
        admin = authorizedAdminClient()
        if admin:
            apps = admin.client.apps
            self.render(u'select_app', admin=admin, apps=apps)
        else:
            self.render(u'unauthorized', user=users.get_current_user(), 
                        login_url=users.create_login_url("/"), 
                        logout_url=users.create_logout_url("/"))

class AppMenuHandler(BaseClientHandler):
    def get(self):
        admin = authorizedAdminClient()
        if admin:
            app_id = cgi.escape(self.request.get("app"))
            encoded_app_id = base64.b64encode(app_id)
            apps = App.all()
            apps.filter('app_id =', app_id)
            app = apps.get()
            self.render(u'app_menu', app=app, encoded_app_id=encoded_app_id)
        else:
            self.render(u'unauthorized', user=users.get_current_user(), 
                        login_url=users.create_login_url("/"), 
                        logout_url=users.create_logout_url("/"))

    
class AdminAccountManager(BaseClientHandler):
    def get(self):
        allTimeZones = TimeZone.all().order('offset')
        timezones = []
        class Tz:
            pass
        
        from utils.timezone import pretty_print
        for timezone in allTimeZones:
            tz = Tz()
            tz.id = timezone.key().id_or_name()
            description = pretty_print(timezone)
            tz.description = description 
            timezones.append(tz)
        
        admin = authorizedAdminClient()
        if admin:
            self.render(u'admin_update_page', admin=admin, timezones=timezones)
        else:
            self.render(u'unauthorized', user=users.get_current_user(), 
                        login_url=users.create_login_url("/"), 
                        logout_url=users.create_logout_url("/"))

class SaveAccountHandler(BaseClientHandler):
    def post(self):
        timezone_id = cgi.escape(self.request.get("timezone"))
        timezone = TimeZone.get_by_id(long(timezone_id))
        admin = authorizedAdminClient()
        if admin:
            admin.timezone = timezone
            admin.put()
            self.response.out.write("Saved changes for admin %s. Time zone is now %s." % 
                                    (admin.name, timezone.description))
        else:
            self.render(u'unauthorized', user=users.get_current_user(), 
                        login_url=users.create_login_url("/"), 
                        logout_url=users.create_logout_url("/"))
        
    
class SelectPermissionsHandler(BaseClientHandler):
    def get(self):
        app_id = cgi.escape(self.request.get("app"))
        self.redirect("/ask_permissions?app=" + app_id)

class AskPermissionsHandler(BaseClientHandler):
    def get(self):
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
                        name=profile["name"], email=profile["email"], access_token=access_token,
                        profile_url=profile["link"], token_status="Active")
            user.put()
            set_cookie(self.response, "fb_user", str(profile["id"]),
                       expires=time.time() + 30 * 86400, secret=app_secret)
            
            encoded_app_id = base64.b64encode(app_id)
            self.redirect("/show_users?app_id=" + encoded_app_id)
        else:
            scope = cgi.escape(self.request.get("scope"))
            custom_scope = "&scope=" + scope
            custom_request_url="https://www.facebook.com/dialog/oauth?" + urllib.urlencode(args) + custom_scope
            self.redirect(custom_request_url)
        
class ShowSelectedUsersHandler(BaseClientHandler):
    def get(self):
        encoded_app_id = self.request.get("app_id")
        app_id = base64.b64decode(encoded_app_id)
        selected_users = db.Query(App_User).filter('app_id =', app_id)
        app = db.Query(App).filter("app_id =", app_id).get()
        admin = authorizedAdminClient()
        from utils.timezone import pretty_print
        self.render(u'message_posting_form', app=app, users=selected_users, 
                    date_range=range(1, 32), year_range=range(2011, 2021), 
                    hour_range=range(24), minute_range=range(60), 
                    timezone_description = pretty_print(admin.timezone),
                    timezone = admin.timezone.offset)
        
class PostMessagesHandler(BaseClientHandler):
    def post(self):
        app_id = self.request.get("app_id")
        message = cgi.escape(self.request.get("message"))
        selected_user_ids = self.request.get_all("selected_users")
        selected_users = db.Query(App_User).filter("app_id =", app_id).filter("id IN ", selected_user_ids)
        timezone = cgi.escape(self.request.get("timezone"))
        timezone = float(timezone)
        timedelta = datetime.timedelta(hours=-timezone)
        
        schedule = self.request.get_all("schedule")
        time_to_post=None
        if "later" in schedule:
            month=int(cgi.escape(self.request.get("month")))
            date=int(cgi.escape(self.request.get("date")))
            year=int(cgi.escape(self.request.get("year")))
            hour=int(cgi.escape(self.request.get("hour")))
            minute=int(cgi.escape(self.request.get("minute")))
            time_to_post=datetime.datetime(year, month, date, hour, minute)
            time_to_post = time_to_post + timedelta
           
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

class SearchHandler(BaseClientHandler):    
    def get(self):
        app = cgi.escape(self.request.get("app"))
        if app:
            self.redirect("/search?app_id=" + base64.b64encode(app))
        
        app_id = cgi.escape(self.request.get("app_id"))
        if app_id:
            original_query = cgi.escape(self.request.get("query"))
            if original_query:
                app_id = base64.b64decode(app_id)
                #Remove leading, trailing, and multiple white spaces from the string query.
                query = original_query
                query = ' '.join(query.split())
                results = self.search(app_id, query=query)
                if len(results) > 0:
                    self.render(u'search_results', users=results)
                else:
                    self.render(u'search_results', users=None, query=query)                
            else:
                self.render(u'search_form', app_id=app_id)
        
    def search(self, app_id, query):
        #case-insensitive matching
        query = query.lower() 
        q = App_User.all()
        all = q.count()
        q.filter("app_id =", app_id)
        app_users = q.fetch(all)
        results = set()
         
        for user in app_users:
            name_index = user.name.lower().find(query)
            id_index = user.id.lower().find(query)
            email_index = -1
            if user.email:
                email_index = user.email.lower().find(query)
            matches = name_index >= 0 or id_index >= 0 or email_index >= 0
            if matches:
                results.add(user) 
                        
        return results

class PopulateDatabase(BaseClientHandler):
    def get(self):
        from utils.datastore import populate_timezone
        populate_timezone()
        self.response.out.write("Timezones populated.")

clients = {
  'client1.clickin-tech.appspot.com': webapp.WSGIApplication([
    ('/', MasterHandler),
    #(r"/search", Client1SearchHandler),
    #('/(.*)', Client1Handler)
    ]),
           
  'client2.clickin-tech.appspot.com': webapp.WSGIApplication([
    ('/', MasterHandler),
    #('/(.*)', Client2Handler)
    ]),
           
  'clickin-tech.appspot.com': webapp.WSGIApplication([
    (r"/select_permissions", SelectPermissionsHandler),
    (r"/ask_permissions", AskPermissionsHandler),
    (r"/permissions", PermissionsHandler),
    (r"/gettoken", GetAccessTokenHandler),
    (r"/show_users", ShowSelectedUsersHandler),
    (r"/post_messages", PostMessagesHandler),
    (r"/post_a_message", Post_A_Message), 
    (r"/tasks/monitor", OnlinePresenceMonitor),
    (r"/search", SearchHandler),
    (r"/select_app", SelectAppHandler),
    (r"/app_menu", AppMenuHandler),
    (r"/account", AdminAccountManager),
    (r"/save_account", SaveAccountHandler),
    #(r"/populate", PopulateDatabase),
    (r"/", MasterHandler)])
}

def main():
    run_wsgi_app(clients[os.environ['HTTP_HOST']])

if __name__ == "__main__":
    main()
    