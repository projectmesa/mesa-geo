"""
The geoagent class for the mesa_geo framework.

Core Objects: GeoAgent

"""
import geojson
import geopandas as gpd
from mesa import Agent
from mesa_geo.utilities import transform
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
        properties = dict(vars(self))
        properties["model"] = str(self.model)
        shape = properties.pop("shape")

        shape = transform(
            shape, self.model.grid.crs, pyproj.Proj({"init": "epsg:4326"})
        )

        return {"type": "Feature", "geometry": mapping(shape), "properties": properties}


class AgentCreator:
    def __init__(self, agent_class, agent_kwargs, crs={"init": "epsg:4326"}):
        self.agent_class = agent_class
        self.agent_kwargs = agent_kwargs
        self.crs = crs

    def create_agent(self, shape, unique_id):

        new_agent = self.agent_class(
            unique_id=unique_id, shape=shape, **self.agent_kwargs
        )

        return new_agent

    def from_GeoDataFrame(self, gdf, unique_id="index", set_attributes=True):

        if unique_id != "index":
            gdf = gdf.set_index(unique_id)

        if self.crs:
            gdf = gdf.to_crs(self.crs)

        agents = list()

        for index, row in gdf.iterrows():
            shape = row.geometry
            new_agent = self.create_agent(shape=shape, unique_id=index)

            if set_attributes:
                for col in row.index:
                    if col == "geometry":
                        continue
                    setattr(new_agent, col, row[col])
            agents.append(new_agent)
        return agents

    def from_file(self, filename, unique_id="index", set_attributes=True):
        gdf = gpd.read_file(filename)
        agents = self.from_GeoDataFrame(
            gdf, unique_id=unique_id, set_attributes=set_attributes
        )
        return agents

    def from_GeoJSON(self, GeoJSON, unique_id="index", set_attributes=True):
        if type(GeoJSON) is str:
            gj = geojson.loads(GeoJSON)
        else:
            gj = GeoJSON

        gdf = gpd.GeoDataFrame.from_features(gj)
        agents = self.from_GeoDataFrame(
            gdf, unique_id=unique_id, set_attributes=set_attributes
        )
        return agents
