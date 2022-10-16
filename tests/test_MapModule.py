import unittest
import uuid

import mesa
import mesa_geo as mg
from shapely.geometry import Point, LineString, Polygon


class TestMapModule(unittest.TestCase):
    def setUp(self) -> None:
        self.model = mesa.Model()
        self.model.space = mg.GeoSpace(crs="epsg:4326")
        self.agent_creator = mg.AgentCreator(
            agent_class=mg.GeoAgent, model=self.model, crs="epsg:4326"
        )
        self.points = [Point(1, 1)] * 7
        self.point_agents = [
            self.agent_creator.create_agent(point, unique_id=uuid.uuid4().int)
            for point in self.points
        ]
        self.lines = [LineString([(1, 1), (2, 2)])] * 9
        self.line_agents = [
            self.agent_creator.create_agent(line, unique_id=uuid.uuid4().int)
            for line in self.lines
        ]
        self.polygons = [Polygon([(1, 1), (2, 2), (4, 4)])] * 3
        self.polygon_agents = [
            self.agent_creator.create_agent(polygon, unique_id=uuid.uuid4().int)
            for polygon in self.polygons
        ]

    def tearDown(self) -> None:
        pass

    def test_render_point_agents(self):
        map_module = mg.visualization.MapModule(
            portrayal_method=lambda x: {"color": "Red", "radius": 7}
        )
        self.model.space.add_agents(self.point_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents"),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": (1.0, 1.0)},
                        "properties": {"pointToLayer": {"color": "Red", "radius": 7}},
                    }
                ]
                * len(self.point_agents),
            },
        )

        map_module = mg.visualization.MapModule(
            portrayal_method=lambda x: {
                "color": "Red",
                "radius": 7,
                "description": "popupMsg",
            }
        )
        self.model.space.add_agents(self.point_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents"),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": (1.0, 1.0)},
                        "properties": {
                            "pointToLayer": {"color": "Red", "radius": 7},
                            "popupProperties": "popupMsg",
                        },
                    }
                ]
                * len(self.point_agents),
            },
        )

    def test_render_line_agents(self):
        map_module = mg.visualization.MapModule(
            portrayal_method=lambda x: {"color": "#3388ff", "weight": 7}
        )
        self.model.space.add_agents(self.line_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents"),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": ((1.0, 1.0), (2.0, 2.0)),
                        },
                        "properties": {"style": {"color": "#3388ff", "weight": 7}},
                    }
                ]
                * len(self.line_agents),
            },
        )

        map_module = mg.visualization.MapModule(
            portrayal_method=lambda x: {
                "color": "#3388ff",
                "weight": 7,
                "description": "popupMsg",
            }
        )
        self.model.space.add_agents(self.line_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents"),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": ((1.0, 1.0), (2.0, 2.0)),
                        },
                        "properties": {
                            "style": {"color": "#3388ff", "weight": 7},
                            "popupProperties": "popupMsg",
                        },
                    }
                ]
                * len(self.line_agents),
            },
        )

    def test_render_polygon_agents(self):

        self.maxDiff = None

        map_module = mg.visualization.MapModule(
            portrayal_method=lambda x: {"fillColor": "#3388ff", "fillOpacity": 0.7}
        )
        self.model.space.add_agents(self.polygon_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents"),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": (
                                ((1.0, 1.0), (2.0, 2.0), (4.0, 4.0), (1.0, 1.0)),
                            ),
                        },
                        "properties": {
                            "style": {"fillColor": "#3388ff", "fillOpacity": 0.7}
                        },
                    }
                ]
                * len(self.polygon_agents),
            },
        )

        map_module = mg.visualization.MapModule(
            portrayal_method=lambda x: {
                "fillColor": "#3388ff",
                "fillOpacity": 0.7,
                "description": "popupMsg",
            }
        )
        self.model.space.add_agents(self.polygon_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents"),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": (
                                ((1.0, 1.0), (2.0, 2.0), (4.0, 4.0), (1.0, 1.0)),
                            ),
                        },
                        "properties": {
                            "style": {"fillColor": "#3388ff", "fillOpacity": 0.7},
                            "popupProperties": "popupMsg",
                        },
                    }
                ]
                * len(self.polygon_agents),
            },
        )
