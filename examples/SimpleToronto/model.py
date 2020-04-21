from mesa.datacollection import DataCollector
from mesa import Model
from mesa.time import RandomActivation
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
from shapely.geometry import Point
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
        self.atype = agent_type

    def move_point(self, dx, dy):
        """ Move a point by creating a new one"""
        return Point(self.shape.x + dx, self.shape.y + dy)

    def step(self):
        mobility_range = 100
        move_x = random.randint(0, mobility_range)
        move_y = random.randint(0, mobility_range)
        self.shape = self.move_point(move_x, move_y)  # Reassign shape
        self.atype = "infected" if self.random.random() > 0.5 else "susceptible"


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

        # Set up the grid with patches for every region
        AC = AgentCreator(NeighbourhoodAgent, {"model": self})
        neighbourhood_agents = AC.from_file("TorontoNeighbourhoods.geojson")
        self.grid.add_agents(neighbourhood_agents)
        # Set up agents
        for agent in neighbourhood_agents:
            self.schedule.add(agent)

        pedromorales_string = {
            "type": "FeatureCollection",
            "name": "pedromorales",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "AGENTNUM": 42,
                        "NAME": "Pedro Morales"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            -79.404282800449266,
                            43.647979616068149
                        ]
                    }
                }
            ]
        }
        # Create a person Agent, add it to grid and scheduler
        ac_person = AgentCreator(PersonAgent, {"model": self})
        person_agent = ac_person.from_GeoJSON(pedromorales_string)
        # person_agent = ac_person.from_file("pedromorales.geojson")
        for agent in person_agent:
            self.grid.add_agents(agent)
            self.schedule.add(agent)

    def step(self):
        """Run one step of the model.

        After 10 steps, halt the model.
        """
        self.infected += 1
        self.schedule.step()
        # self.datacollector.collect(self)

        # Run for 10 steps
        if self.infected == 10:
            self.running = False
