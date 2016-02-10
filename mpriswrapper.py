"""
Wrapper for MPRIS
"""
from dbus.mainloop.glib import DBusGMainLoop
from mpris2 import get_players_uri
from mpris2 import Player


class MPRISWrapper(object):
    """a wrapper for MPRIS"""
    def __init__(self, properties_changed_handler):
        """
        :param properties_changed_handler: a function that will be executed on
        status changes like `def handler(self, *args, **kw)`
        """
        # DEBUG:
        self.next_title = "Next wonderful track"
        # initialize DBus:
        DBusGMainLoop(set_as_default=True)
        self.uri = next(get_players_uri())
        self.player = Player(dbus_interface_info={'dbus_uri': self.uri})
        self.player.PropertiesChanged = properties_changed_handler

    def get_current_title(self):
        """returns the title of the current track"""
        meta = self.player.Metadata
        return str(meta.get(meta.TITLE))

    def get_next_title(self):
        """returns the title of the next track"""
        return self.next_title

    def previous(self):
        """jump to previous track"""
        self.player.Previous()

    def play(self):
        """start playing"""
        self.player.Play()

    def stop(self):
        """stop playing"""
        self.player.Stop()

    def pause(self):
        """pause playing"""
        self.player.Pause()

    def next(self):
        """jump to the next track"""
        self.player.Next()
