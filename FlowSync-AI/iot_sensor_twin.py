"""
FlowSync AI — IoT Sensor Digital Twin (Feature Four)
Simulates inductive loops, radar occupancy, optical relays, and acoustic siren detectors.
Provides fault injection (disconnect, stale, noise, recover) and safe fallback handling.
"""

from dataclasses import dataclass, field
import random
from typing import Dict, List, Any, Optional

@dataclass
class SensorDevice:
    sensor_id: str
    junction_idx: int
    junction_name: str
    sensor_type: str        # "INDUCTIVE_LOOP", "RADAR_OCCUPANCY", "OPTICAL_SIGNAL", "ACOUSTIC_ARRAY"
    protocol: str           # "MQTT/JSON", "CoAP/UDP", "RS-485/Modbus", "DSRC/802.11p"
    health_status: str      # "HEALTHY", "STALE", "DISCONNECTED", "NOISY"
    last_update_sec: int
    is_simulated: bool = True
    raw_reading: Any = None
    fallback_applied: bool = False
    diagnostic_message: str = "Operating within nominal calibration."

class IoTSensorTwin:
    """Digital Twin representation of the physical traffic sensing edge layer."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.sensors: Dict[str, SensorDevice] = {}
        self._init_sensor_suite()

    def _init_sensor_suite(self):
        junction_names = ["J1 - North Gate", "J2 - Market Road", "J3 - College Circle", "J4 - Hospital Road"]
        for i, name in enumerate(junction_names):
            prefix = f"J{i+1}"
            # 1. Inductive loop (vehicle count)
            self.sensors[f"{prefix}-LOOP-01"] = SensorDevice(
                sensor_id=f"{prefix}-LOOP-01",
                junction_idx=i,
                junction_name=name,
                sensor_type="INDUCTIVE_LOOP",
                protocol="MQTT/JSON",
                health_status="HEALTHY",
                last_update_sec=0
            )
            # 2. Downstream radar occupancy
            self.sensors[f"{prefix}-RADAR-02"] = SensorDevice(
                sensor_id=f"{prefix}-RADAR-02",
                junction_idx=i,
                junction_name=name,
                sensor_type="RADAR_OCCUPANCY",
                protocol="CoAP/UDP",
                health_status="HEALTHY",
                last_update_sec=0
            )
            # 3. Optical signal actuator feedback
            self.sensors[f"{prefix}-SIGNAL-03"] = SensorDevice(
                sensor_id=f"{prefix}-SIGNAL-03",
                junction_idx=i,
                junction_name=name,
                sensor_type="OPTICAL_SIGNAL",
                protocol="RS-485/Modbus",
                health_status="HEALTHY",
                last_update_sec=0
            )
            # 4. Acoustic siren sensor
            self.sensors[f"{prefix}-ACOUSTIC-04"] = SensorDevice(
                sensor_id=f"{prefix}-ACOUSTIC-04",
                junction_idx=i,
                junction_name=name,
                sensor_type="ACOUSTIC_ARRAY",
                protocol="DSRC/802.11p",
                health_status="HEALTHY",
                last_update_sec=0
            )

    def sync_with_simulation(self, snapshot: Dict[str, Any], emergency_active: bool = False):
        """Updates digital twin telemetry from authoritative simulator state."""
        time_sec = snapshot.get("time_seconds", 0)
        junctions = snapshot.get("junctions", [])

        for i, j_data in enumerate(junctions):
            prefix = f"J{i+1}"
            loop_id = f"{prefix}-LOOP-01"
            radar_id = f"{prefix}-RADAR-02"
            sig_id = f"{prefix}-SIGNAL-03"
            acoust_id = f"{prefix}-ACOUSTIC-04"

            # Sync Loop
            loop = self.sensors[loop_id]
            if loop.health_status == "HEALTHY":
                loop.raw_reading = j_data["vehicles_waiting"]
                loop.last_update_sec = time_sec
                loop.fallback_applied = False
                loop.diagnostic_message = "Nominal inductive coil resonance."
            elif loop.health_status == "NOISY":
                noise = self.rng.randint(-4, 5)
                loop.raw_reading = max(0, j_data["vehicles_waiting"] + noise)
                loop.last_update_sec = time_sec
                loop.fallback_applied = False
                loop.diagnostic_message = f"Coil inductance fluctuating (+/-{abs(noise)} jitter)."
            elif loop.health_status == "STALE":
                # Stale reading: does NOT update last_update_sec; holds older value
                loop.fallback_applied = True
                loop.diagnostic_message = f"Heartbeat missed for > {time_sec - loop.last_update_sec}s. Fallback prior engaged."
            elif loop.health_status == "DISCONNECTED":
                # Disconnected: Raw reading is MISSING (None), not 0!
                loop.raw_reading = None
                loop.fallback_applied = True
                loop.diagnostic_message = "Signal line severed / link timeout. Safe fallback default active."

            # Sync Radar Occupancy
            radar = self.sensors[radar_id]
            if radar.health_status == "HEALTHY":
                radar.raw_reading = j_data["downstream_occupancy"]
                radar.last_update_sec = time_sec
                radar.fallback_applied = False
            elif radar.health_status == "DISCONNECTED":
                radar.raw_reading = None
                radar.fallback_applied = True

            # Sync Signal Relay
            sig = self.sensors[sig_id]
            if sig.health_status == "HEALTHY":
                sig.raw_reading = j_data["signal"]
                sig.last_update_sec = time_sec

            # Sync Acoustic Siren
            acoust = self.sensors[acoust_id]
            if acoust.health_status == "HEALTHY":
                acoust.raw_reading = 96.4 if emergency_active else 54.2
                acoust.last_update_sec = time_sec

    # Fault Injection Controls
    def set_fault(self, sensor_id: str, fault_type: str):
        """fault_type: 'DISCONNECTED', 'STALE', 'NOISY', 'HEALTHY'"""
        if sensor_id in self.sensors:
            self.sensors[sensor_id].health_status = fault_type
            if fault_type == "HEALTHY":
                self.sensors[sensor_id].diagnostic_message = "Sensor restored and recalibrated."

    def recover_all(self):
        for s in self.sensors.values():
            s.health_status = "HEALTHY"
            s.diagnostic_message = "Operating within nominal calibration."

    def get_effective_queue(self, junction_idx: int, simulator_queue: int) -> int:
        """
        Safe Fallback Policy:
        If the loop sensor is disconnected or stale, we DO NOT use zero!
        We use an estimated safe prior (e.g. historical average or fallback value).
        """
        loop_id = f"J{junction_idx+1}-LOOP-01"
        sensor = self.sensors.get(loop_id)
        if not sensor or sensor.health_status == "DISCONNECTED" or sensor.raw_reading is None:
            # Fallback: maintain safe estimated queue
            return max(12, simulator_queue)
        return int(sensor.raw_reading)
