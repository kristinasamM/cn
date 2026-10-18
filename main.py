"""
main.py
=======
Main Execution Entry Point for Network Resilience SDN Failover Simulation.

Reproduces the simulation methodology described in:
"Analysis of Software-Defined Networking Resilience to Link Failure through Failover Routing Simulation"
Authors: Naharotul Istiqomah, Muhammad David Irsyadus Sholihin, Innasya' Putri Hidayati
Publication: G-Tech: Jurnal Teknologi Terapan, Vol. 10, No. 1, 2026.
DOI: https://doi.org/10.70609/g-tech.v10i1.8971

Execution:
    python main.py
"""

import os
import sys
from topology import create_topology, print_topology, TOPOLOGY_LINKS
from simulation import NetworkSimulation
from metrics import save_results_to_csv, compile_results_dataframe
from visualization import (
    plot_initial_topology,
    plot_failure_topology,
    plot_failover_topology,
    plot_phase_progression_overview,
    plot_link_utilization,
    plot_throughput,
    plot_recovery_time,
    plot_routing_strategies_comparison,
)


def print_banner(text: str) -> None:
    """Print standard section divider banner."""
    print("=" * 60)
    print(text)
    print("=" * 60)


def main() -> int:
    """Execute the complete research paper simulation pipeline."""
    # Ensure working output directories exist (Section 34: Error Handling)
    os.makedirs("results/csv", exist_ok=True)
    os.makedirs("results/graphs", exist_ok=True)

    # Set console encoding to UTF-8 with fallback to avoid cp1252 UnicodeEncodeError on Windows
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass

    print_banner("NETWORK RESILIENCE -- SDN FAILOVER SIMULATION")
    print("Research Reproduction: Analysis of SDN Resilience to Link Failure")
    print("G-Tech: Jurnal Teknologi Terapan (2026)\n")

    # Step 1: Create network topology
    G = create_topology(default_capacity=100.0)

    # Step 2: Print topology information
    print_topology(G)
    print()

    # Step 3: Initialize Simulation Engine
    sim = NetworkSimulation(
        G=G,
        source="Edge1",
        destination="LMS",
        demand_traffic=70.0,
        background_traffic=10.0,
    )

    # =========================================================================
    # PHASE 1: Normal Operation
    # =========================================================================
    print_banner("PHASE 1 -- NORMAL OPERATION")
    try:
        p1_record = sim.run_normal_operation()
    except Exception as e:
        print(f"Error during normal operation: {e}")
        return 1

    primary_path_str = " -> ".join(sim.primary_path)
    print(f"Primary Path:\n{primary_path_str}\n")
    print(f"Primary Flow: {sim.source} to {sim.destination} ({sim.demand_traffic} Mbps)")
    print(f"Average Utilization: {p1_record['average_utilization']}%")
    print(f"Maximum Utilization: {p1_record['maximum_utilization']}%")
    print(f"Throughput:          {p1_record['throughput']} Mbps [Active / 100%]")
    print(f"Packet Loss:         {p1_record['packet_loss']}%")
    print(f"Recovery Time:       {p1_record['recovery_time']} ms")

    # Save Phase 1 Initial Topology Graph
    init_graph_path = "results/graphs/initial_topology.png"
    plot_initial_topology(sim.G, sim.primary_path, init_graph_path)
    print(f"-> Generated Initial Topology: {init_graph_path}\n")

    # =========================================================================
    # PHASE 2: Link Failure
    # =========================================================================
    print_banner("PHASE 2 -- LINK FAILURE")
    failed_u, failed_v = "Edge1", "Core1"
    print(f"FAILED LINK:\n{failed_u} <-> {failed_v}\n")

    try:
        p2_record = sim.simulate_link_failure(u=failed_u, v=failed_v)
        print("Link status changed to FAILED.")
    except ValueError as val_err:
        print(f"Invalid failure link: {val_err}")
        return 1

    # Verify primary path availability
    primary_available = sim.is_path_available(sim.primary_path)
    if not primary_available:
        print(f"Detection: Primary Path ({primary_path_str}) is UNAVAILABLE.")

    print(f"Average Utilization: {p2_record['average_utilization']}%")
    print(f"Maximum Utilization: {p2_record['maximum_utilization']}%")
    print(f"Throughput:          {p2_record['throughput']} Mbps [SEVERED / 0%]")
    print(f"Packet Loss:         {p2_record['packet_loss']}% [CRITICAL FLOW DROP]")
    print(f"Recovery Time:       {p2_record['recovery_time']} ms")

    # Save Phase 2 Failure Topology Graph
    fail_graph_path = "results/graphs/failure_topology.png"
    plot_failure_topology(sim.G, sim.primary_path, (failed_u, failed_v), fail_graph_path)
    print(f"-> Generated Failure Topology: {fail_graph_path}\n")

    # =========================================================================
    # PHASE 3: Failover Recovery
    # =========================================================================
    print_banner("PHASE 3 -- FAILOVER RECOVERY")
    try:
        p3_record = sim.execute_failover()
    except RuntimeError as r_err:
        # Section 34 requirement: Display 'No alternative path available.' gracefully
        print(f"{r_err}")
        return 1

    backup_path_str = " -> ".join(sim.backup_path)
    print(f"Backup Path Selected:\n{backup_path_str}\n")
    print("Status: Automatic Failover Activated | Traffic Rerouted.")
    print("\nPerformance After Failover:\n")
    print(f"Average Utilization: {p3_record['average_utilization']}%")
    print(f"Maximum Utilization: {p3_record['maximum_utilization']}%")
    print(f"Throughput:          {p3_record['throughput']} Mbps [RESTORED / 100%]")
    print(f"Packet Loss:         {p3_record['packet_loss']}% [RECOVERED]")
    print(f"Recovery Time:       {p3_record['recovery_time']} ms")

    # Save Phase 3 Failover Topology Graph
    failover_graph_path = "results/graphs/failover_topology.png"
    plot_failover_topology(sim.G, sim.backup_path, (failed_u, failed_v), failover_graph_path)
    print(f"-> Generated Failover Topology: {failover_graph_path}\n")

    # Save 3-Phase Progression Overview Graph
    overview_graph_path = "results/graphs/phase_progression_overview.png"
    plot_phase_progression_overview(sim.G, sim.primary_path, sim.backup_path, (failed_u, failed_v), sim.recovery_time, overview_graph_path)
    print(f"-> Generated 3-Phase Overview:  {overview_graph_path}\n")

    # =========================================================================
    # Metrics Compilation, CSV Export & Performance Graphs
    # =========================================================================
    print_banner("CONSOLIDATED RESULTS & EXPORT")
    df = compile_results_dataframe(sim.records)

    csv_path = "results/csv/simulation_results.csv"
    save_results_to_csv(df, csv_path)
    print(f"Results CSV successfully saved to:\n{os.path.abspath(csv_path)}\n")

    print("Simulation Results Summary Table:")
    print("-" * 75)
    print(df.to_string(index=False))
    print("-" * 75)
    print()

    # Generate Performance Evaluation Graphs
    util_graph_path = "results/graphs/link_utilization.png"
    tp_graph_path = "results/graphs/throughput.png"
    rec_graph_path = "results/graphs/recovery_time.png"

    plot_link_utilization(df, util_graph_path)
    plot_throughput(df, tp_graph_path)
    plot_recovery_time(sim.recovery_time, rec_graph_path)

    print("Performance Evaluation Graphs:")
    print(f"- Link Utilization Graph: {util_graph_path}")
    print(f"- Throughput Graph:       {tp_graph_path}")
    print(f"- Recovery Time Graph:    {rec_graph_path}")
    print()

    # =========================================================================
    # Routing Strategies Comparison (Specification Section 29 & 30)
    # =========================================================================
    print_banner("ROUTING STRATEGIES EVALUATION (SECTIONS 29 & 30)")
    strategies_df = sim.compare_routing_strategies()
    strat_csv_path = "results/csv/routing_strategies_comparison.csv"
    strategies_df.to_csv(strat_csv_path, index=False)
    strat_graph_path = "results/graphs/routing_strategies_comparison.png"
    plot_routing_strategies_comparison(strategies_df, strat_graph_path)

    print(strategies_df[["Routing Strategy", "Path", "Hops", "Before", "During", "After", "Throughput_After", "Packet_Loss_After"]].to_string(index=False))
    print(f"\n-> Saved Strategies Comparison CSV:   {strat_csv_path}")
    print(f"-> Saved Strategies Comparison Graph: {strat_graph_path}\n")

    # =========================================================================
    # Optional Extension: Network Restore / Failback (Specification Section 37)
    # =========================================================================
    print_banner("EXTENSION: NETWORK RESTORE / FAILBACK (SECTION 37)")
    restored = sim.restore_primary_link("Edge1", "Core1")
    if restored:
        print(f"Primary Link ({failed_u} <-> {failed_v}) RESTORED to ACTIVE.")
        print("Network resilience verification completed: Link can be recovered for failback.")
    print()

    print_banner("SIMULATION EXECUTION COMPLETED SUCCESSFULLY")
    print("All 3 phases verified. All graphs and CSV results generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
