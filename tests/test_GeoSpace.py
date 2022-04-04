import unittest
import uuid
import random

from mesa_geo.geospace import GeoSpace
from mesa_geo.geoagent import GeoAgent, AgentCreator
from shapely.geometry import Point


class TestGeoSpace(unittest.TestCase):
    def setUp(self) -> None:
        self.agent_creator = AgentCreator(
            agent_class=GeoAgent, agent_kwargs={"model": None}
        )
        self.shapes = [Point(1, 1)] * 7
        self.agents = [
            self.agent_creator.create_agent(shape=shape, unique_id=uuid.uuid4().int)
            for shape in self.shapes
        ]
        self.geo_space = GeoSpace()

    def tearDown(self) -> None:
        pass

    def test_add_agents(self):
        self.assertEqual(len(self.geo_space.agents), 0)
        self.geo_space.add_agents(self.agents)

        self.assertEqual(len(self.geo_space.agents), len(self.agents))

    def test_remove_agent(self):
        self.geo_space.add_agents(self.agents)
        agent_to_remove = random.choice(self.agents)
        self.geo_space.remove_agent(agent_to_remove)
        remaining_agent_idx = set(agent.unique_id for agent in self.geo_space.agents)

        self.assertEqual(len(self.geo_space.agents), len(self.agents) - 1)
        self.assertTrue(agent_to_remove.unique_id not in remaining_agent_idx)
