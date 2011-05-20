'''
Created on May 20, 2011

@author: Brian
'''
from utils.base import BaseClientHandler

class Client2Handler(BaseClientHandler):
    def get(self):
        self.response.out.write("<center><b>Page under construction. Please check back later!</b></center>")

