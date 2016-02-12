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
from mpriswrapper import MPRISWrapper
from helpers import log, set_verbosity


class StartPage(tornado.web.RequestHandler):
    """
    A normal webpage providing some html, css and js, which uses websockets
    """
    def get(self):
        """the handler for get requests"""
        self.render(
            "index.html",
            title=__project__,
            description=__doc__,
            author=__authors__,
            license=__license__,
            url=__url__,
            authors_url='/'.join(__url__.split('/')[:-1]),
        )

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
            "titles": {
                "current": APP.mpris_wrapper.get_current_title(),
                "next": APP.mpris_wrapper.get_next_title(),
            },
            "status": APP.mpris_wrapper.get_playback_status(),
            "player": {
                "canControl": APP.mpris_wrapper.get_can_control(),
                "canGoNext": APP.mpris_wrapper.get_can_go_next(),
                "canGoPrevious": APP.mpris_wrapper.get_can_go_previous(),
                "canPlay": APP.mpris_wrapper.get_can_play(),
                "canPause": APP.mpris_wrapper.get_can_pause(),
            },
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


def mpris_prop_change_handler(*args, **kw):
    """function will be executed on mpris player property changes"""
    log("MPRIS status changed: {0} {1}".format(args, kw), min_verbosity=1)
    for client in APP.clients:
        client.send_status()


SETTINGS = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}


def make_app():
    """create a new application and specify the url patterns"""
    return tornado.web.Application([
        tornado.web.URLSpec(r"/websocket", WebSocket, name="websocket"),
        (r"/", StartPage),
        (r"/static/", tornado.web.StaticFileHandler,
         dict(path=SETTINGS['static_path'])),
    ], **SETTINGS)

if __name__ == "__main__":
    APP = make_app()
    set_verbosity(5)  # TODO argparse
    APP.clients = []  # global list of all connected websocket clients
    APP.mpris_wrapper = MPRISWrapper(mpris_prop_change_handler)
    APP.listen(8888)
    tornado.ioloop.IOLoop.current().start()
