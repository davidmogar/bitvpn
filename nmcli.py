from dataclasses import dataclass

from command import Command


@dataclass
class Vpn:

    name: str
    uuid: str
    device: str = None


class Nmcli:

    @staticmethod
    def get_available_vpns():
        vpns = []

        output = Command.check_output(['nmcli', '-t', 'connection'])
        for line in output.split('\n'):
            if len((item := line.split(':'))) == 4 and item[2] == 'vpn':
                vpns.append(Vpn(item[0], item[1], item[3] or None))

        return vpns

    @staticmethod
    def is_connected_to_vpn(vpn_name: str):
        for vpn in Nmcli.get_available_vpns():
            if vpn.device is not None and vpn.name == vpn_name:
                return True

        return False

    @staticmethod
    def connect_to_vpn(vpn_name: str, password: str = None):
        if password:
            Command.check_return_code(['nmcli', '--wait', '30', 'connection', 'up', vpn_name, 'passwd-file', '/dev/fd/0'],
                                 f"vpn.secrets.password:{password}")
        else:
            Command.check_return_code(['nmcli', 'connection', 'up', vpn_name])

    @staticmethod
    def disconnect_from_vpn(vpn_name: str):
        Command.check_return_code(['nmcli', 'connection', 'down', vpn_name])
