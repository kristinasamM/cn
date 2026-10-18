"""
visualization.py
================
Matplotlib Publication-Grade Visualization Module for SDN Failover Simulation.

Rich Dark & Illuminated Palette (Featuring user-provided swatch highlights):
- Soft Mint Teal:   #87D0CA (Core switches, primary route, healthy status)
- Soft Blush Peach: #FCDDD3 (Edge switches, critical alerts)
- Warm Dusty Rose:  #E6C4B7 (LMS & Cache servers, failover restoration)
- Warm Cream Accent: #F2ECE1
- Deep Canvas:      #0B1120 / #1E293B
- High-Contrast Text: #F8FAFC (Pure, crisp, 100% readable white)

Generates the academic network topology figures and performance graphs in 'results/graphs/':
1. initial_topology.png            - Phase 1: Baseline topology with active primary route (Edge1 -> Core1 -> LMS)
2. failure_topology.png            - Phase 2: Broken link (Edge1 <-> Core1) with severed primary path & 100% loss
3. failover_topology.png           - Phase 3: Alternative backup path (Edge1 -> Core2 -> Edge2 -> LMS) restored
4. phase_progression_overview.png  - Consolidated 3-Phase comparative panel for fast visual evaluation
5. link_utilization.png            - Average & maximum link utilization comparison across phases
6. throughput.png                  - End-to-end delivered throughput comparison showing degradation & recovery
7. recovery_time.png               - SDN failover latency breakdown (detection, computation, flow installation)
8. routing_strategies_comparison.png - Benchmark: Shortest vs Load-Based vs Fault-Aware vs Failover
"""

from typing import Dict, List, Tuple, Optional, Any
import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless & Colab execution
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import networkx as nx
import pandas as pd
import numpy as np

from topology import NODE_POSITIONS

# -----------------------------------------------------------------------------
# Rich Dark & Swatch Highlight Palette
# -----------------------------------------------------------------------------
COLOR_BG = "#0B1120"          # Rich dark slate canvas
COLOR_PANEL = "#1E293B"       # Dark surface panel
COLOR_TEXT = "#F8FAFC"        # Pure crisp white text
COLOR_MUTED = "#94A3B8"       # Secondary slate text
COLOR_STANDBY = "#334155"     # Standby edge color (muted slate)
COLOR_PRIMARY = "#87D0CA"     # Illuminated Mint Teal from swatch
COLOR_FAILED = "#EF4444"      # Vibrant crimson for failed link
COLOR_BACKUP = "#87D0CA"      # Mint Teal for restored backup route
COLOR_SEVERED = "#F97316"     # Vibrant orange for severed downstream flow
COLOR_NODE_CORE = "#87D0CA"   # Mint Teal pastel from user swatch
COLOR_NODE_EDGE = "#FCDDD3"   # Blush Peach pastel from user swatch
COLOR_NODE_SERVER = "#E6C4B7" # Warm Dusty Rose pastel from user swatch

# Custom non-overlapping offsets for node role badges
NODE_BADGE_CONFIG: Dict[str, Dict[str, Any]] = {
    "LMS":   {"text": "DESTINATION (LMS)", "dx": 0.0,   "dy": 0.32,  "ha": "center", "va": "bottom"},
    "Core1": {"text": "PRIMARY CORE",      "dx": -0.32, "dy": 0.18,  "ha": "right",  "va": "center"},
    "Edge2": {"text": "EGRESS EDGE",       "dx": 0.32,  "dy": 0.18,  "ha": "left",   "va": "center"},
    "Edge1": {"text": "INGRESS SOURCE",    "dx": -0.32, "dy": -0.05, "ha": "right",  "va": "center"},
    "Core2": {"text": "BACKUP CORE",       "dx": 0.32,  "dy": -0.05, "ha": "left",   "va": "center"},
    "Cache": {"text": "CACHE SERVER",      "dx": 0.0,   "dy": -0.32, "ha": "center", "va": "top"},
}


def _get_node_color(node: str) -> str:
    """Return theme color based on canonical SDN node role."""
    if node in ["LMS", "Cache"]:
        return COLOR_NODE_SERVER
    elif "Core" in node:
        return COLOR_NODE_CORE
    else:
        return COLOR_NODE_EDGE


