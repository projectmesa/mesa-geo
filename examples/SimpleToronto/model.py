from mesa.datacollection import DataCollector
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
import random


class PersonAgent(GeoAgent):
    """Person Agent."""
    def __init__(self, unique_id, model, agent_type="susceptible"):
        """ Create a new Person agent.

        Args:
            unique_id: Unique identifier for the agent
            agent_type: Indicator if agent is infected ("infected" or "susceptible")
            """
        super().__init__(unique_id, model, "Point")
        self.infected = 0
        self.agent_type = agent_type

    def step(self):
        # The agent's step will go here.
        self.infected += 1
        print(f"AGENT COUNTER: {self.infected}")


class NeighbourhoodAgent(GeoAgent):
    """Neighbourhood agent."""

    def __init__(self, unique_id, model, shape, agent_type=None):
        """Create a new Neighbourhood agent.

        Args:
            unique_id: Unique identifier for the agent.
            agent_type: Indicator if neighborhood is infected ("infected" or None)
        """
        super().__init__(unique_id, model, shape)
        self.atype = agent_type

    def step(self):
        """Advance agent one step."""
        similar = 0
        different = 0
        neighbors = self.model.grid.get_neighbors(self)
        if neighbors:
            for neighbor in neighbors:
                if neighbor.atype is None:
                    continue
                elif neighbor.atype == self.atype:
                    similar += 1
                else:
                    different += 1

        # If unhappy, move:
        if similar < different:
            # Select an empty region
            empties = [a for a in self.model.grid.agents if a.atype is None]
            # Switch atypes and add/remove from scheduler
            new_region = random.choice(empties)
            new_region.atype = self.atype
            self.model.schedule.add(new_region)
            self.atype = None
            self.model.schedule.remove(self)
        else:
            self.model.infected += 1

    def __repr__(self):
        return "Agent " + str(self.unique_id)


class InfectedModel(Model):
    """Model class for a simplistic infection model."""

    def __init__(self, density, minority_pc):
        self.density = density
        self.minority_pc = minority_pc

        self.schedule = RandomActivation(self)
        self.grid = GeoSpace()

        self.infected = 0
        self.datacollector = DataCollector({"infected": "infected"})

        self.running = True

        # Set up the grid with patches for every NUTS region
        AC = AgentCreator(NeighbourhoodAgent, {"model": self})
        agents = AC.from_file("TorontoNeighbourhoods.geojson")
        self.grid.add_agents(agents)

        # Create a person Agent, add it
        person = PersonAgent('test', self)
        self.grid.add_agents(person)
        self.schedule.add(person)

        # Set up agents
        for agent in agents:
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent.atype = 1
                else:
                    agent.atype = 0
                self.schedule.add(agent)

    def step(self):
        """Run one step of the model.

        If All agents are happy, halt the model.
        """
        self.infected = 0  # Reset counter of happy agents
        self.schedule.step()
        # self.datacollector.collect(self)

        if self.infected == self.schedule.get_agent_count():
            self.running = False
