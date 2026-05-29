from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    discord_allowed_user_ids: tuple[int, ...]
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


def _parse_int_list(value: str) -> tuple[int, ...]:
    if not value.strip():
        return ()
    parsed = []
    for item in value.split(","):
        candidate = item.strip()
        if not candidate:
            continue
        try:
            parsed.append(int(candidate))
        except ValueError as exc:
            raise ValueError(
                f"DISCORD_ALLOWED_USER_IDS contains an invalid integer value: {candidate}"
            ) from exc
    return tuple(parsed)


def load_settings() -> Settings:
    return Settings(
        discord_bot_token=_required("DISCORD_BOT_TOKEN"),
        discord_allowed_user_ids=_parse_int_list(os.environ.get("DISCORD_ALLOWED_USER_IDS", "")),
        proxmox_host=_required("PROXMOX_HOST"),
        proxmox_user=_required("PROXMOX_USER"),
        proxmox_password=_required("PROXMOX_PASSWORD"),
        proxmox_verify_ssl=_to_bool(os.environ.get("PROXMOX_VERIFY_SSL", "true")),
    )