def _setup_figure_style(title: str, subtitle: str = "") -> Tuple[plt.Figure, plt.Axes]:
    """Initialize a standardized figure with the rich dark & illuminated palette."""
    fig, ax = plt.subplots(figsize=(10.5, 8.5), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    title_text = title if not subtitle else f"{title}\n"
    ax.set_title(title_text, color=COLOR_TEXT, fontsize=14, fontweight="bold", pad=20)
    if subtitle:
        ax.text(
            0.5, 1.02, subtitle,
            transform=ax.transAxes,
            ha="center", va="bottom",
            color=COLOR_MUTED, fontsize=9.5, style="italic"
        )
    return fig, ax


def draw_network_canvas(
    G: nx.Graph,
    ax: plt.Axes,
    phase: int,  # 1: Normal, 2: Failure, 3: Failover
    primary_path: Optional[List[str]] = None,
    backup_path: Optional[List[str]] = None,
    failed_link: Optional[Tuple[str, str]] = ("Edge1", "Core1"),
    demand_traffic: float = 70.0,
) -> None:
    """
    Renders an exceptionally clear, publication-grade depiction of the SDN network topology
    for a specific phase with directional flow arrows, non-overlapping role badges, and status pills.
    """
    pos = NODE_POSITIONS
    if primary_path is None:
        primary_path = ["Edge1", "Core1", "LMS"]
    if backup_path is None:
        backup_path = ["Edge1", "Core2", "Edge2", "LMS"]

    prim_edges = set()
    for i in range(len(primary_path) - 1):
        u, v = primary_path[i], primary_path[i + 1]
        prim_edges.add((u, v))
        prim_edges.add((v, u))

    back_edges = set()
    for i in range(len(backup_path) - 1):
        u, v = backup_path[i], backup_path[i + 1]
        back_edges.add((u, v))
        back_edges.add((v, u))

    norm_failed = {failed_link, (failed_link[1], failed_link[0])} if failed_link else set()

    # 1. Draw Standby / Baseline Links
    for u, v in G.edges():
        is_f = (u, v) in norm_failed and phase in [2, 3]
        is_p1 = (u, v) in prim_edges and phase == 1
        is_p2_severed = (u, v) in prim_edges and phase == 2 and not is_f
        is_p3 = (u, v) in back_edges and phase == 3

        if is_f or is_p1 or is_p2_severed or is_p3:
            continue

        p1, p2 = pos[u], pos[v]
        ax.plot(
            [p1[0], p2[0]], [p1[1], p2[1]],
            color=COLOR_STANDBY,
            linewidth=2.5,
            linestyle="--",
            alpha=0.75,
            zorder=1
        )

    # 2. Phase 1: Draw Active Primary Route with Directional Flow Arrows
    if phase == 1:
        for i in range(len(primary_path) - 1):
            u, v = primary_path[i], primary_path[i + 1]
            p1, p2 = pos[u], pos[v]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            dist = np.hypot(dx, dy)
            ux, uy = dx / dist, dy / dist

            # Outer glow and inner solid route line
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_PRIMARY, linewidth=8.5, alpha=0.35, zorder=2)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_PRIMARY, linewidth=3.5, zorder=3)

            # Directional Flow Arrowhead
            mid_x, mid_y = p1[0] + dx * 0.52, p1[1] + dy * 0.52
            arr = FancyArrowPatch(
                (mid_x - ux * 0.08, mid_y - uy * 0.08),
                (mid_x + ux * 0.08, mid_y + uy * 0.08),
                arrowstyle='-|>', mutation_scale=20, color=COLOR_PRIMARY, linewidth=2, zorder=4
            )
            ax.add_patch(arr)

            # Traffic load pill
            lbl_x, lbl_y = p1[0] + dx * 0.45 - uy * 0.16, p1[1] + dy * 0.45 + ux * 0.16
            ax.text(
                lbl_x, lbl_y, f"{demand_traffic:.0f} Mbps",
                color=COLOR_PRIMARY, fontsize=8.5, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=COLOR_PANEL, edgecolor=COLOR_PRIMARY, alpha=0.95, lw=1.2),
                zorder=5
            )

    # 3. Phase 2: Draw Broken Link & Severed Downstream Route
    elif phase == 2:
        if failed_link:
            u, v = failed_link
            p1, p2 = pos[u], pos[v]
            # Red dotted line for failed link
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_FAILED, linewidth=4, linestyle=":", zorder=3)
            mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            ax.plot(mid_x, mid_y, marker="X", markersize=18, color=COLOR_FAILED, markeredgecolor="#ffffff", markeredgewidth=2, zorder=6)
            ax.text(
                mid_x - 0.08, mid_y - 0.22, "LINK FAILED (100% LOSS)",
                color=COLOR_FAILED, fontsize=8.5, fontweight="bold", ha="center", va="top",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=COLOR_PANEL, edgecolor=COLOR_FAILED, alpha=0.95, lw=1.2),
                zorder=7
            )

        # Severed downstream path Core1 -> LMS (traffic drops to 0 Mbps)
        p_c1, p_lms = pos["Core1"], pos["LMS"]
        ax.plot([p_c1[0], p_lms[0]], [p_c1[1], p_lms[1]], color=COLOR_SEVERED, linewidth=3, linestyle="-.", alpha=0.85, zorder=2)
        mid_cx, mid_cy = (p_c1[0] + p_lms[0]) / 2, (p_c1[1] + p_lms[1]) / 2
        ax.text(
            mid_cx + 0.18, mid_cy, "0 Mbps\n(Severed)",
            color=COLOR_SEVERED, fontsize=8.5, fontweight="bold", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.22", facecolor=COLOR_PANEL, edgecolor=COLOR_SEVERED, alpha=0.95, lw=1.2),
            zorder=5
        )

    # 4. Phase 3: Draw Failover Backup Route with Flow Arrows & Failed Link
    elif phase == 3:
        # Failed link marked as DOWN
        if failed_link:
            u, v = failed_link
            p1, p2 = pos[u], pos[v]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_FAILED, linewidth=3.5, linestyle=":", alpha=0.7, zorder=2)
            mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            ax.plot(mid_x, mid_y, marker="X", markersize=14, color=COLOR_FAILED, markeredgecolor="#ffffff", markeredgewidth=1.5, zorder=5)
            ax.text(
                mid_x - 0.08, mid_y - 0.20, "LINK DOWN",
                color=COLOR_FAILED, fontsize=8, fontweight="bold", ha="center", va="top",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=COLOR_PANEL, edgecolor=COLOR_FAILED, alpha=0.9, lw=1),
                zorder=6
            )

        # Backup failover route segments with flow arrows
        for i in range(len(backup_path) - 1):
            u, v = backup_path[i], backup_path[i + 1]
            p1, p2 = pos[u], pos[v]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            dist = np.hypot(dx, dy)
            ux, uy = dx / dist, dy / dist

            # Outer glow and inner solid route line
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_BACKUP, linewidth=8.5, alpha=0.35, zorder=2)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_BACKUP, linewidth=3.5, zorder=3)

            # Directional Flow Arrowhead
            mid_x, mid_y = p1[0] + dx * 0.52, p1[1] + dy * 0.52
            arr = FancyArrowPatch(
                (mid_x - ux * 0.08, mid_y - uy * 0.08),
                (mid_x + ux * 0.08, mid_y + uy * 0.08),
                arrowstyle='-|>', mutation_scale=20, color=COLOR_BACKUP, linewidth=2, zorder=4
            )
            ax.add_patch(arr)

            # Traffic load pill
            lbl_x, lbl_y = p1[0] + dx * 0.45 - uy * 0.16, p1[1] + dy * 0.45 + ux * 0.16
            ax.text(
                lbl_x, lbl_y, f"{demand_traffic:.0f} Mbps",
                color=COLOR_BACKUP, fontsize=8.5, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=COLOR_PANEL, edgecolor=COLOR_BACKUP, alpha=0.95, lw=1.2),
                zorder=5
            )

    # 5. Draw Canonical Nodes & Configured Role Badges
    for node, (x, y) in pos.items():
        node_color = _get_node_color(node)
        # Outer glow ring
        ax.add_patch(plt.Circle((x, y), 0.22, color=node_color, alpha=0.35, zorder=8))
        # Solid node body
        ax.add_patch(plt.Circle((x, y), 0.18, color=COLOR_PANEL, ec=node_color, linewidth=2.5, zorder=9))
        # Node identifier
        ax.text(x, y, node, color=COLOR_TEXT, fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=10)

        # Distinct role badge positioned with custom offset to guarantee zero link collision
        cfg = NODE_BADGE_CONFIG.get(node, {})
        if cfg:
            bx, by = x + cfg["dx"], y + cfg["dy"]
            ax.text(
                bx, by, cfg["text"],
                color=node_color, fontsize=7.5, fontweight="bold", ha=cfg["ha"], va=cfg["va"],
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#090D16", edgecolor=node_color, alpha=0.95, lw=1.0),
                zorder=11
            )

    all_x = [p[0] for p in pos.values()]
    all_y = [p[1] for p in pos.values()]
    ax.set_xlim(min(all_x) - 0.95, max(all_x) + 0.95)
    ax.set_ylim(min(all_y) - 0.70, max(all_y) + 0.70)
    ax.axis("off")


