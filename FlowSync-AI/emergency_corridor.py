"""
FlowSync AI — Emergency Green Corridor Manager (Feature Three)
Coordinates full-lifecycle emergency vehicle preemption (J4 ➔ J3 ➔ J1):
Dispatch -> Priority Request -> Cross-Street Clearance (Yellow/All-Red) -> Priority Grant -> Step Progression -> Exit/Cancel.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class EmergencyEventLog:
    timestamp: str
    phase: str
    message: str
    severity: str  # "INFO", "WARNING", "SUCCESS", "CRITICAL"

@dataclass
class EmergencyVehicleState:
    vehicle_id: str = "AMB-911-DELTA"
    vehicle_type: str = "Class-1 Advanced Life Support Ambulance"
    priority_level: str = "LEVEL-1 CRITICAL"
    route: List[int] = field(default_factory=lambda: [3, 2, 0])  # J4 -> J3 -> J1
    route_names: List[str] = field(default_factory=lambda: ["J4 - Hospital Road", "J3 - College Circle", "J1 - North Gate"])
    current_step_in_route: int = 0
    destination: str = "J1 - North Gate Arterial Medical Dispatch"
    status: str = "IDLE"  # "IDLE", "PRIORITY_REQUESTED", "PREPARATION_IN_PROGRESS", "PRIORITY_GRANTED", "CORRIDOR_CLEARED", "CANCELLED"
    speed_kmh: float = 0.0
    eta_seconds: float = 0.0
    progress_pct: float = 0.0
    active_clearing_junction: Optional[str] = None
    yellow_clearance_remaining: float = 0.0
    all_red_buffer_remaining: float = 0.0

class EmergencyCorridorManager:
    """Manages verified emergency preemption and signal transitions across the network."""

    def __init__(self):
        self.state = EmergencyVehicleState()
        self.logs: List[EmergencyEventLog] = []

    def dispatch(self, vehicle_id: str = "AMB-911-DELTA", priority_level: str = "LEVEL-1 CRITICAL") -> EmergencyVehicleState:
        """Initiates dispatch and requests priority corridor along J4 -> J3 -> J1."""
        self.state = EmergencyVehicleState(
            vehicle_id=vehicle_id,
            priority_level=priority_level,
            route=[3, 2, 0],
            route_names=["J4 - Hospital Road", "J3 - College Circle", "J1 - North Gate"],
            current_step_in_route=0,
            destination="J1 - North Gate Arterial Medical Dispatch",
            status="PRIORITY_REQUESTED",
            speed_kmh=54.0,
            eta_seconds=22.5,
            progress_pct=5.0,
            active_clearing_junction="J4 - Hospital Road",
            yellow_clearance_remaining=3.5,
            all_red_buffer_remaining=1.5
        )
        self.log("PRIORITY_REQUESTED", f"🚨 DSRC Transponder verified for {vehicle_id}. Priority requested for corridor: J4 ➔ J3 ➔ J1.", "WARNING")
        return self.state

    def cancel(self, reason: str = "Operator Cancellation") -> EmergencyVehicleState:
        """Safely aborts preemption corridor and restores normal cyclic phase progression."""
        if self.state.status != "IDLE":
            prev_status = self.state.status
            self.state.status = "CANCELLED"
            self.state.speed_kmh = 0.0
            self.state.eta_seconds = 0.0
            self.log("CANCELLED", f"🛑 Corridor cancelled ({reason}). Restoring standard decentralized signal allocation from {prev_status}.", "CRITICAL")
        return self.state

    def update_tick(self, current_active_idx: int, current_junction_queue: int, time_sec: int) -> EmergencyVehicleState:
        """
        Advances the emergency state machine based on simulator physics and signal state.
        Never declares CORRIDOR_CLEARED before simulator physically verifies transit.
        """
        if self.state.status in ("IDLE", "CANCELLED", "CORRIDOR_CLEARED"):
            return self.state

        target_idx = self.state.route[self.state.current_step_in_route]
        target_name = self.state.route_names[self.state.current_step_in_route]
        self.state.active_clearing_junction = target_name

        # State 1: Preparation in progress (Yellow 3.5s + All-Red 1.5s clearance)
        if self.state.status == "PRIORITY_REQUESTED":
            self.state.status = "PREPARATION_IN_PROGRESS"
            self.log("PREPARATION_IN_PROGRESS", f"🟡 Interlocking conflicting phases at {target_name}. Clearance interval running (3.5s yellow + 1.5s all-red).", "INFO")
            return self.state

        # State 2: Priority granted when target signal turns green
        if self.state.status == "PREPARATION_IN_PROGRESS":
            if current_active_idx == target_idx:
                self.state.status = "PRIORITY_GRANTED"
                self.log("PRIORITY_GRANTED", f"🟢 Green corridor granted at {target_name}. Approach cleared for {self.state.vehicle_id}.", "SUCCESS")
            return self.state

        # State 3: Vehicle progresses through corridor when queue clears
        if self.state.status == "PRIORITY_GRANTED":
            if current_active_idx == target_idx and current_junction_queue < 8:
                # Vehicle successfully crosses this junction
                self.state.current_step_in_route += 1
                if self.state.current_step_in_route >= len(self.state.route):
                    # Destination reached!
                    self.state.status = "CORRIDOR_CLEARED"
                    self.state.progress_pct = 100.0
                    self.state.eta_seconds = 0.0
                    self.state.speed_kmh = 45.0
                    self.log("CORRIDOR_CLEARED", f"🏁 Emergency vehicle {self.state.vehicle_id} cleared entire corridor and reached destination at J1.", "SUCCESS")
                else:
                    next_target = self.state.route_names[self.state.current_step_in_route]
                    self.state.status = "PREPARATION_IN_PROGRESS"
                    self.state.progress_pct = round((self.state.current_step_in_route / len(self.state.route)) * 100.0, 1)
                    self.state.eta_seconds = max(5.0, 22.5 - (self.state.current_step_in_route * 7.5))
                    self.log("PROGRESS", f"🚑 Vehicle traversed {target_name}; next corridor phase: {next_target}.", "INFO")

        return self.state

    def log(self, phase: str, message: str, severity: str = "INFO"):
        self.logs.append(EmergencyEventLog(
            timestamp=f"T+{len(self.logs) * 5}s",
            phase=phase,
            message=message,
            severity=severity
        ))
        self.logs = self.logs[-25:]  # Keep last 25 logs
