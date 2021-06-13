import os
import sys
from abc import ABC, abstractmethod
from enum import Enum
from getpass import getpass
from shutil import which

from command import Command, CommandError


class MediatorError(Exception):
    """Exception to be raised when there is an error."""


class InputManager(ABC):

    @abstractmethod
    def get_secret(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_selection(self, prompt: str, items: list) -> str:
        pass

    @abstractmethod
    def get_text(self, prompt: str) -> str:
        pass


class NotificationUrgency(str, Enum):
    CRITICAL = 'critical'
    LOW = 'low'
    NORMAL = 'normal'


class OutputManager(ABC):

    @abstractmethod
    def show(self, body: str, summary: str = None, urgency: NotificationUrgency = None):
        pass


class NotificationOutputManager(OutputManager):

    def show(self, body: str, summary: str = None, urgency: NotificationUrgency = NotificationUrgency.NORMAL):
        app_name = os.path.basename(sys.argv[0])

        if summary is None:
            summary = app_name

        Command.check_return_code(['notify-send', '-u', urgency, '-a', app_name, summary, body])


class RofiInputManager(InputManager):

    def get_secret(self, prompt: str) -> str:
        return Command.check_output(['rofi', '-no-fixed-num-lines', '-dmenu', '-password', '-p', prompt]).strip()

    def get_selection(self, prompt: str, items: list) -> str:
        return Command.check_output(['rofi', '-no-fixed-num-lines', '-dmenu'], '\n'.join(items)).strip()

    def get_text(self, prompt: str) -> str:
        return Command.check_output(['rofi', '-no-fixed-num-lines', '-dmenu', '-p', prompt]).strip()


class StdInputManager(InputManager):

    def get_secret(self, prompt: str) -> str:
        return getpass(f"{prompt}: ")

    def get_selection(self, prompt: str, items: list) -> str:
        for id, item in enumerate(items, start=1):
            print(f"{id}. {item}")

        while True:
            try:
                return items[int(input(f"{prompt}: ")) - 1]
            except (IndexError, ValueError):
                print('Please, select a valid index')
                continue

    def get_text(self, prompt: str) -> str:
        return input(f"{prompt}: ")


class StdOutputManager(OutputManager):

    def show(self, body: str, summary: str = None, urgency: NotificationUrgency = None):
        print(body)


class Mediator(InputManager, OutputManager):

    inputManager: InputManager = None
    outputManager: OutputManager = None

    def __init__(self, force_std: bool = False):
        if force_std or (which('rofi') is None):
            self.inputManager = StdInputManager()
        else:
            self.inputManager = RofiInputManager()

        if force_std or (which('notify-send') is None):
            self.outputManager = StdOutputManager()
        else:
            self.outputManager = NotificationOutputManager()

    def get_secret(self, prompt: str) -> str:
        return self.inputManager.get_secret(prompt)

    def get_selection(self, prompt: str, items: list) -> str:
        return self.inputManager.get_selection(prompt, items)

    def get_text(self, prompt: str) -> str:
        return self.inputManager.get_text(prompt)

    def show(self, body: str, summary: str = None, urgency=NotificationUrgency.NORMAL):
        return self.outputManager.show(body, summary, urgency)
