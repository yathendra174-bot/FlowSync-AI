import os
import sys
import base64
from pathlib import Path
from collections import deque

_app_dir = Path(__file__).resolve().parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))
import time
import inspect
import importlib
import textwrap
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import traffic_simulator
importlib.reload(traffic_simulator)
from traffic_simulator import TrafficNetwork
from metrics import summarize_metrics
from congestion_predictor import CongestionPredictor
from cooperative_intelligence import CooperativeController
from emergency_corridor import EmergencyCorridorManager
from iot_sensor_twin import IoTSensorTwin
from incident_manager import IncidentManager
from xai_explainer import DecisionExplainer
from scenario_lab import ScenarioLab, SCENARIO_PROFILES

# Resolve and base64-encode background image
bg_path = Path(__file__).parent / "assets" / "traffic_bg.jpg"
if not bg_path.exists():
    bg_path = Path(__file__).parent.parent / "assets" / "traffic_bg.jpg"

if bg_path.exists():
    with open(bg_path, "rb") as _bf:
        bg_b64 = base64.b64encode(_bf.read()).decode("utf-8")
    bg_css_rule = f"""
    background: linear-gradient(135deg, rgba(8, 14, 28, 0.74) 0%, rgba(15, 23, 42, 0.85) 100%),
                url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
    background-size: cover !important;
    """
else:
    bg_css_rule = "background: linear-gradient(135deg, #0A0F1D 0%, #0F172A 100%) !important;"

# Helper for robust HTML rendering without Markdown indentation code-block bugs
def html(content: str):
    # Strip every line and omit empty lines to guarantee zero Markdown code-block interpretation
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


# Page configuration
st.set_page_config(
    page_title="FlowSync AI • Smart Traffic Orchestrator",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Background from User Uploaded Cyber City Image
html(f"""
<style>
/* Cyber City Traffic Background Across Viewport */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    {bg_css_rule}
    color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
</style>
""")

# Custom Styling with Dark Cyber-Glass, Crisp White Typography, and Categorized Large Navigation
html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Crisp high-contrast WHITE headings on dark canvas with increased font size */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95) !important;
}

h1 { font-size: 2.6rem !important; }
h2 { font-size: 2.1rem !important; }
h3 { font-size: 1.75rem !important; margin-top: 0.7rem !important; margin-bottom: 0.4rem !important; }
h4 { font-size: 1.45rem !important; margin-top: 0.6rem !important; margin-bottom: 0.35rem !important; }

/* Subtitles, Captions & Descriptions: Luminous White/Ice Blue with Increased Font Size */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #F1F5F9 !important;
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.9) !important;
    font-size: 1.12rem !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
}

/* All canvas body text in luminous white */
p, span, div, label, li, small {
    color: #FFFFFF !important;
}

/* Streamlit widget labels with increased font size */
.stWidgetLabel label, [data-testid="stWidgetLabel"] p, .stSelectbox label, .stRadio label, .stSlider label {
    color: #FFFFFF !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.95) !important;
}

.stRadio div[role="radiogroup"] label {
    font-size: 1.08rem !important;
    color: #FFFFFF !important;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
    max-width: 96% !important;
}

/* Translucent Dark Cyber Glass Sidebar */
[data-testid="stSidebar"] {
    background: rgba(10, 16, 32, 0.94) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1.5px solid rgba(56, 189, 248, 0.35) !important;
    box-shadow: 6px 0 30px rgba(0, 0, 0, 0.75) !important;
}

[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, 
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4, [data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

/* Moving Rainbow Gradient Strip (VIBGYOR) */
@keyframes rainbow-flow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.rainbow-strip {
    height: 6px;
    width: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #7C3AED, #4F46E5, #0284C7, #059669, #EAB308, #EA580C, #E11D48);
    background-size: 300% 300%;
    animation: rainbow-flow 6s ease infinite;
    margin-bottom: 0.75rem;
}

/* Ultra-Premium Glassmorphic Hero Banner (Dark Cyber-Glass) */
.hero-container {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.88) 100%) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.4) !important;
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.35rem;
    box-shadow: 0 16px 36px -6px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -50px;
    right: -50px;
    width: 240px;
    height: 240px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(147, 51, 234, 0.12) 50%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero-title {
    font-size: 2.45rem !important;
    font-weight: 800 !important;
    margin: 0;
    color: #FFFFFF !important;
    background: linear-gradient(135deg, #FFFFFF 0%, #38BDF8 60%, #34D399 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5) !important;
}

.hero-subtitle {
    font-size: 1.15rem !important;
    color: #F1F5F9 !important;
    margin-top: 0.45rem;
    font-weight: 600 !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8) !important;
}

/* Status Pill */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 5px 14px;
    border-radius: 999px;
    background: rgba(6, 78, 59, 0.8);
    color: #34D399;
    border: 1px solid #059669;
}

.pulse-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background-color: #10B981;
    animation: dot-pulse 1.8s infinite;
}

@keyframes dot-pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Metric Cards with Dark Cyber Glass & Neon Accents */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.1rem;
    margin-bottom: 1.4rem;
}

.metric-box {
    border-radius: 18px;
    padding: 1.25rem 1.4rem;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
}

.metric-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 36px rgba(0, 0, 0, 0.65) !important;
}

/* Violet Card */
.metric-violet {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(168, 85, 247, 0.6) !important;
}
.metric-violet:hover {
    box-shadow: 0 8px 28px rgba(168, 85, 247, 0.45) !important;
}

