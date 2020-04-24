from mesa.datacollection import DataCollector
from mesa import Model
from mesa.time import RandomActivation
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
from mesa_geo.utilities import transform
from shapely.geometry import Point


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
        move_x = self.random.randint(-mobility_range, mobility_range)
        move_y = self.random.randint(-mobility_range, mobility_range)
        self.shape = self.move_point(move_x, move_y)  # Reassign shape

    def __repr__(self):
        return "Person " + str(self.unique_id)


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
        hotspot_threshold = 1
        neighbors = self.model.grid.get_intersecting_agents(self)
        infected_neighbors = [neighbor for neighbor in neighbors if neighbor.atype == 'infected']
        if len(infected_neighbors) >= hotspot_threshold:
            self.atype = "hotspot"
        else:
            self.atype = 'safe'

    def __repr__(self):
        return "Neighborhood " + str(self.unique_id)


class InfectedModel(Model):
    """Model class for a simplistic infection model."""
    MAP_COORDS = [43.741667, -79.373333]  # Toronto

    def __init__(self, pop_size, init_infected):
        self.schedule = RandomActivation(self)
        self.grid = GeoSpace()

        self.infected = 0
        self.datacollector = DataCollector({"infected": "infected"})

        self.running = True

        # Set up the grid with patches for every region in file
        AC = AgentCreator(NeighbourhoodAgent, {"model": self})
        neighbourhood_agents = AC.from_file("TorontoNeighbourhoods.geojson", unique_id="HOODNUM")
        self.grid.add_agents(neighbourhood_agents)
        # Set up region agents
        for agent in neighbourhood_agents:
            self.schedule.add(agent)

        # Generate PersonAgent population
        lat, long = self.MAP_COORDS
        spread_x, spread_y = (5000, 5000)  # Range of initial population spread
        center_shape = transform(Point(long, lat), self.grid.WGS84, self.grid.crs)  # Convert to projection coordinates
        center_x, center_y = (center_shape.x, center_shape.y)
        ac_population = AgentCreator(PersonAgent, {"model": self})
        for i in range(pop_size):
            this_x = center_x + self.random.randint(0, spread_x) - spread_x / 2
            this_y = center_y + self.random.randint(0, spread_y) - spread_y / 2
            this_person = ac_population.create_agent(Point(this_x, this_y), "P" + str(i))
            if self.random.random() < init_infected:
                this_person.atype = "infected"
            self.grid.add_agents(this_person)
            self.schedule.add(this_person)

    def step(self):
        """Run one step of the model.

        After 10 steps, halt the model.
        """
        self.infected += 1
        self.schedule.step()
        self.grid._recreate_rtree([])  # Recalculate spatial tree, because agents are moving
        # self.datacollector.collect(self)

        # Run for 10 steps
        if self.infected == 10:
            self.running = False
