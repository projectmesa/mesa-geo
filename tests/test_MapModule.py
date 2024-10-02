import unittest

import mesa
import numpy as np
import xyzservices.providers as xyz
from ipyleaflet import Circle, CircleMarker, Marker
from shapely.geometry import LineString, Point, Polygon

import mesa_geo as mg
import mesa_geo.visualization as mgv


class TestMapModule(unittest.TestCase):
    def setUp(self) -> None:
        self.model = mesa.Model()
        self.model.space = mg.GeoSpace(crs="epsg:4326")
        self.agent_creator = mg.AgentCreator(
            agent_class=mg.GeoAgent, model=self.model, crs="epsg:4326"
        )
        self.points = [Point(1, 1)] * 7
        self.point_agents = [
            self.agent_creator.create_agent(point) for point in self.points
        ]
        self.lines = [LineString([(1, 1), (2, 2)])] * 9
        self.line_agents = [
            self.agent_creator.create_agent(line) for line in self.lines
        ]
        self.polygons = [Polygon([(1, 1), (2, 2), (4, 4)])] * 3
        self.polygon_agents = [
            self.agent_creator.create_agent(polygon) for polygon in self.polygons
        ]
        self.raster_layer = mg.RasterLayer(
            1, 1, crs="epsg:4326", total_bounds=[0, 0, 1, 1], model=self.model
        )
        self.raster_layer.apply_raster(np.array([[[0]]]))

    def tearDown(self) -> None:
        pass

    def test_render_point_agents(self):
        # test length point agents and Circle marker as default
        map_module = mgv.MapModule(
            portrayal_method=lambda x: {"color": "Green"},
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.point_agents)
        self.assertEqual(len(map_module.render(self.model).get("agents")[1]), 7)
        self.assertIsInstance(map_module.render(self.model).get("agents")[1][3], Circle)
        # test CircleMarker option
        map_module = mgv.MapModule(
            portrayal_method=lambda x: {
                "marker_type": "CircleMarker",
                "color": "Green",
            },
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.point_agents)
        self.assertIsInstance(
            map_module.render(self.model).get("agents")[1][3], CircleMarker
        )

        # test Marker option
        map_module = mgv.MapModule(
            portrayal_method=lambda x: {
                "marker_type": "AwesomeIcon",
                "name": "bus",
                "color": "Green",
            },
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.point_agents)
        self.assertEqual(len(map_module.render(self.model).get("agents")[1]), 7)
        self.assertIsInstance(map_module.render(self.model).get("agents")[1][3], Marker)
        # test popupProperties for Point
        map_module = mgv.MapModule(
            portrayal_method=lambda x: {
                "color": "Red",
                "radius": 7,
                "description": "popupMsg",
            },
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.point_agents)
        print(map_module.render(self.model).get("agents")[0])
        self.assertDictEqual(
            map_module.render(self.model).get("agents")[0],
            {
                "type": "FeatureCollection",
                "features": [] * len(self.point_agents),
            },
        )

        # test ValueError if not known markertype
        map_module = mgv.MapModule(
            portrayal_method=lambda x: {"marker_type": "Hexagon", "color": "Green"},
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.point_agents)
        with self.assertRaises(ValueError):
            map_module.render(self.model)

    def test_render_line_agents(self):
        map_module = mgv.MapModule(
            portrayal_method=lambda x: {"color": "#3388ff", "weight": 7},
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.line_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents")[0],
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

        map_module = mgv.MapModule(
            portrayal_method=lambda x: {
                "color": "#3388ff",
                "weight": 7,
                "description": "popupMsg",
            },
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.line_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents")[0],
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

        map_module = mgv.MapModule(
            portrayal_method=lambda x: {"fillColor": "#3388ff", "fillOpacity": 0.7},
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.polygon_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents")[0],
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

        map_module = mgv.MapModule(
            portrayal_method=lambda x: {
                "fillColor": "#3388ff",
                "fillOpacity": 0.7,
                "description": "popupMsg",
            },
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_agents(self.polygon_agents)
        self.assertDictEqual(
            map_module.render(self.model).get("agents")[0],
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

    def test_render_raster_layers(self):
        map_module = mgv.MapModule(
            portrayal_method=lambda x: (255, 255, 255, 0.5),
            tiles=xyz.OpenStreetMap.Mapnik,
        )
        self.model.space.add_layer(self.raster_layer)
        self.model.space.add_layer(
            self.raster_layer.to_image(colormap=lambda x: (0, 0, 0, 1))
        )
        self.assertDictEqual(
            map_module.render(self.model).get("layers"),
            {
                "rasters": [
                    {
                        "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mP4DwQACfsD/Wj6HMwAAAAASUVORK5CYII=",
                        "bounds": [[0.0, 0.0], [1.0, 1.0]],
                    },
                    {
                        "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNgYGD4DwABBAEAgLvRWwAAAABJRU5ErkJggg==",
                        "bounds": [[0.0, 0.0], [1.0, 1.0]],
                    },
                ],
                "total_bounds": [[0.0, 0.0], [1.0, 1.0]],
                "vectors": [],
            },
        )
