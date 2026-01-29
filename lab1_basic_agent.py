import asyncio
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour


class BasicDisasterAgent(Agent):
    
    class SetupBehaviour(OneShotBehaviour):
        
        async def run(self):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent Setup Initiated")
            print(f"  Agent JID: {self.agent.jid}")
            print(f"  Agent Name: {self.agent.name}")
            print("  Status: ACTIVE")
            print("-" * 50)
    
    class HeartbeatBehaviour(CyclicBehaviour):
        
        def __init__(self, max_iterations=5):
            super().__init__()
            self.counter = 0
            self.max_iterations = max_iterations
        
        async def run(self):
            self.counter += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] Heartbeat #{self.counter} - Agent is operational")
            
            if self.counter >= self.max_iterations:
                print(f"Completed {self.max_iterations} heartbeat cycles")
                await self.agent.stop()
            
            await asyncio.sleep(2)
    
    async def setup(self):
        print("=" * 50)
        print("  DISASTER RESPONSE AGENT - INITIALIZATION")
        print("=" * 50)
        self.add_behaviour(self.SetupBehaviour())
        self.add_behaviour(self.HeartbeatBehaviour(max_iterations=5))


async def main():
    print("#" * 60)
    print("#  DCIT 403 - LAB 1: BASIC SPADE AGENT DEMONSTRATION")
    print("#  Student: Noel Osei-Tutu | ID: 11285438")
    print("#" * 60)
    
    agent = BasicDisasterAgent("disaster_agent_11285438@jabber.fr", "dcit403lab1")
    
    try:
        await agent.start(auto_register=True)
        print("Agent started successfully!")
        while agent.is_alive():
            await asyncio.sleep(1)
    finally:
        if agent.is_alive():
            await agent.stop()
        print("AGENT TERMINATED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(main())
