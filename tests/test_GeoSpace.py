import unittest
import uuid
import random

from mesa_geo.geospace import GeoSpace
from mesa_geo.geoagent import GeoAgent, AgentCreator
from shapely.geometry import Point


class TestGeoSpace(unittest.TestCase):
    def setUp(self) -> None:
        self.agent_creator = AgentCreator(
            agent_class=GeoAgent,
            crs="epsg:3857",
        )
        self.geometries = [Point(1, 1)] * 7
        self.agents = [
            self.agent_creator.create_agent(
                geometry=geometry, unique_id=uuid.uuid4().int
            )
            for geometry in self.geometries
        ]
        self.geo_space = GeoSpace()
        self.geo_space_with_different_crs = GeoSpace(crs="epsg:2283")

    def tearDown(self) -> None:
        pass

    def test_add_agents_with_the_same_crs(self):
        self.assertEqual(len(self.geo_space.agents), 0)
        self.geo_space.add_agents(self.agents)
        self.assertEqual(len(self.geo_space.agents), len(self.agents))

        for agent in self.geo_space.agents:
            self.assertEqual(agent.crs, self.geo_space.crs)

    def test_add_agents_with_different_crs(self):
        self.assertEqual(len(self.geo_space_with_different_crs.agents), 0)
        with self.assertRaises(ValueError):
            self.geo_space_with_different_crs.add_agents(self.agents)

        self.geo_space_with_different_crs.add_agents(self.agents, auto_convert_crs=True)
        self.assertEqual(
            len(self.geo_space_with_different_crs.agents), len(self.agents)
        )

        for agent in self.geo_space_with_different_crs.agents:
            self.assertEqual(agent.crs, self.geo_space_with_different_crs.crs)

    def test_remove_agent(self):
        self.geo_space.add_agents(self.agents)
        agent_to_remove = random.choice(self.agents)
        self.geo_space.remove_agent(agent_to_remove)
        remaining_agent_idx = set(agent.unique_id for agent in self.geo_space.agents)

        self.assertEqual(len(self.geo_space.agents), len(self.agents) - 1)
        self.assertTrue(agent_to_remove.unique_id not in remaining_agent_idx)
