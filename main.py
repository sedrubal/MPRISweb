#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Control your musicplayer through the web.
"""

__project__ = "MPRISweb"
__authors__ = "sedrubal"
__email__ = "sebastian.endres@online.de",
__license__ = "GPLv3 & non military"
__url__ = "https://github.com/sedrubal/" + __project__.lower()


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
                    title=__project__,
                    description=__doc__,
                    author=__authors__,
                    license=__license__,
                    url=__url__,
                    authors_url='/'.join(__url__.split('/')[:-1]))


class MPRISWrapper(object):
    """a wrapper for mpris"""
    def __init__(self, arg):
        self.arg = arg
        self.current_title = "My wonderful track"
        self.next_title = "Next wonderful track"

    def get_current_title(self):
        """returns the title of the current track"""
        return self.current_title

    def get_next_title(self):
        """returns the title of the next track"""
        return self.next_title


class WebSocket(tornado.websocket.WebSocketHandler):
    """
    The websocket server part
    """
    def open(self):
        """when a client connects, add this socket to list"""
        APP.clients.append(self)
        self.send_status()
        print("WebSocket opened")

    def on_message(self, message):
        """new message received"""
        print("received: " + message)

    def send_status(self):
        """sends the current and next tracks to the client"""
        msg = {
            "current": APP.mpris_wrapper.get_current_title(),
            "next": APP.mpris_wrapper.get_next_title(),
        }
        self.write_message(json.dumps(msg), binary=False)
        print("send: {0}".format(msg))

    def on_close(self):
        """the client of this socket leaved, remove this socket from list"""
        APP.clients.remove(self)
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
    APP.mpris_wrapper = MPRISWrapper("TODO")
    APP.clients = []  # global list of all connected websocket clients
    tornado.ioloop.IOLoop.current().start()
