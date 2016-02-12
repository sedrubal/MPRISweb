"""
Wrapper for MPRIS
"""
from dbus.mainloop.glib import DBusGMainLoop
import gi.repository.GLib
import mpris2
import signal
import thread
from helpers import log


class MPRISWrapper(object):
    """a wrapper for MPRIS"""
    def __init__(self, prop_changed_handler):
        """
        :param properties_changed_handler: a function that will be executed on
        status changes like `def handler(self, *args, **kw)`
        """
        # DEBUG:
        self.next_title = "Next wonderful track"
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

    def get_current_title(self):
        """returns the title of the current track"""
        meta = self.player.Metadata
        return str(meta.get(meta.TITLE))

    def get_next_title(self):
        """returns the title of the next track"""
        return self.next_title

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
