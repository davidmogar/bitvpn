import argparse
import os

import yaml


NO_CACHEABLE_KEYS = ['cache', 'no_cache', 'no_save']


class Config:

    _namespace: argparse.Namespace
    _parser: argparse.ArgumentParser

    def __init__(self):
        self._parse_args()

        if not self._namespace.no_cache and not os.access(os.path.expanduser(self._namespace.cache), os.R_OK):
            raise PermissionError('Cache file path is not readable')

    def load(self) -> None:
        if not self._namespace.no_cache:
            with open(os.path.expanduser(self._namespace.cache), 'r') as file:
                try:
                    args = []
                    for key, value in yaml.load(file, Loader=yaml.FullLoader).items():
                        args.append(f"--{key.replace('_', '-')}")
                        if not isinstance(value, bool):
                            args.append(value)
                    self._parser.parse_args(args, self._namespace)
                except yaml.YAMLError:
                    pass

        if not self._namespace.no_save and not os.access(os.path.expanduser(self._namespace.cache), os.W_OK):
            raise PermissionError('Cache file path is not writable')

    def save(self) -> None:
        items = {
            key: value
            for key, value in vars(self._namespace).items()
            if key not in NO_CACHEABLE_KEYS and value is not None and self._parser.get_default(key) != value
        }

        with open(os.path.expanduser(self._namespace.cache), 'w+') as file:
            try:
                yaml.dump(items, file)
            except yaml.YAMLError:
                pass

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        elif key in self._namespace:
            object.__setattr__(self._namespace, key, value)

    def __getattr__(self, item):
        if hasattr(self._namespace, item):
            return getattr(self._namespace, item)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def _parse_args(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--two-factor', action='store_true',
                            help='Use 2fa to login to Bitwarden')
        parser.add_argument('--bw-item', type=str,
                            help='Bitwarden item with the VPN password')
        parser.add_argument('--cache', default='~/.bitvpn', type=str,
                            help='Path to the cache file (defaults to ~/.bitvpn)')
        parser.add_argument('--force-std', action='store_true',
                            help='Weather to force the use of standard input and output')
        parser.add_argument('--method', type=int,
                            help='2fa method to use during Bitwarden login')
        parser.add_argument('--no-cache', action='store_true',
                            help='Do not use the cached data')
        parser.add_argument('--no-save', action='store_true',
                            help='Save arguments as defaults values')
        parser.add_argument('--vpn-name', type=str,
                            help='Name of the VPN to connect to')

        self._parser = parser
        self._namespace = parser.parse_args()
