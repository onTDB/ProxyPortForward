from .server import server
from .client import client
from .forward import forward

import PyPortForward as ppf

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
import inspect

class CommandCompleter(Completer):
    def __init__(self, func):
        self.commands = {}
        self.current_command = None

        # check func is a module
        if inspect.ismodule(func):
            functions = inspect.getmembers(func, inspect.isfunction)
        elif inspect.isclass(func):
            functions = inspect.getmembers(func, inspect.isfunction)
        elif inspect.isfunction(func):
            # get functions inside the function
            source = inspect.getsource(func)
            functions = inspect.getmembers(func, inspect.isfunction)

            
        else:
            raise TypeError("func must be a module, class, or function")

        # Store the function names and their parameters
        for name, func in functions:
            self.commands[name] = inspect.signature(func).parameters.keys()

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        self.text = text

        # If we're at the beginning of the line, show all commands
        if not text:
            for command in self.commands:
                yield Completion(command, start_position=0)

        # If we're after the first word, show completions for that command
        elif ' ' in text:
            command, arg_text = text.split(' ', 1)
            if command in self.commands:
                self.current_command = command
                for param in self.commands[command]:
                    if param.startswith(arg_text):
                        yield Completion(param, start_position=-len(arg_text))

        # If we're typing the first word, show all commands that match
        else:
            for command in self.commands:
                if command.startswith(text):
                    yield Completion(command, start_position=0)

    def get_toolbar():

        pass

def prompt(module) -> str:
    """
    Prompt the user for input
    """

    return ppf.session.prompt("PyPortForward> ", completer=ppf.commands.CommandCompleter(module))
