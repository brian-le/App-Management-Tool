'''
Created on May 20, 2011

@author: Brian
'''

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class BaseClientHandler(webapp.RequestHandler):
    def render(self, name, **data):
        """Render a template in the 'templates' folder."""
        self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), '../templates', name + '.html'), data))
