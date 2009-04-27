import wsgiref.handlers
from google.appengine.ext import webapp

import urllib, xmlhighlight
from qype import Qype

template = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>%(title)s</title>
<style type="text/css">
ol {
	list-style-type: none;
	padding: 0;
}
li {
    padding-left: 2em;
}
a.apilink {
    color: green;
}
span.t {
	color: #999;
}
span.a {
	color: #666;
}
span.key {
	color: #999;
}
#main {
	padding-top: 1.12em;
	font-family: courier;
	font-size: 0.9em;
	background-color: #fff;
}
h1 {
	font-family: georgia;
}
h1 a {
    font-size: 0.4em;
}
</style>
</head>
<body>
<h1>Qype API explorer <a href="http://apidocs.qype.com/">API documentation</a></h1>
<div id="main">
%(main)s
</div>
</body>
</html>
"""

class MainHandler(webapp.RequestHandler):
    def get(self, path):
        # Do we have an API key and secret?
        api_details = self.request.cookies.get('api_details', ':')
        api_key, api_secret = api_details.split(':', 1)
        if not api_key or not api_secret:
            self.response.out.write(template % {
                'title': 'Enter your API key and secret',
                'main': '''
                <h2>Enter your API key and secret</h2>
                <form action="/set-api-details" method="post">
                <p><label for="api_key">API key:</label>
                    <input type="text" name="api_key" id="api_key">
                </p>
                <p><label for="api_secret">API secret:</label>
                    <input type="text" name="api_secret" id="api_secret">
                </p>
                <p><input type="submit" value="Go"></p>
                </form>
                '''
            })
            return
        
        qype = Qype(api_key, api_secret)
        path = '/' + path
        if self.request.query_string:
            path += '?' + self.request.query_string
        et = qype.get_et('http://api.qype.com' + path)
        html = xmlhighlight.highlight(et).encode('utf8')
        self.response.out.write(template % {
            'title': path,
            'main': html
        })

class ApiDetailsHandler(webapp.RequestHandler):
    def post(self):
        details = str('%s:%s' % (
            self.request.get('api_key', ''),
            self.request.get('api_secret', '')
        ))
        self.response.headers.add_header(
            'Set-Cookie',
            'api_details=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT' % details
        )
        self.redirect('/')

def main():
    application = webapp.WSGIApplication([
        ('/set-api-details', ApiDetailsHandler),
        ('/(.*)', MainHandler)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()

