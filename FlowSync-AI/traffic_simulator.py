from dataclasses import dataclass
import random
from collections import deque

JUNCTION_NAMES = ["J1 - North Gate", "J2 - Market Road", "J3 - College Circle", "J4 - Hospital Road"]
# Simplified directed ring: J1 -> J2 -> J4 -> J3 -> J1
NEXT = {0: 1, 1: 3, 3: 2, 2: 0}

@dataclass
class Junction:
    name: str
    queue: deque
    signal: str = "RED"
    green_seconds: int = 20
    avg_wait: float = 0.0
    downstream_occupancy: int = 0
    phase_tick: int = 0

class TrafficNetwork:
    """Small, deterministic-enough traffic simulation for a hackathon demo.

    Each step represents five seconds. Vehicle counts are simulated; they are not
    observations from real roads. The fixed controller and adaptive controller are
    tracked in parallel using the same arrival rate.
    """
    STEP_SECONDS = 5
    QUEUE_CAPACITY = 45

    def __init__(self, seed=7):
        self.rng = random.Random(seed)
        self.time_step = 0
        self.junctions = [Junction(name, deque()) for name in JUNCTION_NAMES]
        self.metrics = {"total_wait": 0.0, "vehicles_served": 0, "stops": 0, "wait_samples": 0}
        self.fixed_metrics = {"total_wait": 0.0, "vehicles_served": 0, "stops": 0, "wait_samples": 0}
        self.fixed_queues = [deque() for _ in range(4)]
        self.emergency_active = False
        self.emergency_route = deque()
        self.emergency_started = False
        self.last_events = []
        self._init_queues()

    def _init_queues(self):
        # Seed a varied initial state so the dashboard is interesting immediately.
        initial = [12, 7, 18, 5]
        for i, count in enumerate(initial):
            for _ in range(count):
                self.junctions[i].queue.append({"wait": self.rng.randint(0, 25), "emergency": False})
                self.fixed_queues[i].append({"wait": self.rng.randint(0, 25)})

    def _calculate_green(self, idx):
        j = self.junctions[idx]
        queue = len(j.queue)
        waiting = sum(v["wait"] for v in j.queue) / max(queue, 1)
        downstream_idx = NEXT[idx]
        occupancy = int(100 * len(self.junctions[downstream_idx].queue) / self.QUEUE_CAPACITY)
        j.downstream_occupancy = min(100, occupancy)
        # Demand combines queue length, average waiting time, and arrivals proxy.
        score = 0.55 * queue + 0.25 * waiting / 5 + 0.20 * max(0, queue - 4)
        # Cooperative penalty when the next junction is close to full.
        score *= max(0.15, 1 - occupancy / 120)
        if self.emergency_active and self.emergency_route and self.emergency_route[0] == idx:
            score += 100
        return max(10, min(45, int(10 + score)))

    def _set_signals(self, manual_override=None):
        green_times = [self._calculate_green(i) for i in range(4)]
        if manual_override == "ALL_RED":
            active_idx = None
        elif isinstance(manual_override, int) and 0 <= manual_override < 4:
            active_idx = manual_override
        elif self.emergency_active and self.emergency_route:
            active_idx = self.emergency_route[0]
        else:
            # Select largest weighted demand, with a rotating tie-breaker.
            active_idx = max(range(4), key=lambda i: (green_times[i], -((i - self.time_step) % 4)))
        for i, j in enumerate(self.junctions):
            j.green_seconds = green_times[i]
            j.signal = "GREEN" if (active_idx is not None and i == active_idx) else "RED"
            j.phase_tick = 0

    def _arrivals(self, demand_multiplier):
        for i in range(4):
            # Traffic arrival rates vary slightly by junction.
            rate = [2, 1, 2, 1][i] * demand_multiplier
            count = int(rate)
            if self.rng.random() < (rate - count):
                count += 1
            for _ in range(count):
                if len(self.junctions[i].queue) < self.QUEUE_CAPACITY:
                    self.junctions[i].queue.append({"wait": 0, "emergency": False})
                if len(self.fixed_queues[i]) < self.QUEUE_CAPACITY:
                    self.fixed_queues[i].append({"wait": 0})

    def _serve(self, demand_multiplier):
        active = next((i for i, j in enumerate(self.junctions) if j.signal == "GREEN"), None)
        if active is not None:
            queue = self.junctions[active].queue
            # Each 5-sec step can clear several vehicles; blocked downstream reduces discharge.
            downstream = NEXT[active]
            occupancy = len(self.junctions[downstream].queue) / self.QUEUE_CAPACITY
            if occupancy < 0.90:
                capacity = 5 if occupancy < 0.65 else 2
                for _ in range(min(capacity, len(queue))):
                    queue.popleft()
                    self.metrics["vehicles_served"] += 1
                    self.metrics["stops"] += 1
        # Fixed controller: fixed cyclic order, one junction green each step.
        fixed_active = self.time_step % 4
        fixed_downstream = NEXT[fixed_active]
        if len(self.fixed_queues[fixed_downstream]) < self.QUEUE_CAPACITY * 0.90:
            for _ in range(min(4, len(self.fixed_queues[fixed_active]))):
                self.fixed_queues[fixed_active].popleft()
                self.fixed_metrics["vehicles_served"] += 1
                self.fixed_metrics["stops"] += 1

    def step(self, demand_multiplier=1.0, request_emergency=False, manual_override=None):
        events = []
        if manual_override == "ALL_RED":
            events.append("🚨 [OVERRIDE-ACTUATOR] Police Intercept: ALL-RED clearance phase locked.")
        elif isinstance(manual_override, int) and 0 <= manual_override < 4:
            events.append(f"👮 [OVERRIDE-ACTUATOR] Operator Manual Hold: {self.junctions[manual_override].name} forced GREEN.")
        elif request_emergency and not self.emergency_started:
            self.emergency_active = True
            self.emergency_started = True
            # Route follows the network ring for a short journey.
            self.emergency_route = deque([3, 2, 0])
            events.append("🚑 [SIREN-PREEMPT] Emergency transponder verified: priority corridor J4 ➔ J3 ➔ J1 locked.")
        self._arrivals(demand_multiplier)
        self._set_signals(manual_override=manual_override)
        self._serve(demand_multiplier)

        # Wait accumulation for vehicles still queued.
        for j in self.junctions:
            for vehicle in j.queue:
                vehicle["wait"] += self.STEP_SECONDS
            if j.queue:
                self.metrics["total_wait"] += sum(v["wait"] for v in j.queue) / len(j.queue)
                self.metrics["wait_samples"] += 1
            j.avg_wait = sum(v["wait"] for v in j.queue) / max(len(j.queue), 1)
        for queue in self.fixed_queues:
            for vehicle in queue:
                vehicle["wait"] += self.STEP_SECONDS
            if queue:
                self.fixed_metrics["total_wait"] += sum(v["wait"] for v in queue) / len(queue)
                self.fixed_metrics["wait_samples"] += 1

        # Emergency vehicle advances when its current junction is green and has cleared.
        if self.emergency_active and self.emergency_route:
            current = self.emergency_route[0]
            if self.junctions[current].signal == "GREEN" and len(self.junctions[current].queue) < 8:
                self.emergency_route.popleft()
                if self.emergency_route:
                    events.append(f"🚑 [CORRIDOR-PROGRESS] Emergency vehicle advanced; next clearance: {self.junctions[self.emergency_route[0]].name}.")
                else:
                    self.emergency_active = False
                    events.append("✅ [CORRIDOR-CLEAR] Emergency vehicle exited grid; returning to decentralized dynamic actuation.")

        self.time_step += 1
        self.last_events = events
        return events

    def snapshot(self):
        junctions = []
        for i, j in enumerate(self.junctions):
            downstream = self.junctions[NEXT[i]]
            junctions.append({
                "name": j.name,
                "signal": j.signal,
                "vehicles_waiting": len(j.queue),
                "avg_wait": round(j.avg_wait, 1),
                "downstream_occupancy": min(100, int(100 * len(downstream.queue) / self.QUEUE_CAPACITY)),
                "green_seconds": j.green_seconds,
            })
        adaptive_wait = self.metrics["total_wait"] / max(self.metrics["wait_samples"], 1)
        fixed_wait = self.fixed_metrics["total_wait"] / max(self.fixed_metrics["wait_samples"], 1)
        return {
            "time_step": self.time_step,
            "time_seconds": self.time_step * self.STEP_SECONDS,
            "junctions": junctions,
            "adaptive_wait": adaptive_wait,
            "fixed_wait": fixed_wait,
        }
