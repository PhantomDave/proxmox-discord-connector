from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    proxmox_host: str
    proxmox_user: str
    proxmox_password: str
    proxmox_verify_ssl: bool


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} is required.")
    return value


def load_settings() -> Settings:
    return Settings(
        discord_bot_token=os.environ.get("DISCORD_BOT_TOKEN", "").strip(),
        proxmox_host=_required("PROXMOX_HOST"),
        proxmox_user=_required("PROXMOX_USER"),
        proxmox_password=_required("PROXMOX_PASSWORD"),
        proxmox_verify_ssl=_to_bool(os.environ.get("PROXMOX_VERIFY_SSL", "false")),
    )
