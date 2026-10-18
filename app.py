"""
app.py
======
Interactive SDN Resilience & Automatic Failover Dashboard.

Rich Dark & Illuminated Palette (Featuring user-provided swatch highlights):
- Soft Mint Teal:   #87D0CA (Primary flows, active pills, healthy states)
- Soft Blush Peach: #FCDDD3 (Edge nodes, critical fault alerts)
- Warm Dusty Rose:  #E6C4B7 (Servers, failover restoration)
- Deep Midnight:    #0B1120 / #131E33 (Rich dark background)
- Pure Crisp Text:  #F8FAFC / #FFFFFF (100% readable)
"""

import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from topology import get_topology_info
from simulation import NetworkSimulation
from metrics import (
    calculate_average_utilization,
    calculate_maximum_utilization,
)
from visualization import (
    _setup_figure_style,
    draw_network_canvas,
)

# -----------------------------------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SDN Resilience Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Rich Dark & Vibrant Highlight Design System
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Rich Dark Midnight Canvas */
    .stApp {
        background: radial-gradient(circle at 20% 15%, #0f192d 0%, #080d18 100%) !important;
        color: #F8FAFC !important;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.75rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1400px !important;
    }

    /* Header Bar */
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 1.5rem;
    }
    .header-title {
        font-size: 1.65rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-subtitle {
        font-size: 0.88rem;
        color: #94A3B8;
        margin-top: 0.25rem;
        font-weight: 500;
    }

    /* Status Badges with Glowing Borders */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.825rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .status-normal {
        background-color: rgba(135, 208, 202, 0.15);
        color: #87D0CA;
        border: 1.5px solid #87D0CA;
        box-shadow: 0 0 12px rgba(135, 208, 202, 0.3);
    }
    .status-failure {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1.5px solid #EF4444;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
    }
    .status-failover {
        background-color: rgba(230, 196, 183, 0.15);
        color: #E6C4B7;
        border: 1.5px solid #E6C4B7;
        box-shadow: 0 0 12px rgba(230, 196, 183, 0.3);
    }
    .status-recovery {
        background-color: rgba(135, 208, 202, 0.15);
        color: #87D0CA;
        border: 1.5px solid #87D0CA;
        box-shadow: 0 0 12px rgba(135, 208, 202, 0.3);
    }

    /* Sleek Dark Metric Cards with Glowing Top Border */
    .metric-card {
        background: #111B2E;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        min-height: 92px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #334155;
    }
    .metric-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .metric-number {
        font-size: 1.45rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .metric-desc {
        font-size: 0.775rem;
        color: #64748B;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Action Buttons (Tactile Dark Buttons with Hover Glow) */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        border: 1.5px solid #24334C !important;
        background-color: #131E33 !important;
        color: #F1F5F9 !important;
        padding: 10px 18px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #1A2946 !important;
        border-color: #87D0CA !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(135, 208, 202, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* ===================================================================== */
    /* VIBRANT GLOWING TAB PILLS (Crisp Contrast & Zero Streamlit Red Line)  */
    /* ===================================================================== */
    div[data-testid="stTabs"] > div:first-child {
        background-color: #0E1624 !important;
        padding: 8px !important;
        border-radius: 12px !important;
        border: 1px solid #1C2B40 !important;
        margin-bottom: 1.25rem !important;
        gap: 8px !important;
        display: flex !important;
    }
    div[data-testid="stTabs"] button {
        background-color: #131E30 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        border: 1px solid #1F3048 !important;
        transition: all 0.18s ease-in-out !important;
    }
    div[data-testid="stTabs"] button p {
        color: #CBD5E1 !important; /* Crisp, readable light text */
        font-weight: 700 !important;
        font-size: 0.90rem !important;
        margin: 0 !important;
    }
    div[data-testid="stTabs"] button:hover {
        background-color: #1A2840 !important;
        border-color: #38BDF8 !important;
    }
    div[data-testid="stTabs"] button:hover p {
        color: #FFFFFF !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #16263B !important;
        border: 1.5px solid #87D0CA !important;
        box-shadow: 0 0 16px rgba(135, 208, 202, 0.45) !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Completely eliminate any Streamlit tab underline / border */
    [data-baseweb="tab-highlight"],
    [data-baseweb="tab-border"],
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] div[data-baseweb="tab-border"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        background: transparent !important;
    }

    /* Clean Card Container */
    .content-box {
        background-color: #111B2E;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
    }
    .box-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Dataframe Table Enhancements */
    [data-testid="stDataFrame"] {
        border: 1px solid #1E293B;
        border-radius: 8px;
        background-color: #111B2E;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Stateful Session Handling
# -----------------------------------------------------------------------------
def init_session():
    """Initialize stateful simulation objects."""
    if "sim" not in st.session_state:
        st.session_state.sim = NetworkSimulation()
        st.session_state.state = "NORMAL"
        st.session_state.sim.run_normal_operation()
        st.session_state.metrics_history = [dict(st.session_state.sim.records[0])]


init_session()
sim: NetworkSimulation = st.session_state.sim
current_record = sim.records[-1] if sim.records else {}


# -----------------------------------------------------------------------------
# Top Header Bar (Rich Dark & Swatch Highlight)
# -----------------------------------------------------------------------------
status_map = {
    "NORMAL": ("status-normal", "● NORMAL ROUTING (PRIMARY)"),
    "FAILURE": ("status-failure", "● CRITICAL LINK SEVERED"),
    "FAILOVER": ("status-failover", "● AUTOMATIC FAILOVER RESTORED"),
    "RECOVERY": ("status-recovery", "● RESTORED TO PRIMARY"),
}
css_badge, status_label = status_map.get(st.session_state.state, ("status-normal", "● NORMAL"))

st.markdown(f"""
<div class="header-bar">
    <div>
        <h1 class="header-title">⚡ SDN Resilience & Failover Benchmark</h1>
        <div class="header-subtitle">
            Carrier-grade automatic failover simulation · Reproducing Istiqomah et al., G-Tech 2026
        </div>
    </div>
    <div>
        <span class="status-badge {css_badge}">{status_label}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Action Bar: 4 Uniform Clean Buttons in 1 Row
# -----------------------------------------------------------------------------
col_b1, col_b2, col_b3, col_b4 = st.columns(4)

with col_b1:
    if st.button("▶ 1. Baseline Route", use_container_width=True):
        st.session_state.sim = NetworkSimulation()
        st.session_state.state = "NORMAL"
        st.session_state.sim.run_normal_operation()
        st.session_state.metrics_history = [dict(st.session_state.sim.records[0])]
        st.rerun()

with col_b2:
    if st.button("⚠️ 2. Sever Link (Edge1 ↔ Core1)", use_container_width=True):
        st.session_state.sim.simulate_link_failure("Edge1", "Core1")
        st.session_state.state = "FAILURE"
        st.session_state.metrics_history.append(dict(st.session_state.sim.records[-1]))
        st.rerun()

with col_b3:
    if st.button("⚡ 3. Execute SDN Failover", use_container_width=True):
        try:
            st.session_state.sim.execute_failover()
            st.session_state.state = "FAILOVER"
            st.session_state.metrics_history.append(dict(st.session_state.sim.records[-1]))
        except Exception:
            pass
        st.rerun()

with col_b4:
    if st.button("↺ 4. Restore Primary Link", use_container_width=True):
        st.session_state.sim.restore_primary_link("Edge1", "Core1")
        st.session_state.sim.run_normal_operation()
        st.session_state.state = "RECOVERY"
        st.session_state.metrics_history.append(dict(st.session_state.sim.records[-1]))
        st.rerun()

st.write("")

# -----------------------------------------------------------------------------
# Metric Cards: 4 Uniform Tiles with Palette Accent Borders
# -----------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

# Determine path information
if st.session_state.state in ["NORMAL", "RECOVERY"]:
    path_str = "Edge1 → Core1 → LMS"
    path_hops = "2 hops (Shortest Path)"
elif st.session_state.state == "FAILURE":
    path_str = "Path Broken"
    path_hops = "Edge1 ↔ Core1 Severed"
else:
    path_str = "Edge1 → Core2 → Edge2 → LMS"
    path_hops = "3 hops (Disjoint Backup Route)"

tput = current_record.get('throughput', 0.0)
loss = current_record.get('packet_loss', 0.0)
avg_load = current_record.get('average_utilization', calculate_average_utilization(sim.G))

with m1:
    st.markdown(f"""
    <div class="metric-card" style="border-top: 4px solid #87D0CA;">
        <div class="metric-title">Active Route</div>
        <div class="metric-number" style="font-size: 1.05rem; font-family:'JetBrains Mono'; color:#87D0CA;">{path_str}</div>
        <div class="metric-desc">{path_hops}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    tput_color = "#F87171" if tput == 0 else "#87D0CA"
    st.markdown(f"""
    <div class="metric-card" style="border-top: 4px solid #87D0CA;">
        <div class="metric-title">Delivered Throughput</div>
        <div class="metric-number" style="color: {tput_color};">{tput:.1f} <span style="font-size:0.85rem; color:#94A3B8; font-weight:normal;">Mbps</span></div>
        <div class="metric-desc">Target demand: 70.0 Mbps continuous</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    loss_color = "#F87171" if loss > 0 else "#87D0CA"
    loss_desc = "100% loss during physical disconnect" if loss > 0 else "0% packet drop (Carrier grade)"
    st.markdown(f"""
    <div class="metric-card" style="border-top: 4px solid #FCDDD3;">
        <div class="metric-title">Packet Loss Rate</div>
        <div class="metric-number" style="color: {loss_color};">{loss:.1f}%</div>
        <div class="metric-desc">{loss_desc}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    rec_val = f"{sim.recovery_time:.2f} ms" if st.session_state.state == "FAILOVER" else "Sub-50ms Std"
    rec_desc = "Carrier-grade compliant restoration" if st.session_state.state == "FAILOVER" else "Fast-Failover group table"
    st.markdown(f"""
    <div class="metric-card" style="border-top: 4px solid #E6C4B7;">
        <div class="metric-title">Failover Latency</div>
        <div class="metric-number" style="color: #E6C4B7;">{rec_val}</div>
        <div class="metric-desc">{rec_desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# Main Navigation Tabs (High Contrast & Clear Visibility)
# -----------------------------------------------------------------------------
tab_sim, tab_overview, tab_metrics, tab_data = st.tabs([
    "Live Network Topology",
    "3-Phase Progression Overview",
    "Performance Evaluation Charts",
    "Simulation Data & Export",
])

# -----------------------------------------------------------------------------
# TAB 1: Live Interactive Topology & Link Load Breakdown
# -----------------------------------------------------------------------------
with tab_sim:
    col_graph, col_info = st.columns([1.6, 1.0])

    with col_graph:
        fig, ax = _setup_figure_style(
            title=f"SDN Topology State: {st.session_state.state}",
            subtitle=f"Flow Demand: 70 Mbps Ingress at Edge1 ➔ Destination at LMS Server"
        )

        if st.session_state.state in ["NORMAL", "RECOVERY"]:
            draw_network_canvas(
                sim.G, ax,
                phase=1,
                primary_path=sim.primary_path,
                demand_traffic=sim.demand_traffic
            )
        elif st.session_state.state == "FAILURE":
            draw_network_canvas(
                sim.G, ax,
                phase=2,
                primary_path=sim.primary_path,
                failed_link=("Edge1", "Core1"),
                demand_traffic=sim.demand_traffic
            )
        elif st.session_state.state == "FAILOVER":
            draw_network_canvas(
                sim.G, ax,
                phase=3,
                backup_path=sim.backup_path,
                failed_link=("Edge1", "Core1"),
                demand_traffic=sim.demand_traffic
            )

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_info:
        st.markdown("<div class='box-title'>Active Link Telemetry (8 Links)</div>", unsafe_allow_html=True)

        topo_info = get_topology_info(sim.G)
        link_rows = []
        for l in topo_info["links"]:
            status_tag = "ACTIVE" if l["status"] == "active" else "FAILED"
            link_rows.append({
                "Segment": f"{l['source']} ↔ {l['target']}",
                "Status": status_tag,
                "Traffic": f"{l['traffic']} Mbps",
                "Load": f"{l['utilization']}%",
            })
        df_links = pd.DataFrame(link_rows)
        st.dataframe(df_links, hide_index=True, use_container_width=True)

        st.write("")
        st.markdown("<div class='box-title'>Controller Observability</div>", unsafe_allow_html=True)

        if st.session_state.state in ["NORMAL", "RECOVERY"]:
            st.info(
                "**Normal Operation:** Traffic flows through optimal 2-hop primary path (`Edge1 → Core1 → LMS`). "
                "Network-wide average load is distributed at 17.5%."
            )
        elif st.session_state.state == "FAILURE":
            st.error(
                "**Link Fault Active:** Link `Edge1 ↔ Core1` is physically severed. Primary path is broken. "
                "Throughput drops to 0.0 Mbps with 100% loss until failover triggers."
            )
        elif st.session_state.state == "FAILOVER":
            st.success(
                f"**Failover Restored:** Centralized SDN controller redirected traffic to disjoint 3-hop "
                f"backup path (`Edge1 → Core2 → Edge2 → LMS`) in **{sim.recovery_time:.2f} ms** with zero loss."
            )

# -----------------------------------------------------------------------------
# TAB 2: Side-by-Side 3-Phase Progression Overview
# -----------------------------------------------------------------------------
with tab_overview:
    st.markdown("<div class='box-title'>Side-by-Side 3-Phase Progression Comparison</div>", unsafe_allow_html=True)
    st.write("Visual progression comparing Normal Baseline, Severed Primary Link, and SDN Automatic Failover.")

    overview_img = "results/graphs/phase_progression_overview.png"
    if os.path.exists(overview_img):
        st.image(overview_img, use_container_width=True)
    else:
        st.warning("Overview diagram not found. Run `python main.py` to regenerate.")

# -----------------------------------------------------------------------------
# TAB 3: Performance Evaluation Charts
# -----------------------------------------------------------------------------
with tab_metrics:
    st.markdown("<div class='box-title'>Resilience & Performance Benchmark Graphs</div>", unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    with g1:
        if os.path.exists("results/graphs/link_utilization.png"):
            st.image("results/graphs/link_utilization.png", caption="Link Utilization Redistribution", use_container_width=True)
    with g2:
        if os.path.exists("results/graphs/throughput.png"):
            st.image("results/graphs/throughput.png", caption="Throughput Across Phases", use_container_width=True)
    with g3:
        if os.path.exists("results/graphs/recovery_time.png"):
            st.image("results/graphs/recovery_time.png", caption="Sub-50ms Recovery Latency Breakdown", use_container_width=True)

    if os.path.exists("results/graphs/routing_strategies_comparison.png"):
        st.write("")
        st.markdown("<div class='box-title'>Routing Strategy Comparison</div>", unsafe_allow_html=True)
        st.image("results/graphs/routing_strategies_comparison.png", caption="Shortest Path vs. Load-Based vs. Fault-Aware vs. SDN Failover", use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: Simulation Data & Export
# -----------------------------------------------------------------------------
with tab_data:
    st.markdown("<div class='box-title'>Phase Telemetry Records</div>", unsafe_allow_html=True)

    if sim.records:
        df_rec = pd.DataFrame(sim.records)
        st.dataframe(df_rec, hide_index=True, use_container_width=True)

        csv_bytes = df_rec.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Telemetry CSV",
            data=csv_bytes,
            file_name="sdn_simulation_telemetry.csv",
            mime="text/csv",
        )

