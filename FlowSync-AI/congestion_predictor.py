"""
FlowSync AI — Congestion Prediction Engine (Feature One)
Calculates transparent, bounded congestion risk scores (0-100), classifications
(LOW, MEDIUM, HIGH), horizon queue growth projections (30s, 60s), and evidence attribution.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class CongestionPrediction:
    junction_idx: int
    junction_name: str
    risk_score: float               # 0.0 to 100.0
    risk_level: str                 # "LOW", "MEDIUM", "HIGH"
    current_queue: int
    predicted_queue_30s: int
    predicted_queue_60s: int
    avg_wait_seconds: float
    downstream_occupancy_pct: int
    primary_bottleneck: str
    evidence_breakdown: Dict[str, float]
    recommendation: str

class CongestionPredictor:
    """Predicts congestion accumulation and risk scores across the traffic network."""

    QUEUE_CAPACITY = 45  # Consistent with TrafficNetwork.QUEUE_CAPACITY

    def __init__(self):
        self.history_samples: List[Dict[str, Any]] = []

    def evaluate_junction(
        self,
        junction_idx: int,
        junction_name: str,
        queue_len: int,
        avg_wait: float,
        downstream_occupancy: int,
        arrival_rate_proxy: float = 2.0,
        recent_queue_trend: float = 0.0,
        is_sensor_healthy: bool = True
    ) -> CongestionPrediction:
        """
        Calculates transparent congestion risk score and projected queue growth.
        Handles missing or stale sensor telemetry gracefully.
        """
        # Safe fallback if sensor telemetry is unhealthy or missing
        if not is_sensor_healthy:
            # Fallback heuristic: moderate estimate based on network priors
            queue_len = max(queue_len, 10)
            avg_wait = max(avg_wait, 15.0)

        # 1. Queue Pressure Factor (0 - 40 points)
        # Ratio of current vehicles to physical road storage capacity
        queue_ratio = min(1.0, queue_len / self.QUEUE_CAPACITY)
        score_queue = queue_ratio * 40.0

        # 2. Wait Delay Factor (0 - 25 points)
        # Vehicles idling longer accumulate exponential delay risk
        wait_ratio = min(1.0, avg_wait / 45.0)
        score_wait = wait_ratio * 25.0

        # 3. Downstream Backpressure Factor (0 - 20 points)
        # Blocked downstream links prevent discharge and cause spillback
        downstream_ratio = min(1.0, downstream_occupancy / 100.0)
        score_downstream = downstream_ratio * 20.0

        # 4. Inflow Surge / Momentum Factor (0 - 15 points)
        # Dynamic rate of incoming vehicles relative to discharge potential
        inflow_ratio = min(1.0, (arrival_rate_proxy + max(0.0, recent_queue_trend)) / 4.0)
        score_inflow = inflow_ratio * 15.0

        raw_score = score_queue + score_wait + score_downstream + score_inflow
        risk_score = round(min(100.0, max(0.0, raw_score)), 1)

        # Classification
        if risk_score < 40.0:
            risk_level = "LOW"
        elif risk_score < 70.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Horizon Queue Growth Projections (30s & 60s)
        # 30s = 6 simulation steps of 5s; 60s = 12 simulation steps
        # Effective discharge capacity is reduced if downstream is congested
        discharge_efficiency = 1.0 if downstream_occupancy < 65 else (0.5 if downstream_occupancy < 85 else 0.15)
        net_inflow_per_step = max(-1.0, arrival_rate_proxy - (2.0 * discharge_efficiency))

        proj_30s = int(max(0, min(self.QUEUE_CAPACITY, queue_len + net_inflow_per_step * 6)))
        proj_60s = int(max(0, min(self.QUEUE_CAPACITY, queue_len + net_inflow_per_step * 12)))

        # Primary Bottleneck Attribution
        factors = {
            "Queue Saturation": score_queue,
            "Dwell Delay": score_wait,
            "Downstream Backpressure": score_downstream,
            "Inflow Surge": score_inflow
        }
        primary_bottleneck = max(factors.items(), key=lambda x: x[1])[0]

        # Recommendation Generation
        if risk_level == "HIGH":
            if primary_bottleneck == "Downstream Backpressure":
                recom = "Throttle upstream release; prioritize clearing downstream corridor."
            else:
                recom = "Extend green phase window to flush critical vehicle mass."
        elif risk_level == "MEDIUM":
            recom = "Monitor queue accumulation; prepare dynamic green extension."
        else:
            recom = "Balanced flow; maintain standard cyclic coordination."

        return CongestionPrediction(
            junction_idx=junction_idx,
            junction_name=junction_name,
            risk_score=risk_score,
            risk_level=risk_level,
            current_queue=queue_len,
            predicted_queue_30s=proj_30s,
            predicted_queue_60s=proj_60s,
            avg_wait_seconds=round(avg_wait, 1),
            downstream_occupancy_pct=downstream_occupancy,
            primary_bottleneck=primary_bottleneck,
            evidence_breakdown={
                "Queue Saturation": round(score_queue, 1),
                "Dwell Delay": round(score_wait, 1),
                "Downstream Backpressure": round(score_downstream, 1),
                "Inflow Surge": round(score_inflow, 1)
            },
            recommendation=recom
        )

    def predict_network(
        self,
        snapshot: Dict[str, Any],
        recent_history: Optional[List[Dict[str, Any]]] = None,
        sensor_health_map: Optional[Dict[int, bool]] = None
    ) -> List[CongestionPrediction]:
        """Runs predictions for all junctions in the current snapshot."""
        predictions = []
        junctions = snapshot.get("junctions", [])

        # Calculate recent queue trends if history exists
        trends = [0.0] * len(junctions)
        if recent_history and len(recent_history) >= 2:
            prev_j = recent_history[-2].get("junctions", [])
            if len(prev_j) == len(junctions):
                for i in range(len(junctions)):
                    trends[i] = junctions[i]["vehicles_waiting"] - prev_j[i]["vehicles_waiting"]

        for idx, j_data in enumerate(junctions):
            is_healthy = True if sensor_health_map is None else sensor_health_map.get(idx, True)
            pred = self.evaluate_junction(
                junction_idx=idx,
                junction_name=j_data["name"],
                queue_len=j_data["vehicles_waiting"],
                avg_wait=j_data["avg_wait"],
                downstream_occupancy=j_data["downstream_occupancy"],
                arrival_rate_proxy=2.0 if idx in (0, 2) else 1.2,
                recent_queue_trend=trends[idx],
                is_sensor_healthy=is_healthy
            )
            predictions.append(pred)

        return predictions
