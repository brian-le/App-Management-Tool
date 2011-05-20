'''
Created on May 20, 2011

@author: Brian
'''
import Cookie, hashlib, hmac, base64
import time
import email.utils

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

