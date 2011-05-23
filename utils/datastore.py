'''
Created on May 20, 2011

@author: Brian
'''
from google.appengine.ext import db

from models import Client
from models import Client_User
from models import App

def populate_datastore():
    client_key_name1='client01'
    client1 = Client(key_name=client_key_name1, id='12345678', name='Organic Oranges LLC', domain=db.Link("http://client1.clickin-tech.appspot.com"))
    client1.put()
    
    client_key_name2='client02'
    client2 = Client(key_name=client_key_name2, id='87654321', name='Green Trees Inc.', domain=db.Link("http://client2.clickin-tech.appspot.com"))
    client2.put()
    
    admin_key_name1='admin001'
    admin1 = Client_User(key_name=admin_key_name1, client=client1, id='001002', name='Daniel Alves', 
                        email='client1_ad1@hotmail.com')
    admin1.put()
        
    admin_key_name2='admin002'
    admin2 = Client_User(key_name=admin_key_name2, client=client1, id='001005', name='Andres Iniesta', 
                        email='client1_ad2@yahoo.com')
    admin2.put()
        

    admin_key_name5='admin05'
    admin5 = Client_User(key_name=admin_key_name5, client=client2, id='0010011', name='Josep Guardiola', 
                        email='client2_ad1@yahoo.com')
    admin5.put()
        
    admin_key_name6='admin06'
    admin6 = Client_User(key_name=admin_key_name6, client=client2, id='0010016', name='Lionel Messi', 
                        email='client2_ad2@live.com')
    admin6.put()
        
    #ClickIn People Search
    app_key_name1='app1'
    app1 = App(key_name=app_key_name1, client=client1, app_id='163185560402939', 
               api_key='807c2277abe596cfe542927858105306', 
               app_secret='aae6abb4d6bf0b41f066c387ab36e486',
               name = 'ClickIn People Search', 
               domain=db.Link("http://app1.client1.clickin-tech.appspot.com/"))
    app1.put()
        
    #Click In People Search 2
    app_key_name2='app2'
    app2 = App(key_name=app_key_name2, client=client1, app_id='114549068628127', 
               api_key='7f15ffb2b72ff6c4a6d08daebca21a52', 
               app_secret='61545bcd8a3d9fc6a8107eaed5cbe4de',
                   name = 'ClickIn People Search 2', 
                   domain=db.Link("http://app2.client1.clickin-tech.appspot.com/"))
    app2.put()
        
    #Cool Running App
    app_key_name3='app3'
    app3 = App(key_name=app_key_name3, client=client2, app_id='107411582680918', 
               api_key='7a55f39fb4e0371aad78e1bd8dd517af', 
               app_secret='c12b89b5f815cebe27636cd8c50a6264',
               name = 'Cool Running App', 
               domain=db.Link("http://app1.client2.clickin-tech.appspot.com/"))

    app3.put()      
