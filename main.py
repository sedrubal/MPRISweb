#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Control your musicplayer through the web.
"""

from __future__ import print_function

__project__ = "MPRISweb"
__authors__ = "sedrubal"
__email__ = "sebastian.endres@online.de",
__license__ = "GPLv3 & non military"
__url__ = "https://github.com/sedrubal/" + __project__.lower()

import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import sys
import json
from mpriswrapper import MPRISWrapper


def log(msg, min_verbosity=0, error=False):
    """log to stdout, if verbosity >= min_verbosity"""
    if APP.verbosity >= min_verbosity:
        print(
            ('[!] {0}' if error else '[i] {0}').format(msg),
            file=sys.stderr if error else sys.stdout
        )


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

    def data_received(self, chunk):
        """override abstract method"""
        pass


class WebSocket(tornado.websocket.WebSocketHandler):
    """
    The websocket server part
    """
    def open(self):
        """when a client connects, add this socket to list"""
        APP.clients.append(self)
        self.send_status()
        log("WebSocket opened", min_verbosity=1)

    def on_message(self, message):
        """new message received"""
        try:
            msg = json.loads(message)
        except ValueError:
            log("Client sent an invalid message: {0}".format(message),
                error=True)
            return
        if not msg['action']:
            return
        elif msg['action'] == 'backward':
            APP.mpris_wrapper.previous()
        elif msg['action'] == 'play':
            APP.mpris_wrapper.play()
        elif msg['action'] == 'pause':
            APP.mpris_wrapper.pause()
        elif msg['action'] == 'stop':
            APP.mpris_wrapper.stop()
        elif msg['action'] == 'forward':
            APP.mpris_wrapper.next()
        else:
            log("invalid action '{0}' received by client".
                format(msg['action']),
                error=True)
        log("received: " + message, min_verbosity=1)

    def send_status(self):
        """sends the current and next tracks to the client"""
        msg = {
            "current": APP.mpris_wrapper.get_current_title(),
            "next": APP.mpris_wrapper.get_next_title(),
        }
        self.write_message(json.dumps(msg), binary=False)
        log("send: {0}".format(msg), min_verbosity=1)

    def on_close(self):
        """the client of this socket leaved, remove this socket from list"""
        APP.clients.remove(self)
        log("WebSocket closed", min_verbosity=1)

    def data_received(self, chunk):
        """override abstract method"""
        pass


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
    APP.verbosity = 5  # TODO argparse
    tornado.ioloop.IOLoop.current().start()
