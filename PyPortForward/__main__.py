'''
 +---------------------------------+     +----------------------------+        +----------------------------------+    +--------------------------------+
 |             Client              |     |        Proxy Server        | (SOCK) |           Home Server            |    |    Internal Server (Carol)     |
 +---------------------------------+     +--------------+-------------+ TUNNEL +----------------+-----------------+    +--------------------------------+
 | $ ssh -p 1022 user@1.2.3.4:1234 |<--->|         1.2.3.4:5000       |<------>| IF 1: 5.6.7.8 | IF 2: 10.0.0.1   |<-->|       IF 1: 10.0.0.2           |
 | user@1.2.3.4's password:        |     +--------------+-------------+        +----------------+-----------------+    +--------------------------------+
 | user@hostname:~$ whoami         |     | $ pff server --port 5000   |        | $ pff client                     |    | 192.168.1.2:22(OpenSSH Server) |
 | user                            |     +--------------+-------------+        +----------------+-----------------+    +--------------------------------+
 +---------------------------------+             
'''

import click
import pathlib

import PyPortForward as ppf

__version__ = "1.0.0-pre2"
ppf.__version__ = __version__

@click.version_option(prog_name="PyPortForward", version=__version__)
@click.group()
def main():
    """
    A port forward client and manager written in Python
    """
    pass

@main.command("server")
@click.option("--host",    default="0.0.0.0", type=str,   help="The host to listen on")
@click.option("--port",    default=5000,      type=int,   help="The port to listen proxy connections on")
@click.option("--debug",   default=False,     type=bool,  help="Enable debug mode", is_flag=True)
@click.option("--logfile", default=None,        type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Log file")
def server(host, port, debug, logfile):
    ppf.config.loggersetup(debug, logfile)
    ppf.commands.server(host, port)

@main.command("client")
@click.option("--debug",      default=False,  type=bool,   help="Enable debug mode", is_flag=True)
@click.option("--logfile",    default=None,     type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Log file")
def client(debug, logfile):
    ppf.config.loggersetup(debug, logfile)
    ppf.commands.client()


@main.command("forward")
@click.option("--listen-host", default="0.0.0.0", type=str, help="The host of the local server")
@click.option("--listen-port", type=int, help="The port of the local server", required=True)
@click.option("--connect-host", type=str, help="The host of the remote server", required=True)
@click.option("--connect-port", type=int, help="The port of the remote server", required=True)
@click.option("--debug", default=False, type=bool, help="Enable debug mode", is_flag=True)
@click.option("--show-data", default=False, type=bool, help="Show data being sent", is_flag=True)
@click.option("--logfile", type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Log file", default="")
def forward(listen_host, listen_port, connect_host, connect_port, debug, show_data, logfile):
    ppf.config.loggersetup(debug, logfile)
    ppf.commands.forward(listen_host, listen_port, connect_host, connect_port, show_data)

if __name__ == "__main__":
    main()
