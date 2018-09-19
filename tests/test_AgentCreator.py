import unittest
from mesa_geo.geoagent import GeoAgent, AgentCreator
from shapely.geometry import Point


class TestAgentCreator(unittest.TestCase):
    def test_create_agent(self):
        AC = AgentCreator(agent_class=GeoAgent, agent_kwargs={"model": None})
        shape = Point(1, 1)
        agent = AC.create_agent(shape=shape, unique_id=0)
        assert isinstance(agent, GeoAgent)
        assert agent.shape == shape
        assert agent.model is None


if __name__ == "__main__":
    unittest.main()