/* Blue/Indigo Card */
.metric-blue {
    background: linear-gradient(135deg, rgba(12, 74, 110, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.6) !important;
}
.metric-blue:hover {
    box-shadow: 0 8px 28px rgba(56, 189, 248, 0.45) !important;
}

/* Green Card */
.metric-green {
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(52, 211, 153, 0.6) !important;
}
.metric-green:hover {
    box-shadow: 0 8px 28px rgba(52, 211, 153, 0.45) !important;
}

/* Amber/Red Card */
.metric-coral {
    background: linear-gradient(135deg, rgba(124, 45, 18, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(251, 146, 60, 0.6) !important;
}
.metric-coral:hover {
    box-shadow: 0 8px 28px rgba(251, 146, 60, 0.45) !important;
}

.metric-emergency-active {
    background: linear-gradient(135deg, rgba(153, 27, 27, 0.95) 0%, rgba(69, 10, 10, 0.94) 100%) !important;
    border: 2px solid #EF4444 !important;
    animation: emergency-glow 1.2s infinite alternate !important;
}

@keyframes emergency-glow {
    0% { box-shadow: 0 0 12px rgba(239, 68, 68, 0.5); border-color: #EF4444; }
    100% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.85); border-color: #DC2626; }
}

.metric-label {
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #FFFFFF !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9) !important;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 0.45rem;
}

.metric-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.35rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.9) !important;
    line-height: 1.2;
}

.metric-subtext {
    font-size: 0.95rem !important;
    font-weight: 500;
    color: #E2E8F0 !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8) !important;
    margin-top: 0.35rem;
}

/* Junction Cards (Translucent Dark Cyber Glass) */
.junction-card {
    border-radius: 18px;
    padding: 1.35rem;
    margin-bottom: 1rem;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
}

.junction-card p, .junction-card span, .junction-card div, .junction-card b {
    color: #FFFFFF !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8) !important;
}

.junction-card:hover {
    transform: translateY(-5px);
}

/* Junction 1: Violet */
.j-theme-violet {
    background: linear-gradient(145deg, rgba(30, 27, 75, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(168, 85, 247, 0.6) !important;
}
.j-theme-violet:hover {
    border-color: #A855F7 !important;
    box-shadow: 0 14px 30px rgba(168, 85, 247, 0.35) !important;
}

/* Junction 2: Indigo/Cyan */
.j-theme-blue {
    background: linear-gradient(145deg, rgba(12, 74, 110, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.6) !important;
}
.j-theme-blue:hover {
    border-color: #38BDF8 !important;
    box-shadow: 0 14px 30px rgba(56, 189, 248, 0.35) !important;
}

/* Junction 3: Green */
.j-theme-green {
    background: linear-gradient(145deg, rgba(6, 78, 59, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(52, 211, 153, 0.6) !important;
}
.j-theme-green:hover {
    border-color: #34D399 !important;
    box-shadow: 0 14px 30px rgba(52, 211, 153, 0.35) !important;
}

/* Junction 4: Orange */
.j-theme-orange {
    background: linear-gradient(145deg, rgba(124, 45, 18, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%) !important;
    border: 1.5px solid rgba(251, 146, 60, 0.6) !important;
}
.j-theme-orange:hover {
    border-color: #FB923C !important;
    box-shadow: 0 14px 30px rgba(251, 146, 60, 0.35) !important;
}

/* Traffic Light Mini Housing */
.traffic-housing {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #0F172A;
    padding: 6px 12px;
    border-radius: 999px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5), 0 4px 6px rgba(0,0,0,0.2);
}

.light-lens {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    opacity: 0.25;
    transition: all 0.3s ease;
}

.light-lens.red { background: #EF4444; }
.light-lens.yellow { background: #F59E0B; }
.light-lens.green { background: #10B981; }

.light-lens.red.active {
    opacity: 1;
    box-shadow: 0 0 12px #EF4444, 0 0 20px #EF4444;
    animation: glow-pulse-red 1.2s infinite alternate;
}

.light-lens.yellow.active {
    opacity: 1;
    box-shadow: 0 0 12px #F59E0B, 0 0 20px #F59E0B;
    animation: glow-pulse-yellow 1.2s infinite alternate;
}

.light-lens.green.active {
    opacity: 1;
    box-shadow: 0 0 14px #10B981, 0 0 22px #10B981;
    animation: glow-pulse-green 1.2s infinite alternate;
}

@keyframes glow-pulse-green {
    0% { transform: scale(1); filter: brightness(1); }
    100% { transform: scale(1.15); filter: brightness(1.3); }
}

@keyframes glow-pulse-red {
    0% { transform: scale(1); filter: brightness(1); }
    100% { transform: scale(1.15); filter: brightness(1.3); }
}

@keyframes glow-pulse-yellow {
    0% { transform: scale(1); filter: brightness(1); }
    100% { transform: scale(1.15); filter: brightness(1.3); }
}

/* Progress bar with flowing stripe */
.bar-track {
    background: rgba(51, 65, 85, 0.8);
    height: 9px;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 6px;
    margin-bottom: 10px;
}

.bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.5s ease-in-out;
}

.bar-fill-violet { background: linear-gradient(90deg, #8B5CF6, #C084FC); }
.bar-fill-blue { background: linear-gradient(90deg, #0284C7, #38BDF8); }
.bar-fill-green { background: linear-gradient(90deg, #059669, #34D399); }
.bar-fill-orange { background: linear-gradient(90deg, #EA580C, #FB923C); }

/* Quick stats table in junction */
.junction-stat-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 10px;
    font-size: 0.92rem;
}

.junction-stat-item {
    background: rgba(30, 41, 59, 0.85);
    border: 1px solid rgba(71, 85, 105, 0.6);
    border-radius: 10px;
    padding: 7px 10px;
    color: #FFFFFF !important;
}

.junction-stat-item b {
    color: #38BDF8 !important;
    font-size: 1.05rem !important;
}

/* Event badges */
.event-card {
    padding: 0.85rem 1.1rem;
    border-radius: 12px;
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(71, 85, 105, 0.6);
    border-left: 5px solid #6366F1;
    color: #FFFFFF !important;
}

.event-emergency {
    background: rgba(69, 10, 10, 0.92);
    border-color: #DC2626;
    border-left: 5px solid #EF4444;
    color: #FEE2E2 !important;
    font-weight: 700;
}

.event-cleared {
    background: rgba(6, 78, 59, 0.92);
    border-color: #059669;
    border-left: 5px solid #10B981;
    color: #ECFDF5 !important;
    font-weight: 700;
}

/* ================= SIDEBAR OPERATOR CONSOLE STYLING (DARK CYBER) ================= */
[data-testid="stSidebar"] {
    background: rgba(10, 16, 32, 0.94) !important;
    border-right: 1.5px solid rgba(56, 189, 248, 0.35) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
}

.station-hud {
    background: rgba(15, 23, 42, 0.92);
    color: #FFFFFF !important;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(56, 189, 248, 0.35);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

@keyframes hud-blink {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.35; transform: scale(0.85); }
}

.live-green-led {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #10B981;
    display: inline-block;
    box-shadow: 0 0 10px #10B981;
    animation: hud-blink 1.5s infinite;
}

.sb-module-card {
    background: rgba(15, 23, 42, 0.88) !important;
    border: 1.5px solid rgba(71, 85, 105, 0.6) !important;
    border-radius: 14px;
    padding: 11px 14px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.sb-module-card:hover {
    border-color: rgba(56, 189, 248, 0.7) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(56, 189, 248, 0.2) !important;
}

.sb-module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    font-size: 0.9rem !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #FFFFFF !important;
}

.sb-module-badge {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    padding: 3px 10px !important;
    border-radius: 999px !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    display: inline-block !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9) !important;
}

.sb-badge-purple {
    background: #6D28D9 !important;
    color: #FFFFFF !important;
    border: 1px solid #A855F7 !important;
    box-shadow: 0 2px 8px rgba(109, 40, 217, 0.5) !important;
}

.sb-badge-blue {
    background: #0284C7 !important;
    color: #FFFFFF !important;
    border: 1px solid #38BDF8 !important;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.5) !important;
}

.sb-badge-yellow {
    background: #B45309 !important;
    color: #FFFFFF !important;
    border: 1px solid #FBBF24 !important;
    box-shadow: 0 2px 8px rgba(180, 83, 9, 0.5) !important;
}

.sb-badge-red {
    background: #B91C1C !important;
    color: #FFFFFF !important;
    border: 1px solid #F87171 !important;
    box-shadow: 0 2px 8px rgba(185, 28, 28, 0.5) !important;
}

.sb-badge-green {
    background: #047857 !important;
    color: #FFFFFF !important;
    border: 1px solid #34D399 !important;
    box-shadow: 0 2px 8px rgba(4, 120, 87, 0.5) !important;
}

/* Sidebar Selectboxes and Inputs - Dark Cyber Glass */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.45) !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #38BDF8 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

.sb-card-scenarios { border-left: 4px solid #8B5CF6; }
.sb-card-demand { border-left: 4px solid #0284C7; }
.sb-card-police { border-left: 4px solid #F59E0B; }
.sb-card-emergency { border-left: 4px solid #EF4444; }

@keyframes sb-emergency-glow {
    0% { border-color: #EF4444; box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }
    100% { border-color: #3B82F6; box-shadow: 0 0 20px rgba(59, 130, 246, 0.7); }
}

.sb-card-emergency-active {
    animation: sb-emergency-glow 1.2s infinite alternate !important;
    background: linear-gradient(145deg, rgba(69, 10, 10, 0.92) 0%, rgba(30, 27, 75, 0.92) 100%) !important;
}

/* Sidebar action button enhancements */
div[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    padding: 10px 16px !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.45) !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stSidebar"] button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(16, 185, 129, 0.6) !important;
}

div[data-testid="stSidebar"] button[kind="secondary"] {
    border-radius: 12px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    border: 1.5px solid rgba(71, 85, 105, 0.7) !important;
    background: rgba(30, 41, 59, 0.85) !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stSidebar"] button[kind="secondary"]:hover {
    color: #EF4444 !important;
    border-color: #EF4444 !important;
    background: rgba(69, 10, 10, 0.85) !important;
    transform: translateY(-2px) !important;
}

/* ================= FLOATING CATEGORY TABS WITH LARGE WHITE FONT ================= */
.stTabs [data-baseweb="tab-list"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
    background: rgba(15, 23, 42, 0.88) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.35) !important;
    border-radius: 20px !important;
    padding: 10px 14px !important;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5) !important;
    margin-bottom: 1.35rem !important;
    align-items: center !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 14px !important;
    padding: 10px 22px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.18rem !important;  /* INCREASED FEATURES FONT SIZE */
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    backdrop-filter: blur(10px) !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #FFFFFF !important;
    background: rgba(56, 189, 248, 0.2) !important;
    border-color: #38BDF8 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(56, 189, 248, 0.4) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #4F46E5 0%, #0284C7 100%) !important;
    color: #FFFFFF !important;
    border: 1.5px solid #38BDF8 !important;
    box-shadow: 0 6px 22px rgba(14, 165, 233, 0.65) !important;
    transform: translateY(-1px) scale(1.03) !important;
    font-weight: 800 !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* Secondary / Sub-Tab Styling inside Categories */
.stTabs .stTabs [data-baseweb="tab-list"] {
    background: rgba(20, 30, 55, 0.75) !important;
    border: 1px solid rgba(147, 197, 253, 0.25) !important;
    padding: 6px 10px !important;
    border-radius: 14px !important;
    margin-bottom: 1rem !important;
}

.stTabs .stTabs [data-baseweb="tab"] {
    font-size: 1.06rem !important;
    padding: 8px 18px !important;
    font-weight: 700 !important;
}

/* ================= CITY ROAD NETWORK ANIMATIONS ================= */
.city-arena-container {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.88) 100%) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.35) !important;
    border-radius: 22px;
    padding: 1.35rem;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5) !important;
    margin-top: 0.75rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
}

@keyframes lane-flow-east {
    0% { stroke-dashoffset: 28; }
    100% { stroke-dashoffset: 0; }
}

@keyframes lane-flow-south {
    0% { stroke-dashoffset: 28; }
    100% { stroke-dashoffset: 0; }
}

@keyframes lane-flow-west {
    0% { stroke-dashoffset: 0; }
    100% { stroke-dashoffset: 28; }
}

@keyframes lane-flow-north {
    0% { stroke-dashoffset: 0; }
    100% { stroke-dashoffset: 28; }
}

@keyframes drive-car-east {
    0% { transform: translateX(0px); opacity: 0; }
    8% { opacity: 1; }
    92% { opacity: 1; }
    100% { transform: translateX(450px); opacity: 0; }
}

@keyframes drive-car-south {
    0% { transform: translateY(0px); opacity: 0; }
    8% { opacity: 1; }
    92% { opacity: 1; }
    100% { transform: translateY(200px); opacity: 0; }
}

@keyframes drive-car-west {
    0% { transform: translateX(0px); opacity: 0; }
    8% { opacity: 1; }
    92% { opacity: 1; }
    100% { transform: translateX(-450px); opacity: 0; }
}

@keyframes drive-car-north {
    0% { transform: translateY(0px); opacity: 0; }
    8% { opacity: 1; }
    92% { opacity: 1; }
    100% { transform: translateY(-200px); opacity: 0; }
}

@keyframes radar-pulse-wave {
    0% { r: 12px; opacity: 0.85; stroke-width: 2.5px; }
    100% { r: 75px; opacity: 0; stroke-width: 0.5px; }
}

@keyframes emer-siren-strobe {
    0% { filter: drop-shadow(0 0 6px #EF4444); }
    50% { filter: drop-shadow(0 0 16px #3B82F6); }
    100% { filter: drop-shadow(0 0 6px #EF4444); }
}

@keyframes emer-road-highlight {
    0% { stroke: #EF4444; stroke-width: 5; opacity: 0.7; }
    50% { stroke: #F59E0B; stroke-width: 7; opacity: 1; filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.7)); }
    100% { stroke: #EF4444; stroke-width: 5; opacity: 0.7; }
}
</style>
""")

# Rainbow flowing header strip
html('<div class="rainbow-strip"></div>')

# State Management
if "network" not in st.session_state or "manual_override" not in inspect.signature(st.session_state.network.step).parameters:
    st.session_state.network = TrafficNetwork(seed=7)
if "history" not in st.session_state:
    st.session_state.history = []
if "last_events" not in st.session_state:
    st.session_state.last_events = []
if "predictor" not in st.session_state:
    st.session_state.predictor = CongestionPredictor()
if "coop_controller" not in st.session_state:
    st.session_state.coop_controller = CooperativeController()
if "emergency_mgr" not in st.session_state:
    st.session_state.emergency_mgr = EmergencyCorridorManager()
if "sensor_twin" not in st.session_state:
    st.session_state.sensor_twin = IoTSensorTwin(seed=42)
if "incident_mgr" not in st.session_state:
    st.session_state.incident_mgr = IncidentManager()
if "explainer" not in st.session_state:
    st.session_state.explainer = DecisionExplainer()
if "scenario_lab" not in st.session_state:
    st.session_state.scenario_lab = ScenarioLab(seed=7)
if "scenario_result" not in st.session_state:
    st.session_state.scenario_result = None

network = st.session_state.network

# Hero Section
html("""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
        <div>
            <h1 class="hero-title">🚦 FlowSync — Smart Urban Traffic Management System</h1>
            <p class="hero-subtitle">Decentralized 4-Junction Adaptive Signal Control • Dynamic Queue Balancing • Priority Emergency Corridors</p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="status-pill">
                <span class="pulse-dot"></span> Edge Node-04: Connected
            </span>
            
        </div>
    </div>
</div>
""")

# Sidebar Controls
with st.sidebar:
    html('<div class="rainbow-strip" style="height:4px; margin-bottom: 0.8rem;"></div>')
    
    # Station Telemetry HUD Header
    html("""
    <div class="station-hud">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 0.78rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px;">🎛️ TOC-SECTOR-04 DISPATCH</span>
            <span style="display: flex; align-items: center; gap: 5px; font-size: 0.72rem; color: #4ADE80; font-weight: 700;">
                <span class="live-green-led"></span> ACTIVE
            </span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; color: #CBD5E1;">
            <span>Controller: NEMA TS2</span>
            <span>Loop Scan: 200ms</span>
        </div>
    </div>
    """)
    
    # Module 1: Scenario Presets
    html("""
    <div class="sb-module-card sb-card-scenarios">
        <div class="sb-module-header">
            <span>🎮 Scenario Profile</span>
            <span class="sb-module-badge sb-badge-purple">TEST PROFILES</span>
        </div>
    </div>
    """)
    preset_choice = st.selectbox(
        "Load Test Scenario",
        options=[
            "Standard Balanced Flow",
            "Morning Peak Commute (North Gate J1 Heavy)",
            "College Zone Congestion (Circle J3 Heavy)",
            "Inbound Hospital Priority Run",
            "Late Night Minimal Flow (0.5x)"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
    default_demand = 1.0
    default_emer = False
    if preset_choice == "Morning Peak Commute (North Gate J1 Heavy)":
        default_demand = 1.6
    elif preset_choice == "College Zone Congestion (Circle J3 Heavy)":
        default_demand = 1.4
    elif preset_choice == "Inbound Hospital Priority Run":
        default_demand = 1.2
        default_emer = True
    elif preset_choice == "Late Night Minimal Flow (0.5x)":
        default_demand = 0.5
        
    # Module 2: Inflow Demand
    html("""
    <div class="sb-module-card sb-card-demand" style="margin-top: 10px;">
        <div class="sb-module-header">
            <span>🚗 Inflow Demand Multiplier</span>
            <span class="sb-module-badge sb-badge-blue">SENSOR MULTIPLIER</span>
        </div>
    </div>
    """)
    demand = st.slider("Traffic Demand Multiplier", 0.4, 2.2, default_demand, 0.1, label_visibility="collapsed")
    
    # Module 3: Police Manual Key Override
    html("""
    <div class="sb-module-card sb-card-police" style="margin-top: 10px;">
        <div class="sb-module-header">
            <span>👮 Police Cabinet Key</span>
            <span class="sb-module-badge sb-badge-yellow">MANUAL INTERCEPT</span>
        </div>
    </div>
    """)
    override_choice = st.selectbox(
        "Physical Cabinet Override Switch",
        options=[
            "Autonomous Adaptive Control (Default)",
            "Force Green: J1 - North Gate",
            "Force Green: J2 - Market Road",
            "Force Green: J3 - College Circle",
            "Force Green: J4 - Hospital Road",
            "Force ALL-RED (Emergency Clearance)"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
    manual_override = None
    if override_choice == "Force Green: J1 - North Gate":
        manual_override = 0
    elif override_choice == "Force Green: J2 - Market Road":
        manual_override = 1
    elif override_choice == "Force Green: J3 - College Circle":
        manual_override = 2
    elif override_choice == "Force Green: J4 - Hospital Road":
        manual_override = 3
    elif override_choice == "Force ALL-RED (Emergency Clearance)":
        manual_override = "ALL_RED"
    
    # Module 4: Emergency Dispatch
    emer_cls = "sb-module-card sb-card-emergency sb-card-emergency-active" if network.emergency_active else "sb-module-card sb-card-emergency"
    html(f"""
    <div class="{emer_cls}" style="margin-top: 10px;">
        <div class="sb-module-header">
            <span>🚨 Priority Siren Transponder</span>
            <span class="sb-module-badge sb-badge-red">DSRC PREEMPTION</span>
        </div>
    </div>
    """)
    emergency = st.checkbox("Trigger Priority Vehicle (Ambulance/Fire Unit)", value=default_emer)
    if emergency:
        st.warning("⚠️ Transponder verified! Corridor preemption locked: J4 ➔ J3 ➔ J1.")
    
    # Module 5: Actuator Execution
    html("""
    <div class="sb-module-card" style="border-left: 4px solid #10B981; margin-top: 10px;">
        <div class="sb-module-header">
            <span>⚡ Cycle Actuator (5s / step)</span>
            <span class="sb-module-badge sb-badge-green">STEP WINDOW</span>
        </div>
    </div>
    """)
    steps = st.select_slider("Cycle Steps to Advance", options=[5, 10, 20, 30, 60], value=20, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_clicked = st.button("▶ Advance Controller Cycle", type="primary", use_container_width=True)
    reset_clicked = st.button("↺ Reset Controller Grid State", use_container_width=True)
    


# Reset action
if reset_clicked:
    st.session_state.network = TrafficNetwork(seed=7)
    st.session_state.history = []
    st.session_state.last_events = []
    st.session_state.emergency_mgr = EmergencyCorridorManager()
    st.session_state.sensor_twin = IoTSensorTwin(seed=42)
    st.session_state.incident_mgr = IncidentManager()
    st.session_state.scenario_result = None
    st.rerun()

# Run action
if run_clicked:
    collected_events = []
    for _ in range(int(steps)):
        try:
            events = network.step(demand_multiplier=demand, request_emergency=emergency, manual_override=manual_override)
        except TypeError:
            st.session_state.network = TrafficNetwork(seed=7)
            network = st.session_state.network
            events = network.step(demand_multiplier=demand, request_emergency=emergency, manual_override=manual_override)
        collected_events.extend(events)
        row = network.snapshot()
        st.session_state.history.append(row)
        
        # Sync state machines on every tick
        active_idx = next((i for i, j in enumerate(row["junctions"]) if j["signal"] == "GREEN"), 0)
        active_q = row["junctions"][active_idx]["vehicles_waiting"]
        st.session_state.emergency_mgr.update_tick(active_idx, active_q, row["time_seconds"])
        st.session_state.sensor_twin.sync_with_simulation(row, network.emergency_active)
        st.session_state.incident_mgr.scan_network_anomalies(row, st.session_state.sensor_twin, st.session_state.emergency_mgr.state)
        
        emergency = False
    if collected_events:
        st.session_state.last_events = collected_events[-12:]
    st.session_state.history = st.session_state.history[-500:]
    st.rerun()

snapshot = network.snapshot()
summary = summarize_metrics(network.metrics, network.fixed_metrics)

# Run intelligence models on authoritative snapshot
predictions = st.session_state.predictor.predict_network(snapshot, st.session_state.history)
coop_data = st.session_state.coop_controller.evaluate_cooperation(
    snapshot,
    network.emergency_active,
    list(network.emergency_route) if network.emergency_route else None
)
explanations = st.session_state.explainer.explain_cycle(
    snapshot,
    coop_data["states"],
    network.emergency_active,
    list(network.emergency_route) if network.emergency_route else None,
    manual_override
)
st.session_state.sensor_twin.sync_with_simulation(snapshot, network.emergency_active)
active_incidents = st.session_state.incident_mgr.scan_network_anomalies(snapshot, st.session_state.sensor_twin, st.session_state.emergency_mgr.state)

total_queued = int(sum(x["vehicles_waiting"] for x in snapshot["junctions"]))
sim_time_sec = network.time_step * 5
adaptive_wait = summary['adaptive_avg_wait']
emergency_active = network.emergency_active

# 4 VIBGYOR Colored Metric Cards
emergency_card_class = "metric-box metric-coral metric-emergency-active" if emergency_active else "metric-box metric-coral"
emergency_text = "🚨 CORRIDOR ACTIVE" if emergency_active else "🟢 Standby Normal"

html(f"""
<div class="metric-row">
    <div class="metric-box metric-violet">
        <div class="metric-label">⏱️ Controller Master Clock</div>
        <div class="metric-value">{sim_time_sec}s</div>
        <div class="metric-subtext">Cycle #{network.time_step} (5.0s actuation step)</div>
    </div>
    <div class="metric-box metric-blue">
        <div class="metric-label">🚗 Grid Queue Mass</div>
        <div class="metric-value">{total_queued}</div>
        <div class="metric-subtext">Peak holding capacity: 180 vehicles</div>
    </div>
    <div class="metric-box metric-green">
        <div class="metric-label">⚡ Commuter Delay Average</div>
        <div class="metric-value">{adaptive_wait:.1f}s</div>
        <div class="metric-subtext">{summary['wait_improvement_pct']:+.1f}% delay reduction vs. cyclic</div>
    </div>
    <div class="{emergency_card_class}">
        <div class="metric-label">🚑 Priority Preemption Interlock</div>
        <div class="metric-value" style="font-size: 1.35rem;">{emergency_text}</div>
        <div class="metric-subtext">{'Dynamic corridor green wave engaged' if emergency_active else 'Optical/Radio transponder listening'}</div>
    </div>
</div>
""")

# =============================================================================
# JUNCTION UI HELPER CONFIG & BADGE PALETTE
# =============================================================================
JUNCTION_STYLES = [
    {"theme": "j-theme-violet", "badge": "#C084FC", "bar": "bar-fill-violet", "tag": "🟣 Junction 1", "road": "North Gate", "cam": "📷 CAM-01 (YOLOv8)"},
    {"theme": "j-theme-blue", "badge": "#38BDF8", "bar": "bar-fill-blue", "tag": "🔵 Junction 2", "road": "Market Road", "cam": "📷 CAM-02 (YOLOv8)"},
    {"theme": "j-theme-green", "badge": "#34D399", "bar": "bar-fill-green", "tag": "🟢 Junction 3", "road": "College Circle", "cam": "📷 CAM-03 (YOLOv8)"},
    {"theme": "j-theme-orange", "badge": "#FB923C", "bar": "bar-fill-orange", "tag": "🟠 Junction 4", "road": "Hospital Road", "cam": "📷 CAM-04 (YOLOv8)"},
]

# =============================================================================
# MASTER FEATURE CATEGORIES (High-Level Hierarchical Navigation)
# =============================================================================
cat_grid, cat_ai, cat_emergency, cat_xai, cat_benchmarks, cat_demo = st.tabs(
    [
        "🏙️ City Grid & Topology",
        "🔮 Predictive & Cooperative AI",
        "🚑 Emergency & IoT Sensors",
        "🧠 Explainable AI (XAI)",
        "🧪 Scenario Lab & Benchmarks",
        "🎬 Demo Video & Specifications"
    ]
)

# -----------------------------------------------------------------------------
# CATEGORY 1: CITY GRID & TOPOLOGY
# -----------------------------------------------------------------------------
with cat_grid:
    tab_live, tab_events = st.tabs(
        [
            "🚏 Active Junction Telemetry & Topology",
            "📟 Edge Controller System Logs"
        ]
    )
    with tab_live:
        st.markdown("### 🚏 Active Junction Telemetry")
        st.caption("Live coordinated signal state, queue density, downstream backpressure, and allocated green timing.")
    
        cols = st.columns(4)
        for i, junction in enumerate(snapshot["junctions"]):
            style = JUNCTION_STYLES[i]
            sig = junction["signal"]
        
            red_cls = "red active" if sig == "RED" else "red"
            yel_cls = "yellow active" if sig == "YELLOW" else "yellow"
            grn_cls = "green active" if sig == "GREEN" else "green"
        
            sig_badge_color = "#10B981" if sig == "GREEN" else ("#F59E0B" if sig == "YELLOW" else "#EF4444")
            sig_bg = "#ECFDF5" if sig == "GREEN" else ("#FEF3C7" if sig == "YELLOW" else "#FEF2F2")
        
            occupancy_pct = junction["downstream_occupancy"]
            queue_count = junction["vehicles_waiting"]
            wait_time = junction["avg_wait"]
            green_alloc = junction["green_seconds"]
        
            with cols[i]:
                card_html = (
                    f'<div class="junction-card {style["theme"]}">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">'
                    f'<span style="font-size: 0.85rem; font-weight: 700; color: {style["badge"]}; text-transform: uppercase;">{style["tag"]}</span>'
                    f'<div class="traffic-housing">'
                    f'<span class="light-lens {red_cls}"></span>'
                    f'<span class="light-lens {yel_cls}"></span>'
                    f'<span class="light-lens {grn_cls}"></span>'
                    f'</div>'
                    f'</div>'
                    f'<div style="display: flex; justify-content: space-between; font-size: 0.73rem; color: #E2E8F0; margin-bottom: 3px;"><span>{style["cam"]}</span><span style="color: #10B981; font-weight: 700;">● STREAM 1080p</span></div>'
                    f'<div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.5rem; font-family: Outfit, sans-serif;">{style["road"]}</div>'
                    f'<div style="display: flex; align-items: center; justify-content: space-between; margin: 0.6rem 0;">'
                    f'<span style="font-weight: 700; font-size: 0.85rem; padding: 4px 10px; border-radius: 999px; background: {sig_bg}; color: {sig_badge_color};">● {sig} SIGNAL</span>'
                    f'<span style="font-weight: 600; font-size: 0.85rem; color: #F1F5F9;">Green: <b>{green_alloc}s</b></span>'
                    f'</div>'
                    f'<div style="font-size: 0.8rem; font-weight: 600; color: #E2E8F0; margin-top: 0.5rem; display: flex; justify-content: space-between;">'
                    f'<span>Downstream Backpressure</span>'
                    f'<span>{occupancy_pct}%</span>'
                    f'</div>'
                    f'<div class="bar-track">'
                    f'<div class="bar-fill {style["bar"]}" style="width: {min(occupancy_pct, 100)}%;"></div>'
                    f'</div>'
                    f'<div class="junction-stat-grid">'
                    f'<div class="junction-stat-item">🚗 Queue: <b>{queue_count}</b></div>'
                    f'<div class="junction-stat-item">⏱️ Wait: <b>{wait_time:.1f}s</b></div>'
                    f'</div>'
                    f'</div>'
                )
                html(card_html)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🗺️ City Road Network Topology & Live Simulation")
        st.caption("Coordinated 4-junction ring flow: **J1 (North)** ➔ **J2 (Market)** ➔ **J4 (Hospital)** ➔ **J3 (College)** ➔ **J1 (North)**")
    
        view_sim, view_graph = st.tabs(["🏙️ Live Animated City Grid", "📊 Analytical Topology Graph"])
    
        with view_sim:
            j1 = snapshot["junctions"][0]
            j2 = snapshot["junctions"][1]
            j3 = snapshot["junctions"][2]
            j4 = snapshot["junctions"][3]
        
            j1_sig_color = "#10B981" if j1["signal"] == "GREEN" else ("#F59E0B" if j1["signal"] == "YELLOW" else "#EF4444")
            j2_sig_color = "#10B981" if j2["signal"] == "GREEN" else ("#F59E0B" if j2["signal"] == "YELLOW" else "#EF4444")
            j3_sig_color = "#10B981" if j3["signal"] == "GREEN" else ("#F59E0B" if j3["signal"] == "YELLOW" else "#EF4444")
            j4_sig_color = "#10B981" if j4["signal"] == "GREEN" else ("#F59E0B" if j4["signal"] == "YELLOW" else "#EF4444")
        
            active_name = next((j["name"] for j in snapshot["junctions"] if j["signal"] == "GREEN"), "Coordinated Cycle")
            active_time = next((j["green_seconds"] for j in snapshot["junctions"] if j["signal"] == "GREEN"), 20)
        
            # Priority corridor overlay paths
            emer_overlay_html = ""
            if emergency_active:
                emer_overlay_html = (
                    '<path d="M 660,335 L 180,335 L 180,95" fill="none" class="emer-road-highlight" style="animation: emer-road-highlight 1.2s infinite alternate; stroke-dasharray: 12 6;" />'
                    '<g style="animation: emer-siren-strobe 0.8s infinite alternate;">'
                    '<rect x="390" y="324" width="38" height="20" rx="5" fill="#FFFFFF" stroke="#EF4444" stroke-width="2"/>'
                    '<text x="409" y="338" font-size="11" font-weight="900" text-anchor="middle" fill="#EF4444" font-family="Outfit">🚑 PRIORITY</text>'
                    '</g>'
                )
        
            city_svg = f"""
            <div class="city-arena-container">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-weight: 700; font-size: 0.95rem; color: #FFFFFF;">🏙️ Downtown Arterial Loop</span>
                        <span style="background: #EEF2FF; color: #4F46E5; font-size: 0.75rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; border: 1px solid #C7D2FE;">
                            ⚡ Clockwise Coordinated Wave
                        </span>
                    </div>
                    <div style="font-size: 0.85rem; color: #E2E8F0;">
                        Active Phase: <b style="color: #059669;">{active_name}</b> ({active_time}s allocated)
                    </div>
                </div>
            
                <svg width="100%" height="410" viewBox="0 0 840 410" style="background: linear-gradient(135deg, #F8FAFC 0%, #EEF2F6 100%); border-radius: 16px; border: 1px solid rgba(56, 189, 248, 0.35);">
                    <defs>
                        <linearGradient id="bg-grid" width="40" height="40" patternUnits="userSpaceOnUse">
                            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#E2E8F0" stroke-width="0.8"/>
                        </linearGradient>
                    </defs>
                
                    <!-- City Blocks & Parks -->
                    <rect x="230" y="130" width="380" height="170" rx="16" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.5" />
                    <rect x="245" y="145" width="350" height="140" rx="12" fill="#FFFFFF" opacity="0.6" />
                
                    <!-- Central Command Radar Pulse -->
                    <circle cx="420" cy="215" r="14" fill="none" stroke="#10B981" style="animation: radar-pulse-wave 2.8s infinite;" />
                    <circle cx="420" cy="215" r="14" fill="none" stroke="#6366F1" style="animation: radar-pulse-wave 2.8s infinite 1.4s;" />
                    <circle cx="420" cy="215" r="18" fill="#4F46E5" />
                    <text x="420" y="219" font-size="11" text-anchor="middle" fill="white" font-weight="bold">AI</text>
                
                    <text x="420" y="250" font-size="12" font-weight="700" text-anchor="middle" fill="#1E293B" font-family="Outfit">Central Coordination Hub</text>
                    <text x="420" y="266" font-size="10" text-anchor="middle" fill="#64748B">Dynamic Queue Lookahead & Priority Dispatch</text>
                
                    <!-- Asphalt Ring Roads (44px width) -->
                    <!-- North Road (J1 -> J2) -->
                    <line x1="180" y1="95" x2="660" y2="95" stroke="#1E293B" stroke-width="42" stroke-linecap="round" />
                    <!-- East Road (J2 -> J4) -->
                    <line x1="660" y1="95" x2="660" y2="335" stroke="#1E293B" stroke-width="42" stroke-linecap="round" />
                    <!-- South Road (J4 -> J3) -->
                    <line x1="660" y1="335" x2="180" y2="335" stroke="#1E293B" stroke-width="42" stroke-linecap="round" />
                    <!-- West Road (J3 -> J1) -->
                    <line x1="180" y1="335" x2="180" y2="95" stroke="#1E293B" stroke-width="42" stroke-linecap="round" />
                
                    <!-- Flowing Yellow Centerlines -->
                    <line x1="180" y1="95" x2="660" y2="95" stroke="#FBBF24" stroke-width="2.5" stroke-dasharray="10 8" style="animation: lane-flow-east 1.8s linear infinite;" />
                    <line x1="660" y1="95" x2="660" y2="335" stroke="#FBBF24" stroke-width="2.5" stroke-dasharray="10 8" style="animation: lane-flow-south 1.8s linear infinite;" />
                    <line x1="660" y1="335" x2="180" y2="335" stroke="#FBBF24" stroke-width="2.5" stroke-dasharray="10 8" style="animation: lane-flow-west 1.8s linear infinite;" />
                    <line x1="180" y1="335" x2="180" y2="95" stroke="#FBBF24" stroke-width="2.5" stroke-dasharray="10 8" style="animation: lane-flow-north 1.8s linear infinite;" />
                
                    <!-- Zebra Crossings -->
                    <!-- J1 East Crossing -->
                    <g stroke="#FFFFFF" stroke-width="2.5" opacity="0.8">
                        <line x1="225" y1="80" x2="225" y2="110"/> <line x1="230" y1="80" x2="230" y2="110"/> <line x1="235" y1="80" x2="235" y2="110"/>
                    </g>
                    <!-- J2 South Crossing -->
                    <g stroke="#FFFFFF" stroke-width="2.5" opacity="0.8">
                        <line x1="645" y1="140" x2="675" y2="140"/> <line x1="645" y1="145" x2="675" y2="145"/> <line x1="645" y1="150" x2="675" y2="150"/>
                    </g>
                    <!-- J4 West Crossing -->
                    <g stroke="#FFFFFF" stroke-width="2.5" opacity="0.8">
                        <line x1="615" y1="320" x2="615" y2="350"/> <line x1="610" y1="320" x2="610" y2="350"/> <line x1="605" y1="320" x2="605" y2="350"/>
                    </g>
                    <!-- J3 North Crossing -->
                    <g stroke="#FFFFFF" stroke-width="2.5" opacity="0.8">
                        <line x1="165" y1="290" x2="195" y2="290"/> <line x1="165" y1="285" x2="195" y2="285"/> <line x1="165" y1="280" x2="195" y2="280"/>
                    </g>
                
                    <!-- Emergency Priority Corridor Overlay -->
                    {emer_overlay_html}
                
                    <!-- ANIMATED DRIVING VEHICLES -->
                    <!-- Northbound Highway (Eastbound cars: J1 -> J2) -->
                    <g style="animation: drive-car-east 3.8s linear infinite;">
                        <rect x="200" y="87" width="22" height="12" rx="4" fill="#3B82F6"/>
                        <rect x="205" y="89" width="9" height="8" rx="2" fill="#DBEAFE"/>
                        <circle cx="204" cy="99" r="2" fill="#0F172A"/> <circle cx="218" cy="99" r="2" fill="#0F172A"/>
                    </g>
                    <g style="animation: drive-car-east 3.8s linear infinite 1.9s;">
                        <rect x="200" y="87" width="22" height="12" rx="4" fill="#10B981"/>
                        <rect x="205" y="89" width="9" height="8" rx="2" fill="#D1FAE5"/>
                        <circle cx="204" cy="99" r="2" fill="#0F172A"/> <circle cx="218" cy="99" r="2" fill="#0F172A"/>
                    </g>
                
                    <!-- East Highway (Southbound cars: J2 -> J4) -->
                    <g style="animation: drive-car-south 2.9s linear infinite;">
                        <rect x="654" y="115" width="12" height="22" rx="4" fill="#F59E0B"/>
                        <rect x="656" y="120" width="8" height="9" rx="2" fill="#FEF3C7"/>
                        <circle cx="653" cy="119" r="2" fill="#0F172A"/> <circle cx="653" cy="133" r="2" fill="#0F172A"/>
                    </g>
                    <g style="animation: drive-car-south 2.9s linear infinite 1.45s;">
                        <rect x="654" y="115" width="12" height="22" rx="4" fill="#8B5CF6"/>
                        <rect x="656" y="120" width="8" height="9" rx="2" fill="#EDE9FE"/>
                        <circle cx="653" cy="119" r="2" fill="#0F172A"/> <circle cx="653" cy="133" r="2" fill="#0F172A"/>
                    </g>
                
                    <!-- South Highway (Westbound cars: J4 -> J3) -->
                    <g style="animation: drive-car-west 3.8s linear infinite;">
                        <rect x="640" y="327" width="22" height="12" rx="4" fill="#EC4899"/>
                        <rect x="645" y="329" width="9" height="8" rx="2" fill="#FCE7F3"/>
                        <circle cx="644" cy="339" r="2" fill="#0F172A"/> <circle cx="658" cy="339" r="2" fill="#0F172A"/>
                    </g>
                    <g style="animation: drive-car-west 3.8s linear infinite 1.9s;">
                        <rect x="640" y="327" width="22" height="12" rx="4" fill="#06B6D4"/>
                        <rect x="645" y="329" width="9" height="8" rx="2" fill="#CFFAFE"/>
                        <circle cx="644" cy="339" r="2" fill="#0F172A"/> <circle cx="658" cy="339" r="2" fill="#0F172A"/>
                    </g>
                
                    <!-- West Highway (Northbound cars: J3 -> J1) -->
                    <g style="animation: drive-car-north 2.9s linear infinite;">
                        <rect x="174" y="315" width="12" height="22" rx="4" fill="#EA580C"/>
                        <rect x="176" y="320" width="8" height="9" rx="2" fill="#FFEDD5"/>
                        <circle cx="173" cy="319" r="2" fill="#0F172A"/> <circle cx="173" cy="333" r="2" fill="#0F172A"/>
                    </g>
                    <g style="animation: drive-car-north 2.9s linear infinite 1.45s;">
                        <rect x="174" y="315" width="12" height="22" rx="4" fill="#14B8A6"/>
                        <rect x="176" y="320" width="8" height="9" rx="2" fill="#CCFBF1"/>
                        <circle cx="173" cy="319" r="2" fill="#0F172A"/> <circle cx="173" cy="333" r="2" fill="#0F172A"/>
                    </g>
                
                    <!-- Road Direction Badges -->
                    <g fill="#94A3B8" font-size="11" font-weight="700">
                        <text x="420" y="80" text-anchor="middle">Northbound Arterial ➔</text>
                        <text x="695" y="215" text-anchor="middle" transform="rotate(90 695 215)">Eastern Bypass ➔</text>
                        <text x="420" y="365" text-anchor="middle">⬅ Hospital Parkway</text>
                        <text x="145" y="215" text-anchor="middle" transform="rotate(-90 145 215)">⬅ University Ring</text>
                    </g>
                
                    <!-- ================= JUNCTION TOWERS ================= -->
                    <!-- Junction 1: Violet (180, 95) -->
                    <g>
                        <circle cx="180" cy="95" r="32" fill="#FFFFFF" stroke="#7C3AED" stroke-width="4" filter="drop-shadow(0 4px 8px rgba(124, 58, 237, 0.2))"/>
                        <circle cx="180" cy="95" r="14" fill="{j1_sig_color}" stroke="#FFFFFF" stroke-width="2.5"/>
                        <text x="180" y="99" font-size="11" font-weight="900" text-anchor="middle" fill="#FFFFFF" font-family="Outfit">J1</text>
                        <!-- Floating label -->
                        <rect x="110" y="22" width="140" height="28" rx="8" fill="#FFFFFF" stroke="#DDD6FE" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.06))"/>
                        <text x="180" y="36" font-size="11" font-weight="800" text-anchor="middle" fill="#7C3AED" font-family="Outfit">🟣 North Gate</text>
                        <text x="180" y="47" font-size="9" font-weight="600" text-anchor="middle" fill="#64748B">🚗 {j1['vehicles_waiting']} Queued • {j1['signal']}</text>
                    </g>
                
                    <!-- Junction 2: Blue (660, 95) -->
                    <g>
                        <circle cx="660" cy="95" r="32" fill="#FFFFFF" stroke="#0284C7" stroke-width="4" filter="drop-shadow(0 4px 8px rgba(2, 132, 199, 0.2))"/>
                        <circle cx="660" cy="95" r="14" fill="{j2_sig_color}" stroke="#FFFFFF" stroke-width="2.5"/>
                        <text x="660" y="99" font-size="11" font-weight="900" text-anchor="middle" fill="#FFFFFF" font-family="Outfit">J2</text>
                        <!-- Floating label -->
                        <rect x="590" y="22" width="140" height="28" rx="8" fill="#FFFFFF" stroke="#BAE6FD" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.06))"/>
                        <text x="660" y="36" font-size="11" font-weight="800" text-anchor="middle" fill="#0284C7" font-family="Outfit">🔵 Market Road</text>
                        <text x="660" y="47" font-size="9" font-weight="600" text-anchor="middle" fill="#64748B">🚗 {j2['vehicles_waiting']} Queued • {j2['signal']}</text>
                    </g>
                
                    <!-- Junction 4: Orange (660, 335) -->
                    <g>
                        <circle cx="660" cy="335" r="32" fill="#FFFFFF" stroke="#EA580C" stroke-width="4" filter="drop-shadow(0 4px 8px rgba(234, 88, 12, 0.2))"/>
                        <circle cx="660" cy="335" r="14" fill="{j4_sig_color}" stroke="#FFFFFF" stroke-width="2.5"/>
                        <text x="660" y="339" font-size="11" font-weight="900" text-anchor="middle" fill="#FFFFFF" font-family="Outfit">J4</text>
                        <!-- Floating label -->
                        <rect x="590" y="375" width="140" height="28" rx="8" fill="#FFFFFF" stroke="#FED7AA" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.06))"/>
                        <text x="660" y="389" font-size="11" font-weight="800" text-anchor="middle" fill="#EA580C" font-family="Outfit">🟠 Hospital Road</text>
                        <text x="660" y="400" font-size="9" font-weight="600" text-anchor="middle" fill="#64748B">🚗 {j4['vehicles_waiting']} Queued • {j4['signal']}</text>
                    </g>
                
                    <!-- Junction 3: Green (180, 335) -->
                    <g>
                        <circle cx="180" cy="335" r="32" fill="#FFFFFF" stroke="#059669" stroke-width="4" filter="drop-shadow(0 4px 8px rgba(5, 150, 105, 0.2))"/>
                        <circle cx="180" cy="335" r="14" fill="{j3_sig_color}" stroke="#FFFFFF" stroke-width="2.5"/>
                        <text x="180" y="339" font-size="11" font-weight="900" text-anchor="middle" fill="#FFFFFF" font-family="Outfit">J3</text>
                        <!-- Floating label -->
                        <rect x="110" y="375" width="140" height="28" rx="8" fill="#FFFFFF" stroke="#BBF7D0" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.06))"/>
                        <text x="180" y="389" font-size="11" font-weight="800" text-anchor="middle" fill="#059669" font-family="Outfit">🟢 College Circle</text>
                        <text x="180" y="400" font-size="9" font-weight="600" text-anchor="middle" fill="#64748B">🚗 {j3['vehicles_waiting']} Queued • {j3['signal']}</text>
                    </g>
                </svg>
            </div>
            """
            html(city_svg)
        
        with view_graph:
            pos = {
                "J1": (0, 1),
                "J2": (1.5, 1),
                "J4": (1.5, 0),
                "J3": (0, 0)
            }
            fig_map = go.Figure()
            roads = [
                ("J1", "J2", "Northbound Arterial", "#8B5CF6"),
                ("J2", "J4", "Eastern Express Corridor", "#0284C7"),
                ("J4", "J3", "Hospital Link Boulevard", "#EA580C"),
                ("J3", "J1", "University Ring Road", "#059669")
            ]
            for start, end, road_name, r_color in roads:
                x0, y0 = pos[start]
                x1, y1 = pos[end]
                fig_map.add_trace(go.Scatter(
                    x=[x0, x1], y=[y0, y1],
                    mode="lines",
                    line=dict(width=7, color="#E2E8F0"),
                    hoverinfo="text",
                    hovertext=f"Roadway: {road_name}",
                    showlegend=False
                ))
                fig_map.add_trace(go.Scatter(
                    x=[x0, x1], y=[y0, y1],
                    mode="lines",
                    line=dict(width=3, color=r_color, dash="dot"),
                    hoverinfo="skip",
                    showlegend=False
                ))
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                fig_map.add_annotation(
                    x=mx, y=my, ax=x0, ay=y0,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=3, arrowsize=1.6, arrowwidth=2.5, arrowcolor=r_color
                )
            j_keys = ["J1", "J2", "J3", "J4"]
            vibgyor_node_colors = ["#7C3AED", "#0284C7", "#059669", "#EA580C"]
            for idx, key in enumerate(j_keys):
                j_data = snapshot["junctions"][idx]
                x, y = pos[key]
                q_size = max(28, min(j_data["vehicles_waiting"] * 2.5 + 24, 65))
                sig_color = "#10B981" if j_data["signal"] == "GREEN" else ("#F59E0B" if j_data["signal"] == "YELLOW" else "#EF4444")
                fig_map.add_trace(go.Scatter(
                    x=[x], y=[y],
                    mode="markers+text",
                    marker=dict(size=q_size, color=vibgyor_node_colors[idx], opacity=0.9, line=dict(width=5, color=sig_color)),
                    text=[f"<b>{key}</b><br>{j_data['signal']}"],
                    textposition="middle center",
                    textfont=dict(color="white", size=11, family="Outfit"),
                    hoverinfo="text",
                    hovertext=(
                        f"<b>{j_data['name']}</b><br>"
                        f"Signal: {j_data['signal']}<br>"
                        f"Queued Vehicles: {j_data['vehicles_waiting']}<br>"
                        f"Average Wait: {j_data['avg_wait']}s<br>"
                        f"Green Window: {j_data['green_seconds']}s"
                    ),
                    name=j_data["name"]
                ))
            fig_map.update_layout(
                xaxis=dict(visible=False, range=[-0.3, 1.8]),
                yaxis=dict(visible=False, range=[-0.25, 1.3]),
                height=370,
                margin=dict(l=15, r=15, t=10, b=10),
                plot_bgcolor="rgba(15, 23, 42, 0.85)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11))
            )
            st.plotly_chart(fig_map, use_container_width=True)


    with tab_events:
        st.markdown("### 📡 Edge Controller Telemetry & Field Event Logs")
        st.caption("Live terminal trace documenting sensor loop polling, actuator relay states, and preemption transactions.")
    
        # Terminal-styled edge log viewer
        terminal_logs = []
        if st.session_state.last_events:
            for i, ev in enumerate(reversed(st.session_state.last_events)):
                ts = f"00:{(network.time_step * 5 - i * 5) // 60:02d}:{(network.time_step * 5 - i * 5) % 60:02d}"
                terminal_logs.append(f'<div style="font-family: monospace; font-size: 0.86rem; padding: 4px 0; border-bottom: 1px solid #1E293B;"><span style="color: #E2E8F0;">[{ts}]</span> {ev}</div>')
        else:
            terminal_logs.append('<div style="font-family: monospace; font-size: 0.86rem; color: #94A3B8;">[00:00:00] [SYSTEM-INIT] Edge controller node initialized. Virtual loop telemetry active on Sector 4 ring.</div>')
    
        terminal_html = f"""
        <div style="background: #0F172A; color: #E2E8F0; padding: 1.25rem; border-radius: 14px; border: 1.5px solid #334155; box-shadow: inset 0 2px 6px rgba(0,0,0,0.4); margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 10px;">
                <span style="font-weight: 700; font-size: 0.85rem; color: #38BDF8;">📟 NEMA TS2 Edge Controller Console • Baud 115200</span>
                <span style="font-size: 0.75rem; color: #4ADE80; font-weight: 700;">● RS-485 BUS HEALTHY</span>
            </div>
            {"".join(terminal_logs)}
        </div>
        """
        html(terminal_html)
    
        st.markdown("""
        #### 🛡️ Fail-Safe Preemption & Clearance Protocol (NTCIP 1202 Standard):
        1. **Authentication:** Siren RF transponder validates cryptographically signed emergency dispatch certificates.
        2. **Corridor Lock:** Cross-conflicting approaches receive guaranteed 3.5s yellow + 1.5s all-red clearance interval before upstream release.
        3. **Pedestrian Interlock:** Walk-phase minimum timers (7.0s) are respected to prevent pedestrian stranding.
        """)



# -----------------------------------------------------------------------------
# CATEGORY 2: PREDICTIVE & COOPERATIVE AI
# -----------------------------------------------------------------------------
with cat_ai:
    tab_predict, tab_coop = st.tabs(
        [
            "🔮 AI Congestion Prediction (30s / 60s Horizon)",
            "🤝 Cooperative Intelligence & DSRC Mesh"
        ]
    )
    with tab_predict:
        st.markdown("### 🔮 AI Congestion Prediction & Queue Horizon Forecasting")
        st.caption("Decentralized multi-factor congestion risk evaluation (0-100), horizon growth estimation (30s/60s), and primary bottleneck attribution.")
    
        # 4 Congestion Risk Cards
        pred_cols = st.columns(4)
        for i, pred in enumerate(predictions):
            style = JUNCTION_STYLES[i]
        
            if pred.risk_level == "HIGH":
                risk_pill = '<span style="background: #FEE2E2; color: #DC2626; font-size: 0.75rem; font-weight: 800; padding: 3px 10px; border-radius: 999px;">🔴 HIGH RISK</span>'
                risk_color = "#DC2626"
            elif pred.risk_level == "MEDIUM":
                risk_pill = '<span style="background: #FEF3C7; color: #FBBF24; font-size: 0.75rem; font-weight: 800; padding: 3px 10px; border-radius: 999px;">🟡 MEDIUM RISK</span>'
                risk_color = "#D97706"
            else:
                risk_pill = '<span style="background: #DCFCE7; color: #059669; font-size: 0.75rem; font-weight: 800; padding: 3px 10px; border-radius: 999px;">🟢 LOW RISK</span>'
                risk_color = "#059669"
            
            with pred_cols[i]:
                html(f"""
                <div class="junction-card {style['theme']}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 0.82rem; font-weight: 800; color: {style['badge']}; text-transform: uppercase;">{style['tag']}</span>
                        {risk_pill}
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.4rem; font-family: Outfit;">{pred.junction_name}</div>
                    <div style="display: flex; align-items: baseline; gap: 6px; margin: 0.4rem 0;">
                        <span style="font-size: 1.85rem; font-weight: 800; color: {risk_color}; font-family: Outfit;">{pred.risk_score}</span>
                        <span style="font-size: 0.85rem; color: #E2E8F0;">/ 100 Risk Score</span>
                    </div>
                    <div style="font-size: 0.78rem; color: #F1F5F9; margin-bottom: 0.6rem;">
                        Primary Bottleneck: <b style="color: #FFFFFF;">{pred.primary_bottleneck}</b>
                    </div>
                    <div class="junction-stat-grid" style="margin-top: 0.4rem;">
                        <div class="junction-stat-item">🚗 Now: <b>{pred.current_queue}</b></div>
                        <div class="junction-stat-item">⏱️ Wait: <b>{pred.avg_wait_seconds}s</b></div>
                        <div class="junction-stat-item">🔮 30s: <b>{pred.predicted_queue_30s}</b></div>
                        <div class="junction-stat-item">🔮 60s: <b>{pred.predicted_queue_60s}</b></div>
                    </div>
                    <div style="margin-top: 0.6rem; font-size: 0.74rem; color: #F1F5F9; background: rgba(255,255,255,0.7); padding: 5px 8px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.35);">
                        💡 <i>{pred.recommendation}</i>
                    </div>
                </div>
                """)

        st.markdown("<br>", unsafe_allow_html=True)
    
        # Prediction Charts
        c_pred1, c_pred2 = st.columns([1.1, 0.9])
    
        with c_pred1:
            st.markdown("#### 📈 Queue Horizon Forecast: Current vs. 30s vs. 60s Projections")
            horizon_df = pd.DataFrame([
                {"Junction": p.junction_name.split(" - ")[0], "Horizon": "Current Queue", "Vehicles": p.current_queue}
                for p in predictions
            ] + [
                {"Junction": p.junction_name.split(" - ")[0], "Horizon": "+30 Seconds Proj.", "Vehicles": p.predicted_queue_30s}
                for p in predictions
            ] + [
                {"Junction": p.junction_name.split(" - ")[0], "Horizon": "+60 Seconds Proj.", "Vehicles": p.predicted_queue_60s}
                for p in predictions
            ])
        
            fig_horizon = px.bar(
                horizon_df,
                x="Junction",
                y="Vehicles",
                color="Horizon",
                barmode="group",
                color_discrete_sequence=["#6366F1", "#0284C7", "#EA580C"],
                text="Vehicles"
            )
            fig_horizon.update_layout(
                height=320,
                plot_bgcolor="rgba(15, 23, 42, 0.85)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=15, r=15, t=25, b=15),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_horizon, use_container_width=True)

        with c_pred2:
            st.markdown("#### 🧩 Transparent Risk Evidence Breakdown")
            breakdown_rows = []
            for p in predictions:
                j_short = p.junction_name.split(" - ")[0]
                for factor_name, factor_val in p.evidence_breakdown.items():
                    breakdown_rows.append({"Junction": j_short, "Factor": factor_name, "Points": factor_val})
            breakdown_df = pd.DataFrame(breakdown_rows)
        
            fig_evidence = px.bar(
                breakdown_df,
                x="Junction",
                y="Points",
                color="Factor",
                color_discrete_sequence=["#8B5CF6", "#0284C7", "#F59E0B", "#10B981"],
                title="Factor Attribution Points (Total = 100)"
            )
            fig_evidence.update_layout(
                height=320,
                plot_bgcolor="rgba(15, 23, 42, 0.85)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=15, r=15, t=35, b=15),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=10))
            )
            st.plotly_chart(fig_evidence, use_container_width=True)

        # Historical Congestion Trend
        if len(st.session_state.history) >= 3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📉 Dynamic Congestion Risk Evolution Over Time")
            trend_records = []
            for row in st.session_state.history:
                t_sec = row["time_seconds"]
                for idx, j_rec in enumerate(row["junctions"]):
                    score = min(100.0, (j_rec["vehicles_waiting"] / 45.0) * 45.0 + (j_rec["avg_wait"] / 40.0) * 35.0 + (j_rec["downstream_occupancy"] / 100.0) * 20.0)
                    trend_records.append({
                        "Time (s)": t_sec,
                        "Junction": j_rec["name"].split(" - ")[0],
                        "Risk Score": round(score, 1)
                    })
            trend_df = pd.DataFrame(trend_records)
            fig_trend = px.line(
                trend_df,
                x="Time (s)",
                y="Risk Score",
                color="Junction",
                color_discrete_map={"J1": "#7C3AED", "J2": "#0284C7", "J3": "#059669", "J4": "#EA580C"}
            )
            fig_trend.update_layout(
                height=280,
                plot_bgcolor="rgba(15, 23, 42, 0.85)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=15, r=15, t=10, b=10)
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        html("""
        <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 12px 16px; margin-top: 10px; font-size: 0.82rem; color: #F1F5F9;">
            <b>🛡️ Explainability & Safe Fallback Notice:</b> Congestion scores are calculated using transparent physical queue-pressure dynamics rather than unverified black-box neural networks. If an inductive loop sensor becomes stale or disconnected, the predictor automatically falls back to moving historical priors to prevent false preemption.
        </div>
        """)


    with tab_coop:
        st.markdown("### 🤝 Cooperative Junction Intelligence & Inter-Node Mesh")
        st.caption("Decentralized backpressure lookahead coordination across J1 (North) ➔ J2 (Market) ➔ J4 (Hospital) ➔ J3 (College) ➔ J1 (North).")
    
        # Active Coordinated Recommendation Banner
        rec_name = coop_data["recommended_name"]
        rec_idx = coop_data["recommended_idx"]
        rec_state = coop_data["states"][rec_idx]
    
        html(f"""
        <div style="background: linear-gradient(135deg, rgba(30, 27, 75, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%); border: 1.5px solid rgba(168, 85, 247, 0.6); border-radius: 16px; padding: 1.1rem 1.4rem; margin-bottom: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="font-size: 0.75rem; font-weight: 800; color: #4F46E5; text-transform: uppercase;">⚡ ACTIVE COOPERATIVE RECOMMENDATION</span>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF; font-family: Outfit;">{rec_name} — Allocated {rec_state.recommended_green_seconds}s Green Phase</div>
                    <div style="font-size: 0.85rem; color: #F1F5F9; margin-top: 3px;">{rec_state.reasoning}</div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.8rem; color: #E2E8F0;">Cooperative Score:</span>
                    <div style="font-size: 2rem; font-weight: 800; color: #4F46E5; font-family: Outfit;">{rec_state.cooperative_score:.1f}</div>
                </div>
            </div>
        </div>
        """)
    
        # 4 Cooperative State Cards
        c_cols = st.columns(4)
        for i, state in enumerate(coop_data["states"]):
            style = JUNCTION_STYLES[i]
            with c_cols[i]:
                occ_color = "#10B981" if state.downstream_occupancy_pct < 60 else ("#F59E0B" if state.downstream_occupancy_pct < 80 else "#EF4444")
                html(f"""
                <div class="junction-card {style['theme']}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                        <span style="font-size: 0.82rem; font-weight: 800; color: {style['badge']}; text-transform: uppercase;">{style['tag']}</span>
                        <span style="font-size: 0.72rem; font-weight: 700; background: #EEF2FF; color: #4F46E5; padding: 2px 7px; border-radius: 999px;">➔ {state.downstream_name.split(' - ')[0]}</span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.4rem; font-family: Outfit;">{state.name}</div>
                    <div style="font-size: 0.78rem; color: #E2E8F0; display: flex; justify-content: space-between;">
                        <span>Downstream Occupancy</span>
                        <b style="color: {occ_color};">{state.downstream_occupancy_pct}%</b>
                    </div>
                    <div class="bar-track" style="margin: 4px 0 8px 0;">
                        <div class="bar-fill" style="width: {state.downstream_occupancy_pct}%; background: {occ_color};"></div>
                    </div>
                    <div class="junction-stat-grid">
                        <div class="junction-stat-item">🛑 Red Cycles: <b>{state.consecutive_red_cycles}</b></div>
                        <div class="junction-stat-item">⚖️ Fairness Boost: <b>+{state.starvation_boost}</b></div>
                        <div class="junction-stat-item">🎯 Coop Score: <b>{state.cooperative_score}</b></div>
                        <div class="junction-stat-item">⏱️ Rec. Green: <b>{state.recommended_green_seconds}s</b></div>
                    </div>
                    <div style="font-size: 0.73rem; color: #F1F5F9; margin-top: 8px; line-height: 1.3;">
                        <i>{state.reasoning}</i>
                    </div>
                </div>
                """)

        st.markdown("<br>", unsafe_allow_html=True)
    
        # Inter-Junction DSRC / C-V2X Message Bus
        st.markdown("#### 📡 Inter-Junction DSRC / C-V2X Wireless Message Bus (Live Mesh Trace)")
        st.caption("Broadcast channel exchanging backpressure warnings, platoon clearance tokens, and green wave reservations.")
    
        msg_html_items = []
        if coop_data["messages"]:
            for msg in reversed(coop_data["messages"][-8:]):
                b_color = "#38BDF8" if msg.msg_type == "GREEN_WAVE_TOKEN" else ("#F59E0B" if msg.msg_type == "BACKPRESSURE_WARN" else "#4ADE80")
                msg_html_items.append(
                    f'<div style="font-family: monospace; font-size: 0.84rem; padding: 6px 0; border-bottom: 1px solid #1E293B;">'
                    f'<span style="color: #E2E8F0;">[{msg.timestamp}]</span> '
                    f'<span style="color: {b_color}; font-weight: 700;">[{msg.msg_type}]</span> '
                    f'<span style="color: #A78BFA;">{msg.sender_name.split(" - ")[0]} ➔ {msg.receiver_name.split(" - ")[0]}:</span> '
                    f'<span style="color: #E2E8F0;">{msg.content}</span>'
                    f'</div>'
                )
        else:
            msg_html_items.append('<div style="font-family: monospace; font-size: 0.84rem; color: #94A3B8;">[00:00:00] [SYSTEM-INIT] DSRC inter-junction mesh operational on 5.9 GHz ITS band. All 4 nodes connected.</div>')

        html(f"""
        <div style="background: #0F172A; border-radius: 14px; padding: 1.1rem; border: 1.5px solid #334155; box-shadow: inset 0 2px 8px rgba(0,0,0,0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 10px;">
                <span style="font-weight: 700; font-size: 0.85rem; color: #38BDF8;">📻 IEEE 802.11p WAVE Wireless Transceiver • Packet Loss: 0.0%</span>
                <span style="font-size: 0.75rem; color: #4ADE80; font-weight: 700;">● MESH SYNCHRONIZED</span>
            </div>
            {"".join(msg_html_items)}
        </div>
        """)



# -----------------------------------------------------------------------------
# CATEGORY 3: EMERGENCY & IOT SENSORS
# -----------------------------------------------------------------------------
with cat_emergency:
    tab_emer, tab_iot = st.tabs(
        [
            "🚑 Priority Emergency Green Corridor",
            "📡 IoT Sensor Digital Twin & Incident Lab"
        ]
    )
    with tab_emer:
        st.markdown("### 🚑 Emergency Green Corridor Dispatch & Interlock Control")
        st.caption("Verifiable emergency priority preemption across arterial route **J4 (Hospital Road)** ➔ **J3 (College Circle)** ➔ **J1 (North Gate)**.")
    
        emer_mgr = st.session_state.emergency_mgr
        emer_st = emer_mgr.state
    
        # Dispatch & Safe Cancellation Controls
        col_em_ctrl1, col_em_ctrl2, col_em_ctrl3, col_em_ctrl4 = st.columns([1.2, 1.2, 1.2, 1.2])
        with col_em_ctrl1:
            v_id_input = st.selectbox("Emergency Vehicle Unit", ["AMB-911-DELTA", "MEDIC-RESCUE-04", "FIRE-ENGINE-12"], index=0)
        with col_em_ctrl2:
            v_prio_input = st.selectbox("Priority Preemption Class", ["LEVEL-1 CRITICAL (Ambulance)", "LEVEL-2 ESCORT (Fire Unit)"], index=0)
        with col_em_ctrl3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🚨 Dispatch Priority Vehicle", type="primary", use_container_width=True):
                emer_mgr.dispatch(vehicle_id=v_id_input, priority_level=v_prio_input)
                network.emergency_active = True
                network.emergency_started = True
                network.emergency_route = deque([3, 2, 0])
                st.success(f"Dispatched {v_id_input}! Corridor J4 ➔ J3 ➔ J1 locked.")
                st.rerun()
        with col_em_ctrl4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🛑 Safe Abort / Cancel Preemption", use_container_width=True):
                emer_mgr.cancel(reason="Operator Abort")
                network.emergency_active = False
                network.emergency_route = deque()
                st.warning("Corridor preemption aborted safely; standard cyclic control restored.")
                st.rerun()

        # Corridor Status HUD
        status_color_map = {
            "IDLE": ("#F1F5F9", "#64748B", "⚪ STANDBY IDLE"),
            "PRIORITY_REQUESTED": ("#FEF3C7", "#D97706", "🟡 PRIORITY REQUESTED"),
            "PREPARATION_IN_PROGRESS": ("#FEF3C7", "#B45309", "🟠 PREPARATION IN PROGRESS (CLEARING)"),
            "PRIORITY_GRANTED": ("#DCFCE7", "#059669", "🟢 PRIORITY GRANTED (GREEN WAVE)"),
            "CORRIDOR_CLEARED": ("#E0F2FE", "#0284C7", "🏁 CORRIDOR CLEARED & COMPLETED"),
            "CANCELLED": ("#FEE2E2", "#DC2626", "🛑 PREEMPTION CANCELLED")
        }
        bg_c, txt_c, pill_txt = status_color_map.get(emer_st.status, ("#F1F5F9", "#64748B", emer_st.status))
    
        html(f"""
        <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 16px; padding: 1.2rem 1.4rem; margin: 1rem 0; box-shadow: 0 4px 14px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="font-weight: 800; font-size: 1.25rem; color: #FFFFFF; font-family: Outfit;">🚑 Vehicle: {emer_st.vehicle_id}</span>
                    <span style="font-size: 0.82rem; color: #E2E8F0; margin-left: 8px;">{emer_st.vehicle_type}</span>
                </div>
                <span style="background: {bg_c}; color: {txt_c}; font-size: 0.82rem; font-weight: 800; padding: 4px 14px; border-radius: 999px;">
                    {pill_txt}
                </span>
            </div>
        
            <div style="margin: 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #F1F5F9; margin-bottom: 4px;">
                    <span>Corridor Route Progress: <b>J4 ➔ J3 ➔ J1</b></span>
                    <span>{emer_st.progress_pct:.0f}% Completed</span>
                </div>
                <div class="bar-track" style="height: 12px; margin: 0;">
                    <div class="bar-fill" style="width: {emer_st.progress_pct}%; background: linear-gradient(90deg, #EF4444, #10B981);"></div>
                </div>
            </div>
        
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 1rem;">
                <div class="junction-stat-item">📍 Active Junction: <br><b>{emer_st.active_clearing_junction or 'None'}</b></div>
                <div class="junction-stat-item">🏁 Destination: <br><b>{emer_st.destination.split(' - ')[0]}</b></div>
                <div class="junction-stat-item">🏎️ Transit Speed: <br><b>{emer_st.speed_kmh} km/h</b></div>
                <div class="junction-stat-item">⏱️ Estimated Arrival: <br><b>{emer_st.eta_seconds:.1f}s</b></div>
            </div>
        </div>
        """)
    
        # Fail-Safe Interlock Verification Matrix
        st.markdown("#### 🛡️ NEMA TS2 / NTCIP 1202 Fail-Safe Interlock Checklist")
        c_safe1, c_safe2, c_safe3, c_safe4 = st.columns(4)
        with c_safe1:
            html("""
            <div style="background: rgba(6, 78, 59, 0.85); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 12px; padding: 12px;">
                <div style="font-weight: 800; color: #059669; font-size: 0.85rem;">🔒 Conflicting Phase Lock</div>
                <div style="font-size: 0.78rem; color: #A7F3D0; margin-top: 4px;">Simultaneous green on conflicting cross-streets is hardware-inhibited by MMU (Malfunction Management Unit).</div>
            </div>
            """)
        with c_safe2:
            html("""
            <div style="background: rgba(6, 78, 59, 0.85); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 12px; padding: 12px;">
                <div style="font-weight: 800; color: #059669; font-size: 0.85rem;">⏱️ 3.5s Yellow Clearance</div>
                <div style="font-size: 0.78rem; color: #A7F3D0; margin-top: 4px;">Active cross-street approaches receive mandatory 3.5s yellow deceleration interval before preemption green grant.</div>
            </div>
            """)
        with c_safe3:
            html("""
            <div style="background: rgba(6, 78, 59, 0.85); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 12px; padding: 12px;">
                <div style="font-weight: 800; color: #059669; font-size: 0.85rem;">🛑 1.5s All-Red Buffer</div>
                <div style="font-size: 0.78rem; color: #A7F3D0; margin-top: 4px;">Full intersection all-red safety buffer empties remaining cross-traffic before corridor gates open.</div>
            </div>
            """)
        with c_safe4:
            html("""
            <div style="background: rgba(6, 78, 59, 0.85); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 12px; padding: 12px;">
                <div style="font-weight: 800; color: #059669; font-size: 0.85rem;">🚶 Pedestrian Safety Buffer</div>
                <div style="font-size: 0.78rem; color: #A7F3D0; margin-top: 4px;">Pedestrian don't-walk flash timers are respected to prevent pedestrian trapping in crosswalks.</div>
            </div>
            """)

        # Corridor Event Logs
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📋 Emergency Preemption Audit Log")
        em_logs = []
        if emer_mgr.logs:
            for l in reversed(emer_mgr.logs[-10:]):
                c_badge = "#10B981" if l.severity == "SUCCESS" else ("#F59E0B" if l.severity == "WARNING" else ("#EF4444" if l.severity == "CRITICAL" else "#38BDF8"))
                em_logs.append(f'<div style="font-family: monospace; font-size: 0.84rem; padding: 5px 0; border-bottom: 1px solid #1E293B;"><span style="color:#64748B;">[{l.timestamp}]</span> <span style="color:{c_badge}; font-weight:700;">[{l.phase}]</span> <span style="color:#E2E8F0;">{l.message}</span></div>')
        else:
            em_logs.append('<div style="font-family: monospace; font-size: 0.84rem; color: #94A3B8;">[00:00:00] [IDLE] No emergency transponder active. DSRC receiver scanning Sector 4 corridor.</div>')
        
        html(f"""
        <div style="background: #0F172A; border-radius: 14px; padding: 1.1rem; border: 1.5px solid #334155;">
            {"".join(em_logs)}
        </div>
        """)


    with tab_iot:
        st.markdown("### 📡 IoT Sensor Digital Twin & Anomaly Incident Recovery")
        st.caption("Real-time digital twin monitoring 16 virtual roadside IoT devices, sensor fault injection, and automated anomaly recovery.")
    
        sensor_tw = st.session_state.sensor_twin
        inc_mgr = st.session_state.incident_mgr
    
        # 4 Junction Sensor Fleet
        st.markdown("#### 🎛️ Roadside IoT Sensor Fleet (Edge Telemetry)")
        iot_cols = st.columns(4)
        for j_i, j_style in enumerate(JUNCTION_STYLES):
            prefix = f"J{j_i+1}"
            with iot_cols[j_i]:
                html(f"""
                <div class="junction-card {j_style['theme']}">
                    <div style="font-size: 0.85rem; font-weight: 800; color: {j_style['badge']}; text-transform: uppercase; margin-bottom: 8px;">
                        {j_style['tag']} Edge Sensors
                    </div>
                """)
                for s_key in [f"{prefix}-LOOP-01", f"{prefix}-RADAR-02", f"{prefix}-SIGNAL-03", f"{prefix}-ACOUSTIC-04"]:
                    sensor = sensor_tw.sensors[s_key]
                    h_badge = "#10B981" if sensor.health_status == "HEALTHY" else ("#F59E0B" if sensor.health_status == "NOISY" else "#EF4444")
                    disp_val = str(sensor.raw_reading) if sensor.raw_reading is not None else "⚠️ UNAVAIL (N/A)"
                    html(f"""
                    <div style="background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 8px; padding: 6px 8px; margin-bottom: 6px; font-size: 0.76rem;">
                        <div style="display: flex; justify-content: space-between; font-weight: 700; color: #FFFFFF;">
                            <span>{sensor.sensor_type.replace('_', ' ')}</span>
                            <span style="color: {h_badge};">● {sensor.health_status}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #E2E8F0; margin-top: 2px;">
                            <span>Reading: <b>{disp_val}</b></span>
                            <span style="font-size: 0.68rem;">{sensor.protocol}</span>
                        </div>
                    </div>
                    """)
                html("</div>")

        # Fault Injection & Calibration Panel
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🧪 Edge Sensor Fault Injection Console")
        col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.2, 1.2, 1.2])
        with col_f1:
            target_s_id = st.selectbox("Select Roadside Sensor", list(sensor_tw.sensors.keys()), index=0)
        with col_f2:
            fault_type_sel = st.selectbox("Fault Mode to Inject", ["DISCONNECTED", "STALE", "NOISY", "HEALTHY"], index=0)
        with col_f3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("⚠️ Inject Sensor Fault", use_container_width=True):
                sensor_tw.set_fault(target_s_id, fault_type_sel)
                st.warning(f"Fault injected into {target_s_id}: {fault_type_sel}")
                st.rerun()
        with col_f4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Recalibrate & Recover All Sensors", type="primary", use_container_width=True):
                sensor_tw.recover_all()
                st.success("All 16 edge sensors restored to HEALTHY state.")
                st.rerun()

        # Incident Detection & Management Feed
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🚨 Active Incident Detection & Resolution Feed")
        st.caption("Continuous anomaly scanning identifies excessive queue spikes, road blockages, and sensor dropouts.")
    
        if active_incidents:
            for inc in active_incidents:
                sev_color = "#DC2626" if inc.severity == "CRITICAL" else ("#D97706" if inc.severity == "WARNING" else "#0284C7")
                sev_bg = "#FEE2E2" if inc.severity == "CRITICAL" else ("#FEF3C7" if inc.severity == "WARNING" else "#E0F2FE")
                st_color = "#059669" if inc.status == "RESOLVED" else ("#D97706" if inc.status in ("ACKNOWLEDGED", "RECOVERING") else "#DC2626")
            
                c_inc1, c_inc2 = st.columns([3, 1])
                with c_inc1:
                    html(f"""
                    <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid rgba(56, 189, 248, 0.35); border-left: 5px solid {sev_color}; border-radius: 12px; padding: 10px 14px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 800; color: #FFFFFF; font-size: 0.88rem;">[{inc.incident_id}] {inc.incident_type.replace('_', ' ')} — {inc.junction_name}</span>
                            <div style="display: flex; gap: 6px;">
                                <span style="background: {sev_bg}; color: {sev_color}; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 999px;">{inc.severity}</span>
                                <span style="background: #F1F5F9; color: {st_color}; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 999px;">● {inc.status}</span>
                            </div>
                        </div>
                        <div style="font-size: 0.8rem; color: #F1F5F9;"><b>Evidence:</b> {inc.evidence}</div>
                        <div style="font-size: 0.8rem; color: #0284C7; margin-top: 2px;"><b>Corrective Action:</b> {inc.recommended_action}</div>
                    </div>
                    """)
                with c_inc2:
                    if inc.status == "DETECTED":
                        if st.button(f"Acknowledge", key=f"ack_{inc.incident_id}", use_container_width=True):
                            inc_mgr.acknowledge(inc.incident_id)
                            st.rerun()
                    elif inc.status == "ACKNOWLEDGED":
                        if st.button(f"Initiate Recovery", key=f"rec_{inc.incident_id}", use_container_width=True):
                            inc_mgr.initiate_recovery(inc.incident_id)
                            st.rerun()
                    elif inc.status == "RECOVERING":
                        if st.button(f"Mark Resolved", key=f"clr_{inc.incident_id}", use_container_width=True):
                            inc_mgr.clear_incident(inc.incident_id, sim_time_sec)
                            st.rerun()
        else:
            st.info("🟢 No active anomalies detected. All 4 intersections operating within standard safety thresholds.")

        # Manual Incident Injection tool
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🔨 Manual Incident Injection (Resilience Testing)")
        col_inj1, col_inj2, col_inj3 = st.columns([1.5, 1.2, 1.2])
        with col_inj1:
            inj_type = st.selectbox("Anomaly Scenario to Inject", ["ROAD_BLOCKAGE", "DOWNSTREAM_GRIDLOCK", "EMERGENCY_OBSTRUCTED"], index=0)
        with col_inj2:
            inj_j = st.selectbox("Target Junction", [0, 1, 2, 3], format_func=lambda i: JUNCTION_STYLES[i]["road"])
        with col_inj3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("💥 Inject Anomaly Event", use_container_width=True):
                inc_mgr.inject_incident(inj_type, inj_j, sim_time_sec)
                st.warning(f"Injected {inj_type} at {JUNCTION_STYLES[inj_j]['road']}.")
                st.rerun()



# -----------------------------------------------------------------------------
# CATEGORY 4: EXPLAINABLE AI (XAI)
# -----------------------------------------------------------------------------
with cat_xai:
    tab_xai = st.container()
    with tab_xai:
        st.markdown("### 🧠 Explainable AI (XAI) — Transparent Signal Decision Attribution")
        st.caption("Verifiable, natural-language explanation of why the controller selected or rejected signal phases, factor contributions, and safety bounds.")
    
        # Active Decision Banner
        active_exp = next((exp for exp in explanations if exp.is_active_green), explanations[0])
        html(f"""
        <div style="background: linear-gradient(135deg, rgba(6, 78, 59, 0.92) 0%, rgba(15, 23, 42, 0.94) 100%); border: 1.5px solid rgba(52, 211, 153, 0.6); border-radius: 16px; padding: 1.2rem 1.4rem; margin-bottom: 1.25rem;">
            <div style="font-size: 0.75rem; font-weight: 800; color: #059669; text-transform: uppercase;">🎯 ACTIVE ACTUATION EXPLANATION (EXECUTED)</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #34D399; font-family: Outfit; margin: 3px 0;">{active_exp.junction_name} — Ranked #1 (Urgency Score: {active_exp.decision_score})</div>
            <div style="font-size: 0.9rem; color: #A7F3D0; margin-top: 4px; line-height: 1.4;">{active_exp.narrative_explanation}</div>
        </div>
        """)
    
        # 4 Detailed Junction Explanations
        xai_cols = st.columns(4)
        for i, exp in enumerate(explanations):
            style = JUNCTION_STYLES[i]
            with xai_cols[i]:
                sig_badge = '<span style="background: #DCFCE7; color: #059669; font-weight: 800; font-size: 0.72rem; padding: 2px 8px; border-radius: 999px;">● GREEN (DISCHARGE)</span>' if exp.is_active_green else '<span style="background: #FEE2E2; color: #DC2626; font-weight: 800; font-size: 0.72rem; padding: 2px 8px; border-radius: 999px;">● RED (HOLDING)</span>'
                html(f"""
                <div class="junction-card {style['theme']}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                        <span style="font-size: 0.82rem; font-weight: 800; color: {style['badge']}; text-transform: uppercase;">{style['tag']}</span>
                        {sig_badge}
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.4rem; font-family: Outfit;">{exp.junction_name}</div>
                    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.6rem;">
                        <span style="font-size: 0.82rem; color: #E2E8F0;">Priority Rank: <b>#{exp.decision_rank} of 4</b></span>
                        <span style="font-size: 1.25rem; font-weight: 800; color: {style['badge']}; font-family: Outfit;">{exp.decision_score}</span>
                    </div>
                    <div style="font-size: 0.78rem; color: #F8FAFC; background: rgba(255,255,255,0.85); padding: 8px; border-radius: 10px; border: 1px solid rgba(56, 189, 248, 0.35); margin-bottom: 8px; line-height: 1.35;">
                        <b>Narrative Rationale:</b><br>{exp.narrative_explanation}
                    </div>
                    <div style="font-size: 0.75rem; color: #F1F5F9; margin-bottom: 6px;">
                        <b>Primary Factors:</b>
                        <ul style="margin: 4px 0 0 16px; padding: 0;">
                            {"".join(f"<li>{f}</li>" for f in exp.primary_influencing_factors[:3])}
                        </ul>
                    </div>
                    <div style="font-size: 0.74rem; color: #E2E8F0; margin-top: 6px;">
                        <b>Alternative Comparison:</b><br><i>{exp.why_alternatives_not_chosen}</i>
                    </div>
                    <div style="font-size: 0.72rem; color: #0284C7; margin-top: 6px;">
                        ⏱️ Reassessment Window: <b>{exp.next_reassessment_time}</b>
                    </div>
                </div>
                """)



# -----------------------------------------------------------------------------
# CATEGORY 5: SCENARIO LAB & BENCHMARKS
# -----------------------------------------------------------------------------
with cat_benchmarks:
    tab_scenarios, tab_compare = st.tabs(
        [
            "🧪 Scenario Lab (7 Stress Test Profiles)",
            "📊 Live Baseline Benchmark: FlowSync AI vs Fixed"
        ]
    )
    with tab_scenarios:
        st.markdown("### 🧪 Scenario Lab & Reproducible Scientific Benchmark Replay")
        st.caption("Rigorous comparative evaluation of FlowSync Adaptive AI versus Fixed-Time Cyclic control across 7 municipal smart-city scenarios.")
    
        scen_lab = st.session_state.scenario_lab
    
        # Scenario Configuration
        col_sc1, col_sc2 = st.columns([1.5, 1])
        with col_sc1:
            chosen_scen = st.selectbox("Select Scenario Profile", list(SCENARIO_PROFILES.keys()), index=0)
            scen_info = SCENARIO_PROFILES[chosen_scen]
            st.markdown(f"**Scenario Blueprint:** {scen_info['description']} *(Demand: {scen_info['demand']}x, Horizon: {scen_info['steps']} steps)*")
        with col_sc2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("▶ Run Reproducible Benchmark Simulation", type="primary", use_container_width=True):
                with st.spinner("Running synchronized simulation trials across both controllers..."):
                    res = scen_lab.run_benchmark(chosen_scen)
                    st.session_state.scenario_result = res
                st.success(f"Benchmark completed for '{chosen_scen}'!")
                st.rerun()

        # Display Benchmark Results
        bench_res = st.session_state.scenario_result
        if bench_res:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"#### 📊 Empirical Findings: {bench_res.scenario_name}")
        
            # 4 KPI Cards
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
            with col_kpi1:
                html(f"""
                <div class="junction-card j-theme-green" style="text-align: center; padding: 1.1rem;">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #059669; text-transform: uppercase;">Adaptive Avg. Wait</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #34D399; font-family: Outfit; margin: 4px 0;">{bench_res.adaptive_avg_wait:.1f}s</div>
                    <div style="font-size: 0.74rem; color: #6EE7B7;">Max Queue: {bench_res.adaptive_max_queue} veh</div>
                </div>
                """)
            with col_kpi2:
                html(f"""
                <div class="junction-card j-theme-orange" style="text-align: center; padding: 1.1rem;">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #EA580C; text-transform: uppercase;">Fixed Cyclic Avg. Wait</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #FB923C; font-family: Outfit; margin: 4px 0;">{bench_res.fixed_avg_wait:.1f}s</div>
                    <div style="font-size: 0.74rem; color: #FDBA74;">Max Queue: {bench_res.fixed_max_queue} veh</div>
                </div>
                """)
            with col_kpi3:
                imp_c = "#059669" if bench_res.delay_reduction_pct >= 0 else "#DC2626"
                html(f"""
                <div class="junction-card j-theme-violet" style="text-align: center; padding: 1.1rem;">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #7C3AED; text-transform: uppercase;">Delay Reduction</div>
                    <div style="font-size: 2rem; font-weight: 800; color: {imp_c}; font-family: Outfit; margin: 4px 0;">{bench_res.delay_reduction_pct:+.1f}%</div>
                    <div style="font-size: 0.74rem; color: #C084FC;">AI Travel Time Saved</div>
                </div>
                """)
            with col_kpi4:
                html(f"""
                <div class="junction-card j-theme-blue" style="text-align: center; padding: 1.1rem;">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #0284C7; text-transform: uppercase;">Throughput Served</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #38BDF8; font-family: Outfit; margin: 4px 0;">{bench_res.adaptive_vehicles_served}</div>
                    <div style="font-size: 0.74rem; color: #0284C7;">Fixed: {bench_res.fixed_vehicles_served} ({bench_res.throughput_gain_pct:+.1f}%)</div>
                </div>
                """)

            # Side-by-side Visualizations
            col_ch1, col_ch2 = st.columns([1.1, 0.9])
            with col_ch1:
                st.markdown("##### ⏱️ Delay Dynamics Over Duration")
                df_tl = pd.DataFrame(bench_res.timeline_records)
                fig_tl = go.Figure()
                fig_tl.add_trace(go.Scatter(
                    x=df_tl["time_seconds"], y=df_tl["adaptive_wait"],
                    mode="lines+markers", name="FlowSync Adaptive AI",
                    line=dict(color="#10B981", width=3, shape="spline"),
                    marker=dict(size=4)
                ))
                fig_tl.add_trace(go.Scatter(
                    x=df_tl["time_seconds"], y=df_tl["fixed_wait"],
                    mode="lines", name="Fixed-Time Baseline",
                    line=dict(color="#F97316", width=2.5, dash="dash", shape="spline")
                ))
                fig_tl.update_layout(
                    height=320,
                    xaxis_title="Simulation Elapsed (seconds)",
                    yaxis_title="Average Delay (s)",
                    plot_bgcolor="rgba(15, 23, 42, 0.85)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=15, r=15, t=30, b=15),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_tl, use_container_width=True)

            with col_ch2:
                st.markdown("##### 🚗 Queue Mass Convergence")
                fig_q = go.Figure()
                fig_q.add_trace(go.Scatter(
                    x=df_tl["time_seconds"], y=df_tl["adaptive_queue"],
                    mode="lines", name="Adaptive Queue Mass",
                    line=dict(color="#6366F1", width=2.5)
                ))
                fig_q.add_trace(go.Scatter(
                    x=df_tl["time_seconds"], y=df_tl["fixed_queue"],
                    mode="lines", name="Fixed Queue Mass",
                    line=dict(color="#EA580C", width=2, dash="dot")
                ))
                fig_q.update_layout(
                    height=320,
                    xaxis_title="Time (seconds)",
                    yaxis_title="Queued Vehicles",
                    plot_bgcolor="rgba(15, 23, 42, 0.85)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=15, r=15, t=30, b=15),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_q, use_container_width=True)

            # CSV Data Export
            csv_data = scen_lab.export_csv(bench_res)
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1:
                st.markdown("<b>💾 Export Scientific Telemetry Dataset</b><br><span style='font-size:0.82rem; color:#64748B;'>Download step-level delay convergence, throughput counts, and queues for external R/Python verification.</span>", unsafe_allow_html=True)
            with col_d2:
                st.download_button(
                    label="📥 Download Telemetry (.CSV)",
                    data=csv_data,
                    file_name=f"flowsync_benchmark_{bench_res.scenario_name.split('.')[0].strip()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("👆 Click **'Run Reproducible Benchmark Simulation'** to generate side-by-side empirical trials.")


    with tab_compare:
        st.markdown("### 📊 Performance Benchmark: AI Adaptive vs. Fixed Cyclic Baseline")
        st.caption("Side-by-side evaluation over identical simulated stochastic traffic streams.")
    
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            html(f"""
            <div class="junction-card j-theme-green" style="text-align: center; padding: 1.2rem;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #059669; text-transform: uppercase;">Adaptive Controller Avg. Wait</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #34D399; font-family: 'Outfit'; margin: 0.3rem 0;">{summary['adaptive_avg_wait']:.1f}s</div>
                <div style="font-size: 0.8rem; color: #6EE7B7;">Dynamic green waves & backpressure clearing</div>
            </div>
            """)
        with col_kpi2:
            html(f"""
            <div class="junction-card j-theme-orange" style="text-align: center; padding: 1.2rem;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #EA580C; text-transform: uppercase;">Fixed Cyclic Avg. Wait</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #FB923C; font-family: 'Outfit'; margin: 0.3rem 0;">{summary['fixed_avg_wait']:.1f}s</div>
                <div style="font-size: 0.8rem; color: #FDBA74;">Static round-robin 20s timers</div>
            </div>
            """)
        with col_kpi3:
            imp_color = "#059669" if summary["wait_improvement_pct"] >= 0 else "#DC2626"
            imp_bg = "j-theme-violet" if summary["wait_improvement_pct"] >= 0 else "j-theme-orange"
            html(f"""
            <div class="junction-card {imp_bg}" style="text-align: center; padding: 1.2rem;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #7C3AED; text-transform: uppercase;">Efficiency Differential</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: {imp_color}; font-family: 'Outfit'; margin: 0.3rem 0;">{summary['wait_improvement_pct']:+.1f}%</div>
                <div style="font-size: 0.8rem; color: #F1F5F9;">Positive = AI saves commuters waiting time</div>
            </div>
            """)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
        # Vibrant Comparison Bar Chart
        comp_df = pd.DataFrame([
            {"Controller": "FlowSync AI (Adaptive)", "Average Wait (s)": summary["adaptive_avg_wait"], "Color": "#10B981"},
            {"Controller": "Fixed-Time Baseline", "Average Wait (s)": summary["fixed_avg_wait"], "Color": "#F97316"}
        ])
    
        fig_bar = px.bar(
            comp_df,
            x="Controller",
            y="Average Wait (s)",
            color="Controller",
            color_discrete_map={
                "FlowSync AI (Adaptive)": "#10B981",
                "Fixed-Time Baseline": "#F97316"
            },
            text="Average Wait (s)",
            title="Average Vehicle Delay Comparison (Seconds)"
        )
        fig_bar.update_traces(
            texttemplate='%{text:.1f}s',
            textposition='outside',
            marker_line_width=1.5,
            marker_line_color="#CBD5E1"
        )
        fig_bar.update_layout(
            height=320,
            plot_bgcolor="rgba(15, 23, 42, 0.85)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=50, b=15),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
        # Simulation Timeline Multi-Color Line Graph
        if st.session_state.history:
            st.markdown("### 📈 Real-Time Delay Convergence Timeline")
            hist_df = pd.DataFrame(st.session_state.history)
        
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=hist_df["time_seconds"],
                y=hist_df["adaptive_wait"],
                mode="lines+markers",
                name="FlowSync AI (Adaptive)",
                line=dict(color="#10B981", width=3, shape="spline"),
                marker=dict(size=4)
            ))
            fig_line.add_trace(go.Scatter(
                x=hist_df["time_seconds"],
                y=hist_df["fixed_wait"],
                mode="lines",
                name="Fixed-Time Baseline",
                line=dict(color="#F97316", width=2.5, dash="dash", shape="spline")
            ))
            fig_line.update_layout(
                height=340,
                title="Waiting Time Dynamics Over Duration",
                xaxis_title="Simulation Time Elapsed (seconds)",
                yaxis_title="Average Waiting Time (seconds)",
                plot_bgcolor="rgba(15, 23, 42, 0.85)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=15, r=15, t=45, b=15),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
            # CSV Data Export for Evaluation
            csv_data = hist_df.to_csv(index=False).encode('utf-8')
            col_dl1, col_dl2 = st.columns([2, 1])
            with col_dl1:
                st.markdown("<b>💾 Export Empirical Run Data</b><br><span style='font-size:0.85rem; color:#64748B;'>Download step-level queue measurements, delays, and downstream backpressure metrics for offline analysis.</span>", unsafe_allow_html=True)
            with col_dl2:
                st.download_button(
                    label="📥 Download Telemetry Dataset (.CSV)",
                    data=csv_data,
                    file_name=f"flowsync_telemetry_t{network.time_step}.csv",
                    mime="text/csv",
                    use_container_width=True
                )



# -----------------------------------------------------------------------------
# CATEGORY 6: DEMO VIDEO & SPECIFICATIONS
# -----------------------------------------------------------------------------
with cat_demo:
    tab_demo, tab_about = st.tabs(
        [
            "🎬 Simulation & Audio-Visual Demo Video",
            "🛠️ System Architecture & Specifications"
        ]
    )
    with tab_demo:
        st.markdown("### 🎬 FlowSync Autonomous Simulation & Edge Preemption Demo Video")
        st.caption("Comprehensive demonstration showing multi-junction grid micro-simulation, dual acoustic & computer vision sensor detection, dynamic red-to-green light switching, and low-latency inter-junction wireless message passing.")
    
        # Resolve video path
        video_dir = Path(__file__).parent / "assets"
        video_path = video_dir / "flowsync_simulation_demo.mp4"
        if not video_path.exists():
            alt_path = Path(__file__).parent.parent / "assets" / "flowsync_simulation_demo.mp4"
            if alt_path.exists():
                video_path = alt_path
            else:
                try:
                    import generate_demo_video
                    with st.spinner("Generating high-definition demo simulation video (1280x720 24FPS)..."):
                        generate_demo_video.generate_video(str(video_path), duration_sec=18.0, fps=24)
                except Exception as e:
                    st.error(f"Could not auto-generate demo video: {e}")

        # Top Feature Highlights
        html("""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.85rem; margin-bottom: 1.25rem;">
            <div class="junction-card j-theme-violet" style="padding: 0.9rem 1.1rem; margin-bottom: 0;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #7C3AED; text-transform: uppercase;">1. City Simulation</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; margin: 3px 0; font-family: Outfit;">4-Node Arterial Loop</div>
                <div style="font-size: 0.76rem; color: #E2E8F0;">J1 North ➔ J2 Market ➔ J4 Hospital ➔ J3 College Circle with stochastic queues.</div>
            </div>
            <div class="junction-card j-theme-orange" style="padding: 0.9rem 1.1rem; margin-bottom: 0;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #EA580C; text-transform: uppercase;">2. Dual Edge Sensors</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; margin: 3px 0; font-family: Outfit;">Sound & Vision Fusion</div>
                <div style="font-size: 0.76rem; color: #E2E8F0;">Acoustic siren array (>94 dB match) + YOLOv8 vision picture vehicle bounding box.</div>
            </div>
            <div class="junction-card j-theme-green" style="padding: 0.9rem 1.1rem; margin-bottom: 0;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #059669; text-transform: uppercase;">3. Signal Actuation</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; margin: 3px 0; font-family: Outfit;">Red ➔ Green Priority</div>
                <div style="font-size: 0.76rem; color: #E2E8F0;">Safely clears conflicting approaches (Yellow/All-Red) and grants priority green.</div>
            </div>
            <div class="junction-card j-theme-blue" style="padding: 0.9rem 1.1rem; margin-bottom: 0;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #0284C7; text-transform: uppercase;">4. Inter-Junction V2X</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; margin: 3px 0; font-family: Outfit;">DSRC Packet Passing</div>
                <div style="font-size: 0.76rem; color: #E2E8F0;">J1 broadcasts message packet to J2 ahead of time to synchronize a continuous green wave.</div>
            </div>
        </div>
        """)

        # Main Demo Section: Video Player & Interactive Stage Inspector
        col_video, col_interactive = st.columns([1.15, 0.85])

        with col_video:
            st.markdown("#### 📺 High-Definition Video Player (1280x720 • 24 FPS)")
            st.caption("Standard HTML5 MP4 stream generated with hardware-accelerated telemetry rendering.")
        
            if video_path.exists():
                video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                with open(video_path, "rb") as vf:
                    vid_bytes = vf.read()
                st.video(str(video_path), format="video/mp4")
            
                c_btn1, c_btn2 = st.columns([1.2, 1])
                with c_btn1:
                    st.download_button(
                        label=f"📥 Download Video (.MP4, {video_size_mb:.1f} MB)",
                        data=vid_bytes,
                        file_name="flowsync_simulation_demo.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                with c_btn2:
                    if st.button("🔄 Re-generate Video File", use_container_width=True):
                        try:
                            import generate_demo_video
                            with st.spinner("Re-rendering demo video in H.264..."):
                                generate_demo_video.generate_video(str(video_path), duration_sec=18.0, fps=24)
                            st.success("Video re-rendered successfully!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Re-generation failed: {ex}")
            else:
                st.warning("Video file is generating. Please refresh in a moment.")

        with col_interactive:
            st.markdown("#### 🕹️ Interactive Scenario Stage Inspector")
            st.caption("Scrub through the 5 simulation phases to inspect real-time sensor waveforms, camera picture detection HUD, signal relays, and transmitted DSRC message packets.")
        
            stages = [
                "1️⃣ Stage 1: Congestion & Red Light Hold",
                "2️⃣ Stage 2: Dual Sensor Detection (Sound & Picture)",
                "3️⃣ Stage 3: Dynamic Red ➔ Green Signal Preemption",
                "4️⃣ Stage 4: J1 ➔ J2 Inter-Junction Message Passing",
                "5️⃣ Stage 5: Downstream Green Wave Reception & Transit"
            ]
        
            selected_stage = st.radio("Select Simulation Phase to Inspect:", stages, index=1, label_visibility="collapsed")
        
            if "Stage 1" in selected_stage:
                html("""
                <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 1.1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <span style="font-weight: 800; color: #EF4444; font-size: 0.9rem;">🚦 PHASE: CONGESTION HOLD</span>
                        <span style="background: #FEE2E2; color: #DC2626; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">J1 Signal: RED</span>
                    </div>
                    <p style="font-size: 0.84rem; color: #F1F5F9; margin-bottom: 0.8rem;">
                        Junction 1 holds Northbound traffic at a solid <b>RED</b> light. 12 commuter vehicles are accumulated in the queue, incurring high delay before the emergency vehicle arrives.
                    </p>
                    <div style="background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 0.8rem; font-size: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>Commuter Wait Time:</span><b style="color: #EA580C;">42.5s</b></div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>Approach Queue:</span><b>12 Vehicles</b></div>
                        <div style="display: flex; justify-content: space-between;"><span>Downstream Backpressure:</span><b>28%</b></div>
                    </div>
                </div>
                """)
            elif "Stage 2" in selected_stage:
                html("""
                <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid #FDE68A; border-radius: 14px; padding: 1.1rem; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.08);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <span style="font-weight: 800; color: #FBBF24; font-size: 0.9rem;">🎯 DUAL-SENSOR FUSION HUD</span>
                        <span style="background: #FEF3C7; color: #B45309; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">Dual Verified</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 0.8rem;">
                        <div style="background: #0F172A; color: #F1F5F9; border-radius: 10px; padding: 0.8rem; border: 1px solid #334155;">
                            <div style="font-size: 0.75rem; font-weight: 800; color: #F59E0B; margin-bottom: 4px;">🔊 SOUND SENSOR</div>
                            <div style="font-family: monospace; font-size: 0.75rem; color: #38BDF8;">SPL: 96.4 dB</div>
                            <div style="font-size: 0.72rem; color: #94A3B8;">Freq: 940Hz - 1.45kHz</div>
                            <div style="font-size: 0.75rem; font-weight: 700; color: #4ADE80; margin-top: 4px;">● 99.2% Siren Match</div>
                        </div>
                        <div style="background: #0F172A; color: #F1F5F9; border-radius: 10px; padding: 0.8rem; border: 1px solid #334155;">
                            <div style="font-size: 0.75rem; font-weight: 800; color: #38BDF8; margin-bottom: 4px;">📷 PICTURE SENSOR</div>
                            <div style="font-family: monospace; font-size: 0.75rem; color: #4ADE80;">YOLOv8: AMBULANCE</div>
                            <div style="font-size: 0.72rem; color: #94A3B8;">Bounding Box: [X:836, Y:235]</div>
                            <div style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; margin-top: 4px;">● 98.7% Confidence</div>
                        </div>
                    </div>
                    <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 10px; padding: 0.7rem; font-size: 0.8rem; color: #34D399;">
                        <b>✅ Consensus Established:</b> Optical visual picture confirmed emergency vehicle target simultaneously with acoustic siren decibel signature. False positive probability &lt; 0.01%.
                    </div>
                </div>
                """)
            elif "Stage 3" in selected_stage:
                html("""
                <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid #A7F3D0; border-radius: 14px; padding: 1.1rem; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <span style="font-weight: 800; color: #059669; font-size: 0.9rem;">🟢 SIGNAL ACTUATION: RED ➔ GREEN</span>
                        <span style="background: #DCFCE7; color: #6EE7B7; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">NEMA TS2 Preempt</span>
                    </div>
                    <p style="font-size: 0.84rem; color: #F1F5F9; margin-bottom: 0.8rem;">
                        NEMA TS2 solid-state relays execute clearance protocol: conflicting cross-street phases undergo guaranteed 1.5s Yellow + 1.0s All-Red before snapping Junction 1 to <b>GREEN</b>.
                    </p>
                    <div style="display: flex; align-items: center; justify-content: space-around; background: #0F172A; border-radius: 12px; padding: 0.9rem; margin-bottom: 0.8rem;">
                        <div style="text-align: center;">
                            <div style="width: 22px; height: 22px; border-radius: 50%; background: #EF4444; opacity: 0.2; margin: 0 auto;"></div>
                            <span style="font-size: 0.7rem; color: #E2E8F0;">RED</span>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 22px; height: 22px; border-radius: 50%; background: #F59E0B; opacity: 0.2; margin: 0 auto;"></div>
                            <span style="font-size: 0.7rem; color: #E2E8F0;">YELLOW</span>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 26px; height: 26px; border-radius: 50%; background: #10B981; box-shadow: 0 0 16px #10B981; margin: 0 auto;"></div>
                            <span style="font-size: 0.75rem; font-weight: 800; color: #4ADE80;">GREEN ● ACTIVE</span>
                        </div>
                    </div>
                    <div style="font-size: 0.8rem; color: #059669;">
                        <b>Delay Eliminated:</b> Queue released immediately; emergency vehicle crosses Junction 1 with 0 waiting time.
                    </div>
                </div>
                """)
            elif "Stage 4" in selected_stage:
                html("""
                <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid #DDD6FE; border-radius: 14px; padding: 1.1rem; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.08);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <span style="font-weight: 800; color: #7C3AED; font-size: 0.9rem;">📡 INTER-JUNCTION V2X TRANSMISSION</span>
                        <span style="background: #EDE9FE; color: #C084FC; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">DSRC IEEE 802.11p</span>
                    </div>
                    <p style="font-size: 0.84rem; color: #F1F5F9; margin-bottom: 0.8rem;">
                        Junction 1 sends a high-priority corridor reservation packet over the arterial link to Junction 2 ahead of vehicle arrival.
                    </p>
                    <div style="background: #0F172A; color: #E2E8F0; border-radius: 10px; padding: 0.8rem; font-family: monospace; font-size: 0.75rem; border: 1px solid #334155;">
                        <div style="color: #A78BFA; font-weight: 700; margin-bottom: 4px;">// NTCIP 1202 V2X Packet Payload</div>
                        <div>{</div>
                        <div style="padding-left: 12px;">"msg_type": "GREEN_WAVE_PREEMPT",</div>
                        <div style="padding-left: 12px;">"source": "JUNCTION_1_NORTH_GATE",</div>
                        <div style="padding-left: 12px; color: #38BDF8;">"target": "JUNCTION_2_MARKET_ROAD",</div>
                        <div style="padding-left: 12px; color: #4ADE80;">"eta_to_target_sec": 4.2,</div>
                        <div style="padding-left: 12px;">"vehicle_class": "AMBULANCE",</div>
                        <div style="padding-left: 12px; color: #F59E0B;">"auth_token": "VALIDATED_DSRC_0x9B4E"</div>
                        <div>}</div>
                    </div>
                </div>
                """)
            else:
                html("""
                <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid #BAE6FD; border-radius: 14px; padding: 1.1rem; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.08);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <span style="font-weight: 800; color: #0284C7; font-size: 0.9rem;">⚡ NEXT JUNCTION GREEN WAVE SYNC</span>
                        <span style="background: #E0F2FE; color: #38BDF8; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;">Pre-Cleared</span>
                    </div>
                    <p style="font-size: 0.84rem; color: #F1F5F9; margin-bottom: 0.8rem;">
                        Junction 2 (Market Road) receives the packet, preemptively clears opposing traffic 3 seconds before arrival, and locks its light to <b>GREEN</b>.
                    </p>
                    <div style="background: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 10px; padding: 0.8rem; font-size: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>Corridor Travel Time:</span><b style="color: #059669;">-84.2% Delay</b></div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>J2 Stop Count:</span><b>0 (Continuous Flow)</b></div>
                        <div style="display: flex; justify-content: space-between;"><span>Spillback Gridlock Risk:</span><b>Zero</b></div>
                    </div>
                </div>
                """)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔬 How FlowSync SUTC Architecture Works Under The Hood")
    
        html("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div class="junction-card j-theme-violet">
                <h4 style="color: #7C3AED; margin-top: 0;">1. Dual Sensor Fusion Protocol</h4>
                <p style="font-size: 0.85rem; color: #F1F5F9;">
                    Standard emergency preemption often triggers false positives from horns or reflections. FlowSync combines microphone array acoustic spectral estimation with edge YOLOv8 visual classification. Preemption only trips when both sensors independently exceed 90% confidence.
                </p>
            </div>
            <div class="junction-card j-theme-green">
                <h4 style="color: #059669; margin-top: 0;">2. NEMA TS2 Actuator Safety Buffer</h4>
                <p style="font-size: 0.85rem; color: #F1F5F9;">
                    Signals never transition instantly to green if conflicting vehicles or pedestrians are in the cross-walk. The controller interlock automatically executes a compliant yellow clearance (3.5s) followed by all-red (1.5s) interval before opening the priority corridor.
                </p>
            </div>
            <div class="junction-card j-theme-blue">
                <h4 style="color: #0284C7; margin-top: 0;">3. Multi-Hop C-V2X Wireless Relay</h4>
                <p style="font-size: 0.85rem; color: #F1F5F9;">
                    Each roadside unit (RSU) communicates over IEEE 802.11p / C-V2X mesh channels. When J1 detects priority traffic, it calculates arrival ETA for downstream J2 and forwards encrypted tokens so J2 pre-clears queues before arrival.
                </p>
            </div>
        </div>
        """)
        st.markdown("<br>", unsafe_allow_html=True)


    with tab_about:
        st.markdown("### 🛠️ System Architecture & Engineering Specifications")
        st.caption("Technical blueprint of the FlowSync Urban Traffic Management System designed for smart municipal intersections.")
    
        html("""
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.2rem; margin-top: 1rem;">
            <div class="junction-card j-theme-violet">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <h4 style="color: #7C3AED; margin: 0;">1. Perception Layer & IoT Sensor Suite</h4>
                    <span style="font-size: 0.75rem; font-weight: 700; background: #EDE9FE; color: #7C3AED; padding: 2px 8px; border-radius: 999px;">Perception Layer</span>
                </div>
                <p style="font-size: 0.88rem; color: #F1F5F9; margin: 0;">
                    High-definition RTSP camera streams decoded via lightweight YOLOv8 models running on edge accelerators. Bounding boxes are filtered across virtual approach polygons to compute vehicle queue volume and accumulation rates with sub-50ms latency.
                </p>
            </div>
        
            <div class="junction-card j-theme-blue">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <h4 style="color: #0284C7; margin: 0;">2. Decentralized Backpressure Optimization</h4>
                    <span style="font-size: 0.75rem; font-weight: 700; background: #E0F2FE; color: #0284C7; padding: 2px 8px; border-radius: 999px;">Control Core</span>
                </div>
                <p style="font-size: 0.88rem; color: #F1F5F9; margin: 0;">
                    Implements a decentralized Max-Weight queue balancing algorithm. Approach phases are weighted dynamically using instantaneous vehicle accumulation, cumulative dwell delay, and downstream storage capacity penalties to prevent urban gridlock spillback.
                </p>
            </div>
        
            <div class="junction-card j-theme-green">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <h4 style="color: #059669; margin: 0;">3. Emergency Priority Wave (DSRC/C-V2X)</h4>
                    <span style="font-size: 0.75rem; font-weight: 700; background: #DCFCE7; color: #059669; padding: 2px 8px; border-radius: 999px;">Preemption</span>
                </div>
                <p style="font-size: 0.88rem; color: #F1F5F9; margin: 0;">
                    Interlocks with emergency responder transponders to construct dynamic green corridors across multi-hop routes (J4 ➔ J3 ➔ J1). Minimizes ambulance travel latency while strictly maintaining pedestrian clearance safety buffers on cross-streets.
                </p>
            </div>
        
            <div class="junction-card j-theme-orange">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <h4 style="color: #EA580C; margin: 0;">4. Hardware Deployment & Controller Interface</h4>
                    <span style="font-size: 0.75rem; font-weight: 700; background: #FFEDD5; color: #EA580C; padding: 2px 8px; border-radius: 999px;">Embedded Edge</span>
                </div>
                <p style="font-size: 0.88rem; color: #F1F5F9; margin: 0;">
                    Benchmarked for deployment on NVIDIA Jetson Orin Nano / Raspberry Pi CM4 platforms. Actuation outputs interface with standard municipal NEMA TS2 / Model 2070 traffic signal cabinets via RS-485 serial buses and solid-state relay isolators.
                </p>
            </div>
        </div>
        """)
    
        st.markdown("<br>", unsafe_allow_html=True)
        html("""
        <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 1.1rem 1.4rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-weight: 800; font-size: 0.95rem; color: #FFFFFF; font-family: Outfit, sans-serif;">🚦 FlowSync Urban Traffic Management System</div>
                <div style="font-size: 0.82rem; color: #E2E8F0;">Smart Urban Infrastructure & Intelligent Mobility Systems Architecture</div>
            </div>
            <div style="font-size: 0.82rem; font-weight: 700; color: #4F46E5; background: #EEF2FF; padding: 6px 14px; border-radius: 999px; border: 1px solid #C7D2FE;">
                📦 Open Source MIT License • Ready for SUMO/NTCIP Integration
            </div>
        </div>
        """)
