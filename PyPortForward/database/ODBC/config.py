import PyPortForward as ppf

default_config = {
    'driver': 'Oracle in instantclient_19_8',
    'profile': True,
    'profile_name': 'oracle_db_high',
    'host': 'localhost',
    'port': 1521,
    'user': 'system',
    'password': 'oracle',
    'encoding': 'UTF-8',
}

def setup():
    """
    Setup the Oracle Database configuration
    """
    default_config["profile"] = False
