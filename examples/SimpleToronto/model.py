from mesa.datacollection import DataCollector
from mesa import Model
from mesa.time import RandomActivation
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
import random


class PersonAgent(GeoAgent):
    """Person Agent."""

    def __init__(self, unique_id, model, shape, agent_type="susceptible"):
        """ Create a new Person agent.

        Args:
            unique_id: Unique identifier for the agent
            agent_type: Indicator if agent is infected ("infected" or "susceptible")
            """
        super().__init__(unique_id, model, shape)
        self.infected = 0
        self.agent_type = agent_type

    def step(self):
        # The agent's step will go here.
        self.infected += 1
        print(f"AGENT COUNTER: {self.infected}")


class NeighbourhoodAgent(GeoAgent):
    """Neighbourhood agent."""

    def __init__(self, unique_id, model, shape, agent_type="safe"):
        """Create a new Neighbourhood agent.

        Args:
            unique_id: Unique identifier for the agent.
            agent_type: Indicator if neighborhood is hot-spot ("hotspot" or "safe")
        """
        super().__init__(unique_id, model, shape)
        self.atype = agent_type

    def step(self):
        """Advance agent one step."""
        "dumb test"
        self.atype = "hotspot" if self.random.random() > 0.5 else "safe"

    def __repr__(self):
        return "Agent " + str(self.unique_id)


class InfectedModel(Model):
    """Model class for a simplistic infection model."""

    def __init__(self, density, minority_pc):
        self.schedule = RandomActivation(self)
        self.grid = GeoSpace()

        self.infected = 0
        self.datacollector = DataCollector({"infected": "infected"})

        self.running = True

        # Set up the grid with patches for every NUTS region
        AC = AgentCreator(NeighbourhoodAgent, {"model": self})
        neighbourhood_agents = AC.from_file("TorontoNeighbourhoods.geojson")
        self.grid.add_agents(neighbourhood_agents)
        # Set up agents
        for agent in neighbourhood_agents:
            self.schedule.add(agent)

        # Create a person Agent, add it to grid and scheduler
        # shape_pedromorales = {"type": "Feature",
        #                       "properties": {"AGENTNUM": 42, "NAME": "Pedro Morales"},
        #                       "geometry": {"type": "Point", "coordinates": [[[-79.404282800449266, 43.647979616068149]]]}}
        # person_agent = PersonAgent('test', self, shape_pedromorales)
        # self.grid.add_agents(person_agent)
        # self.schedule.add(person_agent)

    def step(self):
        """Run one step of the model.

        After 10 steps, halt the model.
        """
        self.infected = 0  # Reset counter of happy agents
        self.schedule.step()
        # self.datacollector.collect(self)

        # Run for 10 steps
        if self.infected == 10:
            self.running = False
