"""
metrics.py
==========
Performance Metrics Calculation and Evaluation Module.

Calculates key SDN performance indicators:
1. Link Utilization (Average, Maximum, Normalized %)
2. Throughput (Carried / Delivered traffic in Mbps)
3. Packet Loss (%)
4. Recovery Time (Failover elapsed time in ms/seconds)

Outputs standardized Pandas DataFrame and CSV formats according to the
research paper specification.
"""

from typing import Dict, List, Any, Optional
import os
import networkx as nx
import pandas as pd
import numpy as np


def update_link_utilizations(G: nx.Graph) -> None:
    """
    Update the utilization percentage of every edge in the graph based on its
    current traffic and bandwidth capacity:
    Utilization (%) = (Traffic / Capacity) * 100
    """
    for u, v in G.edges():
        capacity = G[u][v].get("capacity", 100.0)
        traffic = G[u][v].get("traffic", 0.0)
        status = G[u][v].get("status", "active")

        if capacity > 0 and status == "active":
            utilization = (traffic / capacity) * 100.0
        else:
            utilization = 0.0

        G[u][v]["utilization"] = round(utilization, 2)


def calculate_average_utilization(G: nx.Graph, active_only: bool = False) -> float:
    """
    Calculate the average link utilization across the network links.

    Args:
        G: NetworkX graph.
        active_only: If True, computes mean only across active links.

    Returns:
        float: Average utilization percentage.
    """
    update_link_utilizations(G)
    utils = []
    for u, v in G.edges():
        if active_only and G[u][v].get("status") != "active":
            continue
        utils.append(G[u][v].get("utilization", 0.0))

    if not utils:
        return 0.0
    return round(float(np.mean(utils)), 2)


def calculate_maximum_utilization(G: nx.Graph) -> float:
    """
    Calculate the maximum link utilization among all links in the network.

    Args:
        G: NetworkX graph.

    Returns:
        float: Maximum utilization percentage.
    """
    update_link_utilizations(G)
    utils = [G[u][v].get("utilization", 0.0) for u, v in G.edges()]
    if not utils:
        return 0.0
    return round(float(np.max(utils)), 2)


def calculate_normalized_utilization(G: nx.Graph) -> float:
    """
    Calculate normalized link utilization:
    Ratio of total traffic carried over total network link capacity, expressed as %.

    Args:
        G: NetworkX graph.

    Returns:
        float: Normalized utilization index.
    """
    total_traffic = sum(G[u][v].get("traffic", 0.0) for u, v in G.edges() if G[u][v].get("status") == "active")
    total_capacity = sum(G[u][v].get("capacity", 100.0) for u, v in G.edges() if G[u][v].get("status") == "active")

    if total_capacity == 0:
        return 0.0
    return round((total_traffic / total_capacity) * 100.0, 2)


def get_link_utilization_breakdown(G: nx.Graph) -> Dict[str, float]:
    """
    Get a dictionary mapping canonical link names 'NodeA <-> NodeB' to utilization %.

    Args:
        G: NetworkX graph.

    Returns:
        Dict[str, float]: Link name to utilization percentage.
    """
    update_link_utilizations(G)
    breakdown = {}
    for u, v in G.edges():
        link_name = f"{u} <-> {v}"
        breakdown[link_name] = G[u][v].get("utilization", 0.0)
    return breakdown


def create_phase_record(
    phase: str,
    average_utilization: float,
    maximum_utilization: float,
    throughput: float,
    packet_loss: float,
    recovery_time: float,
) -> Dict[str, Any]:
    """
    Create a standardized metrics dictionary record for a simulation phase.

    Args:
        phase: Phase name ('Before Failure', 'During Failure', 'After Failover').
        average_utilization: Average link utilization percentage.
        maximum_utilization: Maximum link utilization percentage.
        throughput: Carried throughput in Mbps.
        packet_loss: Packet loss percentage (0.0 to 100.0).
        recovery_time: Failover recovery time in seconds or milliseconds.

    Returns:
        Dict[str, Any] matching the required DataFrame and CSV structure.
    """
    return {
        "phase": phase,
        "average_utilization": round(average_utilization, 2),
        "maximum_utilization": round(maximum_utilization, 2),
        "throughput": round(throughput, 2),
        "packet_loss": round(packet_loss, 2),
        "recovery_time": round(recovery_time, 4),
    }


def compile_results_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of phase metric records into a clean Pandas DataFrame.

    Args:
        records: List of phase metric dictionaries.

    Returns:
        pd.DataFrame with columns:
        [phase, average_utilization, maximum_utilization, throughput, packet_loss, recovery_time]
    """
    columns = [
        "phase",
        "average_utilization",
        "maximum_utilization",
        "throughput",
        "packet_loss",
        "recovery_time",
    ]
    df = pd.DataFrame(records, columns=columns)
    return df


def save_results_to_csv(df: pd.DataFrame, filepath: str = "results/csv/simulation_results.csv") -> str:
    """
    Export the simulation results DataFrame to a CSV file.
    Creates parent directories automatically if they do not exist.

    Args:
        df: Pandas DataFrame containing simulation results.
        filepath: Output CSV file path.

    Returns:
        str: Absolute path of saved CSV.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    return os.path.abspath(filepath)


if __name__ == "__main__":
    from topology import create_topology
    g = create_topology()
    g["Edge1"]["Core1"]["traffic"] = 70.0
    g["Core1"]["LMS"]["traffic"] = 70.0
    rec = create_phase_record(
        phase="Before Failure",
        average_utilization=calculate_average_utilization(g),
        maximum_utilization=calculate_maximum_utilization(g),
        throughput=70.0,
        packet_loss=0.0,
        recovery_time=0.0,
    )
    df = compile_results_dataframe([rec])
    print(df.to_string())
