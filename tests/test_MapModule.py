import unittest
import uuid

from mesa.model import Model
from shapely.geometry import Point

from mesa_geo import AgentCreator, GeoAgent, GeoSpace
from mesa_geo.visualization.modules import MapModule


class TestMapModule(unittest.TestCase):
    def setUp(self) -> None:
        self.model = Model()
        self.model.space = GeoSpace()
        self.agent_creator = AgentCreator(
            agent_class=GeoAgent, agent_kwargs={"model": self.model}
        )
        self.shapes = [Point(1, 1)] * 7
        self.agents = [
            self.agent_creator.create_agent(shape=shape, unique_id=uuid.uuid4().int)
            for shape in self.shapes
        ]
        self.model.space.add_agents(self.agents)

    def tearDown(self) -> None:
        pass

    def test_render(self):
        map_module = MapModule(portrayal_method=lambda x: {"color": "red", "radius": 7})
        self.assertDictEqual(
            map_module.render(self.model),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": (
                                8.983152841195214e-06,
                                8.983152841195177e-06,
                            ),
                        },
                        "properties": {"color": "red", "radius": 7},
                    }
                ]
                * len(self.agents),
            },
        )
