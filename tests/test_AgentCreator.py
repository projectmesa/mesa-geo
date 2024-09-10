import unittest

import geopandas as gpd
import mesa
import pandas as pd
from shapely.geometry import Point

import mesa_geo as mg


class TestAgentCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.model = mesa.Model()
        self.model.space = mg.GeoSpace(crs="epsg:4326")
        self.agent_creator_without_crs = mg.AgentCreator(
            agent_class=mg.GeoAgent, model=self.model
        )
        self.agent_creator_with_crs = mg.AgentCreator(
            model=self.model,
            agent_class=mg.GeoAgent,
            crs="epsg:3857",
        )
        self.df = pd.DataFrame(
            {
                "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
                "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
                "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
                "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
            }
        )

        self.geojson_str = {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "0",
                    "type": "Feature",
                    "properties": {"col1": "name1"},
                    "geometry": {"type": "Point", "coordinates": (1.0, 2.0)},
                    "bbox": (1.0, 2.0, 1.0, 2.0),
                },
                {
                    "id": "1",
                    "type": "Feature",
                    "properties": {"col1": "name2"},
                    "geometry": {"type": "Point", "coordinates": (2.0, 1.0)},
                    "bbox": (2.0, 1.0, 2.0, 1.0),
                },
            ],
            "bbox": (1.0, 1.0, 2.0, 2.0),
        }

    def tearDown(self) -> None:
        pass

    def test_create_agent_with_crs(self):
        agent = self.agent_creator_with_crs.create_agent(geometry=Point(1, 1))
        self.assertIsInstance(agent, mg.GeoAgent)
        self.assertEqual(agent.geometry, Point(1, 1))
        self.assertEqual(agent.model, self.model)
        self.assertEqual(agent.crs, self.agent_creator_with_crs.crs)

    def test_create_agent_without_crs(self):
        with self.assertRaises(TypeError):
            self.agent_creator_without_crs.create_agent(geometry=Point(1, 1))

    def test_from_GeoDataFrame_with_default_geometry_name(self):
        gdf = gpd.GeoDataFrame(
            self.df,
            geometry=gpd.points_from_xy(self.df.Longitude, self.df.Latitude),
            crs="epsg:3857",
        )
        agents = self.agent_creator_without_crs.from_GeoDataFrame(gdf)

        self.assertEqual(len(agents), 5)

        self.assertEqual(agents[0].City, "Buenos Aires")
        self.assertEqual(agents[0].Country, "Argentina")
        self.assertEqual(agents[0].geometry, Point(-58.66, -34.58))
        self.assertEqual(agents[0].crs, gdf.crs)

    def test_from_GeoDataFrame_with_custom_geometry_name(self):
        gdf = gpd.GeoDataFrame(
            self.df,
            geometry=gpd.points_from_xy(self.df.Longitude, self.df.Latitude),
            crs="epsg:3857",
        )
        gdf.rename_geometry("custom_name", inplace=True)

        agents = self.agent_creator_without_crs.from_GeoDataFrame(gdf)

        self.assertEqual(len(agents), 5)

        self.assertEqual(agents[0].City, "Buenos Aires")
        self.assertEqual(agents[0].Country, "Argentina")
        self.assertEqual(agents[0].geometry, Point(-58.66, -34.58))
        self.assertFalse(hasattr(agents[0], "custom_name"))
        self.assertEqual(agents[0].crs, gdf.crs)

    def test_from_GeoJSON_and_agent_creator_without_crs(self):
        agents = self.agent_creator_without_crs.from_GeoJSON(self.geojson_str)

        self.assertEqual(len(agents), 2)

        self.assertEqual(agents[0].unique_id, 1)
        self.assertEqual(agents[0].col1, "name1")
        self.assertEqual(agents[0].geometry, Point(1.0, 2.0))
        self.assertEqual(agents[0].crs, "epsg:4326")

        self.assertEqual(agents[1].unique_id, 2)
        self.assertEqual(agents[1].col1, "name2")
        self.assertEqual(agents[1].geometry, Point(2.0, 1.0))
        self.assertEqual(agents[1].crs, "epsg:4326")

    def test_from_GeoJSON_and_agent_creator_with_crs(self):
        agents = self.agent_creator_with_crs.from_GeoJSON(self.geojson_str)

        self.assertEqual(len(agents), 2)

        self.assertEqual(agents[0].unique_id, 1)
        self.assertEqual(agents[0].col1, "name1")
        self.assertTrue(
            agents[0].geometry.equals_exact(
                Point(111319.49079327357, 222684.20850554403), tolerance=1e-6
            )
        )
        self.assertEqual(agents[0].crs, self.agent_creator_with_crs.crs)

        self.assertEqual(agents[1].unique_id, 2)
        self.assertEqual(agents[1].col1, "name2")
        self.assertTrue(
            agents[1].geometry.equals_exact(
                Point(222638.98158654713, 111325.14286638508), tolerance=1e-6
            )
        )
        self.assertEqual(agents[1].crs, self.agent_creator_with_crs.crs)

    def test_from_GeoDataFrame_without_crs_and_agent_creator_without_crs(self):
        gdf = gpd.GeoDataFrame(
            self.df, geometry=gpd.points_from_xy(self.df.Longitude, self.df.Latitude)
        )
        with self.assertRaises(TypeError):
            self.agent_creator_without_crs.from_GeoDataFrame(gdf)

    def test_from_GeoDataFrame_without_crs_and_agent_creator_with_crs(self):
        gdf = gpd.GeoDataFrame(
            self.df, geometry=gpd.points_from_xy(self.df.Longitude, self.df.Latitude)
        )
        agents = self.agent_creator_with_crs.from_GeoDataFrame(gdf)

        self.assertEqual(len(agents), 5)

        self.assertEqual(agents[0].City, "Buenos Aires")
        self.assertEqual(agents[0].Country, "Argentina")
        self.assertEqual(agents[0].geometry, Point(-58.66, -34.58))
        self.assertEqual(agents[0].crs, self.agent_creator_with_crs.crs)

    def test_from_GeoDataFrame_with_crs_and_agent_creator_without_crs(self):
        gdf = gpd.GeoDataFrame(
            self.df,
            geometry=gpd.points_from_xy(self.df.Longitude, self.df.Latitude),
            crs="epsg:2263",
        )
        agents = self.agent_creator_without_crs.from_GeoDataFrame(gdf)

        self.assertEqual(len(agents), 5)

        self.assertEqual(agents[0].City, "Buenos Aires")
        self.assertEqual(agents[0].Country, "Argentina")
        self.assertEqual(agents[0].geometry, Point(-58.66, -34.58))
        self.assertEqual(agents[0].crs, gdf.crs)
