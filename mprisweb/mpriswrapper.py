"""
Wrapper for MPRIS
"""

from __future__ import unicode_literals
from __future__ import absolute_import

from dbus.mainloop.glib import DBusGMainLoop
import gi.repository.GLib
import mpris2
import signal
import time
import dbus
try:
    import thread  # TODO use threading
except ImportError:
    import _thread as thread
from mprisweb.helpers import log


class MPRISWrapper(object):
    """a wrapper for MPRIS"""
    def __init__(self, prop_changed_handler):
        """
        :param properties_changed_handler: a function that will be executed on
        status changes like `def handler(self, *args, **kw)`
        """
        # initialize DBus:
        DBusGMainLoop(set_as_default=True)
        self.prop_changed_handler = prop_changed_handler
        self.try_connect()
        if not self.player:
            log("No MPRIS player available. " +
                "Please start your favourite music player with MPRIS support.",
                min_verbosity=0, error=True)
        self.mloop = gi.repository.GLib.MainLoop()
        thread.start_new_thread(self.glib_loop_thread, ())
        thread.start_new_thread(self.check_connection_thread, ())
        signal.signal(signal.SIGINT, self.sigint_handler)

    def sigint_handler(self, sig, frame):
        """Stop on sigint (Ctrl+C)"""
        log("Signal {0} in frame {1} caught".format(sig, frame),
            min_verbosity=1)
        self.mloop.quit()
        exit(0)

    def glib_loop_thread(self):
        """
        runs the GLib main loop to get notified about player status changes
        """
        self.mloop.run()
        log("GLib loop exited", min_verbosity=2)
        thread.exit_thread()

    def check_connection_thread(self):
        """
        checks if the currently connected player is connected and
        tries to reconnect if not
        """
        while True:
            time.sleep(5)
            try:
                self.player.CanControl
                # -> AttributeError when None
                # -> DBusException when not connected anymore
                # I found no other method to test this
                # -> better sorry than safe
                log("Player is still connected", min_verbosity=5)
            # except AttributeError, dbus.exceptions.DBusException:
            except (AttributeError, dbus.exceptions.DBusException):
                log("Player is NOT connected", min_verbosity=5)
                self.try_connect()
                self.prop_changed_handler()

    def try_connect(self):
        """
        Sets self.player to a player and sets the prop_changed_handler
        if there is a mpris player on dbus or sets self.player to None
        """
        log("Try to connect to player", min_verbosity=4)
        uris = list(mpris2.get_players_uri())
        if len(uris):
            self.player = mpris2.Player(dbus_interface_info={
                'dbus_uri': uris[0]  # connects to the first player
            })
            self.player.PropertiesChanged = self.prop_changed_handler
            log("Connected to player", min_verbosity=4)
        else:
            log("Can't connect. No MPRIS player available",
                min_verbosity=4, error=True)
            self.player = None

    def _get_player(self):
        """:return current player or None if no player is connected"""
        if self.player is None:
            return None
        try:
            self.player.CanControl
            # I found no other method to test, if connected
            # -> better sorry than safe
            return self.player
        except dbus.exceptions.DBusException:
            return None

    @staticmethod
    def _convert(value):
        """
        convert MPRIS datatypes to python types
        :reference https://dbus.freedesktop.org/doc/dbus-python/doc/tutorial.html#basic-types
        """
        if isinstance(value, dbus.Boolean):
            return bool(value)
        elif isinstance(value, dbus.Byte) or \
                isinstance(value, dbus.UInt16) or \
                isinstance(value, dbus.UInt32) or \
                isinstance(value, dbus.Int16) or \
                isinstance(value, dbus.Int32) or \
                isinstance(value, dbus.Int64):
            return int(value)
        elif isinstance(value, dbus.UInt64):
            return int(value)
        elif isinstance(value, dbus.Double):
            return float(value)
        elif isinstance(value, dbus.String) or \
                isinstance(value, dbus.ObjectPath) or \
                isinstance(value, dbus.Signature):
            return str(value.encode('utf-8').decode('utf-8'))
        if isinstance(value, dbus.String):
            return str(value.encode('utf-8').decode('utf-8'))
        elif isinstance(value, dbus.Array):
            return [MPRISWrapper._convert(v) for v in value]
        elif value is None or \
                isinstance(value, bool) or \
                isinstance(value, int) or \
                isinstance(value, float) or \
                isinstance(value, str):
            return value
        else:
            raise TypeError("Unknown type '{}'".format(value))

    def get_current_metadata(self):
        """returns the metadata of the current track"""
        if self._get_player() is None:
            return {}
        mprismeta = self._get_player().Metadata

        def get(prop):
            """wrapper function to get properties"""
            return MPRISWrapper._convert(mprismeta.get(prop))
        meta = {
            'album': get(mprismeta.ALBUM),
            'albumArtist': get(mprismeta.ALBUM_ARTIST),
            'artist': get(mprismeta.ARTIST),
            'artUri': get(mprismeta.ART_URI),
            'asText': get(mprismeta.AS_TEXT),
            'audioBpm': get(mprismeta.AUDIO_BPM),
            'autoRating': get(mprismeta.AUTO_RATING),
            'comment': get(mprismeta.COMMENT),
            'composer': get(mprismeta.COMPOSER),
            'contentCreated ': get(mprismeta.CONTENT_CREATED),
            'discNumber': get(mprismeta.DISC_NUMBER),
            'firstUsed': get(mprismeta.FIRST_USED),
            'genre': get(mprismeta.GENRE),
            'lastUsed': get(mprismeta.LAST_USED),
            'length': get(mprismeta.LENGTH),
            'lyricist': get(mprismeta.LYRICIST),
            'title': get(mprismeta.TITLE),
            'trackid': get(mprismeta.TRACKID),
            'trackNumber': get(mprismeta.TRACK_NUMBER),
            'url': get(mprismeta.URL),
            'userRating': get(mprismeta.USER_RATING),
            'useCount': get(mprismeta.USE_COUNT),
        }
        return meta

    def get_current_title(self):
        """returns the title of the current track"""
        metadata = self.get_current_metadata()
        if 'title' in metadata.keys():
            return self.get_current_metadata()['title']
        else:
            return ''

    def get_next_title(self):
        """returns the title of the next track"""
        return None  # TODO

    def get_playback_status(self):
        """
        :return a string representing the current player status:
            (playing|pause|stopped)
        """
        if self._get_player() is None:
            return 'stopped'
        return str(self._get_player().PlaybackStatus).lower()

    def get_can_control(self):
        """
        :return if there is a player that allows to be controled via MPRIS
        """
        if self._get_player() is None:
            return False
        return bool(self._get_player().CanControl)

    def get_can_go_next(self):
        """
        :return if there is a player allows to go to next track via MPRIS
        """
        return self.get_can_control() and bool(self._get_player().CanGoNext)

    def get_can_go_previous(self):
        """
        :return if there is a player allows to go to previous track via MPRIS
        """
        return self.get_can_control() and \
            bool(self._get_player().CanGoPrevious)

    def get_can_play(self):
        """
        :return if there is a player that allows to start playing via MPRIS
        """
        return self.get_can_control() and bool(self._get_player().CanPlay)

    def get_can_pause(self):
        """
        :return if there is a player that allows to pausing via MPRIS
        """
        return self.get_can_control() and bool(self._get_player().CanPause)

    def get_volume(self):
        """:return the current players volume"""
        if self._get_player() is None:
            return 0
        return MPRISWrapper._convert(self._get_player().Volume)

    def set_volume(self, value):
        """:param value float"""
        if self.get_can_control():
            self._get_player().Volume = dbus.Double(value)

    def previous(self):
        """jump to previous track"""
        if self.get_can_go_previous():
            self._get_player().Previous()

    def play(self):
        """start playing"""
        if self.get_can_play():
            self._get_player().Play()

    def stop(self):
        """stop playing"""
        if self.get_can_control():
            self._get_player().Stop()

    def pause(self):
        """pause playing"""
        if self.get_can_pause():
            self._get_player().Pause()

    def next(self):
        """jump to the next track"""
        if self.get_can_go_next():
            self._get_player().Next()
