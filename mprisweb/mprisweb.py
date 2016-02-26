#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""
Control your musicplayer through the web.
"""

import __init__
import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
import magic
import base64
import re
from mpriswrapper import MPRISWrapper
from helpers import log, parse_args

APP = None


class StartPage(tornado.web.RequestHandler):
    """
    A normal webpage providing some html, css and js, which uses websockets
    """
    def get(self):
        """the handler for get requests"""
        self.render(
            "index.html",
            title=__init__.__project__,
            description=__init__.__doc__,
            author=__init__.__authors__,
            license=__init__.__license__,
            url=__init__.__url__,
            authors_url='/'.join(__init__.__url__.split('/')[:-1]),
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
        mpris_prop_change_handler()
        self.send_status()
        log("WebSocket opened. {0} child(s) connected".
            format(len(APP.clients)), min_verbosity=1)

    def on_message(self, message):
        """new message received"""
        try:
            msg = json.loads(message)
        except ValueError:
            log("Client sent an invalid message: {0}".format(message),
                error=True)
            return
        if 'action' not in msg:
            log("invalid message received from client: '{0}'".
                format(str(msg)),
                min_verbosity=2, error=True)
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
        elif msg['action'] == 'volume':
            if 'value' in msg.keys():
                try:
                    APP.mpris_wrapper.set_volume(float(msg['value']))
                except ValueError as err:
                    log(("Invalid value '{0}' for volume " +
                         "in message from client: {1}").
                        format(msg['value'], err.message),
                        min_verbosity=1, error=True)
            else:
                log("Missing value for action 'volume' in message from client",
                    min_verbosity=1, error=True)
        else:
            log("invalid action '{0}' received from client".
                format(msg['action']),
                min_verbosity=1, error=True)
        log("received: " + message, min_verbosity=2)

    def send_status(self):
        """sends the current and next tracks to the client"""
        self.write_message(json.dumps(APP.meta_status), binary=False)
        log("send: {0}".format(APP.meta_status), min_verbosity=3)

    def on_close(self):
        """the client of this socket leaved, remove this socket from list"""
        APP.clients.remove(self)
        log("WebSocket closed. {0} child(s) connected".
            format(len(APP.clients)), min_verbosity=1)

    def data_received(self, chunk):
        """override abstract method"""
        pass


def base64_encode_image(filename):
    """:return the base64 encoded image if filename was a image else None"""
    try:
        imgfile = open(filename, "rb")
        img = imgfile.read(1024)
    except IOError as err:
        log("Artwork '{0}' won't be displayed: {2}".
            format(filename, err.message), min_verbosity=1, error=True)
        return None
    mimetype = APP.magic.buffer(img).lower()
    mimere = re.compile(r'(?P<mimetype>image/(png|jpeg|jpg|bmp|gif)).*')
    mimes = mimere.findall(mimetype)
    if len(mimes) == 1:
        mimetype = mimes[0][0]
        img += imgfile.read()  # read remeaning file
        imgfile.close()
        imgstr = base64.encodestring(img)
        imgstr = imgstr.replace('\n', '')
        return "data:{mime};base64,{base64}".format(
            mime=mimetype, base64=imgstr)
    else:
        log("Artwork '{0}' rejected: invalid mimetype '{1}'".
            format(filename, mimetype), min_verbosity=1, error=True)
        imgfile.close()
        return None


def mpris_prop_change_handler(*args, **kw):
    """function will be executed on mpris player property changes"""
    meta = {
        "titles": {
            "current": APP.mpris_wrapper.get_current_title(),
            "next": APP.mpris_wrapper.get_next_title(),
        },
        "trackMetadata": APP.mpris_wrapper.get_current_metadata(),
        "status": APP.mpris_wrapper.get_playback_status(),
        "player": {
            "canControl": APP.mpris_wrapper.get_can_control(),
            "canGoNext": APP.mpris_wrapper.get_can_go_next(),
            "canGoPrevious": APP.mpris_wrapper.get_can_go_previous(),
            "canPlay": APP.mpris_wrapper.get_can_play(),
            "canPause": APP.mpris_wrapper.get_can_pause(),
        },
        "volume": APP.mpris_wrapper.get_volume(),
    }
    if 'trackMetadata' in meta.keys() and \
            'artUri' in meta['trackMetadata'].keys() and \
            meta['trackMetadata']['artUri']:
        arturi = meta['trackMetadata']['artUri']
        arturi = arturi.strip().replace("file://", '')
        if arturi and os.path.isfile(arturi):
            image = base64_encode_image(arturi)
            if image:
                meta['trackMetadata']['art'] = image
            else:
                log("Artwork '{0}' won't be displayed: could not open file".
                    format(arturi), min_verbosity=1, error=True)
        else:
            log("Artwork '{0}' won't be displayed: file not found".
                format(arturi), min_verbosity=3, error=True)
        del meta['trackMetadata']['artUri']
    else:
        log("Track has no Artwork", min_verbosity=4)

    APP.meta_status = meta
    for client in APP.clients:
        client.send_status()


SETTINGS = {
    "template_path": os.path.join(os.path.dirname(__file__), "../templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "../static"),
}


def make_app():
    """create a new application and specify the url patterns"""
    return tornado.web.Application([
        tornado.web.URLSpec(r"/websocket", WebSocket, name="websocket"),
        (r"/", StartPage),
        (r"/static/", tornado.web.StaticFileHandler,
         dict(path=SETTINGS['static_path'])),
    ], **SETTINGS)


def main():
    """the main function starts the server"""
    global APP
    APP = make_app()
    APP.args = parse_args()
    APP.clients = []  # global list of all connected websocket clients
    APP.mpris_wrapper = MPRISWrapper(mpris_prop_change_handler)
    log("Loading magic file for mimetypes. Please wait.", min_verbosity=1)
    APP.magic = magic.open(magic.MAGIC_MIME_TYPE)
    APP.magic.load()
    log("Loading finished.", min_verbosity=2)
    APP.listen(APP.args.port, address=APP.args.ip)
    log("App will listen on http://{ip}:{port}".format(
        ip=APP.args.ip, port=APP.args.port))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
