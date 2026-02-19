import asyncio
import random
import time
from enum import Enum
from datetime import datetime


class DisasterType(Enum):
    NONE = "None"
    FLOOD = "Flood"
    EARTHQUAKE = "Earthquake"
    FIRE = "Fire"
    LANDSLIDE = "Landslide"


class SeverityLevel(Enum):
    NONE = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4


STATE_IDLE = "IDLE"
STATE_ALERT = "ALERT_RECEIVED"
STATE_ASSESSING = "ASSESSING"
STATE_RESPONDING = "RESPONDING"
STATE_COMPLETING = "COMPLETING"

VALID_TRANSITIONS = {
    STATE_IDLE: [STATE_ALERT],
    STATE_ALERT: [STATE_ASSESSING, STATE_IDLE],
    STATE_ASSESSING: [STATE_RESPONDING, STATE_IDLE],
    STATE_RESPONDING: [STATE_COMPLETING],
    STATE_COMPLETING: [STATE_IDLE],
}


class DisasterEnvironment:
    def __init__(self):
        self.zones = {
            "Zone-A": {"name": "Residential District", "base_risk": 0.3},
            "Zone-B": {"name": "Commercial Hub", "base_risk": 0.25},
            "Zone-C": {"name": "Industrial Area", "base_risk": 0.35},
            "Zone-D": {"name": "Coastal Region", "base_risk": 0.4},
            "Zone-E": {"name": "Highland Sector", "base_risk": 0.2},
        }
        self.active_disasters = {}

    def generate_event(self):
        zone_id = random.choice(list(self.zones.keys()))
        zone = self.zones[zone_id]

        if random.random() < zone["base_risk"]:
            disaster = random.choice(
                [DisasterType.FLOOD, DisasterType.EARTHQUAKE, DisasterType.FIRE, DisasterType.LANDSLIDE]
            )
            severity = random.choice(
                [SeverityLevel.LOW, SeverityLevel.MODERATE, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
            )
            event = {
                "zone": zone_id,
                "zone_name": zone["name"],
                "disaster_type": disaster,
                "severity": severity,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "temperature": round(random.uniform(25, 60) if disaster == DisasterType.FIRE else random.uniform(20, 32), 1),
                "water_level": round(random.uniform(4, 10) if disaster == DisasterType.FLOOD else random.uniform(0.5, 2), 2),
                "seismic": round(random.uniform(3.0, 7.5) if disaster == DisasterType.EARTHQUAKE else random.uniform(0, 0.5), 1),
            }
            self.active_disasters[zone_id] = event
            return event
        return None


class RescueGoal:
    def __init__(self, goal_type, priority, target_zone, disaster_event):
        self.goal_type = goal_type
        self.priority = priority
        self.target_zone = target_zone
        self.disaster_event = disaster_event
        self.status = "PENDING"
        self.created_at = datetime.now().strftime("%H:%M:%S")

    def __repr__(self):
        return f"Goal({self.goal_type}, {self.priority}, {self.target_zone}, {self.status})"


class RescueAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.current_state = STATE_IDLE
        self.goals = []
        self.active_goal = None
        self.state_history = [(STATE_IDLE, datetime.now().strftime("%H:%M:%S"), "Agent initialized")]
        self.completed_missions = 0
        self.execution_log = []

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{self.agent_id}] [{self.current_state}] {message}"
        self.execution_log.append(entry)
        print(entry)

    def transition_to(self, new_state, reason=""):
        if new_state not in VALID_TRANSITIONS.get(self.current_state, []):
            self.log(f"INVALID TRANSITION: {self.current_state} -> {new_state}")
            return False
        old_state = self.current_state
        self.current_state = new_state
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.state_history.append((new_state, timestamp, reason))
        self.log(f"Transition: {old_state} -> {new_state} | {reason}")
        return True

    def receive_alert(self, event):
        if event is None:
            return

        severity = event["severity"]
        disaster = event["disaster_type"]
        zone = event["zone"]

        goal_type = self._determine_goal(disaster)
        priority = severity.value

        goal = RescueGoal(goal_type, priority, zone, event)
        self.goals.append(goal)
        self.log(f"New goal created: {goal_type} in {zone} (Severity: {severity.name})")

        if self.current_state == STATE_IDLE:
            self.transition_to(STATE_ALERT, f"Disaster alert: {disaster.value} in {zone}")

    def _determine_goal(self, disaster_type):
        goal_map = {
            DisasterType.FLOOD: "EVACUATE_AND_RESCUE",
            DisasterType.EARTHQUAKE: "SEARCH_AND_RESCUE",
            DisasterType.FIRE: "FIRE_SUPPRESSION_AND_RESCUE",
            DisasterType.LANDSLIDE: "DEBRIS_CLEARANCE_AND_RESCUE",
        }
        return goal_map.get(disaster_type, "GENERAL_RESCUE")

    def assess_situation(self):
        if not self.goals:
            self.transition_to(STATE_IDLE, "No pending goals")
            return

        self.goals.sort(key=lambda g: g.priority, reverse=True)
        self.active_goal = self.goals.pop(0)
        self.active_goal.status = "ACTIVE"

        event = self.active_goal.disaster_event
        self.log(
            f"Assessing: {self.active_goal.goal_type} | "
            f"Zone: {event['zone']} ({event['zone_name']}) | "
            f"Severity: {event['severity'].name} | "
            f"Temp: {event['temperature']}C | Water: {event['water_level']}m | Seismic: {event['seismic']}"
        )
        self.transition_to(STATE_ASSESSING, f"Assessing {self.active_goal.goal_type}")

    def execute_response(self):
        if self.active_goal is None:
            return

        self.transition_to(STATE_RESPONDING, f"Executing {self.active_goal.goal_type}")
        event = self.active_goal.disaster_event
        disaster = event["disaster_type"]
        severity = event["severity"]

        actions = self._get_response_actions(disaster, severity)
        for action in actions:
            self.log(f"  ACTION: {action}")
            time.sleep(0.3)

    def _get_response_actions(self, disaster, severity):
        base_actions = {
            DisasterType.FLOOD: [
                "Deploying water rescue boats",
                "Activating flood barriers",
                "Evacuating residents to higher ground",
            ],
            DisasterType.EARTHQUAKE: [
                "Deploying seismic rescue units",
                "Scanning collapsed structures",
                "Setting up triage stations",
            ],
            DisasterType.FIRE: [
                "Dispatching fire suppression units",
                "Establishing firebreaks",
                "Evacuating affected buildings",
            ],
            DisasterType.LANDSLIDE: [
                "Deploying heavy debris removal equipment",
                "Scanning for buried survivors",
                "Securing unstable terrain",
            ],
        }

        actions = base_actions.get(disaster, ["Initiating general rescue protocol"])
        if severity.value >= SeverityLevel.HIGH.value:
            actions.append("Requesting additional backup units")
            actions.append("Alerting medical emergency teams")
        if severity == SeverityLevel.CRITICAL:
            actions.append("Declaring zone-wide emergency evacuation")

        return actions

    def complete_mission(self):
        if self.active_goal:
            self.active_goal.status = "COMPLETED"
            self.completed_missions += 1
            self.log(f"Mission completed: {self.active_goal.goal_type} in {self.active_goal.target_zone}")
            self.transition_to(STATE_COMPLETING, "Mission wrap-up")
            self.active_goal = None
            self.transition_to(STATE_IDLE, "Ready for next assignment")

    def run_fsm_cycle(self):
        if self.current_state == STATE_IDLE:
            return
        elif self.current_state == STATE_ALERT:
            self.assess_situation()
        elif self.current_state == STATE_ASSESSING:
            self.execute_response()
        elif self.current_state == STATE_RESPONDING:
            self.complete_mission()


