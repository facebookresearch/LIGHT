# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import socket

DEFAULT_HOSTNAME = "localhost"
DEFAULT_PORT = 35497


def send_to_connection(c, txt):
    txt = txt.rstrip("\n").lstrip(" ").lstrip("\n")
    if len(txt) > 0:
        txt += "\n"
        c[0].send(str.encode(txt))


class TelnetClient:
    def __init__(self, model, client_id, connection_details):
        self.model = model
        self.c = connection_details
        self.text = ""
        self.alive = True
        self.client_id = client_id

    def act(self):
        """
        Pull an action stored from the last alive check
        """
        if self.text != "":
            agent_id = str(self.client_id)
            print(agent_id + ":" + str(self.text))
            # self.model.parse_exec(agent_id, self.text)
            self.observe()
            self.text = ""

    def observe(self):
        """
        Send any observed content to the client.
        This method should query the graph for what it needs, and should
        clear the graph content when this happens.
        """
        agent_id = self.client_id
        txt = "blah!"
        send_to_connection(self.c, txt)

    def is_alive(self):
        """
        As alive checks are called every tick, we both check liveliness and
        store the last action if one existed
        """
        # import pdb; pdb.set_trace()
        try:
            data = self.c[0].recv(1024)
            if data != b"":
                try:
                    self.text = data.decode()
                    print(self.text)
                except UnicodeDecodeError:
                    self.text = ""
            else:
                # dead connection, unspawn the client
                self.alive = False
                print("[" + str(self.client_id) + " has disconnected]")
        except BlockingIOError:
            pass

        return self.alive


class TelnetClientProvider:
    def __init__(self, model, ip="127.0.0.1", port=35496):
        self.ip = ip
        self.port = port
        self._setup_socket()
        self._cnt = 0
        self.model = model

    def _setup_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.ip, self.port))
        print("Server socket bound with with ip {} port {}".format(self.ip, self.port))
        server_socket.listen()
        server_socket.settimeout(0.0)
        self.server_socket = server_socket

    def get_new_clients(self):
        """
        Should check the potential source of clients for new clients. If
        a client exists, this should instantiate a relevant Client object
        for each potential new client and return them.

        This particular implementation only checks for one client at a time
        """
        try:
            (clientConnection, clientAddress) = self.server_socket.accept()
            if clientConnection:
                self._cnt += 1
                client_id = self._cnt
                c = (clientConnection, clientAddress, client_id)
                print("added a connection to model server!: " + str(c))
                c[0].settimeout(0.0)
                if client_id == -1:
                    send_to_connection(c, "Sorry the model server is full!")
                    return []
                new_client = TelnetClient(self.model, client_id, c)
                return [new_client]
        except BlockingIOError:
            pass
        return []


def main():
    import random
    import numpy

    parser = argparse.ArgumentParser(description="Start the telnet server.")
    parser.add_argument(
        "--light-model-root",
        type=str,
        default="/Users/jju/Desktop/LIGHT/",
        help="models path. For local setup, use: /checkpoint/jase/projects/light/dialog/",
    )
    parser.add_argument(
        "-port",
        metavar="port",
        type=int,
        default=DEFAULT_PORT,
        help="port to run the server on.",
    )
    parser.add_argument(
        "--hostname",
        metavar="hostname",
        type=str,
        default=DEFAULT_HOSTNAME,
        help="host to run the server on.",
    )
    FLAGS = parser.parse_args()

    random.seed(6)
    numpy.random.seed(6)
    model = []

    provider = TelnetClientProvider(model, FLAGS.hostname, FLAGS.port)
    clients = []
    while True:
        # try to get new clients
        clients += provider.get_new_clients()

        # Clear disconnected clients
        left_clients = [p for p in clients if not p.is_alive()]
        for client in left_clients:
            clients.remove(client)

        # Check existing clients
        for client in clients:
            # import pdb; pdb.set_trace()
            act = client.act()


if __name__ == "__main__":
    main()
