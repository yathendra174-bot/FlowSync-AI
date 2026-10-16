"""
FlowSync AI — Incident Detection and Automated Recovery Engine (Feature Five)
Detects abnormal bottlenecks, road blockages, sensor dropouts, and gridlock spillbacks.
Tracks state progression: DETECTED -> ACKNOWLEDGED -> RECOVERING -> RESOLVED.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class Incident:
    incident_id: str
    incident_type: str              # "EXCESSIVE_QUEUE", "ROAD_BLOCKAGE", "SENSOR_FAULT", "DOWNSTREAM_GRIDLOCK", "EMERGENCY_OBSTRUCTED"
    severity: str                   # "CRITICAL", "WARNING", "INFO"
    junction_idx: int
    junction_name: str
    detected_time_sec: int
    evidence: str
    recommended_action: str
    status: str = "DETECTED"        # "DETECTED", "ACKNOWLEDGED", "RECOVERING", "RESOLVED"
    resolved_time_sec: Optional[int] = None
    is_simulated_injection: bool = False

class IncidentManager:
    """Manages active traffic incidents, anomaly detection, and recovery verification."""

    def __init__(self):
        self.incidents: List[Incident] = []
        self._incident_counter = 1

    def scan_network_anomalies(
        self,
        snapshot: Dict[str, Any],
        sensor_twin: Optional[Any] = None,
        emergency_state: Optional[Any] = None
    ) -> List[Incident]:
        """Automatically scans telemetry for abnormal conditions."""
        time_sec = snapshot.get("time_seconds", 0)
        junctions = snapshot.get("junctions", [])

        for idx, j_data in enumerate(junctions):
            q_len = j_data["vehicles_waiting"]
            downstream_occ = j_data["downstream_occupancy"]

            # Anomaly 1: Excessive Queue Growth (> 35 vehicles)
            if q_len >= 32:
                inc_id = f"INC-Q-{idx+1}"
                if not any(inc.incident_id == inc_id and inc.status != "RESOLVED" for inc in self.incidents):
                    self.incidents.append(Incident(
                        incident_id=inc_id,
                        incident_type="EXCESSIVE_QUEUE",
                        severity="WARNING",
                        junction_idx=idx,
                        junction_name=j_data["name"],
                        detected_time_sec=time_sec,
                        evidence=f"Queue density at {q_len}/45 vehicles ({int(q_len/45*100)}% capacity).",
                        recommended_action="Execute green window extension and prioritize upstream holding."
                    ))

            # Anomaly 2: Downstream Gridlock / Severe Spillback Risk (> 85%)
            if downstream_occ >= 85:
                inc_id = f"INC-DS-{idx+1}"
                if not any(inc.incident_id == inc_id and inc.status != "RESOLVED" for inc in self.incidents):
                    self.incidents.append(Incident(
                        incident_id=inc_id,
                        incident_type="DOWNSTREAM_GRIDLOCK",
                        severity="CRITICAL",
                        junction_idx=idx,
                        junction_name=j_data["name"],
                        detected_time_sec=time_sec,
                        evidence=f"Immediate downstream link at {downstream_occ}% capacity. Spillback impending.",
                        recommended_action="Throttle approach discharge rate; divert traffic to parallel arterial."
                    ))

        # Anomaly 3: Check IoT Sensor Failures
        if sensor_twin:
            for s_id, sensor in sensor_twin.sensors.items():
                if sensor.health_status in ("DISCONNECTED", "STALE"):
                    inc_id = f"INC-SENS-{s_id}"
                    if not any(inc.incident_id == inc_id and inc.status != "RESOLVED" for inc in self.incidents):
                        self.incidents.append(Incident(
                            incident_id=inc_id,
                            incident_type="SENSOR_FAULT",
                            severity="WARNING" if sensor.health_status == "STALE" else "CRITICAL",
                            junction_idx=sensor.junction_idx,
                            junction_name=sensor.junction_name,
                            detected_time_sec=time_sec,
                            evidence=f"Sensor {s_id} reported {sensor.health_status} state. Telemetry unavailable.",
                            recommended_action="Engage robust prior-queue fallback policy; dispatch field maintenance."
                        ))

        # Auto-verify recovery conditions
        for inc in self.incidents:
            if inc.status in ("ACKNOWLEDGED", "RECOVERING"):
                if inc.incident_type == "EXCESSIVE_QUEUE":
                    if junctions[inc.junction_idx]["vehicles_waiting"] < 20:
                        inc.status = "RESOLVED"
                        inc.resolved_time_sec = time_sec
                elif inc.incident_type == "DOWNSTREAM_GRIDLOCK":
                    if junctions[inc.junction_idx]["downstream_occupancy"] < 65:
                        inc.status = "RESOLVED"
                        inc.resolved_time_sec = time_sec
                elif inc.incident_type == "SENSOR_FAULT":
                    if sensor_twin:
                        matching_sensor = next((s for s_id, s in sensor_twin.sensors.items() if s_id in inc.incident_id), None)
                        if matching_sensor and matching_sensor.health_status == "HEALTHY":
                            inc.status = "RESOLVED"
                            inc.resolved_time_sec = time_sec

        return self.incidents

    # Operator Controls
    def inject_incident(self, incident_type: str, junction_idx: int, time_sec: int) -> Incident:
        """Manually injects an incident for scenario testing."""
        junction_names = ["J1 - North Gate", "J2 - Market Road", "J3 - College Circle", "J4 - Hospital Road"]
        inc_id = f"INC-SIM-{self._incident_counter}"
        self._incident_counter += 1

        if incident_type == "ROAD_BLOCKAGE":
            evidence = "Debris / Vehicle breakdown detected blocking primary travel lane."
            action = "Close lane in network model; detour upstream traffic; extend green wave on alternate path."
            sev = "CRITICAL"
        elif incident_type == "EMERGENCY_OBSTRUCTED":
            evidence = "Emergency vehicle unable to proceed due to stopped cross-lane queue."
            action = "Trigger dynamic all-red clearance interval on all conflicting approaches."
            sev = "CRITICAL"
        else:
            evidence = "Manual anomaly injected for resilience testing."
            action = "Monitor recovery protocol."
            sev = "WARNING"

        inc = Incident(
            incident_id=inc_id,
            incident_type=incident_type,
            severity=sev,
            junction_idx=junction_idx,
            junction_name=junction_names[junction_idx],
            detected_time_sec=time_sec,
            evidence=evidence,
            recommended_action=action,
            status="DETECTED",
            is_simulated_injection=True
        )
        self.incidents.append(inc)
        return inc

    def acknowledge(self, incident_id: str):
        for inc in self.incidents:
            if inc.incident_id == incident_id and inc.status == "DETECTED":
                inc.status = "ACKNOWLEDGED"

    def initiate_recovery(self, incident_id: str):
        for inc in self.incidents:
            if inc.incident_id == incident_id:
                inc.status = "RECOVERING"

    def clear_incident(self, incident_id: str, time_sec: int):
        for inc in self.incidents:
            if inc.incident_id == incident_id:
                inc.status = "RESOLVED"
                inc.resolved_time_sec = time_sec
