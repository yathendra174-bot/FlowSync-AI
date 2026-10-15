# 🚦 FlowSync: Smart Urban Traffic Management System (SUTC)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.35%2B-red.svg)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/Standard-NEMA%20TS2%20%2F%20NTCIP%201202-success.svg)]()
[![Hackathon](https://img.shields.io/badge/Hackathon-Smart%20Cities%202026-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FlowSync** is an intelligent urban traffic control platform designed to reduce commuter delays, prevent gridlock spillback, and provide automated priority green corridors for emergency first responders.

Built with Python, Streamlit, and Plotly, FlowSync implements decentralized queue pressure balancing with upstream/downstream lookahead coordination across connected municipal intersections.

---

## 🏗️ System Architecture

```text
  [ Traffic CCTV Feeds ]       [ Inductive Loop Sensors ]
             │                              │
             ▼                              ▼
    ┌──────────────────────────────────────────────┐
    │     Edge Perception Layer (YOLOv8 / RTSP)    │
    │  - Vehicle Detection & Virtual Queue Counting│
    └──────────────────────┬───────────────────────┘
                           │ MQTT / CoAP (JSON Telemetry)
                           ▼
    ┌──────────────────────────────────────────────┐
    │        FlowSync Optimization Engine          │
    │  - Max-Weight Queue Pressure Balancer        │
    │  - Downstream Backpressure Lookahead Check   │
    │  - Dynamic Green Phase Allocator (10s - 45s) │
    │  - Priority Emergency Preemption Interlock   │
    └──────────────────────┬───────────────────────┘
                           │ Relay Actuation Signals
                           ▼
    ┌──────────────────────────────────────────────┐
    │    Municipal Signal Cabinets (NEMA TS2)      │
    │  - Fail-safe Yellow (3.5s) & All-Red (1.5s)  │
    │  - Manual Police Cabinet Override Switch     │
    └──────────────────────────────────────────────┘
```

---

## ✨ Key Capabilities & Engineering Features

1. **Decentralized Queue-Pressure Optimization**:
   Dynamically weights green phase durations based on instantaneous queue accumulation, dwell wait times, and downstream link occupancy.
2. **Backpressure Congestion Prevention**:
   Prevents vehicle spillback by penalizing green extension when the immediate downstream intersection exceeds safe road storage capacity (>75%).
3. **Emergency Vehicle Preemption (DSRC / Optical Strobe)**:
   Simulates emergency responder vehicle detection, preemptively clearing corridors (`J4 ➔ J3 ➔ J1`) while preserving minimum safe clearance intervals on cross-streets.
4. **Manual Police Intervention Console**:
   Hardware override panel simulating on-site traffic police key switches (Force Green on any junction or trigger an emergency All-Red hold).
5. **Preconfigured Real-World Scenarios**:
   One-click testing for Morning Peak Commute, School Zone Rush, Hospital Priority Inbound, and Night Low-Volume flow.
6. **Live Telemetry & CSV Data Export**:
   Real-time edge controller terminal logs and single-click dataset export (.CSV) for analytical reporting.

---

## 🚀 Quick Start Guide (Windows)

### 1. Open Terminal in Project Directory
Open PowerShell in the `FlowSync-AI` directory:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Launch the FlowSync Controller
```powershell
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to interact with the system.

---

## 🎯 Demo Walkthrough for Evaluators

1. **Autonomous Operation**: Run the simulation with default demand and observe the controller adjusting green windows between junctions.
2. **Scenario Stress-Testing**: Select `"Morning Peak Commute"` from the sidebar presets to evaluate how the system handles heavy North Gate inbound traffic.
3. **Emergency Preemption**: Check `"Trigger Emergency Vehicle"` and advance steps to witness the prioritized corridor (`J4 ➔ J3 ➔ J1`) with flashing beacons and route preemption.
4. **Manual Police Override**: Select `"Force ALL-RED"` or `"Force Green: J2"` to demonstrate manual police intervention overriding the automated system.
5. **Export Metrics**: Open the **Benchmarks** tab and click `"Download Telemetry Dataset (.CSV)"` to inspect the exported run data.

---

## 👥 Project Team

- **Team**: FlowSync Engineering Group
- **Track**: Smart Mobility & Intelligent Transportation Systems (ITS)
- **Competition**: Smart Cities Hackathon 2026
- **License**: MIT Open Source License
