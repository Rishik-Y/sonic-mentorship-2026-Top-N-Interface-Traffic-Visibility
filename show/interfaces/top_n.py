"""Implementation for `show interfaces counters top-n`."""

from __future__ import annotations

import json
import time
from typing import Dict, List, Optional

import click
from tabulate import tabulate

from db_connector import CountersDbClient, CountersDbUnavailable, InterfaceCounters

_COUNTER_WRAP_MODULUS = 2**64


def create_counters_db_client(namespace: Optional[str] = None) -> CountersDbClient:
    return CountersDbClient(namespace=namespace)


def calculate_counter_delta(previous: int, current: int) -> int:
    if current >= previous:
        return current - previous
    return (_COUNTER_WRAP_MODULUS - previous) + current


def format_rate(rate_bps: float) -> str:
    units = [(1_000_000_000, "Gbps"), (1_000_000, "Mbps"), (1_000, "Kbps")]
    for threshold, unit in units:
        if rate_bps >= threshold:
            return f"{rate_bps / threshold:.2f} {unit}"
    return f"{rate_bps:.2f} bps"


def build_top_n_results(
    first_snapshot: Dict[str, InterfaceCounters],
    second_snapshot: Dict[str, InterfaceCounters],
    interval: float,
    top: int,
) -> List[dict]:
    results: List[dict] = []

    for interface_name, second in second_snapshot.items():
        first = first_snapshot.get(interface_name)
        if not first:
            continue

        rx_delta_bytes = calculate_counter_delta(first.rx_bytes, second.rx_bytes)
        tx_delta_bytes = calculate_counter_delta(first.tx_bytes, second.tx_bytes)

        rx_rate_bps = (rx_delta_bytes * 8.0) / interval
        tx_rate_bps = (tx_delta_bytes * 8.0) / interval
        total_rate_bps = rx_rate_bps + tx_rate_bps

        results.append(
            {
                "interface": interface_name,
                "rx_rate_bps": rx_rate_bps,
                "tx_rate_bps": tx_rate_bps,
                "total_rate_bps": total_rate_bps,
                "rx_rate": format_rate(rx_rate_bps),
                "tx_rate": format_rate(tx_rate_bps),
                "total_rate": format_rate(total_rate_bps),
            }
        )

    results.sort(key=lambda row: row["total_rate_bps"], reverse=True)
    return results[:top]


def _render_table(results: List[dict]) -> str:
    rows = [
        [
            row["interface"],
            row["rx_rate"],
            row["tx_rate"],
            row["total_rate"],
        ]
        for row in results
    ]
    return tabulate(rows, headers=["Interface", "RX Rate", "TX Rate", "Total Rate"])


@click.command(name="top-n")
@click.option("--top", "top", type=click.IntRange(1), default=5, show_default=True)
@click.option("--interval", type=click.FloatRange(min=0, min_open=True), default=1.0, show_default=True)
@click.option("--json", "json_output", is_flag=True, default=False, help="Output in JSON format")
@click.option("--namespace", default=None, help="ASIC namespace")
def top_n(top: int, interval: float, json_output: bool, namespace: Optional[str]):
    """Show top interfaces by throughput using RX+TX octet deltas."""

    client = None
    try:
        client = create_counters_db_client(namespace=namespace)
        first = client.get_snapshot()
        time.sleep(interval)
        second = client.get_snapshot()
    except CountersDbUnavailable as exc:
        raise click.ClickException(f"Unable to access COUNTERS_DB: {exc}")
    finally:
        if client is not None:
            client.close()

    results = build_top_n_results(first, second, interval, top)

    if json_output:
        click.echo(json.dumps(results))
        return

    if not results:
        click.echo("No interface counters found in COUNTERS_DB.")
        return

    click.echo(_render_table(results))
