
'''
 +---------------------------------+     +-----------------------------+        +--------------------------------+    +--------------------------------+
 |             Client              |     |        Proxy Server         |        |           Home Server          |    |    Internal Server (Carol)     |
 +---------------------------------+     +--------------+--------------+ TUNNEL +----------------+---------------+    +--------------------------------+
 | $ ssh -p 1022 user@1.2.3.4:1234 |<--->|         1.2.3.4:5000        |<------>| IF 1: 5.6.7.8 | IF 2: 10.0.0.1 |<-->|       IF 1: 10.0.0.2           |
 | user@1.2.3.4's password:        |     +--------------+--------------+        +----------------+---------------+    +--------------------------------+
 | user@hostname:~$ whoami         |     | $ python ppf.py --server    |        | $ python ppf.py --client       |    | 192.168.1.2:22(OpenSSH Server) |
 | user                            |     |                 --port 5000 |        |      --server-ip 1.2.3.4:5000  |    +--------------------------------+
 +---------------------------------+     +--------------+--------------+        +----------------+---------------+
'''

import click
import logging
import pathlib

import PyPortForward as ppf

__version__ = "1.0.0-pre2"

@click.version_option(prog_name="PyPortForward", version=__version__)
@click.group()
def main():
    """
    A port forward client and manager written in Python
    """
    pass

@main.command("server")
@click.option("--host", default="0.0.0.0", type=str, help="The host to listen on")
@click.option("--port", default=5000, type=int, help="The port to listen manage commands")
@click.option("--sock-port", default=5001, type=int, help="The port to listen on for socket connections")
@click.option("--debug", default=False, type=bool, help="Enable debug mode")
@click.option("--logfile", type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Log file", default="ppf.log")
def server(host, port, sock_port, debug, logfile):
    logging.getLogger("PyPortForward").setLevel(logging.DEBUG if debug else logging.INFO)
    ppf.commands.server(host, port, sock_port)

@main.command("client")
@click.option("--server-host", type=str, help="The host of the server", required=True)
@click.option("--server-port", type=int, help="The port of the server", required=True)
@click.option("--login", type=str, help="The login to the server")
@click.option("--logfile", type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Log file", default="ppf.log")
def client(server_host, server_port, login, logfile):
    ppf.commands.client(server_host, server_port, login)

@main.command("forward")
@click.option("--listen-host", default="0.0.0.0", type=str, help="The host of the local server")
@click.option("--listen-port", type=int, help="The port of the local server", required=True)
@click.option("--connect-host", type=str, help="The host of the remote server", required=True)
@click.option("--connect-port", type=int, help="The port of the remote server", required=True)
@click.option("--debug", default=False, type=bool, help="Enable debug mode")
@click.option("--show-data", default=False, type=bool, help="Show data being sent")
@click.option("--logfile", type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Log file", default="ppf.log")
def forward(listen_host, listen_port, connect_host, connect_port, debug, show_data, logfile):
    logging.getLogger("PyPortForward").setLevel(logging.DEBUG if debug else logging.INFO)
    logging.getLogger("PyPortForward").addHandler(logging.FileHandler(logfile))
    logging.getLogger("PyPortForward").handlers[1].setFormatter(logging.Formatter("%(levelname)s - [%(asctime)s] [%(filename)s:%(lineno)d] # %(message)s"))
    logging.getLogger("PyPortForward").handlers[1].setLevel(logging.DEBUG)
    ppf.commands.forward(listen_host, listen_port, connect_host, connect_port, show_data)

if __name__ == "__main__":
    main()
