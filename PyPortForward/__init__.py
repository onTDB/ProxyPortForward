import PyPortForward.commands
import PyPortForward.network
import PyPortForward.ports
import PyPortForward.users
import PyPortForward.database
import PyPortForward.security
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

connections = {}
