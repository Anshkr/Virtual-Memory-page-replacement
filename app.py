import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import importlib

import utils.statistics
importlib.reload(utils.statistics)
from utils.statistics import calculate_statistics

from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.optimal import optimal
from algorithms.lfu import lfu
from algorithms.clock import clock
from algorithms.allocation import equal_allocation, proportional_allocation, simulate_local, simulate_global
from algorithms.thrashing import working_set_sizes, analyze_thrashing, recommended_frames
from algorithms.page_size import page_size_analysis, theoretical_optimal_page_size
from algorithms.segmentation import demand_segmentation

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Virtual Memory & Page Replacement Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# PROFESSIONAL DARK GLASSO-TECH THEME STYLES
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    code, pre, .mono-font {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Backgrounds */
    .stApp {
        background: radial-gradient(circle at top right, #111827, #0b0f19 80%);
        color: #f1f5f9;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 16px;
        padding: 20px 24px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Accent Pill Badges */
    .badge-hit {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-fault {
        background-color: rgba(244, 63, 94, 0.2);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-neutral {
        background-color: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }

    /* Interactive Stepper Visual Slot */
    .ram-container {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        margin: 15px 0 25px 0;
    }
    .ram-slot {
        flex: 1;
        min-width: 105px;
        background: #131b2e;
        border-radius: 14px;
        border: 2px solid #1e293b;
        padding: 16px 12px;
        text-align: center;
        transition: all 0.25s ease;
        position: relative;
    }
    .ram-slot.active-hit {
        border-color: #10b981;
        background: linear-gradient(180deg, #131b2e 0%, rgba(16, 185, 129, 0.18) 100%);
        box-shadow: 0 0 18px rgba(16, 185, 129, 0.35);
    }
    .ram-slot.active-fault {
        border-color: #f43f5e;
        background: linear-gradient(180deg, #131b2e 0%, rgba(244, 63, 94, 0.18) 100%);
        box-shadow: 0 0 18px rgba(244, 63, 94, 0.35);
    }
    .slot-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .slot-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.85rem;
        font-weight: 800;
        color: #f1f5f9;
    }
    .slot-meta {
        font-size: 0.72rem;
        color: #94a3b8;
        margin-top: 6px;
    }

    /* Explanation Banner */
    .narrative-box {
        background: rgba(30, 41, 59, 0.7);
        border-left: 4px solid #6366f1;
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        margin: 15px 0;
        font-size: 0.95rem;
        color: #e2e8f0;
    }

    /* Custom Alert for Belady Anomaly */
    .anomaly-card {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.15) 0%, rgba(217, 70, 239, 0.15) 100%);
        border: 1px solid rgba(244, 63, 94, 0.4);
        border-radius: 14px;
        padding: 18px 22px;
        margin: 18px 0;
    }

    /* Memory Matrix Table */
    .matrix-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 4px;
        margin: 15px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    .matrix-table th {
        background: #1e293b;
        color: #94a3b8;
        padding: 10px 8px;
        text-align: center;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .matrix-table td {
        padding: 10px 6px;
        text-align: center;
        border-radius: 6px;
        background: #111827;
        color: #cbd5e1;
        font-weight: 600;
    }
    .matrix-cell-hit {
        background: rgba(16, 185, 129, 0.22) !important;
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.45);
        font-weight: 800 !important;
    }
    .matrix-cell-fault {
        background: rgba(244, 63, 94, 0.25) !important;
        color: #fb7185 !important;
        border: 1px solid rgba(244, 63, 94, 0.5);
        font-weight: 800 !important;
    }
    .matrix-cell-empty {
        color: #475569 !important;
        background: rgba(15, 23, 42, 0.4) !important;
    }
    .row-header {
        background: #1e293b !important;
        color: #cbd5e1 !important;
        font-weight: 700;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Header styling */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0 24px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
    .app-title-group h1 {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #ffffff 0%, #a5b4fc 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .app-title-group p {
        margin: 4px 0 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# ALGORITHM REGISTRY & METADATA
# ---------------------------------------------------------
ALGORITHMS = {
    "FIFO": {
        "fn": fifo,
        "name": "First-In, First-Out (FIFO)",
        "desc": "Replaces the page that has been in memory the longest time.",
        "badge": "Non-Stack",
        "belady": True
    },
    "LRU": {
        "fn": lru,
        "name": "Least Recently Used (LRU)",
        "desc": "Replaces the page that has not been referenced for the longest period.",
        "badge": "Stack Algorithm",
        "belady": False
    },
    "Optimal": {
        "fn": optimal,
        "name": "Optimal (MIN / Belady's)",
        "desc": "Replaces the page that will not be used for the longest future duration. Benchmark optimum.",
        "badge": "Theoretical Optimum",
        "belady": False
    },
    "LFU": {
        "fn": lfu,
        "name": "Least Frequently Used (LFU)",
        "desc": "Replaces the page with the lowest cumulative access frequency.",
        "badge": "Frequency-based",
        "belady": True
    },
    "Clock": {
        "fn": clock,
        "name": "Clock (Second Chance)",
        "desc": "Circular buffer FIFO approximation with a reference bit inspected by a clock hand.",
        "badge": "Industry Standard",
        "belady": True
    }
}

PRESETS = {
    "Custom Input": None,
    "Silberschatz OS Textbook Classic": "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1",
    "Belady's Anomaly Demonstration": "1 2 3 4 1 2 5 1 2 3 4 5",
    "High Locality (Working Set Loop)": "1 2 3 2 1 2 3 2 1 4 5 4 5 1 2 3",
    "Sequential Streaming (Scan)": "1 2 3 4 5 6 7 8 9 10 1 2 3 4"
}


# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Simulator Controls")
    
    preset_choice = st.selectbox(
        "📚 Reference Sequence Presets",
        options=list(PRESETS.keys()),
        index=1  # Default to Silberschatz classic
    )

    if preset_choice == "Custom Input":
        default_val = "7 0 1 2 0 3 0 4 2 3"
    else:
        default_val = PRESETS[preset_choice]

    reference_input = st.text_area(
        "Page Reference Sequence",
        value=default_val,
        help="Space or comma-separated list of page numbers (e.g. 7 0 1 2 0 3 0 4)",
        height=75
    )

    # Random Generator Expander
    with st.expander("🎲 Sequence Randomizer"):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            rand_len = st.number_input("Length", min_value=5, max_value=50, value=15, step=1)
        with col_g2:
            rand_max_page = st.number_input("Max Page #", min_value=2, max_value=15, value=6, step=1)
        
        if st.button("Generate Random Sequence", use_container_width=True):
            random_seq = [random.randint(0, rand_max_page) for _ in range(rand_len)]
            st.session_state["generated_seq"] = " ".join(map(str, random_seq))
            st.rerun()

    if "generated_seq" in st.session_state:
        reference_input = st.session_state["generated_seq"]

    st.markdown("---")
    st.markdown("### 🎛️ Memory Architecture")

    frame_count = st.slider(
        "Physical Page Frames (Slots)",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of physical memory frames allocated to this process."
    )

    algorithm_selection = st.selectbox(
        "Algorithm Strategy",
        ["Compare All"] + list(ALGORITHMS.keys()),
        index=0
    )

    with st.expander("⏱️ Access Time Modeling (EMAT)"):
        mat_ns = st.number_input("Memory Access Time (MAT)", min_value=1, max_value=1000, value=100, step=10, help="Nanoseconds (ns)")
        pfst_ms = st.number_input("Page Fault Service Time (PFST)", min_value=1.0, max_value=50.0, value=8.0, step=1.0, help="Milliseconds (ms)")
        pfst_ns = pfst_ms * 1_000_000

    st.markdown("---")
    st.caption("OS Paging Simulator • Computer Systems Architecture")


# ---------------------------------------------------------
# INPUT PARSING & VALIDATION
# ---------------------------------------------------------
valid_input = False
reference_string = []

try:
    cleaned = reference_input.replace(",", " ").strip()
    if not cleaned:
        st.error("⚠️ Reference sequence cannot be empty. Please enter integer page numbers.")
    else:
        reference_string = [int(x) for x in cleaned.split()]
        if any(x < 0 for x in reference_string):
            st.error("⚠️ Page numbers must be non-negative integers (>= 0).")
        else:
            valid_input = True
except ValueError:
    st.error("⚠️ Invalid sequence format. Please enter space- or comma-separated integers.")


# ---------------------------------------------------------
# SIMULATION WORKHORSE
# ---------------------------------------------------------
@st.cache_data
def execute_simulation(ref_str, frames, mat, pfst):
    results_map = {}
    for name, meta in ALGORITHMS.items():
        res, hits, faults = meta["fn"](ref_str, frames)
        try:
            stats = calculate_statistics(hits, faults, len(ref_str), mat, pfst)
        except TypeError:
            # Fallback if an older 3-argument version of calculate_statistics is loaded in memory
            stats = calculate_statistics(hits, faults, len(ref_str))
            
        if "emat_ns" not in stats:
            fault_ratio = stats.get("fault_ratio", faults / len(ref_str) if len(ref_str) > 0 else 0.0)
            stats["emat_ns"] = (1.0 - fault_ratio) * mat + fault_ratio * pfst
        if "total_pages" not in stats:
            stats["total_pages"] = len(ref_str)

        results_map[name] = {
            "results": res,
            "hits": hits,
            "faults": faults,
            "stats": stats,
            "meta": meta
        }
    return results_map


# ---------------------------------------------------------
# MAIN APP BODY
# ---------------------------------------------------------

# App Header
st.markdown("""
<div class="app-header">
    <div class="app-title-group">
        <h1>⚡ Virtual Memory & Page Replacement Simulator</h1>
        <p>Interactive Operating Systems Analysis • Performance Benchmark • Step-by-Step Hardware State</p>
    </div>
</div>
""", unsafe_allow_html=True)

if valid_input:
    # Run all simulations
    sim_data = execute_simulation(tuple(reference_string), frame_count, mat_ns, pfst_ns)

    # Determine which algorithm(s) to highlight
    active_algos = list(ALGORITHMS.keys()) if algorithm_selection == "Compare All" else [algorithm_selection]
    primary_algo = "Optimal" if "Optimal" in active_algos else active_algos[0]
    
    # ---------------- TOP EXECUTIVE METRICS BANNER ----------------
    # Quick KPI highlights from the selected or optimal algorithm
    ref_len = len(reference_string)
    unique_pages = len(set(reference_string))
    
    # Best performing algorithm for this config
    best_algo = min(sim_data.keys(), key=lambda k: sim_data[k]["faults"])
    best_faults = sim_data[best_algo]["faults"]
    best_hit_ratio = sim_data[best_algo]["stats"]["hit_ratio"] * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">References</div>
            <div class="metric-value">{ref_len}</div>
            <div class="metric-subtitle">{unique_pages} unique virtual pages</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Page Frames</div>
            <div class="metric-value">{frame_count}</div>
            <div class="metric-subtitle">Physical memory slots</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        disp_algo = primary_algo if len(active_algos) == 1 else best_algo
        disp_faults = sim_data[disp_algo]["faults"]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Min Page Faults</div>
            <div class="metric-value" style="color: #fb7185;">{disp_faults}</div>
            <div class="metric-subtitle">Achieved by <b>{disp_algo}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        disp_hit_ratio = sim_data[disp_algo]["stats"]["hit_ratio"] * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Best Hit Ratio</div>
            <div class="metric-value" style="color: #34d399;">{disp_hit_ratio:.1f}%</div>
            <div class="metric-subtitle">{sim_data[disp_algo]["hits"]} total hits</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        disp_emat = sim_data[disp_algo]["stats"]["emat_ns"]
        emat_str = f"{disp_emat / 1_000_000:.2f} ms" if disp_emat >= 1_000_000 else f"{disp_emat:.0f} ns"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Effective Access</div>
            <div class="metric-value" style="color: #a78bfa;">{emat_str}</div>
            <div class="metric-subtitle">EMAT with {disp_algo}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # ---------------- MAIN DASHBOARD TABS ----------------
    (tab_overview, tab_step, tab_sensitivity, tab_theory,
     tab_thrash, tab_alloc, tab_pagesize, tab_seg) = st.tabs([
        "📊 Executive Benchmark & Comparison",
        "🔍 Step-by-Step Memory Visualizer",
        "📈 Frame Sensitivity & Belady's Anomaly",
        "🧠 OS Paging Architecture & Theory",
        "🌪️ Thrashing & Working Set",
        "🗂️ Allocation of Frames",
        "📐 Page Size & Considerations",
        "🧩 Demand Segmentation"
    ])

    # -----------------------------------------------------
    # TAB 1: EXECUTIVE BENCHMARK & COMPARISON
    # -----------------------------------------------------
    with tab_overview:
        st.subheader("🏆 Algorithm Performance Leaderboard")

        # Build comparison dataframe
        comparison_rows = []
        for name, data in sim_data.items():
            stats = data["stats"]
            comparison_rows.append({
                "Algorithm": name,
                "Full Name": ALGORITHMS[name]["name"],
                "Strategy": ALGORITHMS[name]["badge"],
                "Page Hits": stats["hits"],
                "Page Faults": stats["faults"],
                "Hit Ratio (%)": round(stats["hit_ratio"] * 100, 2),
                "Fault Ratio (%)": round(stats["fault_ratio"] * 100, 2),
                "EMAT (ms)": round(stats["emat_ns"] / 1_000_000, 4)
            })

        comp_df = pd.DataFrame(comparison_rows).sort_values(by=["Page Faults", "Hit Ratio (%)"], ascending=[True, False])
        comp_df.reset_index(drop=True, inplace=True)
        comp_df.insert(0, "Rank", [f"#{i+1}" for i in range(len(comp_df))])

        st.dataframe(
            comp_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.TextColumn("Rank", width="small"),
                "Algorithm": st.column_config.TextColumn("Algorithm", width="medium"),
                "Hit Ratio (%)": st.column_config.ProgressColumn(
                    "Hit Ratio",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                ),
                "Page Faults": st.column_config.NumberColumn("Page Faults", format="%d"),
                "EMAT (ms)": st.column_config.NumberColumn("EMAT (ms)", format="%.3f ms")
            }
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Comparative Visualization Charts
        chart_col1, chart_col2 = st.columns([3, 2])

        with chart_col1:
            st.markdown("#### 📊 Hits vs Page Faults Breakdown")
            
            # Melt dataframe for grouped bar chart
            melted_df = pd.melt(
                comp_df,
                id_vars=["Algorithm"],
                value_vars=["Page Hits", "Page Faults"],
                var_name="Metric",
                value_name="Count"
            )

            fig_bar = px.bar(
                melted_df,
                x="Algorithm",
                y="Count",
                color="Metric",
                barmode="group",
                text="Count",
                color_discrete_map={
                    "Page Hits": "#10b981",
                    "Page Faults": "#f43f5e"
                },
                template="plotly_dark"
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
            )
            fig_bar.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with chart_col2:
            st.markdown("#### 🎯 Hit vs Fault Distribution")
            selected_chart_algo = st.selectbox(
                "Inspect Algorithm Distribution",
                options=list(ALGORITHMS.keys()),
                index=list(ALGORITHMS.keys()).index(disp_algo)
            )

            algo_hits = sim_data[selected_chart_algo]["hits"]
            algo_faults = sim_data[selected_chart_algo]["faults"]

            fig_donut = go.Figure(data=[go.Pie(
                labels=["Page Hits", "Page Faults"],
                values=[algo_hits, algo_faults],
                hole=0.6,
                marker=dict(colors=["#10b981", "#f43f5e"]),
                textinfo="label+percent",
                hoverinfo="label+value+percent"
            )])
            fig_donut.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                annotations=[dict(
                    text=f"<b>{selected_chart_algo}</b><br>{sim_data[selected_chart_algo]['stats']['hit_ratio']*100:.1f}% Hit",
                    x=0.5, y=0.5,
                    font_size=16,
                    showarrow=False
                )]
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        # Cumulative Faults Curve Over Time
        st.markdown("#### 📉 Cumulative Page Faults Progression Over Sequence")
        st.caption("Track when faults occurred along the execution timeline. Steeper slopes indicate periods of intense cache thrashing.")
        
        timeline_rows = []
        for name in active_algos:
            results_list = sim_data[name]["results"]
            running_faults = 0
            for step_idx, step_data in enumerate(results_list, start=1):
                if step_data["Status"] == "Fault":
                    running_faults += 1
                timeline_rows.append({
                    "Step": step_idx,
                    "Page": f"P{step_data['Page']}",
                    "Cumulative Faults": running_faults,
                    "Algorithm": name
                })

        timeline_df = pd.DataFrame(timeline_rows)
        fig_timeline = px.line(
            timeline_df,
            x="Step",
            y="Cumulative Faults",
            color="Algorithm",
            markers=True,
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_timeline.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickmode="linear", dtick=1),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)")
        )
        st.plotly_chart(fig_timeline, use_container_width=True)


    # -----------------------------------------------------
    # TAB 2: STEP-BY-STEP MEMORY VISUALIZER & MATRIX
    # -----------------------------------------------------
    with tab_step:
        st.subheader("🔍 Hardware Memory State & Step-by-Step Execution")

        col_sel_algo, col_view_mode = st.columns([3, 2])
        with col_sel_algo:
            visual_algo = st.selectbox(
                "Select Algorithm to Visualize",
                options=list(ALGORITHMS.keys()),
                index=0
            )
        with col_view_mode:
            display_style = st.radio(
                "Visualization View",
                ["Visual Memory Matrix (Timeline)", "Interactive Single-Step Inspector"],
                horizontal=True
            )

        active_res = sim_data[visual_algo]["results"]

        if display_style == "Visual Memory Matrix (Timeline)":
            st.markdown("##### 🧩 Complete Frame Allocation Matrix")
            st.caption("Columns represent reference steps. Cells show physical memory frame allocations. Green indicates a Page Hit; Red indicates a Page Fault.")

            # Render HTML Memory Matrix
            matrix_html = '<div style="overflow-x: auto; padding-bottom: 10px;"><table class="matrix-table">'
            
            # Step header
            matrix_html += '<tr><th class="row-header">Step</th>'
            for idx in range(1, len(active_res) + 1):
                matrix_html += f'<th>#{idx}</th>'
            matrix_html += '</tr>'

            # Page header
            matrix_html += '<tr><th class="row-header">Page Ref</th>'
            for r in active_res:
                matrix_html += f'<th style="color: #60a5fa; font-weight: 700;">{r["Page"]}</th>'
            matrix_html += '</tr>'

            # Status header
            matrix_html += '<tr><th class="row-header">Status</th>'
            for r in active_res:
                if r["Status"] == "Hit":
                    matrix_html += '<th><span class="badge-hit">HIT</span></th>'
                else:
                    matrix_html += '<th><span class="badge-fault">FAULT</span></th>'
            matrix_html += '</tr>'

            # Frame rows
            for f_idx in range(frame_count):
                matrix_html += f'<tr><td class="row-header">Frame {f_idx + 1}</td>'
                for r in active_res:
                    phys = r.get("PhysicalFrames", [None] * frame_count)
                    page_val = phys[f_idx] if f_idx < len(phys) else None
                    victim_slot = r.get("VictimSlot", None)
                    status = r["Status"]

                    # Check if this exact cell was the touched/victim slot
                    is_touched = (victim_slot == f_idx)

                    if page_val is None:
                        matrix_html += '<td class="matrix-cell-empty">-</td>'
                    elif is_touched and status == "Hit":
                        matrix_html += f'<td class="matrix-cell-hit">{page_val}</td>'
                    elif is_touched and status == "Fault":
                        matrix_html += f'<td class="matrix-cell-fault">{page_val}</td>'
                    else:
                        matrix_html += f'<td>{page_val}</td>'
                matrix_html += '</tr>'

            matrix_html += '</table></div>'
            st.markdown(matrix_html, unsafe_allow_html=True)

            # Frame Data Table (Exportable)
            with st.expander("📄 View Tabular Frame Execution Log (Data Table)"):
                log_rows = []
                for idx, r in enumerate(active_res, start=1):
                    phys = r.get("PhysicalFrames", [None] * frame_count)
                    row_data = {
                        "Step": idx,
                        "Page": r["Page"],
                        "Status": r["Status"],
                        "Evicted": r.get("Evicted") if r.get("Evicted") is not None else "-",
                        "Action Explanation": r.get("Reason", "")
                    }
                    for i in range(frame_count):
                        val = phys[i] if i < len(phys) else None
                        row_data[f"Frame {i+1}"] = val if val is not None else "-"
                    log_rows.append(row_data)

                log_df = pd.DataFrame(log_rows)
                st.dataframe(log_df, use_container_width=True, hide_index=True)
                
                # CSV Download button
                csv_data = log_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download {visual_algo} Trace (CSV)",
                    data=csv_data,
                    file_name=f"{visual_algo}_frame_trace.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        else:
            # Interactive Single-Step Inspector
            st.markdown("##### 🎚️ Interactive Step Inspector")
            
            selected_step = st.slider(
                "Scrub Timeline (Step Number)",
                min_value=1,
                max_value=len(active_res),
                value=1,
                step=1
            )

            current_event = active_res[selected_step - 1]
            phys_frames = current_event.get("PhysicalFrames", [None] * frame_count)
            status = current_event["Status"]
            page = current_event["Page"]
            evicted = current_event.get("Evicted", None)
            victim_slot = current_event.get("VictimSlot", None)
            reason = current_event.get("Reason", "")

            # Event Banner
            status_badge = '<span class="badge-hit">PAGE HIT</span>' if status == "Hit" else '<span class="badge-fault">PAGE FAULT</span>'
            st.markdown(f"""
            <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <span style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Active Event</span>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #f8fafc; margin-top: 2px;">
                        Step #{selected_step}: Referencing Page <span style="color: #60a5fa;">{page}</span>
                    </div>
                </div>
                <div>{status_badge}</div>
            </div>
            """, unsafe_allow_html=True)

            # RAM Slots Physical Visualization
            st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase;'>Physical RAM Frame Slots</p>", unsafe_allow_html=True)
            
            ram_cols = st.columns(frame_count)
            for f_i in range(frame_count):
                val = phys_frames[f_i] if f_i < len(phys_frames) else None
                is_touched = (victim_slot == f_i)
                
                slot_class = "ram-slot"
                badge_slot = ""
                if is_touched:
                    if status == "Hit":
                        slot_class += " active-hit"
                        badge_slot = '<span class="badge-hit" style="font-size: 0.65rem;">HIT TARGET</span>'
                    else:
                        slot_class += " active-fault"
                        if evicted is not None:
                            badge_slot = f'<span class="badge-fault" style="font-size: 0.65rem;">REPLACED P{evicted}</span>'
                        else:
                            badge_slot = '<span class="badge-fault" style="font-size: 0.65rem;">ALLOCATED</span>'

                val_display = str(val) if val is not None else '<span style="color: #475569;">EMPTY</span>'

                with ram_cols[f_i]:
                    st.markdown(f"""
                    <div class="{slot_class}">
                        <div class="slot-label">Frame #{f_i + 1}</div>
                        <div class="slot-value">{val_display}</div>
                        <div class="slot-meta">{badge_slot if badge_slot else "&nbsp;"}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Narrative Reason Box
            st.markdown(f"""
            <div class="narrative-box">
                <b>💡 Kernel Decision Logic:</b> {reason}
            </div>
            """, unsafe_allow_html=True)


    # -----------------------------------------------------
    # TAB 3: FRAME SENSITIVITY & BELADY'S ANOMALY
    # -----------------------------------------------------
    with tab_sensitivity:
        st.subheader("📈 Allocation Sensitivity & Belady's Anomaly Detection")
        st.markdown(
            "An essential concept in Virtual Memory: increasing physical frame allocation usually decreases page faults. "
            "However, **non-stack algorithms (such as FIFO)** can exhibit **Belady's Anomaly**, where adding memory *increases* the fault rate."
        )

        col_sens_range, col_sens_btn = st.columns([3, 1])
        with col_sens_range:
            max_test_frames = st.slider("Maximum Frames to Test", min_value=3, max_value=12, value=max(3, min(8, len(reference_string) + 1)))
        
        # Calculate sensitivity across range
        sensitivity_data = []
        belady_incidents = []

        for count in range(1, max_test_frames + 1):
            for name, meta in ALGORITHMS.items():
                _, _, faults = meta["fn"](reference_string, count)
                sensitivity_data.append({
                    "Frames": count,
                    "Algorithm": name,
                    "Page Faults": faults
                })

        sens_df = pd.DataFrame(sensitivity_data)

        # Scan for Belady's Anomaly in FIFO and others
        for name in ALGORITHMS.keys():
            algo_curve = sens_df[sens_df["Algorithm"] == name].sort_values("Frames").to_dict("records")
            for i in range(len(algo_curve) - 1):
                f_curr = algo_curve[i]["Frames"]
                f_next = algo_curve[i + 1]["Frames"]
                flt_curr = algo_curve[i]["Page Faults"]
                flt_next = algo_curve[i + 1]["Page Faults"]
                if flt_next > flt_curr:
                    belady_incidents.append({
                        "algorithm": name,
                        "from_frames": f_curr,
                        "to_frames": f_next,
                        "from_faults": flt_curr,
                        "to_faults": flt_next
                    })

        # Display Anomaly Alert Card if detected
        if belady_incidents:
            for incident in belady_incidents:
                st.markdown(f"""
                <div class="anomaly-card">
                    <h4 style="margin: 0; color: #fb7185; display: flex; align-items: center; gap: 8px;">
                        ⚠️ Belady's Anomaly Detected! ({incident['algorithm']})
                    </h4>
                    <p style="margin: 8px 0 0 0; color: #f1f5f9; font-size: 0.95rem;">
                        Increasing physical frames from <b>{incident['from_frames']}</b> to <b>{incident['to_frames']}</b> 
                        caused page faults to <b>INCREASE</b> from <b>{incident['from_faults']}</b> to <b style="color: #fb7185;">{incident['to_faults']}</b>!
                    </p>
                    <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                        This occurs because {incident['algorithm']} does not satisfy the <i>inclusion property</i> (stack algorithms like LRU and Optimal are immune).
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No Belady's Anomaly detected for this specific reference sequence. To observe Belady's Anomaly, select the preset 'Belady's Anomaly Demonstration' in the sidebar.")

        # Sensitivity Line Chart
        fig_sens = px.line(
            sens_df,
            x="Frames",
            y="Page Faults",
            color="Algorithm",
            markers=True,
            title="Physical Frame Allocation vs Page Faults (Sensitivity Curve)",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_sens.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickmode="linear", dtick=1),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_sens, use_container_width=True)


    # -----------------------------------------------------
    # TAB 4: OS THEORY & REFERENCE CHEAT SHEET
    # -----------------------------------------------------
    with tab_theory:
        st.subheader("🧠 Virtual Memory & Page Replacement Reference")

        theory_col1, theory_col2 = st.columns(2)

        with theory_col1:
            st.markdown("""
            #### 📌 Paging Fundamentals
            - **Virtual vs Physical Address Space**: Programs reference virtual addresses partitioned into fixed-size *pages*. Physical memory is divided into corresponding *frames*.
            - **Page Fault**: Occurs when a requested page is not currently mapped into physical RAM (invalid bit in page table). The OS kernel triggers an interrupt, fetches the page from disk/swap, and resumes execution.
            - **Effective Memory Access Time (EMAT)**:
            $$EMAT = (1 - p) \\times MAT + p \\times PFST$$
            where:
            - $p$ = Page fault probability (fault ratio)
            - $MAT$ = Main memory access time ($\\sim 100\\text{ ns}$)
            - $PFST$ = Page fault service time (disk I/O $\\sim 8\\text{ ms} = 8,000,000\\text{ ns}$)
            *Because disk I/O is nearly 80,000× slower than RAM, even a 0.1% fault rate drastically degrades system throughput!*
            """)

        with theory_col2:
            st.markdown("""
            #### 🔬 Stack Algorithms & Belady's Anomaly
            - **Stack Property**: An algorithm satisfies the stack property if the set of pages in memory for $n$ frames is always a strict subset of the pages in memory for $n+1$ frames:
            $$M(n, t) \\subseteq M(n+1, t)$$
            - **Immune to Anomaly**: **LRU** and **Optimal** are proven stack algorithms and *never* suffer from Belady's Anomaly.
            - **Susceptible**: **FIFO**, **LFU**, and simple **Clock** can suffer from Belady's Anomaly because the pages maintained do not satisfy inclusion.
            """)

        st.markdown("---")
        st.markdown("#### ⚖️ Algorithm Comparison Matrix")

        theory_matrix = pd.DataFrame([
            {
                "Algorithm": "FIFO",
                "Eviction Criteria": "Oldest loaded page in memory",
                "Stack Property": "❌ No (Belady prone)",
                "Hardware Overhead": "Low (queue / timestamp)",
                "Implementation": "Simple queue pointer"
            },
            {
                "Algorithm": "LRU",
                "Eviction Criteria": "Unused for longest time",
                "Stack Property": "✅ Yes (Immune)",
                "Hardware Overhead": "High (hardware clock / stack)",
                "Implementation": "Doubly linked list / registers"
            },
            {
                "Algorithm": "Optimal (MIN)",
                "Eviction Criteria": "Unused for longest future duration",
                "Stack Property": "✅ Yes (Immune)",
                "Hardware Overhead": "Theoretical (Requires future clairvoyance)",
                "Implementation": "Offline benchmark only"
            },
            {
                "Algorithm": "LFU",
                "Eviction Criteria": "Lowest reference frequency",
                "Stack Property": "❌ No",
                "Hardware Overhead": "Moderate (frequency counters)",
                "Implementation": "Min-heap / counters"
            },
            {
                "Algorithm": "Clock (Second Chance)",
                "Eviction Criteria": "Oldest with reference bit = 0",
                "Stack Property": "❌ No",
                "Hardware Overhead": "Very Low (1 bit per frame)",
                "Implementation": "Circular buffer + clock pointer"
            }
        ])

        st.dataframe(theory_matrix, use_container_width=True, hide_index=True)


    # -----------------------------------------------------
    # SYLLABUS ADD-ONS (Unit 3): helpers shared by new tabs
    # -----------------------------------------------------
    def parse_ints(text, label):
        cleaned_txt = text.replace(",", " ").strip()
        if not cleaned_txt:
            raise ValueError(f"{label}: sequence cannot be empty.")
        try:
            vals = [int(x) for x in cleaned_txt.split()]
        except ValueError:
            raise ValueError(f"{label}: enter space- or comma-separated integers.")
        if any(v < 0 for v in vals):
            raise ValueError(f"{label}: values must be non-negative integers.")
        return vals

    def style_fig(fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig

    # -----------------------------------------------------
    # TAB 5: THRASHING & WORKING SET
    # -----------------------------------------------------
    with tab_thrash:
        st.subheader("🌪️ Thrashing Detection & Working-Set Model")
        st.markdown(
            "**Thrashing** happens when a process has fewer frames than its working set needs, so it spends more time "
            "servicing page faults than executing. A configuration is flagged when its fault ratio reaches the threshold."
        )
        th_c1, th_c2, th_c3 = st.columns(3)
        with th_c1:
            th_algo = st.selectbox("Replacement algorithm", list(ALGORITHMS.keys()), index=1, key="th_algo")
        with th_c2:
            th_threshold = st.slider("Thrashing threshold (fault ratio)", 0.1, 0.9, 0.5, 0.05, key="th_threshold")
        with th_c3:
            th_delta = st.slider("Working-set window Δ (references)", 2, 20, 5, key="th_delta")

        th_max = min(12, max(unique_pages + 1, frame_count, 3))
        th_rows = analyze_thrashing(reference_string, ALGORITHMS[th_algo]["fn"], th_max, mat_ns, pfst_ns, th_threshold)
        th_df = pd.DataFrame(th_rows)
        th_now = th_rows[frame_count - 1] if frame_count <= th_max else th_rows[-1]
        th_rec = recommended_frames(th_rows)

        if th_now["Thrashing"]:
            st.error(
                f"⚠️ Thrashing with {th_now['Frames']} frame(s): fault ratio {th_now['Fault Ratio']:.2f}, "
                f"about {th_now['Slowdown (x)']:,.0f}× slower than a fault-free run."
                + (f" Smallest non-thrashing allocation: {th_rec} frames." if th_rec else " No tested allocation avoids thrashing at this threshold.")
            )
        else:
            st.success(
                f"✅ {th_now['Frames']} frame(s) is stable: fault ratio {th_now['Fault Ratio']:.2f} "
                f"(below the {th_threshold:.2f} threshold)."
            )
        st.caption(
            f"Lower bound: this sequence has {unique_pages} distinct pages, so at least "
            f"{unique_pages / len(reference_string):.2f} of references fault (compulsory misses) even with unlimited frames."
        )

        th_df["Zone"] = th_df["Thrashing"].map({True: "Thrashing", False: "Stable"})
        fig_th = px.bar(
            th_df, x="Frames", y="Fault Ratio", color="Zone",
            color_discrete_map={"Thrashing": "#fb7185", "Stable": "#34d399"},
            title=f"Fault Ratio vs Allocated Frames ({th_algo})", template="plotly_dark"
        )
        fig_th.add_hline(y=th_threshold, line_dash="dash", line_color="#fbbf24", annotation_text="Thrashing threshold")
        fig_th.update_xaxes(tickmode="linear", dtick=1)
        st.plotly_chart(style_fig(fig_th), use_container_width=True)

        show_df = th_df[["Frames", "Faults", "Fault Ratio", "Slowdown (x)", "Zone"]].copy()
        show_df["Fault Ratio"] = show_df["Fault Ratio"].map(lambda v: f"{v:.2f}")
        show_df["Slowdown (x)"] = show_df["Slowdown (x)"].map(lambda v: f"{v:,.0f}")
        st.dataframe(show_df, use_container_width=True, hide_index=True)

        st.markdown("#### 🧺 Working-Set Size over time")
        wss = working_set_sizes(reference_string, th_delta)
        wss_df = pd.DataFrame({"Step": list(range(1, len(wss) + 1)), "Working-Set Size": wss})
        fig_ws = px.line(wss_df, x="Step", y="Working-Set Size", markers=True,
                         title=f"WSS(t) with window Δ = {th_delta}", template="plotly_dark")
        fig_ws.add_hline(y=frame_count, line_dash="dash", line_color="#818cf8", annotation_text="Allocated frames")
        st.plotly_chart(style_fig(fig_ws), use_container_width=True)
        if frame_count < max(wss):
            st.warning(f"Allocated frames ({frame_count}) are below the peak working set ({max(wss)}): thrashing risk.")
        else:
            st.info(f"Allocated frames ({frame_count}) cover the peak working set ({max(wss)}).")

    # -----------------------------------------------------
    # TAB 6: ALLOCATION OF FRAMES
    # -----------------------------------------------------
    with tab_alloc:
        st.subheader("🗂️ Allocation of Frames: Equal vs Proportional, Local vs Global")
        st.markdown(
            "Several processes share one pool of frames. **Equal** gives each m/n frames; **proportional** gives "
            "aᵢ = sᵢ/S × m (here a process's size sᵢ is its number of distinct pages). **Local** replacement stays inside "
            "a process's own frames; **global** replacement lets processes take frames from each other."
        )
        al_c1, al_c2, al_c3 = st.columns(3)
        with al_c1:
            al_nproc = st.radio("Number of processes", [2, 3], horizontal=True, key="al_nproc")
        with al_c2:
            al_total = st.number_input("Total physical frames", min_value=1, max_value=60, value=9, step=1, key="al_total")
        with al_c3:
            al_algo = st.selectbox("Replacement algorithm", list(ALGORITHMS.keys()), index=1, key="al_algo")

        al_defaults = ["1 2 3 4 1 2 5 1 2 3 4 5", "7 0 1 2 0 3 0 4 2 3 0 3", "1 2 1 2 1 2 1 2"]
        al_texts = []
        al_cols = st.columns(al_nproc)
        for i in range(al_nproc):
            with al_cols[i]:
                al_texts.append(st.text_area(f"Process P{i + 1} references", value=al_defaults[i], height=70, key=f"al_ref_{i}"))

        try:
            al_procs = [parse_ints(t, f"P{i + 1}") for i, t in enumerate(al_texts)]
            al_fn = ALGORITHMS[al_algo]["fn"]
            al_sizes = [len(set(p)) for p in al_procs]
            al_eq = equal_allocation(int(al_total), al_nproc)
            al_pr = proportional_allocation(int(al_total), al_sizes)
            loc_eq = simulate_local(al_procs, al_eq, al_fn)
            loc_pr = simulate_local(al_procs, al_pr, al_fn)
            glob = simulate_global(al_procs, int(al_total), al_fn)

            al_rows = []
            for i in range(al_nproc):
                al_rows.append({
                    "Process": f"P{i + 1}", "Size (pages)": al_sizes[i],
                    "Equal: frames": al_eq[i], "Equal: faults": loc_eq[i]["faults"],
                    "Proportional: frames": al_pr[i], "Proportional: faults": loc_pr[i]["faults"],
                    "Global: frames held (end)": glob[i]["frames"], "Global: faults": glob[i]["faults"],
                })
            tot = {"Process": "Total", "Size (pages)": sum(al_sizes)}
            for key in ["Equal: frames", "Equal: faults", "Proportional: frames", "Proportional: faults",
                        "Global: frames held (end)", "Global: faults"]:
                tot[key] = sum(r[key] for r in al_rows)
            al_rows.append(tot)
            st.dataframe(pd.DataFrame(al_rows), use_container_width=True, hide_index=True)

            cmp_df = pd.DataFrame({
                "Strategy": ["Equal + Local", "Proportional + Local", "Global"],
                "Total Page Faults": [tot["Equal: faults"], tot["Proportional: faults"], tot["Global: faults"]],
            })
            fig_al = px.bar(cmp_df, x="Strategy", y="Total Page Faults", color="Strategy", text="Total Page Faults",
                            title="Total Page Faults by Allocation Strategy", template="plotly_dark")
            fig_al.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig_al), use_container_width=True)
            best_al = cmp_df.loc[cmp_df["Total Page Faults"].idxmin(), "Strategy"]
            st.info(f"Lowest total faults for this workload: **{best_al}**. Global replacement adapts to demand but one process can starve another.")
        except ValueError as err:
            st.error(f"⚠️ {err}")

    # -----------------------------------------------------
    # TAB 7: PAGE SIZE & OTHER CONSIDERATIONS
    # -----------------------------------------------------
    with tab_pagesize:
        st.subheader("📐 Page Size Trade-offs & Other Considerations")
        st.markdown(
            "Small pages waste little memory per process but need a large page table; large pages shrink the table and "
            "extend TLB reach but waste more in the last page (internal fragmentation)."
        )
        ps_c1, ps_c2, ps_c3 = st.columns(3)
        with ps_c1:
            ps_kb = st.number_input("Process size (bytes)", min_value=1, max_value=1_000_000_000, value=1_000_000, step=10_000, key="ps_kb")
        with ps_c2:
            ps_pte = st.selectbox("Page-table entry size (bytes)", [2, 4, 8], index=1, key="ps_pte")
        with ps_c3:
            ps_tlb = st.number_input("TLB entries", min_value=1, max_value=4096, value=64, step=16, key="ps_tlb")
        ps_sizes = st.multiselect(
            "Candidate page sizes (bytes)", [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536],
            default=[512, 1024, 2048, 4096, 8192, 16384], key="ps_sizes"
        )
        if not ps_sizes:
            st.warning("Select at least one page size.")
        else:
            try:
                ps_bytes = int(ps_kb)
                ps_df = pd.DataFrame(page_size_analysis(ps_bytes, sorted(ps_sizes), ps_pte, int(ps_tlb)))
                best_ps = int(ps_df.loc[ps_df["Total Overhead (B)"].idxmin(), "Page Size (B)"])
                opt_ps = theoretical_optimal_page_size(ps_bytes, ps_pte)
                m1, m2 = st.columns(2)
                m1.metric("Best candidate (lowest overhead)", f"{best_ps:,} B")
                m2.metric("Theoretical optimum √(2·s·e)", f"{opt_ps:,.0f} B")
                st.dataframe(ps_df, use_container_width=True, hide_index=True)
                melt = ps_df.melt(id_vars="Page Size (B)", value_vars=["Page Table (B)", "Internal Fragmentation (B)"],
                                  var_name="Component", value_name="Bytes")
                melt["Page Size (B)"] = melt["Page Size (B)"].astype(str)
                fig_ps = px.bar(melt, x="Page Size (B)", y="Bytes", color="Component", barmode="stack",
                                title="Memory Overhead by Page Size", template="plotly_dark")
                st.plotly_chart(style_fig(fig_ps), use_container_width=True)
            except ValueError as err:
                st.error(f"⚠️ {err}")
        st.markdown("""
        **Other considerations:** *TLB reach* = entries × page size; *prepaging* loads pages before they fault;
        *program structure* (e.g. row-major vs column-major array access) changes locality; *I/O interlock* pins pages
        involved in DMA so they cannot be evicted.
        """)

    # -----------------------------------------------------
    # TAB 8: DEMAND SEGMENTATION
    # -----------------------------------------------------
    with tab_seg:
        st.subheader("🧩 Demand Segmentation")
        st.markdown(
            "Segments are variable-sized logical units (code, data, stack) loaded only when referenced. To fit a new "
            "segment, resident ones are evicted until enough memory is free. Memory is assumed compacted, so external fragmentation is not modelled."
        )
        sg_c1, sg_c2 = st.columns(2)
        with sg_c1:
            sg_table = st.text_input("Segment table (id:size in KB)", value="0:400, 1:250, 2:300, 3:150, 4:500", key="sg_table")
            sg_refs = st.text_input("Segment reference string", value="0 1 2 0 3 1 4 0 2 3", key="sg_refs")
        with sg_c2:
            sg_cap = st.number_input("Memory capacity (KB)", min_value=1, max_value=100000, value=1000, step=50, key="sg_cap")
            sg_policy = st.radio("Eviction policy", ["LRU", "FIFO"], horizontal=True, key="sg_policy")
        try:
            sg_sizes = {}
            for part in sg_table.replace(";", ",").split(","):
                if not part.strip():
                    continue
                if ":" not in part:
                    raise ValueError(f"Segment table entry '{part.strip()}' must look like id:size.")
                sid, ssize = part.split(":", 1)
                try:
                    sg_sizes[int(sid)] = int(ssize)
                except ValueError:
                    raise ValueError(f"Segment table entry '{part.strip()}' must contain integers.")
            if not sg_sizes:
                raise ValueError("Segment table cannot be empty.")
            sg_list = parse_ints(sg_refs, "Segment references")
            sg_res, sg_hits, sg_faults = demand_segmentation(sg_list, sg_sizes, int(sg_cap), sg_policy)

            sm1, sm2, sm3 = st.columns(3)
            sm1.metric("Segment hits", sg_hits)
            sm2.metric("Segment faults", sg_faults)
            sm3.metric("Hit ratio", f"{sg_hits / len(sg_list):.0%}")

            sg_df = pd.DataFrame([{
                "Step": i + 1, "Segment": r["Segment"], "Status": r["Status"],
                "Resident": str(r["Resident"]), "Used (KB)": r["Used"], "Free (KB)": r["Free"],
                "Evicted": str(r["Evicted"]) if r["Evicted"] else "-", "Reason": r["Reason"],
            } for i, r in enumerate(sg_res)])
            st.dataframe(sg_df, use_container_width=True, hide_index=True)

            fig_sg = px.area(sg_df, x="Step", y="Used (KB)", title="Memory Used over Time", template="plotly_dark")
            fig_sg.add_hline(y=int(sg_cap), line_dash="dash", line_color="#fb7185", annotation_text="Capacity")
            st.plotly_chart(style_fig(fig_sg), use_container_width=True)
        except ValueError as err:
            st.error(f"⚠️ {err}")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
col_foot1, col_foot2 = st.columns([3, 1])
with col_foot1:
    st.caption("💻 **Operating Systems Laboratory** • Virtual Memory Paging Simulator • Developed with Streamlit, Pandas & Plotly")
with col_foot2:
    st.caption("<div style='text-align: right;'>Version 2.0 • Production Ready</div>", unsafe_allow_html=True)
