import unittest

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from mesa_geo.geoagent import GeoAgent, AgentCreator


class TestAgentCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.agent_creator = AgentCreator(
            agent_class=GeoAgent, agent_kwargs={"model": None}
        )
        self.df = pd.DataFrame(
            {
                "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
                "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
                "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
                "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
            }
        )

    def tearDown(self) -> None:
        pass

    def test_create_agent(self):
        agent = self.agent_creator.create_agent(geometry=Point(1, 1), unique_id=0)
        self.assertIsInstance(agent, GeoAgent)
        self.assertEqual(agent.geometry, Point(1, 1))
        self.assertIsNone(agent.model)

    def test_from_GeoDataFrame_with_default_geometry_name(self):
        gdf = gpd.GeoDataFrame(
            self.df,
            geometry=gpd.points_from_xy(self.df.Longitude, self.df.Latitude),
            crs="epsg:3857",
        )
        agents = self.agent_creator.from_GeoDataFrame(gdf)

        self.assertEqual(len(agents), 5)

        self.assertEqual(agents[0].City, "Buenos Aires")
        self.assertEqual(agents[0].Country, "Argentina")
        self.assertEqual(agents[0].geometry, Point(-58.66, -34.58))

    def test_from_GeoDataFrame_with_custom_geometry_name(self):
        gdf = gpd.GeoDataFrame(
            self.df,
            geometry=gpd.points_from_xy(self.df.Longitude, self.df.Latitude),
            crs="epsg:3857",
        )
        gdf.rename_geometry("custom_name", inplace=True)

        agents = self.agent_creator.from_GeoDataFrame(gdf)

        self.assertEqual(len(agents), 5)

        self.assertEqual(agents[0].City, "Buenos Aires")
        self.assertEqual(agents[0].Country, "Argentina")
        self.assertEqual(agents[0].geometry, Point(-58.66, -34.58))
        self.assertFalse(hasattr(agents[0], "custom_name"))
