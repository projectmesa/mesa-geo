"""
The geoagent class for the mesa_geo framework.

Core Objects: GeoAgent

"""
from mesa import Agent
import pyproj
from shapely.geometry import mapping


class GeoAgent(Agent):
    """Base class for a geo model agent."""

    def __init__(self, unique_id, model, shape):
        """Create a new agent.

        unique_id: Id of agent. Uniqueness is not guaranteed!
        model: The associated model of the agent
        shape: A Shapely shape object
        """
        self.unique_id = unique_id
        self.model = model
        self.shape = shape

    def step(self):
        """Advance one step."""
        pass

    def __geo_interface__(self):
        """Return a GeoJSON Feature.

        Removes model and shape from attributes.
        """
        props = dict(vars(self))
        del props['shape']
        del props['model']

        shape = self.model.grid.transform(self.model.grid.crs,
                                          pyproj.Proj(init='epsg:4326'),
                                          self.shape)

        return {'type': 'Feature',
                'geometry': mapping(shape),
                'properties': props}
