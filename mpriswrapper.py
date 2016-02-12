"""
Wrapper for MPRIS
"""
from dbus.mainloop.glib import DBusGMainLoop
import gi.repository.GLib
import mpris2
import signal
import thread
from helpers import log
import dbus


class MPRISWrapper(object):
    """a wrapper for MPRIS"""
    def __init__(self, prop_changed_handler):
        """
        :param properties_changed_handler: a function that will be executed on
        status changes like `def handler(self, *args, **kw)`
        """
        # initialize DBus:
        DBusGMainLoop(set_as_default=True)
        self.uri = next(mpris2.get_players_uri())
        self.player = mpris2.Player(dbus_interface_info={'dbus_uri': self.uri})
        self.player.PropertiesChanged = prop_changed_handler
        self.mloop = gi.repository.GLib.MainLoop()
        thread.start_new_thread(self.loop_thread, ())
        signal.signal(signal.SIGINT, self.sigint_handler)

    def sigint_handler(self, sig, frame):
        """Stop on sigint (Ctrl+C)"""
        log("Signal {0} in frame {1} caught".format(sig, frame),
            min_verbosity=1)
        self.mloop.quit()
        exit(0)

    def loop_thread(self):
        """
        runs the GLib main loop to get notified about player status changes
        """
        self.mloop.run()
        log("GLib loop exited", min_verbosity=2)
        thread.exit_thread()

    @staticmethod
    def _convert(value):
        """convert MPRIS datatypes to python types"""
        if isinstance(value, dbus.String):
            return str(value)
        elif isinstance(value, dbus.ObjectPath):
            return str(value)
        elif isinstance(value, dbus.Int32):
            return int(value)
        elif isinstance(value, dbus.Int64):
            return int(value)  # int is great enough I think
        elif isinstance(value, dbus.Double):
            return float(value)
        elif isinstance(value, dbus.Array):
            return [MPRISWrapper._convert(v) for v in value]

    def get_current_metadata(self):
        """returns the metadata of the current track"""
        mprismeta = self.player.Metadata
        get = lambda x: MPRISWrapper._convert(mprismeta.get(x))
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
        return self.get_current_metadata()['title']

    def get_next_title(self):
        """returns the title of the next track"""
        return None  # TODO

    def get_playback_status(self):
        """
        :return a string representing the current player status:
            (playing|pause|stopped)
        """
        return str(self.player.PlaybackStatus).lower()

    def get_can_control(self):
        """
        :return if there is a player that allows to be controled via MPRIS
        """
        return bool(self.player.CanControl)

    def get_can_go_next(self):
        """
        :return if there is a player allows to go to next track via MPRIS
        """
        return bool(self.player.CanGoNext) and self.get_can_control()

    def get_can_go_previous(self):
        """
        :return if there is a player allows to go to previous track via MPRIS
        """
        return bool(self.player.CanGoPrevious) and self.get_can_control()

    def get_can_play(self):
        """
        :return if there is a player that allows to start playing via MPRIS
        """
        return bool(self.player.CanPlay) and self.get_can_control()

    def get_can_pause(self):
        """
        :return if there is a player that allows to pausing via MPRIS
        """
        return bool(self.player.CanPause) and self.get_can_control()

    def previous(self):
        """jump to previous track"""
        if self.get_can_go_previous():
            self.player.Previous()

    def play(self):
        """start playing"""
        if self.get_can_play():
            self.player.Play()

    def stop(self):
        """stop playing"""
        self.player.Stop()

    def pause(self):
        """pause playing"""
        if self.get_can_pause():
            self.player.Pause()

    def next(self):
        """jump to the next track"""
        if self.get_can_go_next():
            self.player.Next()
