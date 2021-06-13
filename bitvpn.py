#!/usr/bin/env python
from bitwarden import Bitwarden
from command import CommandError
from config import Config
from mediator import Mediator
from nmcli import Nmcli


def get_bitwarden_item_name(config: Config, mediator: Mediator) -> str:
    if not config.bw_item:
        config.bw_item = mediator.get_text('Bitwarden item')

    return config.bw_item


def get_vpn_name(config: Config, mediator: Mediator) -> str:
    if not config.vpn_name:
        vpns = sorted([vpn.name for vpn in Nmcli.get_available_vpns()])
        config.vpn_name = mediator.get_selection('Select a VPN', vpns)

    return config.vpn_name


def get_vpn_password(bw: Bitwarden, config: Config, mediator: Mediator) -> str:
    item = get_bitwarden_item_name(config, mediator)
    password = ''

    try:
        password = bw.get("password", item)
        totp = bw.get("totp", item)

        return password + totp
    except CommandError:
        if password:
            return password
        else:
            raise


def login_and_unlock(bw: Bitwarden, config: Config, mediator: Mediator):
    if not bw.is_logged_in():
        email = mediator.get_text('Bitwarden email')
        master_password = mediator.get_secret('Bitwarden password')
        code = mediator.get_text('2FA token') if config.two_factor else None
        bw.login(email, master_password, code)
    else:
        master_password = mediator.get_secret('Bitwarden password')

    bw.unlock(master_password)


def main():
    config = Config()
    config.load()

    bitwarden = Bitwarden()
    mediator = Mediator(config.force_std)

    vpn_name = get_vpn_name(config, mediator)

    if Nmcli.is_connected_to_vpn(vpn_name):
        mediator.show(f"Already connected to '{vpn_name}'")
    else:
        login_and_unlock(bitwarden, config, mediator)
        Nmcli.connect_to_vpn(vpn_name, get_vpn_password(bitwarden, config, mediator))
        mediator.show(f"Connected to '{vpn_name}'")

    if not config.no_save:
        config.save()


if __name__ == '__main__':
    main()
