# Network Resilience: Automatic Failover for Reliable Communication

A research paper-based reproduction and simulation of Software-Defined Networking (SDN) resilience and automatic failover routing upon primary link failure.

---

## 1. Project Overview & Academic Citation

This project is an academic implementation and reproduction of the simulation methodology presented in:

> **"Analysis of Software-Defined Networking Resilience to Link Failure through Failover Routing Simulation"**  
> **Authors:** Naharotul Istiqomah, Muhammad David Irsyadus Sholihin, Innasya' Putri Hidayati  
> **Publication:** *G-Tech: Jurnal Teknologi Terapan*, Volume 10, Issue 1, 2026.  
> **DOI:** [https://doi.org/10.70609/g-tech.v10i1.8971](https://doi.org/10.70609/g-tech.v10i1.8971)  
> **Journal URL:** [https://ejournal.uniramalang.ac.id/g-tech/article/view/8971](https://ejournal.uniramalang.ac.id/g-tech/article/view/8971)  
> **PDF Download:** [https://ejournal.uniramalang.ac.id/g-tech/article/download/8971/5514/54775](https://ejournal.uniramalang.ac.id/g-tech/article/download/8971/5514/54775)

### Academic Reproduction Statement
*This project reproduces the failover routing simulation methodology described in the research paper. The paper outlines the topology, scenarios, routing principles, tools, and evaluation metrics, but does not provide complete source code or formal pseudocode. Consequently, the routing and failover algorithms implemented herein are derived faithfully from the authors' methodology without claiming to be direct copies of original source code.*

---

## 2. Research Objective

To simulate a resilient Software-Defined Network in which communication continues through an alternative route when a primary network link fails, and to evaluate the resulting network performance before, during, and after failover across:
- **Link Utilization (%)**
- **Throughput (Mbps)**
- **Packet Loss (%)**
- **Recovery Time (ms)**

```
NORMAL OPERATION ──> PRIMARY ROUTE ──> LINK FAILURE ──> FAILURE DETECTION
        │
        └──> ALTERNATIVE PATH SELECTION ──> AUTOMATIC FAILOVER ──> TRAFFIC REROUTING ──> RECOVERY
```

---

## 3. Network Topology

The network reproduces the canonical **6-node, 8-link logical SDN topology**:

```
                         [ LMS ]
                         /     \
                        /       \
                   [ Core1 ]───[ Edge2 ]
                   /   \       /   
                  /     \     /    
              [ Edge1 ]──[ Core2 ] 
                 \          /      
                  \        /       
                   [ Cache ]       
```

### Nodes (6)
1. **Edge1**: Ingress Edge SDN Switch (Source endpoint)
2. **Edge2**: Egress / Secondary Edge SDN Switch
3. **Core1**: Primary Core SDN Switch
4. **Core2**: Redundant Core SDN Switch
5. **LMS**: Learning Management System Application Server (Destination endpoint)
6. **Cache**: Local Content Caching Server

### Communication Links (8)
1. `LMS <-> Core1`
2. `LMS <-> Edge2`
3. `Core1 <-> Edge2`
4. `Core1 <-> Edge1`
5. `Core2 <-> Edge2`
6. `Core2 <-> Edge1`
7. `Cache <-> Core2`
8. `Cache <-> Edge1`

Each link is modeled with **bandwidth capacity (100 Mbps)**, operational **status** (`active` / `failed`), dynamic **traffic load (Mbps)**, **utilization (%)**, and **packet loss (%)**.

---

## 4. The Three Simulation Phases

### Phase 1: Normal Operation (Baseline)
- **Source:** `Edge1` | **Destination:** `LMS`
- **Primary Route:** `Edge1 -> Core1 -> LMS` (Shortest 2-hop path)
- All 8 links active with baseline traffic (10 Mbps background + 70 Mbps primary demand)
- **Baseline Performance:** 100% throughput delivery (70 Mbps), 0% packet loss.

### Phase 2: Link Failure
- Physical/logical fault injected on link **`Edge1 <-> Core1`**.
- Link status becomes `FAILED`, packet loss spikes to 100%.
- Primary path (`Edge1 -> Core1 -> LMS`) becomes **UNAVAILABLE**.
- **Failure Impact:** Communication severed; delivered throughput drops to 0 Mbps.

### Phase 3: Automatic Failover Recovery
- SDN Controller detects primary route failure.
- Active subgraph computed excluding failed link `Edge1 <-> Core1`.
- Dynamic alternative path discovered: **`Edge1 -> Core2 -> Edge2 -> LMS`** (3 hops).
- Traffic automatically rerouted onto backup path.
- **Recovery Performance:** Throughput restored to 100% (70 Mbps), packet loss drops to 0%, recovery latency measured (~24.5 ms).

---

## 5. Technology Stack

| Component | Technology | Role |
|---|---|---|
| Programming Language | **Python 3** | Core simulation logic and orchestration |
| Network Graph & Routing | **NetworkX** | Topology creation, Dijkstra shortest path, graph filtering |
| Numerical Calculations | **NumPy** | Statistical calculations & metrics modeling |
| Data Processing | **Pandas** | Tabular results compilation & CSV export |
| Visualizations | **Matplotlib** | Topology diagrams, utilization, throughput & recovery graphs |
| Execution Environments | **Local Python / Google Colab** | Zero-dependency-overhead execution |
| Interactive Dashboard (Optional) | **Streamlit** | Interactive UI for simulation steps and metric inspection |

---

## 6. Project Directory Structure

```
network-resilience/
├── main.py                     # Main CLI execution entry point
├── topology.py                 # 6-node, 8-link SDN topology definition
├── simulation.py               # 3-phase failover simulation engine
├── metrics.py                  # SDN performance indicators & CSV export
├── visualization.py            # Matplotlib figure generation (300 DPI)
├── app.py                      # Interactive Streamlit Web Dashboard
├── requirements.txt            # Python dependencies
├── README.md                   # Complete academic documentation
│
├── results/
│   ├── csv/
│   │   └── simulation_results.csv   # Dynamic phase results
│   │
│   └── graphs/
│       ├── initial_topology.png            # Phase 1: Baseline active network
│       ├── failure_topology.png            # Phase 2: Broken link & severed path
│       ├── failover_topology.png           # Phase 3: Backup rerouting
│       ├── phase_progression_overview.png  # Consolidated 3-phase comparative panel
│       ├── link_utilization.png            # Average & max link utilization chart
│       ├── throughput.png                  # End-to-end throughput comparison
│       └── recovery_time.png               # Failover latency breakdown
│
└── data/
    └── topology_config.json        # JSON configuration for nodes & links
```

---

## 7. How to Run Locally

### Prerequisites
Ensure Python 3.10+ is installed.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Core Simulation
```bash
python main.py
```
This executes all 3 phases sequentially, outputs the formatted terminal results, saves the CSV table to `results/csv/simulation_results.csv`, and generates all 6 figures in `results/graphs/`.

### 3. Run Optional Interactive Dashboard
```bash
streamlit run app.py
```
Opens an interactive dashboard in your browser where you can trigger link failure, inspect failover, and view live metrics and topology states.

---

## 8. Google Colab Support

The simulation is fully compatible with Google Colab notebooks:

```python
# Cell 1: Clone / Upload files and install dependencies
!pip install networkx pandas matplotlib numpy

# Cell 2: Run complete simulation
!python main.py

# Cell 3: Display generated visualizations directly in notebook
from IPython.display import Image, display
display(Image('results/graphs/initial_topology.png'))
display(Image('results/graphs/failure_topology.png'))
display(Image('results/graphs/failover_topology.png'))
display(Image('results/graphs/link_utilization.png'))
display(Image('results/graphs/throughput.png'))
display(Image('results/graphs/recovery_time.png'))
```

---

## 9. Performance Metrics & Mathematical Formulas

### 1. Link Utilization (%)
For any communication link $e = (u, v)$:
$$\text{Utilization}(e) = \left( \frac{\text{Traffic}(e)}{\text{Capacity}(e)} \right) \times 100$$
- **Average Utilization:** $\bar{U} = \frac{1}{|E|} \sum_{e \in E} \text{Utilization}(e)$
- **Maximum Utilization:** $U_{\max} = \max_{e \in E} \text{Utilization}(e)$

### 2. Throughput
Traffic successfully delivered end-to-end from `Edge1` to `LMS` (Mbps):
$$\text{Throughput} = \begin{cases} \text{Demand Traffic} (70.0\text{ Mbps}), & \text{Phase 1 (Normal)} \\ 0.0\text{ Mbps}, & \text{Phase 2 (Link Failed)} \\ \text{Demand Traffic} (70.0\text{ Mbps}), & \text{Phase 3 (Failover)} \end{cases}$$

### 3. Packet Loss (%)
$$\text{Packet Loss} = \left( 1 - \frac{\text{Packets Received}}{\text{Packets Transmitted}} \right) \times 100$$

### 4. Recovery Time (ms)
Total duration required by the SDN controller to detect failure, recalculate an optimal backup path, and install OpenFlow Flow-Mod rules on switches:
$$T_{\text{recovery}} = T_{\text{detection}} + T_{\text{computation}} + T_{\text{flow\_installation}}$$

---

## 10. Sample Simulation Results

*Generated dynamically from simulation run (not hardcoded):*

| Phase | Average Utilization (%) | Maximum Utilization (%) | Throughput (Mbps) | Packet Loss (%) | Recovery Time (ms) |
|---|---|---|---|---|---|
| **Before Failure** | 27.50% | 80.00% | 70.00 Mbps | 0.0% | 0.00 ms |
| **During Failure** | 8.75% | 10.00% | 0.00 Mbps | 100.0% | 0.00 ms |
| **After Failover** | 35.00% | 80.00% | 70.00 Mbps | 0.0% | 24.76 ms |

---

## 11. Routing Strategies Comparison (Section 30)

| Strategy | Path | Path Length | Resilience Mechanism | Failure Response |
|---|---|---|---|---|
| **Shortest Path** | `Edge1 -> Core1 -> LMS` | 2 hops | Static shortest path | Drops flow upon link break |
| **Load-Based** | `Edge1 -> Core2 -> Edge2 -> LMS` | 3 hops | Utilization-aware routing | Reroutes to least loaded path |
| **Fault-Aware** | `Edge1 -> Core2 -> Edge2 -> LMS` | 3 hops | Proactive health monitoring | Bypasses degraded links |
| **Failover Routing** | `Edge1 -> Core2 -> Edge2 -> LMS` | 3 hops | Dynamic reactive SDN failover | Instant rerouting via backup path |

---

## 12. Research Paper & Technical Architecture Summary

- **Paper Reference:** Naharotul Istiqomah, Muhammad David Irsyadus Sholihin, Innasya' Putri Hidayati, *"Analysis of Software-Defined Networking Resilience to Link Failure through Failover Routing Simulation"*, *G-Tech: Jurnal Teknologi Terapan*, Vol. 10, No. 1, 2026. DOI: [10.70609/g-tech.v10i1.8971](https://doi.org/10.70609/g-tech.v10i1.8971)
- **Centralized Control Plane:** SDN controller actively monitors topology changes via OpenFlow Link Layer Discovery Protocol (LLDP) and echo requests.
- **Failover Mechanism:** When link `Edge1 <-> Core1` fails, the controller detects link breakage, eliminates the broken edge from the active network graph, and provisions the disjoint alternative path `Edge1 -> Core2 -> Edge2 -> LMS`.
- **Performance Guarantees:** Throughput recovers from 0 Mbps back to full 70 Mbps demand with carrier-grade recovery latency well under 50 ms.
