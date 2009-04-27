import httplib, oauth
from xml.etree import ElementTree as ET
from google.appengine.api.urlfetch import fetch
import urlparse, cgi

# boilerplate adapted from http://apidocs.qype.com/authentication_overview
class SimpleOAuthClient(oauth.OAuthClient):
    def __init__(self, server, port=httplib.HTTP_PORT):
        self.server = server
        self.port = port
        self.connection = httplib.HTTPConnection(
            "%s:%d" % (self.server, self.port)
        )
    
    def access_resource(self, oauth_request):
        self.connection.request(
            oauth_request.http_method, oauth_request.to_url()
        )
        response = self.connection.getresponse()
        return response.read()

class AppEngineOAuthClient(oauth.OAuthClient):
    def __init__(self, host):
        pass
    
    def access_resource(self, oauth_request):
        response = fetch(
            oauth_request.to_url(), method = oauth_request.http_method
        )
        return response.content

class Qype(object):
    host = 'api.qype.com'
    
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
    
    def get_oauth_request(self, url):
        client = AppEngineOAuthClient(self.host)
        consumer = oauth.OAuthConsumer(self.api_key, self.api_secret)
        
        bits = urlparse.urlparse(url)
        params = dict(cgi.parse_qsl(bits.query))
        
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            oauth_consumer = consumer,
            token = None,
            http_method = 'GET',
            http_url = url,
            parameters = params
        )
        oauth_request.sign_request(
            oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, None
        )
        return oauth_request
    
    def get(self, url):
        return AppEngineOAuthClient(self.host).access_resource(
            self.get_oauth_request(url)
        )
    
    def get_oauth_url(self, url):
        return self.get_oauth_request(url).to_url()
    
    def get_et(self, url):
        return ET.fromstring(self.get(url))
