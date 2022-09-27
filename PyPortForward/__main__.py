import sys
import click
import logging
import PyPortForward as ppf

__version__ = "1.0.0"

format = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=format)

@click.version_option(prog_name="PyPortForward", version=__version__)
@click.group()
def main():
    """
    A simple port forward client and manager written in Python
    """
    pass

@main.command("server")
@click.option("--host", default="0.0.0.0", type=str, help="The host to listen on")
@click.option("--port", default=5000, type=int, help="The port to listen on")
@click.option("--debug", default=False, type=bool, help="Enable debug mode")
def server(host, port, debug):
    ppf.commands.server(host, port, debug)

@main.command("client")
@click.option("--server-host", type=str, help="The host of the server")
@click.option("--server-port", type=int, help="The port of the server")
@click.option("--login", type=str, help="The login to the server")
def client(server_host, server_port, login):
    ppf.commands.client(server_host, server_port, login)

@main.command("forward")
@click.option("--listen-host", default="0.0.0.0", type=str, help="The host of the local server")
@click.option("--listen-port", type=int, help="The port of the local server", required=True)
@click.option("--connect-host", type=str, help="The host of the remote server", required=True)
@click.option("--connect-port", type=int, help="The port of the remote server", required=True)
@click.option("--debug", default=False, type=bool, help="Enable debug mode")
def forward(listen_host, listen_port, connect_host, connect_port, debug):
    ppf.commands.forward(listen_host, listen_port, connect_host, connect_port, debug)

if __name__ == "__main__":
    main()
