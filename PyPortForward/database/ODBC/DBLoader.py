from prompt_toolkit import print_formatted_text as print

import PyPortForward as ppf

def loader(config):
    cx_Oracle = ppf.database.ODBC.cx_Oracle