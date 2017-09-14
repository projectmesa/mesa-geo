import random
import geojson
from mesa import Model
from mesa_geo import GeoAgent
from mesa.time import RandomActivation
from mesa_geo import GeoSpace
from mesa.datacollection import DataCollector


class SchellingAgent(GeoAgent):
    '''
    Schelling segregation agent
    '''
    def __init__(self, unique_id, model, shape, agent_type=None):
        '''
         Create a new Schelling agent.

         Args:
            unique_id: Unique identifier for the agent.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        '''
        super().__init__(unique_id, model, shape)
        self.atype = agent_type

    def step(self):
        similar = 0
        different = 0
        neighbors = self.model.grid.get_intersecting_agents(self)
        if neighbors:
            for neighbor in neighbors:
                if not neighbor.atype:
                    continue
                elif neighbor.atype == self.atype:
                    similar += 1
                else:
                    different += 1

        # If unhappy, move:
        if similar < different:
            # Select an empty regions
            empties = [a for a in self.model.grid.agents if a.atype is None]
            new_region = random.choice(empties)
            # Switch position/shapes
            own_shape = self.shape
            self.shape = new_region.shape
            new_region.shape = own_shape
            # Since agents have changed position, we need to update the rtree
            self.grid.update_rtree()
        else:
            self.model.happy += 1


class SchellingModel(Model):
    '''
    Model class for the Schelling segregation model.
    '''

    def __init__(self, density, minority_pc):
        '''
        '''
        self.density = density
        self.minority_pc = minority_pc

        self.schedule = RandomActivation(self)
        self.grid = GeoSpace(crs='epsg:4326')

        self.happy = 0
        self.datacollector = DataCollector(
            {"happy": lambda m: m.happy})  # Model-level count of happy agents

        self.running = True

        # Set up the grid with patches for every NUTS region
        regions = geojson.load(open('nuts_rg_60M_2013_lvl_2.geojson'))
        self.grid.create_agents_from_GeoJSON(regions, SchellingAgent,
                                             model=self, unique_id='NUTS_ID')

        # Set up agents
        for agent in self.grid.agents:
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent.atype = 1
                else:
                    agent.atype = 0
                self.schedule.add(agent)

        # Update the bounding box of the grid and the spatial rtree
        self.grid.update_bbox()
        self.grid.update_rtree()

    def step(self):
        '''
        Run one step of the model. If All agents are happy, halt the model.
        '''

        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False
