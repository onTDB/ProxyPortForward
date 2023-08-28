import PyPortForward as ppf
from pathlib import Path
from json import loads
import logging

PROXY_DEFAULT_CONFIG = {
    "host": "proxy.example.com",
    "masterport": 5000,
    "debug": False,
    "logfile": "",
    "pass": "ANYPASSWORD",
    "ports": {
        "start": 10000,
        "end": 50000,
        "exclude": [25565],
        "allow": [80],
    }
}

SERVER_DEFAULT_CONFIG = {
    "proxy": [
        {
            "proxyid": "proxy1",
            "host": "proxy.example.com",
            "port": 5000,
            "pass": "ANYPASSWORD",
            "ports": [
                {
                    "host": "1.2.3.4",
                    "port": 80,
                    "proxyport": 8080,
                    "secure": False,
                },
                {
                    "host": "127.0.0.1",
                    "port": 22,
                    "proxyport": 2222,
                    "secure": True,
                }
            ]
        }
    ]
}

def load_config(configPath: Path):
    if not configPath.exists():
        ppf.logger.error(f"Config file {configPath} not found")
        exit(1)
    config = loads(configPath.read_text())
    for key in PROXY_DEFAULT_CONFIG:
        if key not in config:
            ppf.logger.error(f"Config file {configPath} missing key {key}")
            exit(1)
    
    if config["host"] == "":
        ppf.logger.error(f"Config file {configPath} missing host")
        exit(1)
    elif config["port"] < 1 or config["port"] > 65535:
        ppf.logger.error(f"Config file {configPath} missing port")
        exit(1)
    elif config["mode"] not in ["sock", "ws", "wss"]:
        ppf.logger.error(f"Config file {configPath} missing mode")
        exit(1)
    elif config["pass"] == "":
        ppf.logger.error(f"Config file {configPath} missing password")
        exit(1)
    
    ppf.host = config["host"]
    ppf.port = config["port"]
    ppf.mode = config["mode"]
    ppf.passwd = config["pass"]
    loggersetup(False, config["logfile"])

    



def loggersetup(debug, logfile):
    logger = logging.getLogger("PyPortForward")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.debug("Logger setup OK")
    logger.debug(f"Logfile: {logfile}, {bool(logfile)}")
    if logfile:
        logfile = Path(logfile)
        if not logfile.parent.exists():
            logging.getLogger("PyPortForward").warning(f"Log file directory {logfile.parent} does not exist, creating it")
            logfile.parent.mkdir(parents=True)
        handler = logging.FileHandler(logfile)
        formatter = logging.Formatter('%(levelname)s - [%(asctime)s] [%(filename)s:%(lineno)d] # %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger("PyPortForward").addHandler(handler)
