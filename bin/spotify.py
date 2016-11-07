#!/usr/bin/env python3

import sys
import logging
from subprocess import run, PIPE
from argparse import ArgumentParser


class SpotifyControl(object):

    def __init__(self, app='Spotify', osascript_path='/usr/bin/osascript'):
        self.app = app
        self.osascript_path = osascript_path

    def osascript(self, script):
        logging.debug('Running `{}`.'.format(script))

        process = run([self.osascript_path, '-e', script],
                      stdout=PIPE)
        return process.stdout.decode('utf-8').strip()

    def spotify(self, arg):
        script = 'tell application "{0}" to {1} as string'
        return self.osascript(script.format(self.app, arg))

    def is_running(self):
        command = 'application "{0}" is running'
        output = self.osascript(command.format(self.app))

        if output == 'true':
            return True
        else:
            return False

    def play_track(self, uri):
        return self.spotify('play track "{0}"'.format(uri))

    def state(self):
        return self.spotify('player state')

    def current_track(self):
        data = {}
        data['artist'] = self.spotify('artist of current track')
        data['album'] = self.spotify('album of current track')
        data['name'] = self.spotify('name of current track')
        data['spotify_url'] = self.spotify('spotify url of current track')
        data['artwork_url'] = self.spotify('artwork url of current track')
        return data

    def command_on(self):
        if self.is_running():
            print('Spotify is already on.')
        else:
            self.spotify('activate')

    def command_off(self):
        if not self.is_running():
            print('Spotify is already off.')
        else:
            self.spotify('quit')

    def command_state(self):
        if self.is_running():
            print('{}'.format(self.state()))
        else:
            print('Spotify is not running.')

    def command_current(self):
        if self.is_running():
            print('{name} / {artist}'.format(**self.current_track()))
        else:
            print('Spotify is not running.')

    def command_play(self):
        if self.is_running():
            self.spotify('play')
            self.command_current()
        else:
            print('Spotify is not running.')

    def command_pause(self):
        if self.is_running():
            self.spotify('pause')
        else:
            print('Spotify is not running.')

    def command_toggle(self):
        if self.is_running():
            self.spotify('playpause')
            if self.state() == 'paused':
                self.command_state()
            elif self.state() == 'playing':
                self.command_current()
        else:
            print('Spotify is not running.')

    def command_next(self):
        if self.is_running():
            self.spotify('next track')
            self.command_current()
        else:
            print('Spotify is not running.')

    def command_prev(self):
        if self.is_running():
            self.spotify('previous track')
            self.command_current()
        else:
            print('Spotify is not running.')


def main():
    spotify = SpotifyControl()

    parser = ArgumentParser()

    subparsers = parser.add_subparsers(title='commands')

    on_parser = subparsers.add_parser('on', help='Open the Spotify '
                                                 'application.')
    on_parser.set_defaults(func=spotify.command_on)

    off_parser = subparsers.add_parser('off', help='Close the Sptoify '
                                                   'application.')
    off_parser.set_defaults(func=spotify.command_off)

    state_parser = subparsers.add_parser('state', help='Return the current '
                                                       'state of the Spotify '
                                                       'player.')
    state_parser.set_defaults(func=spotify.command_state)

    play_parser = subparsers.add_parser('play', help='Play the music.')
    play_parser.set_defaults(func=spotify.command_play)

    pause_parser = subparsers.add_parser('pause', help='Pasue the music.')
    pause_parser.set_defaults(func=spotify.command_pause)

    toggle_parser = subparsers.add_parser('toggle', help='Play/Pause the '
                                                         'music.')
    toggle_parser.set_defaults(func=spotify.command_toggle)

    next_parser = subparsers.add_parser('next')
    next_parser.set_defaults(func=spotify.command_next)

    previous_parser = subparsers.add_parser('previous')
    previous_parser.set_defaults(func=spotify.command_prev)

    current_parser = subparsers.add_parser('current', help='Get the current '
                                                           'song playing.')
    current_parser.set_defaults(func=spotify.command_current)

    args = parser.parse_args()
    args.func()


if __name__ == '__main__':
    main()
