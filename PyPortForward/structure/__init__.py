import PyPortForward as ppf

from pathlib import Path
from json import loads, dumps
import socket

import PyPortForward.types as _types

class BaseConfig():
    def __init__(self):
        self.name = None
        self.servers = {}
        self.clients = {}

    def setup(self, configPath: Path):
        if not configPath.exists():
            ppf.logger.error(f"Config file {configPath} not found!")
            exit(1)
        
        self._config = loads(configPath.read_text())
        
        if "name" not in self._config:
            ppf.logger.error(f"Config file {configPath} missing name")
            exit(1)
        self.name = self._config["name"]

        return self._config
    
    def chksetattr(self, key: str):
        if key not in self._config:
            ppf.logger.error(f"Config file {self.configPath} missing key {key}")
            exit(1)
        setattr(self, key, self._config[key])
        
class PortManager():
    def __init__(self):
        self.start = None
        self.end = None
        self.exclude = []
        self.allow = []
        self.multiallow = []
    
    def chksetattr(self, config: dict, key: str):
        if key not in config:
            ppf.logger.error(f"Config file {self.configPath} missing key {key}")
            exit(1)
        setattr(self, key, config[key])
    
    def canAllocate(self, port: int):
        if port in self.exclude:
            return False
        if port in self.multiallow:
            return True
        if port < self.start or port > self.end:
            return False
        
        return True
    
    def isUsing(self, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((self.config.host, port))
            sock.close()
            return False
        except OSError:
            sock.close()
            del(sock)
            return True
        
        


class ProxyConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        self.host = None
        self.masterport = None
        self.passwd = None
        self.dataport = None
        self.logfile = None

        self.ports = PortManager()

    def setup(self, configPath: Path):
        super().setup(configPath)

        for key in ppf.config.PROXY_DEFAULT_CONFIG:
            if key not in self._config:
                ppf.logger.error(f"Config file {self.configPath} missing key {key}")
                exit(1)

        self.chksetattr("host")
        self.chksetattr("masterport")
        self.chksetattr("dataport")
        self.chksetattr("passwd")
        self.chksetattr("logfile")

        self.ports.chksetattr(self._config["ports"], "start")
        self.ports.chksetattr(self._config["ports"], "end")
        self.ports.chksetattr(self._config["ports"], "exclude")
        self.ports.chksetattr(self._config["ports"], "allow")
        self.ports.chksetattr(self._config["ports"], "multiallow")









        


class ServerConfig():
    def __init__(self, configPath: Path):
        self.configPath = configPath

        self.srvid = None
        self.proxy = {}
        self.clients = {}

