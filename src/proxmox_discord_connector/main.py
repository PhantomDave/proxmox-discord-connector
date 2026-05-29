from __future__ import annotations

import logging

from proxmox_discord_connector.app import ProxmoxDiscordApplication
from proxmox_discord_connector.config import Settings, load_settings


def create_application(settings: Settings) -> ProxmoxDiscordApplication:
    return ProxmoxDiscordApplication(settings)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    application = create_application(settings)
    application.run()


if __name__ == "__main__":
    main()
