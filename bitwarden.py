from dataclasses import dataclass, field
from typing import Optional

from command import Command

BASE_COMMAND = ['bw', '--nointeraction', '--raw']


@dataclass
class Bitwarden:
    session_key: Optional[str] = None

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            return lambda *args: self._run_with_session(item, *args)

    @staticmethod
    def is_logged_in():
        return Command.check_return_code(BASE_COMMAND + ['login', '--check']) == 0

    @staticmethod
    def login(email: str, master_password: str, code: str = None, method: int = 0):
        if method is not None and code:
            Command.check_return_code(BASE_COMMAND +
                                      ['login', email, master_password, '--method', str(method), '--code', code])
        else:
            Command.check_return_code(BASE_COMMAND + ['login', email, master_password])

    @staticmethod
    def logout():
        Command.check_return_code(BASE_COMMAND + ['logout'])

    def lock(self):
        self.session_key = None
        Command.check_return_code(BASE_COMMAND + ['lock'])

    def unlock(self, master_password: str):
        self.session_key = Command.check_output(BASE_COMMAND + ['unlock', master_password])

    def _run_with_session(self, command, *args):
        return Command.check_output(BASE_COMMAND + [command, '--session', self.session_key] + list(args))
