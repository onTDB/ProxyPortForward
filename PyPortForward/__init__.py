import logging
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text
session = PromptSession()

class PromptHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        print_formatted_text(msg)
logger = logging.getLogger('PyPortForward')
logger.handlers = [PromptHandler()]
formatter = logging.Formatter('%(levelname)s - [%(asctime)s] [%(filename)s:%(lineno)d] # %(message)s')
logger.handlers[0].setFormatter(formatter)
logger.setLevel(logging.INFO)

host = ""
mode = "sock"
passwd = ""
connections = {}


import PyPortForward.types
import PyPortForward.commands
import PyPortForward.network
import PyPortForward.auth
import PyPortForward.config
import PyPortForward.structure
