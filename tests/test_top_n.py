import json

from click.testing import CliRunner

import show.interfaces.top_n as top_n_module
from db_connector import CountersDbUnavailable, InterfaceCounters
from show.interfaces.top_n import build_top_n_results, top_n


class FakeClient:
    def __init__(self, snapshots):
        self._snapshots = list(snapshots)

    def get_snapshot(self):
        return self._snapshots.pop(0)

    def close(self):
        return None


class FailingClientFactory:
    def __call__(self, namespace=None):
        raise CountersDbUnavailable("mock backend unavailable")


def test_build_top_n_rollover():
    first = {"Ethernet0": InterfaceCounters(rx_bytes=(2**64) - 10, tx_bytes=(2**64) - 20)}
    second = {"Ethernet0": InterfaceCounters(rx_bytes=40, tx_bytes=80)}

    results = build_top_n_results(first, second, interval=1.0, top=5)

    assert len(results) == 1
    assert results[0]["rx_rate_bps"] == 400.0
    assert results[0]["tx_rate_bps"] == 800.0
    assert results[0]["total_rate_bps"] == 1200.0


def test_top_n_json_output(monkeypatch):
    snapshots = [
        {
            "Ethernet0": InterfaceCounters(rx_bytes=100, tx_bytes=100),
            "Ethernet4": InterfaceCounters(rx_bytes=100, tx_bytes=100),
        },
        {
            "Ethernet0": InterfaceCounters(rx_bytes=2100, tx_bytes=3100),
            "Ethernet4": InterfaceCounters(rx_bytes=600, tx_bytes=600),
        },
    ]

    monkeypatch.setattr(top_n_module, "create_counters_db_client", lambda namespace=None: FakeClient(snapshots))
    monkeypatch.setattr(top_n_module.time, "sleep", lambda _: None)

    result = CliRunner().invoke(top_n, ["--json", "--top", "1", "--interval", "1"])
    assert result.exit_code == 0

    payload = json.loads(result.output)
    assert len(payload) == 1
    assert payload[0]["interface"] == "Ethernet0"


def test_top_n_single_interface_table(monkeypatch):
    snapshots = [
        {"Ethernet12": InterfaceCounters(rx_bytes=10, tx_bytes=10)},
        {"Ethernet12": InterfaceCounters(rx_bytes=1010, tx_bytes=2010)},
    ]

    monkeypatch.setattr(top_n_module, "create_counters_db_client", lambda namespace=None: FakeClient(snapshots))
    monkeypatch.setattr(top_n_module.time, "sleep", lambda _: None)

    result = CliRunner().invoke(top_n, ["--top", "5", "--interval", "1"])
    assert result.exit_code == 0
    assert "Ethernet12" in result.output


def test_top_n_empty_db(monkeypatch):
    snapshots = [{}, {}]
    monkeypatch.setattr(top_n_module, "create_counters_db_client", lambda namespace=None: FakeClient(snapshots))
    monkeypatch.setattr(top_n_module.time, "sleep", lambda _: None)

    result = CliRunner().invoke(top_n, ["--top", "5", "--interval", "1"])
    assert result.exit_code == 0
    assert "No interface counters found" in result.output


def test_top_n_unavailable_db(monkeypatch):
    monkeypatch.setattr(top_n_module, "create_counters_db_client", FailingClientFactory())

    result = CliRunner().invoke(top_n, ["--top", "5", "--interval", "1"])
    assert result.exit_code != 0
    assert "Unable to access COUNTERS_DB" in result.output


def test_top_n_namespace_passed(monkeypatch):
    seen = {}
    snapshots = [
        {"Ethernet0": InterfaceCounters(rx_bytes=10, tx_bytes=10)},
        {"Ethernet0": InterfaceCounters(rx_bytes=20, tx_bytes=40)},
    ]

    def _factory(namespace=None):
        seen["namespace"] = namespace
        return FakeClient(snapshots)

    monkeypatch.setattr(top_n_module, "create_counters_db_client", _factory)
    monkeypatch.setattr(top_n_module.time, "sleep", lambda _: None)

    result = CliRunner().invoke(top_n, ["--namespace", "asic0", "--interval", "1"])
    assert result.exit_code == 0
    assert seen["namespace"] == "asic0"
