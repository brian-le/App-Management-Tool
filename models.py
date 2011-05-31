from google.appengine.ext import db

class TimeZone(db.Model):
    description = db.StringProperty(required=True)
    offset = db.FloatProperty(required=True)
    created = db.DateTimeProperty(required=True, auto_now_add=True)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)

class Client(db.Model):
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    domain = db.LinkProperty(required=True)
    created = db.DateTimeProperty(required=True, auto_now_add=True)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)
    
    
class Client_User(db.Model):
    # A client may have many users using different Facebook apps developed by the client
    client = db.ReferenceProperty(Client, collection_name='client_users')
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    email = db.EmailProperty()
    timezone = db.ReferenceProperty(TimeZone)
    created = db.DateTimeProperty(required=True, auto_now_add=True)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)
    
class App(db.Model):
    client = db.ReferenceProperty(Client, collection_name='apps')
    app_id = db.StringProperty(required=True)
    api_key = db.StringProperty(required=True)
    app_secret = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    domain = db.LinkProperty(required=True)
    created = db.DateTimeProperty(required=True, auto_now_add=True)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)

class App_User(db.Model):
    app_id = db.StringProperty(required=True)#reference property, should fix here. A workaround.
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    email = db.EmailProperty()
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    token_status = db.StringProperty(required=True)
    created = db.DateTimeProperty(required=True, auto_now_add=True)
    last_modified = db.DateTimeProperty(required=True, auto_now=True)

class MonitoredUser(db.Model):
    id = db.StringProperty(required=True)
    app_id = db.StringProperty(required=True)
    last_online_presence = db.StringProperty(required=True, default="error")
    message = db.StringProperty()
    access_token = db.StringProperty(required=True)
    time_to_post = db.DateTimeProperty(default=None)
    