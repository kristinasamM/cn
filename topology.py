"""
topology.py
===========
Network Topology Definition Module for SDN Failover Simulation.

Based on the research paper:
"Analysis of Software-Defined Networking Resilience to Link Failure through Failover Routing Simulation"
(Istiqomah, Sholihin, & Hidayati, G-Tech: Jurnal Teknologi Terapan, 2026).

Represents a logical SDN network consisting of:
- 6 Nodes: Edge1, Edge2, Core1, Core2, LMS (Learning Management System), Cache
- 8 Communication Links with configurable capacity, status, and traffic metrics.
"""

from typing import Dict, List, Tuple, Any
import networkx as nx

# Predefined 2D coordinates for clear, planar visualization of the topology
NODE_POSITIONS: Dict[str, Tuple[float, float]] = {
    "LMS": (1.5, 3.2),
    "Core1": (0.7, 2.0),
    "Edge2": (2.3, 2.0),
    "Edge1": (0.0, 1.0),
    "Core2": (1.7, 1.0),
    "Cache": (0.8, 0.0),
}

# Node classifications for role-based styling and metadata
NODE_ROLES: Dict[str, str] = {
    "Edge1": "edge",
    "Edge2": "edge",
    "Core1": "core",
    "Core2": "core",
    "LMS": "server",
    "Cache": "server",
}

# The eight canonical communication links described in the research paper
TOPOLOGY_LINKS: List[Tuple[str, str]] = [
    ("LMS", "Core1"),
    ("LMS", "Edge2"),
    ("Core1", "Edge2"),
    ("Core1", "Edge1"),
    ("Core2", "Edge2"),
    ("Core2", "Edge1"),
    ("Cache", "Core2"),
    ("Cache", "Edge1"),
]


CANONICAL_NODES: List[str] = [
    "Edge1",
    "Edge2",
    "Core1",
    "Core2",
    "LMS",
    "Cache",
]


def create_topology(default_capacity: float = 100.0) -> nx.Graph:
    """
    Construct and initialize the 6-node, 8-link logical SDN network graph.

    Args:
        default_capacity: Default link bandwidth capacity in Mbps (default: 100.0 Mbps).

    Returns:
        nx.Graph: Initialized NetworkX undirected graph with node and link attributes.
    """
    G = nx.Graph()

    # Add 6 nodes in canonical academic order with role and visual position attributes
    for node in CANONICAL_NODES:
        pos = NODE_POSITIONS[node]
        G.add_node(
            node,
            role=NODE_ROLES.get(node, "node"),
            pos=pos,
            label=node,
        )

    # Add 8 communication links with initial operational attributes
    for u, v in TOPOLOGY_LINKS:
        G.add_edge(
            u,
            v,
            status="active",          # Status: 'active' or 'failed'
            capacity=float(default_capacity),  # Bandwidth capacity in Mbps
            traffic=0.0,              # Current traffic load in Mbps
            packet_loss=0.0,          # Packet loss percentage (0.0 - 100.0)
            utilization=0.0,          # Link utilization percentage (0.0 - 100.0)
            weight=1.0,               # Routing cost weight for shortest path
            latency=5.0,              # Link propagation latency in ms
        )

    return G


def get_topology_info(G: nx.Graph) -> Dict[str, Any]:
    """
    Retrieve structural metadata and link states of the topology.

    Args:
        G: NetworkX graph instance.

    Returns:
        Dict containing node count, link count, nodes list, and link details.
    """
    links_info = []
    for u, v, data in G.edges(data=True):
        links_info.append({
            "source": u,
            "target": v,
            "status": data.get("status", "active"),
            "capacity": data.get("capacity", 100.0),
            "traffic": data.get("traffic", 0.0),
            "utilization": data.get("utilization", 0.0),
            "packet_loss": data.get("packet_loss", 0.0),
        })

    return {
        "node_count": G.number_of_nodes(),
        "link_count": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "links": links_info,
    }


def print_topology(G: nx.Graph) -> None:
    """
    Print the topology information formatted in accordance with the paper specification.

    Args:
        G: NetworkX graph instance.
    """
    print("NETWORK TOPOLOGY\n")
    print("Nodes:")
    for node in CANONICAL_NODES:
        if node in G:
            print(f"- {node}")

    print("\nLinks:")
    for u, v in TOPOLOGY_LINKS:
        status = G[u][v].get("status", "active")
        status_suffix = "" if status == "active" else f" [{status.upper()}]"
        print(f"- {u} <-> {v}{status_suffix}")


def get_link_data(G: nx.Graph, u: str, v: str) -> Dict[str, Any]:
    """
    Safely retrieve edge attribute dictionary between two nodes.

    Args:
        G: NetworkX graph.
        u: First node identifier.
        v: Second node identifier.

    Returns:
        Dict of edge attributes.
    """
    if G.has_edge(u, v):
        return G[u][v]
    raise KeyError(f"No link exists between {u} and {v} in the topology.")


def set_link_data(G: nx.Graph, u: str, v: str, **kwargs) -> None:
    """
    Safely update edge attributes between two nodes.

    Args:
        G: NetworkX graph.
        u: First node identifier.
        v: Second node identifier.
        **kwargs: Attributes to update (status, traffic, packet_loss, etc.).
    """
    if not G.has_edge(u, v):
        raise KeyError(f"Cannot update nonexistent link between {u} and {v}.")
    for key, value in kwargs.items():
        G[u][v][key] = value


def reset_topology(G: nx.Graph, default_capacity: float = 100.0) -> None:
    """
    Reset all links in the topology to their baseline active state with zero traffic.

    Args:
        G: NetworkX graph instance.
        default_capacity: Capacity in Mbps to reset links to.
    """
    for u, v in G.edges():
        G[u][v]["status"] = "active"
        G[u][v]["capacity"] = float(default_capacity)
        G[u][v]["traffic"] = 0.0
        G[u][v]["packet_loss"] = 0.0
        G[u][v]["utilization"] = 0.0
        G[u][v]["weight"] = 1.0


if __name__ == "__main__":
    test_graph = create_topology()
    print_topology(test_graph)
    print(f"\nTotal Nodes: {test_graph.number_of_nodes()}")
    print(f"Total Links: {test_graph.number_of_edges()}")
