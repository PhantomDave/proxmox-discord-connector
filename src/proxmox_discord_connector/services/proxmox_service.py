from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any, cast

from proxmoxer import ProxmoxAPI

from proxmox_discord_connector.config import Settings


@dataclass(frozen=True)
class ProxmoxNode:
    name: str
    status: str | None = None


@dataclass(frozen=True)
class ProxmoxLxcContainer:
    node: str
    vmid: int | None
    name: str | None
    status: str | None = None


class ProxmoxService:
    def __init__(
        self,
        *,
        host: str,
        user: str,
        password: str,
        verify_ssl: bool,
    ) -> None:
        self._host = host
        self._user = user
        self._password = password
        self._verify_ssl = verify_ssl

    @classmethod
    def from_settings(cls, settings: Settings) -> "ProxmoxService":
        return cls(
            host=settings.proxmox_host,
            user=settings.proxmox_user,
            password=settings.proxmox_password,
            verify_ssl=settings.proxmox_verify_ssl,
        )

    def _client(self) -> ProxmoxAPI:
        return ProxmoxAPI(
            self._host,
            user=self._user,
            password=self._password,
            verify_ssl=self._verify_ssl,
        )

    @staticmethod
    def _mapping_list(raw_items: Any) -> list[Mapping[str, Any]]:
        if not isinstance(raw_items, list):
            return []

        items: list[Mapping[str, Any]] = []
        for item in cast(list[Any], raw_items):
            if isinstance(item, Mapping):
                items.append(cast(Mapping[str, Any], item))
        return items

    @staticmethod
    def _as_string(value: Any) -> str | None:
        return value if isinstance(value, str) else None

    @staticmethod
    def _as_int(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    def list_nodes(self) -> list[ProxmoxNode]:
        proxmox_any: Any = self._client()
        raw_nodes = self._mapping_list(proxmox_any.nodes.get())
        nodes: list[ProxmoxNode] = []

        for raw in raw_nodes:
            name = self._as_string(raw.get("node"))
            if name is None:
                continue

            nodes.append(
                ProxmoxNode(
                    name=name,
                    status=self._as_string(raw.get("status")),
                )
            )

        return nodes

    def list_lxcs(self) -> list[ProxmoxLxcContainer]:
        proxmox_any: Any = self._client()
        containers: list[ProxmoxLxcContainer] = []

        for node in self.list_nodes():
            raw_lxcs = self._mapping_list(proxmox_any.nodes(node.name).lxc.get())
            for raw in raw_lxcs:
                containers.append(
                    ProxmoxLxcContainer(
                        node=node.name,
                        vmid=self._as_int(raw.get("vmid")),
                        name=self._as_string(raw.get("name")),
                        status=self._as_string(raw.get("status")),
                    )
                )

        return containers

    def list_node_names(self) -> list[str]:
        return [node.name for node in self.list_nodes()]

    def list_lxc_names(self) -> list[str]:
        return [container.name for container in self.list_lxcs() if container.name]
    
    def reboot_lxc(self, target: str) -> None:
        proxmox_any: Any = self._client()
        for node in self.list_nodes():
            raw_lxcs = self._mapping_list(proxmox_any.nodes(node.name).lxc.get())
            for raw in raw_lxcs:
                name = self._as_string(raw.get("name"))
                vmid = self._as_int(raw.get("vmid"))
                if name and vmid is not None and f"{name}/{vmid}" == target:
                    proxmox_any.nodes(node.name).lxc(vmid).status.reboot.post()
                    return
        raise ValueError(f"No LXC container found with target identifier: {target}")
    
    def shutdown_lxc(self, target: str) -> None:
        proxmox_any: Any = self._client()
        for node in self.list_nodes():
            raw_lxcs = self._mapping_list(proxmox_any.nodes(node.name).lxc.get())
            for raw in raw_lxcs:
                name = self._as_string(raw.get("name"))
                vmid = self._as_int(raw.get("vmid"))
                if name and vmid is not None and f"{name}/{vmid}" == target:
                    proxmox_any.nodes(node.name).lxc(vmid).status.shutdown.post()
                    return
        raise ValueError(f"No LXC container found with target identifier: {target}")
    
    def start_lxc(self, target: str) -> None:
        proxmox_any: Any = self._client()
        for node in self.list_nodes():
            raw_lxcs = self._mapping_list(proxmox_any.nodes(node.name).lxc.get())
            for raw in raw_lxcs:
                name = self._as_string(raw.get("name"))
                vmid = self._as_int(raw.get("vmid"))
                if name and vmid is not None and f"{name}/{vmid}" == target:
                    proxmox_any.nodes(node.name).lxc(vmid).status.start.post()
                    return
        raise ValueError(f"No LXC container found with target identifier: {target}")
