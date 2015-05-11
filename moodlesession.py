import requests
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
import config

def connect():
    s = requests.session();
    initial = s.get('https://moodle.hsr.ch/auth/shibboleth/index.php')
    # now we're on the wayf screen

    iSoup = BeautifulSoup(initial.content)
    target = iSoup.find('form')['action']
    url = urlparse(initial.url)
    wayfTarget = url.scheme + '://' + url.netloc + target
    wayfPayload = {'user_idp': 'https://aai-login.hsr.ch/idp/shibboleth', 'Select': 'Select'}

    wayf = s.post(wayfTarget, data = wayfPayload)
    # this is the hsr aai-loginscreen

    loginPayload = {
        'j_username': config.user,
        'j_password': config.password,
        'submit.x': '19',
        'submit.y': '8'
    }

    login = s.post('https://aai-login.hsr.ch/idp/Authn/UserPassword', data=loginPayload)
    #here is the saml continue button
    lSoup = BeautifulSoup(login.content)
    target = lSoup.find('form')['action']
    payload = {
        'RelayState': lSoup.find(attrs={"name": "RelayState"})['value'],
        'SAMLResponse': lSoup.find(attrs={"name": "SAMLResponse"})['value']
    }

    moodle = s.post(target, data = payload)
    #this is the logged in homepage of moodle.

    return s



