# 🚦 FlowSync-AI: AI-Powered Cooperative Traffic Optimization System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.35%2B-red.svg)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/Standard-NEMA%20TS2%20%2F%20NTCIP%201202-success.svg)]()
[![Hackathon](https://img.shields.io/badge/Hackathon-Smart%20Cities%202026-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FlowSync-AI** is an advanced municipal smart-city traffic intelligence and cooperative signal control prototype designed for smart urban corridors. It implements decentralized max-weight queue balancing, upstream/downstream lookahead coordination, multi-hop emergency priority corridors, roadside IoT digital twins with fault tolerance, explainable AI (XAI) decision attribution, and reproducible scientific scenario benchmarking.

---

## 🏗️ System Architecture & 7 Advanced Intelligence Features

```text
  [ Roadside IoT Fleet ]      [ Computer Vision YOLOv8 ]     [ Emergency Transponders ]
  (16 Loop/Radar/Acoustic)    (Virtual Stopbar Camera)       (DSRC IEEE 802.11p C-V2X)
             │                              │                              │
             ▼                              ▼                              ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                       FlowSync Intelligence Subsystems                     │
    │  1. AI Congestion Predictor (0-100 Risk Score, 30s/60s Horizon Forecast)   │
    │  2. Cooperative Junction Mesh (J1➔J2➔J4➔J3➔J1 Backpressure & Fairness)      │
    │  3. Emergency Priority Corridor (J4➔J3➔J1, NEMA TS2 Yellow/All-Red Interlock)│
    │  4. IoT Sensor Digital Twin (16 Edge Sensors, Missing-Data Fallback Policy) │
    │  5. Incident Detection & Recovery (Spike, Blockage, Stale Data Lifecycle)   │
    │  6. Explainable AI Decision Panel (Natural Language Attribution & Bounds)   │
    │  7. Scenario Lab & Scientific Replay (7 Municipal Profiles, CSV Exports)   │
    └──────────────────────────────────────┬──────────────────────────────────────┘
                                           │ RS-485 / NTCIP 1202 Relays
                                           ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                    Municipal Traffic Cabinets (NEMA TS2)                    │
    │  - Mandatory 3.5s Yellow Deceleration + 1.5s All-Red Safety Clearance      │
    │  - Hardware MMU (Malfunction Management Unit) Conflicting Green Inhibitor   │
    │  - Pedestrian Flash Don't-Walk Safe Buffer Interlocks                       │
    └─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Advanced Feature Modules

### 1. 🔮 AI Congestion Prediction & Queue Horizon Forecasting (`congestion_predictor.py`)
- Evaluates queue accumulation, dwell wait time, arrival pressure, and downstream occupancy into a transparent **0-100 Congestion Risk Score**.
- Classifies risk into **LOW (0-39)**, **MEDIUM (40-69)**, and **HIGH (70-100)**.
- Projects queue growth over **+30s** and **+60s** horizons using approach arrival velocity.
- Features transparent evidence breakdown cards attributing exact risk points to physical metrics (never claiming heuristic calculations are black-box ML).
- Automatic safe fallback to moving historical priors when sensor telemetry is disconnected or stale.

### 2. 🤝 Cooperative Junction Intelligence (`cooperative_intelligence.py`)
- Coordinates the 4 municipal intersections across the arterial loop: **J1 (North Gate) ➔ J2 (Market Road) ➔ J4 (Hospital Road) ➔ J3 (College Circle) ➔ J1 (North Gate)**.
- Performs downstream storage capacity lookahead to prevent urban spillback gridlock.
- Implements starvation prevention fairness scaling (`+4.0 pts / unserved red cycle`).
- Features a simulated **IEEE 802.11p DSRC / C-V2X Wireless Message Bus** logging inter-node packet exchanges in real time.

### 3. 🚑 Emergency Green Corridor (`emergency_corridor.py`)
- Verifiable emergency preemption state machine: `IDLE ➔ PRIORITY_REQUESTED ➔ PREPARATION_IN_PROGRESS ➔ PRIORITY_GRANTED ➔ CORRIDOR_CLEARED` (or `CANCELLED`).
- Preempts and tracks emergency vehicle units (e.g. `AMB-911-DELTA`) along the route **J4 ➔ J3 ➔ J1**.
- Guarantees NEMA TS2 safety intervals: cross-street 3.5s yellow + 1.5s all-red clearance before green grant.
- Operator cancellation control restoring standard cyclic control smoothly without signal jarring.

### 4. 📡 IoT Sensor Digital Twin (`iot_sensor_twin.py`)
- Digital twin modeling **16 edge roadside sensors** (4 per junction: Inductive Loop, Radar Occupancy, Signal Relay Telemetry, Acoustic Siren Array).
- Live edge telemetry display with update timestamps, protocols (`MQTT/JSON`, `CoAP`, `Modbus-RTU`, `CAN-Bus`), and raw readings.
- **Fault Injection Console**: test system resilience by injecting `DISCONNECTED`, `STALE`, `NOISY`, or `HEALTHY` states.
- **Missing-Data Fallback**: disconnected sensors report `None` (unavailable), never zero vehicles, preventing false green extension.

### 5. 🚨 Incident Detection & Anomaly Recovery (`incident_manager.py`)
- Automated background anomaly scanning for excessive queue growth, road blockages, sensor dropouts, stale telemetry, and emergency corridor obstructions.
- Multi-stage incident lifecycle management: `DETECTED ➔ ACKNOWLEDGED ➔ RECOVERING ➔ RESOLVED`.
- Interactive resilience testing tool to manually inject incidents and test corrective action protocols.

### 6. 🧠 Explainable AI (XAI) Decision Attribution (`xai_explainer.py`)
- Generates human-readable plain-English narratives explaining the exact justification behind each junction phase grant.
- Breaks down positive and negative factors, safety constraints applied (min/max green timers, MMU interlocks), and explicit explanations for why alternative approaches were held red.
- Displays priority rankings and next reassessment countdown windows.

### 7. 🧪 Scenario Lab & Scientific Benchmark Replay (`scenario_lab.py`)
- Reproducible benchmark testing environment with 7 municipal scenario profiles:
  1. *Normal Baseline Traffic*
  2. *Morning Rush Hour*
  3. *Sudden Arterial Congestion*
  4. *Emergency Response Corridor*
  5. *Sensor Failure & Stale Telemetry*
  6. *Downstream Road Blockage*
  7. *Mixed Multi-Modal Traffic*
- Side-by-side empirical comparison between FlowSync Adaptive AI and Fixed-Time Cyclic control.
- Step-level delay dynamics, queue convergence plots, and single-click CSV dataset export.

---

## 🚀 Local Quick-Start Guide (Windows & Linux)

### Option 1: Direct PowerShell / Terminal Launch (Fastest)

```powershell
# Navigate to the project directory
cd E:\FlowSync-AI\FlowSync-AI

# Install dependencies into virtual environment
.\.venv\Scripts\pip.exe install -r requirements.txt

# Run Streamlit Application
.\.venv\Scripts\streamlit.exe run app.py
```

### Option 2: Windows Batch Launcher

Double-click or run `run_windows.bat`:
```cmd
.\run_windows.bat
```

### Option 3: Standard Virtual Environment Activation

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open **`http://localhost:8501`** in your browser.

---

## 🧪 Unit Testing & Verification

A comprehensive automated test suite verifying all 7 intelligence modules and signal safety regression is included in `tests/test_flowsync_advanced.py`.

Run tests with:
```powershell
.\.venv\Scripts\python.exe -m unittest tests/test_flowsync_advanced.py
```

**Test Results:**
```text
........
----------------------------------------------------------------------
Ran 8 tests in 0.027s

OK
```
All 8 test suites pass with zero errors, zero warnings, and zero regressions.

---

## ☁️ Cloud Deployment Configuration (Render)

To deploy FlowSync-AI on [Render](https://render.com) as a Web Service:

| Setting | Value |
| :--- | :--- |
| **Runtime** | `Python 3` |
| **Root Directory** | `FlowSync-AI` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true` |
| **Health Check Path** | `/_stcore/health` |
| **Auto-Deploy** | `Yes` (Triggered on git push to `main`) |

---

## 📜 Git Version Control Commands

To stage, commit, and push the completed implementation to your Git repository:

```bash
git add .
git commit -m "feat: complete FlowSync-AI advanced traffic intelligence upgrade with 7 core modules, unit tests, and Render deployment config"
git push origin main
```

---

## ⚠️ Prototype Disclaimer
*FlowSync-AI is a smart-city engineering simulation prototype designed for academic and hackathon demonstration purposes. Signal timings comply with NEMA TS2 and NTCIP 1202 conventions in simulation, but physical deployment on real-world municipal intersections requires certified hardware MMUs and regional DOT authorization.*
