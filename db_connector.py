"""COUNTERS_DB access helpers for top-N interface traffic visibility."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional


RX_OCTETS_FIELD = "SAI_PORT_STAT_IF_IN_OCTETS"
TX_OCTETS_FIELD = "SAI_PORT_STAT_IF_OUT_OCTETS"


class CountersDbUnavailable(RuntimeError):
    """Raised when COUNTERS_DB cannot be reached."""


@dataclass
class InterfaceCounters:
    """Minimal counter payload used for traffic-rate calculations."""

    rx_bytes: int
    tx_bytes: int


class CountersDbClient:
    """Read interface traffic counters from COUNTERS_DB."""

    def __init__(self, namespace: Optional[str] = None, backend=None):
        self.namespace = namespace
        self._backend = backend or self._create_backend(namespace)

    def _create_backend(self, namespace: Optional[str]):
        try:
            from swsscommon.swsscommon import SonicV2Connector  # type: ignore
        except Exception as exc:
            raise CountersDbUnavailable(
                "COUNTERS_DB access requires swsscommon in the SONiC environment"
            ) from exc

        connector_kwargs = {}
        if namespace:
            connector_kwargs["namespace"] = namespace

        try:
            connector = SonicV2Connector(**connector_kwargs)
            connector.connect(connector.COUNTERS_DB)
            return connector
        except Exception as exc:
            raise CountersDbUnavailable(
                "Unable to connect to COUNTERS_DB. Ensure swss is running."
            ) from exc

    def _hgetall(self, key: str) -> Mapping[str, str]:
        return self._backend.get_all(self._backend.COUNTERS_DB, key) or {}

    def get_port_name_map(self) -> Mapping[str, str]:
        return self._hgetall("COUNTERS_PORT_NAME_MAP")

    def get_snapshot(self) -> Dict[str, InterfaceCounters]:
        port_name_map = self.get_port_name_map()
        snapshot: Dict[str, InterfaceCounters] = {}

        for interface_name, oid in port_name_map.items():
            key = f"COUNTERS:{oid}"
            row = self._hgetall(key)
            if not row:
                continue

            rx_raw = row.get(RX_OCTETS_FIELD, "0")
            tx_raw = row.get(TX_OCTETS_FIELD, "0")

            try:
                rx_bytes = int(rx_raw)
                tx_bytes = int(tx_raw)
            except (TypeError, ValueError):
                rx_bytes = 0
                tx_bytes = 0

            snapshot[interface_name] = InterfaceCounters(rx_bytes=rx_bytes, tx_bytes=tx_bytes)

        return snapshot

    def close(self):
        close_fn = getattr(self._backend, "close", None)
        if close_fn:
            close_fn()
