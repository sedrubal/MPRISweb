#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Control your musicplayer through the web.
"""

__authors__ = "sedrubal"
__email__ = "sebastian.endres@online.de",
__license__ = "GPLv3 & non military"
__url__ = "https://github.com/sedrubal/dbusmediaweb"


import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json


class StartPage(tornado.web.RequestHandler):
    """
    A normal webpage providing some html, css and js, which uses websockets
    """
    def get(self):
        """the handler for get requests"""
        self.render("index.html",
                    title="DBusMediaWeb",
                    description=__doc__,
                    author=__authors__,
                    license=__license__,
                    url=__url__,
                    authors_url='/'.join(__url__.split('/')[:-1]))


class MediaDBus(object):
    """a wrapper for dbus"""
    def __init__(self, arg):
        self.arg = arg
        self.currentTitle = "My wonderful track"
        self.nextTitle = "Next wonderful track"

    def getCurrentTitle(self):
        """returns the title of the current track"""
        return self.currentTitle

    def getNextTitle(self):
        """returns the title of the next track"""
        return self.nextTitle


class Client(object):
    """
    An object to store the connected clients
    """
    def __init__(self, socket):
        self.socket = socket


class WebSocket(tornado.websocket.WebSocketHandler):
    """
    The websocket server part
    """
    def open(self):
        """when a client connects, add this socket to list"""
        print("WebSocket opened")
        self.client = Client(socket=self)
        APP.clients.append(self.client)
        msg = {
            "current": APP.mediadbus.getCurrentTitle(),
            "next": APP.mediadbus.getNextTitle(),
        }
        for client in APP.clients:
            client.socket.send(json.dumps(msg))

    def on_message(self, message):
        """new message received"""
        print("received: " + message)

    def send(self, message):
        """send a message to my client"""
        print("send: " + message)  # TODO

    def on_close(self):
        """the client of this socket leaved, remove this socket from list"""
        print("WebSocket closed")


SETTINGS = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}


def make_app():
    """create a new application and specify the url patterns"""
    return tornado.web.Application([
        (r"/websocket", WebSocket),
        (r"/", StartPage),
        (r"/static/", tornado.web.StaticFileHandler,
         dict(path=SETTINGS['static_path'])),
    ], **SETTINGS)

if __name__ == "__main__":
    APP = make_app()
    APP.listen(8888)
    APP.mediadbus = MediaDBus("TODO")
    APP.clients = []  # global list of all connected websocket clients
    tornado.ioloop.IOLoop.current().start()
