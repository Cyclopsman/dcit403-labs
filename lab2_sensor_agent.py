import asyncio
import random
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, OneShotBehaviour


class DisasterType(Enum):
    FLOOD = "Flood"
    EARTHQUAKE = "Earthquake"
    FIRE = "Fire"
    LANDSLIDE = "Landslide"
    NONE = "None"


class SeverityLevel(Enum):
    NONE = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class EnvironmentPercept:
    timestamp: str
    location: str
    disaster_type: DisasterType
    severity: SeverityLevel
    temperature: float
    humidity: float
    water_level: float
    seismic_activity: float


class DisasterEnvironment:
    
    def __init__(self):
        self.locations = ["Zone-A (Residential)", "Zone-B (Commercial)",
            "Zone-C (Industrial)", "Zone-D (Coastal)", "Zone-E (Highland)"]
        self.base_temperature = 28.0
        self.base_humidity = 65.0
        self.base_water_level = 2.0
        self.base_seismic = 0.1
        self.event_log = []
    
    def generate_percept(self):
        location = random.choice(self.locations)
        disaster_roll = random.random()
        
        if disaster_roll < 0.15:
            disaster_type = DisasterType.FLOOD
            severity = random.choice([SeverityLevel.LOW, SeverityLevel.MODERATE, SeverityLevel.HIGH])
            water_level = self.base_water_level + random.uniform(3.0, 10.0)
            seismic = self.base_seismic + random.uniform(0, 0.2)
        elif disaster_roll < 0.25:
            disaster_type = DisasterType.EARTHQUAKE
            severity = random.choice([SeverityLevel.MODERATE, SeverityLevel.HIGH, SeverityLevel.CRITICAL])
            water_level = self.base_water_level + random.uniform(-0.5, 0.5)
            seismic = random.uniform(3.0, 7.5)
        elif disaster_roll < 0.35:
            disaster_type = DisasterType.FIRE
            severity = random.choice([SeverityLevel.LOW, SeverityLevel.MODERATE, SeverityLevel.HIGH])
            water_level = self.base_water_level + random.uniform(-1.0, 0)
            seismic = self.base_seismic + random.uniform(0, 0.1)
        elif disaster_roll < 0.40:
            disaster_type = DisasterType.LANDSLIDE
            severity = random.choice([SeverityLevel.MODERATE, SeverityLevel.HIGH])
            water_level = self.base_water_level + random.uniform(1.0, 3.0)
            seismic = random.uniform(1.0, 3.0)
        else:
            disaster_type = DisasterType.NONE
            severity = SeverityLevel.NONE
            water_level = self.base_water_level + random.uniform(-0.5, 0.5)
            seismic = self.base_seismic + random.uniform(-0.05, 0.1)
        
        if disaster_type == DisasterType.FIRE:
            temperature = self.base_temperature + random.uniform(15.0, 35.0)
            humidity = self.base_humidity - random.uniform(20.0, 40.0)
        elif disaster_type == DisasterType.FLOOD:
            temperature = self.base_temperature + random.uniform(-5.0, 5.0)
            humidity = self.base_humidity + random.uniform(15.0, 30.0)
        else:
            temperature = self.base_temperature + random.uniform(-3.0, 5.0)
            humidity = self.base_humidity + random.uniform(-10.0, 10.0)
        
        percept = EnvironmentPercept(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), location=location,
            disaster_type=disaster_type, severity=severity,
            temperature=round(temperature, 1), humidity=round(max(0, min(100, humidity)), 1),
            water_level=round(max(0, water_level), 2), seismic_activity=round(max(0, seismic), 2))
        self.event_log.append(percept)
        return percept


class SensorAgent(Agent):
    
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment
        self.percepts_collected = []
    
    class InitBehaviour(OneShotBehaviour):
        async def run(self):
            print("=" * 60)
            print("  SENSOR AGENT INITIALIZED")
            print("=" * 60)
            print(f"  Agent JID: {self.agent.jid}")
            print(f"  Monitoring Zones: 5")
            print(f"  Scan Interval: 3 seconds")
            print("=" * 60)
    
    class MonitorBehaviour(PeriodicBehaviour):
        def __init__(self, period, max_scans=10):
            super().__init__(period)
            self.scan_count = 0
            self.max_scans = max_scans
        
        async def run(self):
            self.scan_count += 1
            percept = self.agent.environment.generate_percept()
            self.agent.percepts_collected.append(percept)
            
            print(f"[SCAN #{self.scan_count}] {percept.timestamp}")
            print(f"  Location: {percept.location}")
            
            if percept.disaster_type != DisasterType.NONE:
                print(f"  >>> DISASTER DETECTED: {percept.disaster_type.value} <<<")
                print(f"  >>> Severity: {percept.severity.name} <<<")
            else:
                print(f"  Status: Normal conditions")
            
            print(f"  Temperature: {percept.temperature}C | Humidity: {percept.humidity}%")
            print(f"  Water Level: {percept.water_level}m | Seismic: {percept.seismic_activity}")
            
            if self.scan_count >= self.max_scans:
                self.generate_summary()
                await self.agent.stop()
        
        def generate_summary(self):
            percepts = self.agent.percepts_collected
            disasters = [p for p in percepts if p.disaster_type != DisasterType.NONE]
            print("\n  MONITORING SESSION COMPLETE")
            print(f"  Total Scans: {len(percepts)} | Disasters Detected: {len(disasters)}")
    
    async def setup(self):
        self.add_behaviour(self.InitBehaviour())
        self.add_behaviour(self.MonitorBehaviour(period=3, max_scans=10))


async def main():
    print("#" * 60)
    print("#  DCIT 403 - LAB 2: PERCEPTION AND ENVIRONMENT MODELING")
    print("#  Student: Noel Osei-Tutu | ID: 11285438")
    print("#" * 60)
    
    environment = DisasterEnvironment()
    sensor_agent = SensorAgent("sensor_agent_11285438@jabber.fr", "dcit403lab2", environment)
    
    await sensor_agent.start(auto_register=True)
    while sensor_agent.is_alive():
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
