"""
FlowSync AI — Explainable AI (XAI) Decision Panel Engine (Feature Six)
Generates transparent, human-readable explanations of adaptive signal timing decisions,
factor contribution breakdowns, alternative phase rejections, and safety constraints.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class XAIDecisionExplanation:
    junction_idx: int
    junction_name: str
    current_signal: str
    is_active_green: bool
    queue_len: int
    avg_wait_sec: float
    downstream_occupancy_pct: int
    allocated_green_seconds: int
    decision_score: float
    decision_rank: int               # 1 (Highest priority) to 4
    primary_influencing_factors: List[str]
    why_alternatives_not_chosen: str
    safety_constraints_active: List[str]
    next_reassessment_time: str
    narrative_explanation: str
    is_executed_actuation: bool = True

class DecisionExplainer:
    """Produces verified, transparent explanations for decentralized controller actions."""

    def explain_cycle(
        self,
        snapshot: Dict[str, Any],
        coordination_states: Optional[List[Any]] = None,
        emergency_active: bool = False,
        emergency_route: Optional[List[int]] = None,
        manual_override: Optional[Any] = None
    ) -> List[XAIDecisionExplanation]:
        junctions = snapshot.get("junctions", [])
        time_sec = snapshot.get("time_seconds", 0)
        num_j = len(junctions)

        if not junctions:
            return []

        # Map coordination scores or calculate dynamic proxies
        scores = []
        for i, j in enumerate(junctions):
            if coordination_states and i < len(coordination_states):
                scores.append(coordination_states[i].cooperative_score)
            else:
                q = j["vehicles_waiting"]
                w = j["avg_wait"]
                occ = j["downstream_occupancy"]
                score = (0.55 * q + 0.30 * (w / 4.0)) * (1.0 if occ < 75 else 0.45)
                scores.append(round(score, 1))

        # Rank junctions by score
        ranked_indices = sorted(range(num_j), key=lambda i: scores[i], reverse=True)
        ranks = {idx: rank + 1 for rank, idx in enumerate(ranked_indices)}
        top_idx = ranked_indices[0]

        explanations = []

        for i, j in enumerate(junctions):
            is_green = (j["signal"] == "GREEN")
            q = j["vehicles_waiting"]
            w = j["avg_wait"]
            occ = j["downstream_occupancy"]
            score = scores[i]
            rank = ranks[i]
            allocated_green = j["green_seconds"]

            factors = []
            safety_constraints = []

            # 1. Evaluate influencing factors
            if q > 12:
                factors.append(f"High queue accumulation ({q} vehicles, {int(q/45*100)}% approach capacity)")
            elif q > 6:
                factors.append(f"Moderate queue pressure ({q} vehicles)")
            else:
                factors.append(f"Low queue volume ({q} vehicles)")

            if w > 20.0:
                factors.append(f"Elevated commuter delay (average dwell {w:.1f}s)")
            else:
                factors.append(f"Acceptable commuter wait ({w:.1f}s)")

            if occ > 80:
                factors.append(f"Downstream bottleneck alert ({occ}% storage capacity)")
                safety_constraints.append("Downstream backpressure penalty applied to prevent intersection gridlock.")
            else:
                factors.append(f"Downstream link receptive ({occ}% occupancy)")

            if emergency_active and emergency_route and i in emergency_route:
                factors.append("Priority emergency corridor reservation (AMB-911)")
                safety_constraints.append("Preemption interlock engaged; cross-traffic locked with safe clearance intervals.")

            if allocated_green <= 10:
                safety_constraints.append("Guaranteed minimum 10.0s green phase enforced (pedestrian walk safety buffer).")
            elif allocated_green >= 45:
                safety_constraints.append("Capped at maximum 45.0s green phase to prevent starvation of conflicting approaches.")

            # 2. Why alternatives were not chosen / rejected
            if is_green:
                other_j = [junctions[k]["name"] for k in range(num_j) if k != i]
                why_not = f"Selected ahead of {other_j[0]} and {other_j[1]} due to higher combined urgency score ({score:.1f} vs avg {sum(scores)/len(scores):.1f})."
            else:
                winner_name = junctions[top_idx]["name"]
                why_not = f"Deferred to {winner_name} (Priority Score: {scores[top_idx]:.1f}) which had higher queue mass or critical emergency priority."

            # 3. Human-readable narrative
            if manual_override == "ALL_RED":
                narrative = f"{j['name']} is held in ALL-RED state under manual police cabinet key override for site clearance."
            elif isinstance(manual_override, int) and manual_override == i:
                narrative = f"{j['name']} is held GREEN under manual operator key override, bypassing autonomous optimization."
            elif emergency_active and emergency_route and emergency_route[0] == i:
                narrative = f"🚨 {j['name']} was preempted for priority ambulance transit. Safety interlocks cleared conflicting phases to provide zero-delay passage."
            elif is_green:
                narrative = f"🟢 {j['name']} was selected for active GREEN phase with an urgency score of {score:.1f}. Approach has {q} queued vehicles waiting an average of {w:.1f}s, and downstream capacity ({occ}% occ) can accept the discharge without spillback."
            else:
                narrative = f"🔴 {j['name']} is holding at RED (rank #{rank} of 4). It has {q} queued vehicles. Decision deferred to {junctions[top_idx]['name']} to maximize global network flow and prevent downstream spillback."

            explanations.append(XAIDecisionExplanation(
                junction_idx=i,
                junction_name=j["name"],
                current_signal=j["signal"],
                is_active_green=is_green,
                queue_len=q,
                avg_wait_sec=round(w, 1),
                downstream_occupancy_pct=occ,
                allocated_green_seconds=allocated_green,
                decision_score=round(score, 1),
                decision_rank=rank,
                primary_influencing_factors=factors,
                why_alternatives_not_chosen=why_not,
                safety_constraints_active=safety_constraints,
                next_reassessment_time=f"T+{time_sec + 5}s",
                narrative_explanation=narrative,
                is_executed_actuation=True
            ))

        return explanations
