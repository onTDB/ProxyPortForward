import PyPortForward.commands
import PyPortForward.network
import PyPortForward.ports
import PyPortForward.users
import PyPortForward.database
import PyPortForward.io
import logging
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text
session = PromptSession()

global input
global print
global logger

input = session.prompt
print = print_formatted_text
logger = logging.getLogger(__name__)