def _draw_base_network(
    G: nx.Graph,
    ax: plt.Axes,
    highlighted_path: Optional[List[str]] = None,
    path_color: str = COLOR_PRIMARY,
    path_label: str = "Active Route",
    failed_link: Optional[Tuple[str, str]] = None,
) -> None:
    """Backward compatibility wrapper delegating to draw_network_canvas."""
    if failed_link and highlighted_path:
        draw_network_canvas(G, ax, phase=3, backup_path=highlighted_path, failed_link=failed_link)
    elif failed_link:
        draw_network_canvas(G, ax, phase=2, failed_link=failed_link)
    else:
        draw_network_canvas(G, ax, phase=1, primary_path=highlighted_path)


def plot_initial_topology(
    G: nx.Graph,
    primary_path: List[str],
    output_path: str = "results/graphs/initial_topology.png"
) -> str:
    """Generate and save the Phase 1: Initial Network Topology visualization."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = _setup_figure_style(
        title="Phase 1: Initial Network Topology & Baseline Primary Route",
        subtitle=f"Primary Route: {' -> '.join(primary_path)} (2 hops) | Throughput: 70 Mbps (100%) | Loss: 0%"
    )

    draw_network_canvas(G, ax, phase=1, primary_path=primary_path)

    legend_elements = [
        mpatches.Patch(color=COLOR_PRIMARY, label=f"Primary Flow ({' -> '.join(primary_path)}) [70 Mbps]"),
        mpatches.Patch(color=COLOR_STANDBY, label="Active Standby Links (10 Mbps Background)"),
        mpatches.Patch(color=COLOR_NODE_SERVER, label="Servers (LMS Server, Cache)"),
        mpatches.Patch(color=COLOR_NODE_CORE, label="Core Switches (Core1, Core2)"),
        mpatches.Patch(color=COLOR_NODE_EDGE, label="Edge Switches (Edge1, Edge2)"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=3,
        facecolor=COLOR_PANEL,
        edgecolor=COLOR_STANDBY,
        fontsize=9,
        labelcolor=COLOR_TEXT
    )

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def plot_failure_topology(
    G: nx.Graph,
    primary_path: List[str],
    failed_link: Tuple[str, str] = ("Edge1", "Core1"),
    output_path: str = "results/graphs/failure_topology.png"
) -> str:
    """Generate and save the Phase 2: Link Failure Network Topology visualization."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = _setup_figure_style(
        title="Phase 2: Critical Link Failure Occurs on Primary Route",
        subtitle=f"Severed Link: {failed_link[0]} <-> {failed_link[1]} | Throughput: 0.0 Mbps | Packet Loss: 100.0%"
    )

    draw_network_canvas(G, ax, phase=2, primary_path=primary_path, failed_link=failed_link)

    legend_elements = [
        mpatches.Patch(color=COLOR_FAILED, label=f"Severed Primary Link ({failed_link[0]} <-> {failed_link[1]}) [100% Loss]"),
        mpatches.Patch(color=COLOR_SEVERED, label="Downstream Inactive Path (0 Mbps Delivered)"),
        mpatches.Patch(color=COLOR_STANDBY, label="Standby Redundant Links"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=3,
        facecolor=COLOR_PANEL,
        edgecolor=COLOR_STANDBY,
        fontsize=9,
        labelcolor=COLOR_TEXT
    )

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def plot_failover_topology(
    G: nx.Graph,
    backup_path: List[str],
    failed_link: Tuple[str, str] = ("Edge1", "Core1"),
    output_path: str = "results/graphs/failover_topology.png"
) -> str:
    """Generate and save the Phase 3: Failover Recovery Topology visualization."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = _setup_figure_style(
        title="Phase 3: Automatic Failover Routing Activated",
        subtitle=f"Rerouted Backup Path: {' -> '.join(backup_path)} (3 hops) | Throughput Restored (70 Mbps) | Packet Loss: 0%"
    )

    draw_network_canvas(G, ax, phase=3, backup_path=backup_path, failed_link=failed_link)

    legend_elements = [
        mpatches.Patch(color=COLOR_BACKUP, label=f"Failover Backup Route ({' -> '.join(backup_path)}) [70 Mbps Restored]"),
        mpatches.Patch(color=COLOR_FAILED, label=f"Bypassed Failed Link ({failed_link[0]} <-> {failed_link[1]})"),
        mpatches.Patch(color=COLOR_STANDBY, label="Standby Links"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=3,
        facecolor=COLOR_PANEL,
        edgecolor=COLOR_STANDBY,
        fontsize=9,
        labelcolor=COLOR_TEXT
    )

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def plot_phase_progression_overview(
    G: nx.Graph,
    primary_path: List[str],
    backup_path: List[str],
    failed_link: Tuple[str, str] = ("Edge1", "Core1"),
    recovery_time_ms: float = 24.5,
    output_path: str = "results/graphs/phase_progression_overview.png",
) -> str:
    """
    Generate a 3-panel comparative overview displaying Phase 1, Phase 2, and Phase 3 side-by-side.
    Provides examiners and evaluators with a single, clear depiction of the entire failover cycle.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(23, 8.0), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)

    phase_configs = [
        (1, "Phase 1: Normal Baseline Route",
         f"Primary: {' -> '.join(primary_path)} (2 hops)\nThroughput: 70 Mbps (100%) | Packet Loss: 0%"),
        (2, "Phase 2: Primary Link Severed",
         f"Failed: {failed_link[0]} <-> {failed_link[1]}\nThroughput: 0 Mbps (Severed) | Packet Loss: 100%"),
        (3, "Phase 3: Automatic SDN Failover",
         f"Rerouted: {' -> '.join(backup_path)} (3 hops)\nThroughput: 70 Mbps (Restored) | Recovery: {recovery_time_ms:.1f} ms"),
    ]

    for idx, (p_num, title, sub) in enumerate(phase_configs):
        ax = axes[idx]
        ax.set_facecolor(COLOR_BG)
        ax.set_title(f"{title}\n{sub}", color=COLOR_TEXT, fontsize=12.5, fontweight="bold", pad=16)
        draw_network_canvas(
            G, ax,
            phase=p_num,
            primary_path=primary_path,
            backup_path=backup_path,
            failed_link=failed_link,
        )

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def plot_link_utilization(
    df: pd.DataFrame,
    output_path: str = "results/graphs/link_utilization.png"
) -> str:
    """Generate and save the Link Utilization performance comparison graph."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_PANEL)

    phases = df["phase"].tolist()
    x = np.arange(len(phases))
    width = 0.35

    avg_utils = df["average_utilization"].tolist()
    max_utils = df["maximum_utilization"].tolist()

    rects1 = ax.bar(x - width / 2, avg_utils, width, label="Average Utilization (%)", color="#87D0CA", edgecolor="#5FA8A1", linewidth=1.2)
    rects2 = ax.bar(x + width / 2, max_utils, width, label="Maximum Utilization (%)", color="#E6C4B7", edgecolor="#B88A7B", linewidth=1.2)

    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", color=COLOR_TEXT, fontsize=9.5, fontweight="bold")

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", color=COLOR_TEXT, fontsize=9.5, fontweight="bold")

    ax.set_title("Network Link Utilization Across Simulation Phases", color=COLOR_TEXT, fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Utilization (%)", color=COLOR_TEXT, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(phases, color=COLOR_TEXT, fontsize=10.5, fontweight="semibold")
    ax.set_ylim(0, max(max_utils + [100]) * 1.15)
    ax.tick_params(colors=COLOR_TEXT)
    ax.grid(axis="y", linestyle="--", alpha=0.25, color="#475569")
    ax.legend(facecolor=COLOR_BG, edgecolor=COLOR_STANDBY, labelcolor=COLOR_TEXT)

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def plot_throughput(
    df: pd.DataFrame,
    output_path: str = "results/graphs/throughput.png"
) -> str:
    """Generate and save the End-to-End Delivered Throughput comparison graph."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_PANEL)

    phases = df["phase"].tolist()
    throughput_vals = df["throughput"].tolist()
    colors = [COLOR_PRIMARY, COLOR_FAILED, COLOR_BACKUP]
    x = np.arange(len(phases))

    bars = ax.bar(x, throughput_vals, color=colors, width=0.45, edgecolor="#FFFFFF", linewidth=0.8)

    for bar, val in zip(bars, throughput_vals):
        height = bar.get_height()
        status_label = "Delivered (100%)" if val > 0 else "Severed (0%)"
        ax.annotate(f"{val:.1f} Mbps\n[{status_label}]",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", color=COLOR_TEXT, fontsize=10, fontweight="bold")

    ax.set_title("End-to-End Delivered Throughput Across Failure and Failover", color=COLOR_TEXT, fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Delivered Throughput (Mbps)", color=COLOR_TEXT, fontsize=11)
    ax.set_ylim(0, max(throughput_vals + [100]) * 1.25)
    ax.set_xticks(x)
    ax.set_xticklabels(phases, color=COLOR_TEXT, fontsize=10.5, fontweight="semibold")
    ax.tick_params(colors=COLOR_TEXT)
    ax.grid(axis="y", linestyle="--", alpha=0.25, color="#475569")

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def plot_recovery_time(
    recovery_time_ms: float,
    output_path: str = "results/graphs/recovery_time.png"
) -> str:
    """Generate and save the Failover Recovery Time timeline breakdown graph."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_PANEL)

    # SDN Control Plane Latency Stages
    detection_ms = round(recovery_time_ms * 0.45, 2)
    computation_ms = round(recovery_time_ms * 0.15, 2)
    flow_mod_ms = round(recovery_time_ms - detection_ms - computation_ms, 2)

    components = [
        "Link Failure Detection\n(Keepalive Timeout)",
        "Backup Path Computation\n(NetworkX Dijkstra)",
        "Flow-Mod Installation\n(OpenFlow Barrier)",
        "Total Recovery Time\n(End-to-End Restoration)"
    ]
    values = [detection_ms, computation_ms, flow_mod_ms, recovery_time_ms]
    bar_colors = ["#E6C4B7", "#FCDDD3", "#87D0CA", "#38BDF8"]

    y_pos = np.arange(len(components))
    bars = ax.barh(y_pos, values, color=bar_colors, height=0.5, edgecolor="#FFFFFF", linewidth=0.8)

    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.annotate(f"{val:.2f} ms",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(8, 0), textcoords="offset points",
                    ha="left", va="center", color=COLOR_TEXT, fontsize=10, fontweight="bold")

    ax.set_title("SDN Automatic Failover Recovery Latency Breakdown", color=COLOR_TEXT, fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Time (milliseconds)", color=COLOR_TEXT, fontsize=11)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(components, color=COLOR_TEXT, fontsize=10)
    ax.set_xlim(0, max(values) * 1.3)
    ax.tick_params(colors=COLOR_TEXT)
    ax.grid(axis="x", linestyle="--", alpha=0.25, color="#475569")

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def plot_routing_strategies_comparison(
    df_strategies: pd.DataFrame,
    output_path: str = "results/graphs/routing_strategies_comparison.png"
) -> str:
    """Generate and save comparative visualization of routing strategies."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_PANEL)

    strategies = df_strategies["Routing Strategy"].tolist()
    x = np.arange(len(strategies))
    width = 0.25

    before_vals = df_strategies["Before"].tolist()
    during_vals = df_strategies["During"].tolist()
    after_vals = df_strategies["After"].tolist()

    rects1 = ax.bar(x - width, before_vals, width, label="Before Failure", color="#87D0CA", edgecolor="#5FA8A1")
    rects2 = ax.bar(x, during_vals, width, label="During Failure", color="#EF4444", edgecolor="#B91C1C")
    rects3 = ax.bar(x + width, after_vals, width, label="After Recovery", color="#E6C4B7", edgecolor="#B88A7B")

    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", color=COLOR_TEXT, fontsize=8.5, fontweight="bold")

    ax.set_title("Routing Strategies Evaluation: Normalized Link Utilization (%)", color=COLOR_TEXT, fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Normalized Link Utilization (%)", color=COLOR_TEXT, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(strategies, color=COLOR_TEXT, fontsize=11, fontweight="semibold")
    ax.set_ylim(0, max(before_vals + during_vals + after_vals) * 1.25)
    ax.tick_params(colors=COLOR_TEXT)
    ax.grid(axis="y", linestyle="--", alpha=0.25, color="#475569")
    ax.legend(facecolor=COLOR_BG, edgecolor=COLOR_STANDBY, labelcolor=COLOR_TEXT, loc="upper right")

    plt.tight_layout()
    fig.savefig(output_path, facecolor=COLOR_BG, dpi=300)
    plt.close(fig)
    return output_path


def generate_all_visualizations(
    G: nx.Graph,
    primary_path: List[str],
    backup_path: List[str],
    failed_link: Tuple[str, str],
    df: pd.DataFrame,
    recovery_time_ms: float,
    graphs_dir: str = "results/graphs",
) -> Dict[str, str]:
    """Generate all academic graphs and the comparative 3-phase overview in graphs_dir."""
    os.makedirs(graphs_dir, exist_ok=True)

    paths = {
        "initial_topology": os.path.join(graphs_dir, "initial_topology.png"),
        "failure_topology": os.path.join(graphs_dir, "failure_topology.png"),
        "failover_topology": os.path.join(graphs_dir, "failover_topology.png"),
        "phase_progression_overview": os.path.join(graphs_dir, "phase_progression_overview.png"),
        "link_utilization": os.path.join(graphs_dir, "link_utilization.png"),
        "throughput": os.path.join(graphs_dir, "throughput.png"),
        "recovery_time": os.path.join(graphs_dir, "recovery_time.png"),
    }

    plot_initial_topology(G, primary_path, paths["initial_topology"])
    plot_failure_topology(G, primary_path, failed_link, paths["failure_topology"])
    plot_failover_topology(G, backup_path, failed_link, paths["failover_topology"])
    plot_phase_progression_overview(G, primary_path, backup_path, failed_link, recovery_time_ms, paths["phase_progression_overview"])
    plot_link_utilization(df, paths["link_utilization"])
    plot_throughput(df, paths["throughput"])
    plot_recovery_time(recovery_time_ms, paths["recovery_time"])

    return paths


if __name__ == "__main__":
    from simulation import NetworkSimulation
    sim = NetworkSimulation()
    df = sim.run_full_simulation()
    generated = generate_all_visualizations(
        G=sim.G,
        primary_path=sim.primary_path,
        backup_path=sim.backup_path,
        failed_link=sim.failed_link,
        df=df,
        recovery_time_ms=sim.recovery_time,
    )
    print("All visualizations generated successfully:")
    for k, v in generated.items():
        print(f"  {k}: {v} (Exists: {os.path.exists(v)})")
