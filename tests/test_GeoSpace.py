import random
import unittest
import uuid
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

import mesa_geo as mg


class TestGeoSpace(unittest.TestCase):
    def setUp(self) -> None:
        self.agent_creator = mg.AgentCreator(agent_class=mg.GeoAgent, crs="epsg:3857")
        self.geometries = [Point(1, 1)] * 7
        self.agents = [
            self.agent_creator.create_agent(
                geometry=geometry, unique_id=uuid.uuid4().int
            )
            for geometry in self.geometries
        ]
        self.image_layer = mg.ImageLayer(
            values=np.random.uniform(low=0, high=255, size=(3, 500, 500)),
            crs="epsg:4326",
            total_bounds=[
                -122.26638888878,
                42.855833333,
                -121.94972222209202,
                43.01472222189958,
            ],
        )
        self.vector_layer = gpd.GeoDataFrame(
            {"name": ["point_1", "point_2"], "geometry": [Point(1, 2), Point(2, 1)]},
            crs="epsg:4326",
        )
        self.geo_space = mg.GeoSpace()
        self.geo_space_with_different_crs = mg.GeoSpace(crs="epsg:2283")

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
        with self.assertWarns(Warning):
            self.geo_space_with_different_crs.add_agents(self.agents)

        self.geo_space_with_different_crs.warn_crs_conversion = False
        # assert no warning
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.geo_space_with_different_crs.add_agents(self.agents)

        self.geo_space_with_different_crs.add_agents(self.agents)
        self.assertEqual(
            len(self.geo_space_with_different_crs.agents), len(self.agents)
        )

        for agent in self.geo_space_with_different_crs.agents:
            self.assertEqual(agent.crs, self.geo_space_with_different_crs.crs)

    def test_remove_agent(self):
        self.geo_space.add_agents(self.agents)
        agent_to_remove = random.choice(self.agents)
        self.geo_space.remove_agent(agent_to_remove)
        remaining_agent_idx = {agent.unique_id for agent in self.geo_space.agents}

        self.assertEqual(len(self.geo_space.agents), len(self.agents) - 1)
        self.assertTrue(agent_to_remove.unique_id not in remaining_agent_idx)

    def test_add_image_layer(self):
        with self.assertWarns(Warning):
            self.geo_space.add_layer(self.image_layer)
        self.assertEqual(len(self.geo_space.layers), 1)

        self.geo_space.warn_crs_conversion = False
        # assert no warning
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.geo_space.add_layer(self.image_layer)
        self.assertEqual(len(self.geo_space.layers), 2)

    def test_add_vector_layer(self):
        with self.assertWarns(Warning):
            self.geo_space.add_layer(self.vector_layer)
        self.assertEqual(len(self.geo_space.layers), 1)

        self.geo_space.warn_crs_conversion = False
        # assert no warning
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.geo_space.add_layer(self.vector_layer)
        self.assertEqual(len(self.geo_space.layers), 2)

    def test_get_neighbors_within_distance(self):
        self.geo_space.add_agents(self.agents)
        agent_to_check = random.choice(self.agents)

        neighbors = list(
            self.geo_space.get_neighbors_within_distance(
                agent_to_check, distance=1.0, center=True
            )
        )
        self.assertEqual(len(neighbors), 7)

        neighbors = list(
            self.geo_space.get_neighbors_within_distance(agent_to_check, distance=1.0)
        )
        self.assertEqual(len(neighbors), 7)

    def test_get_agents_as_GeoDataFrame(self):
        self.geo_space.add_agents(self.agents)

        agents_list = [
            {"geometry": agent.geometry, "unique_id": agent.unique_id}
            for agent in self.agents
        ]
        agents_gdf = gpd.GeoDataFrame.from_records(agents_list, index="unique_id")
        agents_gdf.crs = self.geo_space.crs

        pd.testing.assert_frame_equal(
            self.geo_space.get_agents_as_GeoDataFrame(), agents_gdf
        )
        self.assertEqual(
            self.geo_space.get_agents_as_GeoDataFrame().crs, agents_gdf.crs
        )
