#!/usr/bin/python

import wsgiref.simple_server
from libviewer import serve

server = wsgiref.simple_server.make_server('', 8000, serve)
print "Server listening on port %d" % 8000
server.serve_forever()