class SensorAgent:
    def __init__(self, environment):
        self.environment = environment
        self.scan_count = 0

    def scan(self):
        self.scan_count += 1
        event = self.environment.generate_event()
        if event:
            print(
                f"\n[SENSOR] Scan #{self.scan_count} | DISASTER DETECTED: "
                f"{event['disaster_type'].value} in {event['zone']} "
                f"({event['zone_name']}) | Severity: {event['severity'].name}"
            )
        else:
            print(f"\n[SENSOR] Scan #{self.scan_count} | No disaster detected")
        return event


def run_simulation():
    print("=" * 70)
    print("  DCIT 403 - LAB 3: GOALS, EVENTS, AND REACTIVE BEHAVIOR")
    print("  Student: Noel Osei-Tutu | ID: 11285438")
    print("  Disaster Response - FSM-Based Rescue Agent")
    print("=" * 70)

    env = DisasterEnvironment()
    sensor = SensorAgent(env)
    rescue = RescueAgent("RescueAgent-01")

    print("\n--- FSM States ---")
    print(f"States: {STATE_IDLE} -> {STATE_ALERT} -> {STATE_ASSESSING} -> {STATE_RESPONDING} -> {STATE_COMPLETING} -> {STATE_IDLE}")
    print(f"Valid transitions: {VALID_TRANSITIONS}")
    print()

    num_cycles = 8
    for cycle in range(1, num_cycles + 1):
        print(f"\n{'─' * 60}")
        print(f"  SIMULATION CYCLE {cycle}/{num_cycles}")
        print(f"{'─' * 60}")

        event = sensor.scan()
        rescue.receive_alert(event)

        while rescue.current_state != STATE_IDLE:
            rescue.run_fsm_cycle()
            time.sleep(0.2)

        time.sleep(0.5)

    print(f"\n{'=' * 70}")
    print("  SIMULATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total scans: {sensor.scan_count}")
    print(f"  Missions completed: {rescue.completed_missions}")
    print(f"  State transitions: {len(rescue.state_history)}")
    print()
    print("  STATE TRANSITION HISTORY:")
    for state, ts, reason in rescue.state_history:
        print(f"    [{ts}] {state:15s} | {reason}")
    print(f"{'=' * 70}")

    return rescue, sensor


if __name__ == "__main__":
    rescue_agent, sensor_agent = run_simulation()
