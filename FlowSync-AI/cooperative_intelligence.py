"""
FlowSync AI — Cooperative Junction Intelligence Engine (Feature Two)
Coordinates connected junctions (J1 -> J2 -> J4 -> J3 -> J1) using decentralized
Max-Weight pressure balancing, downstream spillback suppression, and starvation-free fairness.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

# Topology: 0: J1, 1: J2, 2: J3, 3: J4
NEXT_JUNCTION = {0: 1, 1: 3, 3: 2, 2: 0}
PREV_JUNCTION = {1: 0, 3: 1, 2: 3, 0: 2}

@dataclass
class CooperativeMessage:
    sender_idx: int
    sender_name: str
    receiver_idx: int
    receiver_name: str
    msg_type: str                   # "BACKPRESSURE_WARN", "CLEARANCE_REQ", "GREEN_WAVE_TOKEN"
    content: str
    severity: str                   # "INFO", "WARNING", "ALERT"
    timestamp: str

@dataclass
class JunctionCoordinationState:
    junction_idx: int
    name: str
    local_queue: int
    downstream_idx: int
    downstream_name: str
    downstream_occupancy_pct: int
    consecutive_red_cycles: int     # Fairness tracker
    starvation_boost: float
    cooperative_score: float
    recommended_green_seconds: int
    reasoning: str
    safety_constraints_applied: List[str] = field(default_factory=list)

class CooperativeController:
    """Cooperative decision engine for distributed traffic intersection network."""

    MIN_GREEN = 10
    MAX_GREEN = 45
    QUEUE_CAPACITY = 45

    def __init__(self):
        self.consecutive_red = [0, 0, 0, 0]
        self.message_bus: List[CooperativeMessage] = []

    def evaluate_cooperation(
        self,
        snapshot: Dict[str, Any],
        emergency_active: bool = False,
        emergency_route: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates network state, applies backpressure penalties, prevents starvation,
        generates inter-junction DSRC messages, and recommends the optimal coordinated phase.
        """
        junctions = snapshot.get("junctions", [])
        num_j = len(junctions)
        if num_j != 4:
            return {"recommended_idx": 0, "states": [], "messages": []}

        states: List[JunctionCoordinationState] = []
        new_messages: List[CooperativeMessage] = []
        time_sec = snapshot.get("time_seconds", 0)

        for i, j in enumerate(junctions):
            downstream_i = NEXT_JUNCTION[i]
            downstream_j = junctions[downstream_i]
            downstream_occ = downstream_j["downstream_occupancy"]

            # Starvation prevention: if an approach waits multiple cycles, ramp its fairness boost
            red_count = self.consecutive_red[i]
            starve_boost = 0.0
            if red_count >= 2:
                starve_boost = (red_count - 1) * 6.5

            # 1. Base Demand: Queue mass + Dwell wait time
            q_mass = j["vehicles_waiting"]
            w_time = j["avg_wait"]
            base_demand = 0.55 * q_mass + 0.30 * (w_time / 4.0) + starve_boost

            # 2. Downstream Spillback Penalty (Decentralized Backpressure)
            # When downstream storage exceeds 75%, heavily penalize releasing more vehicles
            safety_notes = []
            if downstream_occ > 80:
                coop_penalty = 0.35  # Throttle to 35% of demand
                safety_notes.append(f"Downstream {downstream_j['name']} is at {downstream_occ}% capacity; throttled to avoid gridlock spillback.")
                new_messages.append(CooperativeMessage(
                    sender_idx=downstream_i,
                    sender_name=downstream_j["name"],
                    receiver_idx=i,
                    receiver_name=j["name"],
                    msg_type="BACKPRESSURE_WARN",
                    content=f"Approach saturated ({downstream_occ}%). Throttle upstream discharge.",
                    severity="WARNING",
                    timestamp=f"T+{time_sec}s"
                ))
            elif downstream_occ > 60:
                coop_penalty = 0.70
                safety_notes.append(f"Downstream occupancy ({downstream_occ}%) moderating discharge.")
            else:
                coop_penalty = 1.05  # Downstream is clear; bonus to create continuous green wave
                if q_mass >= 10:
                    new_messages.append(CooperativeMessage(
                        sender_idx=i,
                        sender_name=j["name"],
                        receiver_idx=downstream_i,
                        receiver_name=downstream_j["name"],
                        msg_type="GREEN_WAVE_TOKEN",
                        content=f"Releasing platoon ({q_mass} veh). Reserve downstream receiving phase.",
                        severity="INFO",
                        timestamp=f"T+{time_sec}s"
                    ))

            score = base_demand * coop_penalty

            # Emergency Priority Override
            if emergency_active and emergency_route and emergency_route[0] == i:
                score += 150.0
                safety_notes.append("Emergency priority transponder verified; absolute right-of-way assigned.")

            # Enforce safety limits on green time
            recommended_green = max(self.MIN_GREEN, min(self.MAX_GREEN, int(10 + score * 0.75)))
            if recommended_green == self.MIN_GREEN:
                safety_notes.append(f"Enforced minimum green safety window ({self.MIN_GREEN}s).")
            elif recommended_green == self.MAX_GREEN:
                safety_notes.append(f"Capped at maximum green phase ({self.MAX_GREEN}s) to prevent cross-street starvation.")

            # Construct natural-language reasoning
            if emergency_active and emergency_route and emergency_route[0] == i:
                reasoning = f"Emergency corridor active on {j['name']}. Immediate preemption."
            elif starve_boost > 0:
                reasoning = f"Starvation prevention engaged for {j['name']} (idle for {red_count} cycles, queue: {q_mass})."
            elif downstream_occ > 80:
                reasoning = f"{j['name']} has {q_mass} queued, but downstream {downstream_j['name']} is congested ({downstream_occ}%). Discharge throttled."
            else:
                reasoning = f"{j['name']} selected with {q_mass} queued (avg wait {w_time:.1f}s) and clear downstream link ({downstream_occ}% occ)."

            states.append(JunctionCoordinationState(
                junction_idx=i,
                name=j["name"],
                local_queue=q_mass,
                downstream_idx=downstream_i,
                downstream_name=downstream_j["name"],
                downstream_occupancy_pct=downstream_occ,
                consecutive_red_cycles=red_count,
                starvation_boost=round(starve_boost, 1),
                cooperative_score=round(score, 1),
                recommended_green_seconds=recommended_green,
                reasoning=reasoning,
                safety_constraints_applied=safety_notes
            ))

        # Select highest-scoring junction for active phase
        recommended_idx = max(range(num_j), key=lambda idx: states[idx].cooperative_score)

        # Update fairness counters
        for idx in range(num_j):
            if idx == recommended_idx:
                self.consecutive_red[idx] = 0
            else:
                self.consecutive_red[idx] += 1

        self.message_bus.extend(new_messages)
        self.message_bus = self.message_bus[-30:]  # Keep last 30 messages in bus

        return {
            "recommended_idx": recommended_idx,
            "recommended_name": junctions[recommended_idx]["name"],
            "states": states,
            "messages": self.message_bus
        }
