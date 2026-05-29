from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    discord_allowed_user_ids: tuple[int, ...]
    discord_sync_guild_id: int | None
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


def _parse_optional_int(name: str, value: str) -> int | None:
    candidate = value.strip()
    if not candidate:
        return None

    try:
        return int(candidate)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer when provided.") from exc


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        discord_bot_token=_required("DISCORD_BOT_TOKEN"),
        discord_allowed_user_ids=_parse_int_list(os.environ.get("DISCORD_ALLOWED_USER_IDS", "")),
        discord_sync_guild_id=_parse_optional_int(
            "DISCORD_SYNC_GUILD_ID", os.environ.get("DISCORD_SYNC_GUILD_ID", "")
        ),
        proxmox_host=_required("PROXMOX_HOST"),
        proxmox_user=_required("PROXMOX_USER"),
        proxmox_password=_required("PROXMOX_PASSWORD"),
        proxmox_verify_ssl=_to_bool(os.environ.get("PROXMOX_VERIFY_SSL", "true")),
    )
