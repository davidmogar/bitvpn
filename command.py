import subprocess
from dataclasses import field, dataclass
from typing import Type


@dataclass
class CommandError(Exception):
    """Exception to be raised when there is an error executing a the command."""

    stderr: str
    stdout: str = None
    return_code: int = -1


@dataclass
class Command:

    @staticmethod
    def check_output(args: list, input: str = None, **kwargs):
        if input:
            return Command._pipe_run(args, input, True, **kwargs)[1]
        else:
            return Command._run(args, capture_output=True, **kwargs)[1]

    @staticmethod
    def check_return_code(args: list, input: str = None, **kwargs):
        if input:
            return Command._pipe_run(args, input, False, **kwargs)[0]
        else:
            return Command._run(args, **kwargs)[0]

    @staticmethod
    def _pipe_run(args: list, input: str, capture_output: bool = True, **kwargs):
        process = subprocess.Popen(args,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE if capture_output else subprocess.DEVNULL,
                                   text=True)

        try:
            stdout, stderr = process.communicate(input)

            if process.returncode is None:
                process.wait()

            if process.returncode != 0:
                raise CommandError(stderr or 'Command returned an non-zero code', return_code=process.returncode)

            return process.returncode, stdout
        except TimeoutError as error:
            raise CommandError(error.strerror)

    @staticmethod
    def _run(args: list, **kwargs):
        process = subprocess.run(args, text=True, **kwargs)

        if process.returncode != 0:
            raise CommandError(process.stderr, process.stdout, process.returncode)

        return process.returncode, process.stdout
