#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


from deploy.web.server.game_instance import (
    Player,
    PlayerProvider,
    GameInstance,
)

import argparse
import socket

DEFAULT_HOSTNAME = "localhost"
DEFAULT_PORT     = 35495


def send_to_connection(c, txt):
    txt = txt.rstrip('\n').lstrip(' ').lstrip('\n')
    if len(txt) > 0:
        txt += '\n'
        c[0].send(str.encode(txt))


class TelnetPlayer(Player):
    def __init__(self, graph, player_id, connection_details):
        self.c = connection_details
        self.text = ''
        self.alive = True
        super().__init__(graph, player_id)

    def act(self):
        """
        Pull an action stored from the last alive check
        """
        if self.text != '':
            agent_id = self.get_agent_id()
            print(agent_id + ":" + str(self.text))
            self.g.parse_exec(agent_id, self.text)
            self.text = ''

    def observe(self):
        """
        Send any observed content to the player.
        This method should query the graph for what it needs, and should
        clear the graph content when this happens.
        """
        agent_id = self.get_agent_id()        
        txt = self.g.get_text(agent_id)
        send_to_connection(self.c, txt)

    def init_observe(self):
        """
        Send any required initialization observations to the player. Will
        only be called the first time this player is initialized.
        """
        agent_id = self.get_agent_id()
        self.g.parse_exec(agent_id, 'look')
        self.observe()

    def is_alive(self):
        """
        As alive checks are called every tick, we both check liveliness and
        store the last action if one existed
        """
        try:
            data = self.c[0].recv(1024)
            if data!=b'':
                try:
                    self.text = data.decode()
                except UnicodeDecodeError:
                    self.text = ''
            else:
                # dead connection, unspawn the player
                self.alive = False
                print("[" + self.id + " has disconnected]")
        except BlockingIOError:
            pass

        return self.alive


class TelnetPlayerProvider(PlayerProvider):
    def __init__(self, graph, ip="127.0.0.1", port=35495):
        super().__init__(graph)
        self.ip = ip
        self.port = port
        self._setup_socket()

    def _setup_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.ip, self.port))
        print("Server socket bound with with ip {} port {}".format(
            self.ip, self.port
        ))
        server_socket.listen()
        server_socket.settimeout(0.0)
        self.server_socket = server_socket

    def get_new_players(self):
        """
        Should check the potential source of players for new players. If
        a player exists, this should instantiate a relevant Player object
        for each potential new player and return them.

        This particular implementation only checks for one player at a time
        """
        try:
            (clientConnection, clientAddress) = self.server_socket.accept()
            if clientConnection:
                player_id = self.g.spawn_player()
                c = (clientConnection, clientAddress, player_id)
                print("added a connection!: " + str(c))
                c[0].settimeout(0.0)
                if player_id == -1:
                    send_to_connection(c, "Sorry the game is full!")
                    return []
                new_player = TelnetPlayer(self.g, player_id, c)
                return [new_player]
        except BlockingIOError:
            pass
        return []

def main():
    import random
    import numpy

    parser = argparse.ArgumentParser(description='Start the telnet server.')
    parser.add_argument('--light-model-root', type=str,
                        default="/Users/jju/Desktop/LIGHT/",
                        help='models path. For local setup, use: /checkpoint/jase/projects/light/dialog/') 
    parser.add_argument('-port', metavar='port', type=int,
                        default=DEFAULT_PORT,
                        help='port to run the server on.')
    parser.add_argument('--hostname', metavar='hostname', type=str,
                        default=DEFAULT_HOSTNAME,
                        help='host to run the server on.')
    FLAGS = parser.parse_args()

    random.seed(6)
    numpy.random.seed(6)

    game = GameInstance()
    graph = game.g
    provider = TelnetPlayerProvider(graph, FLAGS.hostname, FLAGS.port)
    game.register_provider(provider)
    game.run_graph()


if __name__ == "__main__":
    main()
