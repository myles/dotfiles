#!/usr/bin/env python3

from subprocess import run, PIPE
from argparse import ArgumentParser, REMAINDER


class SpotifyControl(object):

    def __init__(self, app='Spotify', osascript_path='/usr/bin/osascript'):
        self.app = app
        self.osascript_path = osascript_path

    def osascript(self, script):
        """
        This is a bridge between Python adn AppleScript using the command line
        application `osascript`.
        """
        process = run([self.osascript_path, '-e', script],
                      stdout=PIPE)
        return process.stdout.decode('utf-8').strip()

    def spotify(self, arg):
        """
        This is so I don't have to repeat a bunch of code.
        """
        script = 'tell application "{0}" to {1} as string'
        return self.osascript(script.format(self.app, arg))

    def is_running(self):
        """
        Check to see if Spotify is currently running.
        """
        command = 'application "{0}" is running'
        output = self.osascript(command.format(self.app))

        if output == 'true':
            return True
        else:
            return False

    def activate(self):
        """
        Start the Spotify application.
        """
        return self.spotify('activate')

    def quit(self):
        """
        Quit the Spotify application.
        """
        return self.spotify('quit')

    def player_state(self):
        """
        Check to see the player state.
        """
        return self.spotify('player state')

    def play(self):
        """
        Start playing music.
        """
        return self.spotify('play')

    def pause(self):
        """
        Pause the music.
        """
        return self.spotify('pause')

    def playpause(self):
        """
        Toggle play/pause.
        """
        return self.spotify('playpause')

    def next_track(self):
        """
        Play the next track.
        """
        return self.spotify('next track')

    def previous_track(self):
        """
        Play the previous track.
        """
        return self.spotify('previous track')

    def play_track(self, uri):
        """
        Start playback of a track in the given context.
        """
        return self.spotify('play track "{0}"'.format(uri))

    def current_track(self):
        """
        Get some meta data from the currently playing track.
        """
        data = {}
        data['artist'] = self.spotify('artist of current track')
        data['album'] = self.spotify('album of current track')
        data['name'] = self.spotify('name of current track')
        data['spotify_url'] = self.spotify('spotify url of current track')
        data['artwork_url'] = self.spotify('artwork url of current track')
        return data


def main():
    parser = ArgumentParser()
    parser.add_argument('command', nargs=REMAINDER)
    args = parser.parse_args()

    s = SpotifyControl()

    if 'on' in args.command:
        if not s.is_running():
            s.activate()
        else:
            print('Spotify is already running.')

    if 'off' in args.command:
        if s.is_running():
            s.quit()
        else:
            print('Sptoify is already not running.')

    if 'state' in args.command:
        print('Sptoify is in the state of "{}".'.format(s.player_state()))

    if 'play' in args.command:
        s.play()

    if 'pause' in args.command:
        s.pause()

    if 'toggle' in args.command:
        s.playpause()

    if 'next' in args.command:
        s.next_track()
        print('Playing: {name} by {artist}'.format(**s.current_track()))

    if 'previous' in args.command:
        s.previous_track()
        print('Playing: {name} by {artist}'.format(**s.current_track()))

    if 'current' in args.command:
        print('Playing: {name} by {artist}'.format(**s.current_track()))


if __name__ == '__main__':
    main()
