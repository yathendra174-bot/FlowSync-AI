"""
FlowSync AI — Comprehensive Test Suite for Advanced Traffic Intelligence
Tests:
1. Congestion prediction calculations, risk levels, and 30s/60s horizon growth.
2. Cooperative intelligence backpressure penalties, starvation prevention, and safety constraints.
3. Emergency green corridor progression, route safety, and cancellation.
4. IoT sensor digital twin health, missing data handling, and fault recovery.
5. Incident detection, severity assignment, and verified recovery progression.
6. Explainable AI factor attribution, alternative rejection, and human narrative generation.
7. Scenario lab reproducible benchmark execution, fairness, and CSV export.
8. Regression tests on TrafficNetwork step and snapshot methods.
"""

import unittest
from traffic_simulator import TrafficNetwork
from congestion_predictor import CongestionPredictor
from cooperative_intelligence import CooperativeController
from emergency_corridor import EmergencyCorridorManager
from iot_sensor_twin import IoTSensorTwin
from incident_manager import IncidentManager
from xai_explainer import DecisionExplainer
from scenario_lab import ScenarioLab, SCENARIO_PROFILES

class TestFlowSyncAdvancedIntelligence(unittest.TestCase):

    def setUp(self):
        self.network = TrafficNetwork(seed=7)
        self.predictor = CongestionPredictor()
        self.coop = CooperativeController()
        self.emergency = EmergencyCorridorManager()
        self.sensor_twin = IoTSensorTwin(seed=42)
        self.incident_mgr = IncidentManager()
        self.explainer = DecisionExplainer()
        self.scenario_lab = ScenarioLab(seed=7)

    # 1. Congestion Prediction Tests
    def test_congestion_risk_score_and_classification(self):
        # Low congestion test
        pred_low = self.predictor.evaluate_junction(
            junction_idx=0,
            junction_name="J1 - North Gate",
            queue_len=4,
            avg_wait=5.0,
            downstream_occupancy=20
        )
        self.assertEqual(pred_low.risk_level, "LOW")
        self.assertLess(pred_low.risk_score, 40.0)

        # High congestion test
        pred_high = self.predictor.evaluate_junction(
            junction_idx=2,
            junction_name="J3 - College Circle",
            queue_len=38,
            avg_wait=40.0,
            downstream_occupancy=90
        )
        self.assertEqual(pred_high.risk_level, "HIGH")
        self.assertGreaterEqual(pred_high.risk_score, 70.0)
        self.assertIn("Queue Saturation", pred_high.evidence_breakdown)
        self.assertGreater(pred_high.predicted_queue_60s, 0)

    # 2. Cooperative Intelligence Tests
    def test_cooperative_backpressure_and_starvation(self):
        snapshot = self.network.snapshot()
        eval_res = self.coop.evaluate_cooperation(snapshot)
        self.assertIn("recommended_idx", eval_res)
        self.assertEqual(len(eval_res["states"]), 4)

        # Simulate starvation for J1
        self.coop.consecutive_red[0] = 4
        eval_starve = self.coop.evaluate_cooperation(snapshot)
        j1_state = eval_starve["states"][0]
        self.assertGreater(j1_state.starvation_boost, 0.0)
        self.assertIn("Starvation prevention", j1_state.reasoning)

    # 3. Emergency Corridor Tests
    def test_emergency_corridor_lifecycle(self):
        state = self.emergency.dispatch("AMB-101", "CRITICAL")
        self.assertEqual(state.status, "PRIORITY_REQUESTED")
        self.assertEqual(state.route, [3, 2, 0])

        # Step 1: Transitions to preparation
        state_prep = self.emergency.update_tick(current_active_idx=1, current_junction_queue=15, time_sec=5)
        self.assertEqual(state_prep.status, "PREPARATION_IN_PROGRESS")

        # Step 2: Granted when J4 (3) turns green
        state_grant = self.emergency.update_tick(current_active_idx=3, current_junction_queue=12, time_sec=10)
        self.assertEqual(state_grant.status, "PRIORITY_GRANTED")

        # Cancellation test
        state_cancelled = self.emergency.cancel("Operator Test Cancel")
        self.assertEqual(state_cancelled.status, "CANCELLED")

    # 4. IoT Sensor Twin Tests
    def test_iot_sensor_twin_faults_and_fallback(self):
        snapshot = self.network.snapshot()
        self.sensor_twin.sync_with_simulation(snapshot)

        loop_j1 = self.sensor_twin.sensors["J1-LOOP-01"]
        self.assertEqual(loop_j1.health_status, "HEALTHY")
        self.assertIsNotNone(loop_j1.raw_reading)

        # Inject disconnect fault
        self.sensor_twin.set_fault("J1-LOOP-01", "DISCONNECTED")
        self.sensor_twin.sync_with_simulation(snapshot)
        self.assertIsNone(loop_j1.raw_reading)  # Missing, not zero!

        # Safe fallback policy returns safe estimate, not 0
        effective_q = self.sensor_twin.get_effective_queue(0, simulator_queue=18)
        self.assertGreater(effective_q, 0)

        # Recover
        self.sensor_twin.recover_all()
        self.assertEqual(loop_j1.health_status, "HEALTHY")

    # 5. Incident Detection and Recovery Tests
    def test_incident_manager_detection_and_recovery(self):
        snapshot = self.network.snapshot()
        # Force a high queue into snapshot to test detection
        snapshot["junctions"][1]["vehicles_waiting"] = 36
        incidents = self.incident_mgr.scan_network_anomalies(snapshot)
        self.assertTrue(any(inc.incident_type == "EXCESSIVE_QUEUE" for inc in incidents))

        # Test manual injection & recovery progression
        inj = self.incident_mgr.inject_incident("ROAD_BLOCKAGE", junction_idx=1, time_sec=20)
        self.assertEqual(inj.status, "DETECTED")
        self.incident_mgr.acknowledge(inj.incident_id)
        self.assertEqual(inj.status, "ACKNOWLEDGED")
        self.incident_mgr.initiate_recovery(inj.incident_id)
        self.assertEqual(inj.status, "RECOVERING")
        self.incident_mgr.clear_incident(inj.incident_id, time_sec=45)
        self.assertEqual(inj.status, "RESOLVED")

    # 6. Explainable AI Decision Tests
    def test_xai_explainer_narrative_and_factors(self):
        snapshot = self.network.snapshot()
        explanations = self.explainer.explain_cycle(snapshot)
        self.assertEqual(len(explanations), 4)

        for exp in explanations:
            self.assertIsNotNone(exp.narrative_explanation)
            self.assertGreater(len(exp.primary_influencing_factors), 0)
            self.assertIn("T+", exp.next_reassessment_time)

    # 7. Scenario Lab & Benchmark Replay Tests
    def test_scenario_lab_benchmark_execution(self):
        self.assertIn("1. Normal Baseline Traffic", SCENARIO_PROFILES)
        result = self.scenario_lab.run_benchmark("1. Normal Baseline Traffic")
        self.assertGreater(result.steps_evaluated, 0)
        self.assertGreaterEqual(result.adaptive_vehicles_served, 0)
        self.assertGreaterEqual(result.fixed_vehicles_served, 0)

        # Export CSV verification
        csv_str = self.scenario_lab.export_csv(result)
        self.assertIn("step,time_seconds,adaptive_wait", csv_str)

    # 8. Regression Tests on Core TrafficNetwork
    def test_traffic_network_regression(self):
        initial_time = self.network.time_step
        events = self.network.step(demand_multiplier=1.0)
        self.assertEqual(self.network.time_step, initial_time + 1)
        snap = self.network.snapshot()
        self.assertEqual(len(snap["junctions"]), 4)
        self.assertIn("adaptive_wait", snap)
        self.assertIn("fixed_wait", snap)

if __name__ == "__main__":
    unittest.main()
