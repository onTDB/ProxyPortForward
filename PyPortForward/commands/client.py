import PyPortForward as ppf
import PyPortForward.commands.client as _client

from threading import Thread




def client():
    while True:
        a = ppf.commands.prompt(_client)
        print(a)
        try:
            args = a.split(" ")[1:]
            getattr(_client, a.split(" ")[0])(*args)
        except AttributeError as e:
            ppf.logger.error(f"Invalid command: {a}")
            raise e
            continue
        except TypeError as e:
            ppf.logger.error(str(e).split("()")[1])
            continue


def exit():
    ppf.session.running = False
    ppf.logger.info("Exiting...")
    ppf.session.proxyid = None
    exit(0)

def connect(serverip: str, serverport: int):
    pass
    
    
def port(mode: str, proxyid: str, port: int):
    a = ppf.commands.prompt(port)
    pass

def connection():
    if ppf.session.proxyid is None:
        ppf.logger.error(f"Please select a proxy first")
        return False
    
    if ppf.session.portid is None:
        ppf.logger.error(f"Please select a port first")
        return False
    
    if ppf.session.connid is None:
        ppf.logger.error(f"Please select a connection first")
        return False
    
    return True

