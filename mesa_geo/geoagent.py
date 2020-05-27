"""
The geoagent class for the mesa_geo framework.

Core Objects: GeoAgent

"""
import json
import geopandas as gpd
from mesa import Agent
from shapely.ops import transform
from shapely.geometry import mapping
from shapely.geometry.base import BaseGeometry
import warnings


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
        self._geom = self.shape._geom

    def step(self):
        """Advance one step."""
        pass

    def __geo_interface__(self):
        """Return a GeoJSON Feature.

        Removes shape from attributes.
        """
        properties = dict(vars(self))
        properties["model"] = str(self.model)
        shape = properties.pop("shape")

        shape = transform(self.model.grid.Transformer.transform, shape)

        return {"type": "Feature", "geometry": mapping(shape), "properties": properties}


class AgentCreator:
    """Create GeoAgents from files, GeoDataFrames, GeoJSON or Shapely objects."""

    def __init__(self, agent_class, agent_kwargs, crs="epsg:3857"):
        """Define the agent_class and required agent_kwargs.

        Args:
            agent_class: Reference to a GeoAgent class
            agent_kwargs: Dictionary with required agent creation arguments.
                Must at least include 'model' and must NOT include unique_id
            crs: Coordinate reference system. If shapes are loaded from file
                they will be converted into this crs automatically.
        """
        if "unique_id" in agent_kwargs:
            agent_kwargs.remove("unique_id")
            warnings.warn("Unique_id should not be in the agent_kwargs")

        self.agent_class = agent_class
        self.agent_kwargs = agent_kwargs
        self.crs = crs

    def create_agent(self, shape, unique_id):
        """Create a single agent from a shape and a unique_id

        Shape must be a valid Shapely object."""

        if not isinstance(shape, BaseGeometry):
            raise TypeError("Shape must be a Shapely Geometry")

        new_agent = self.agent_class(
            unique_id=unique_id, shape=shape, **self.agent_kwargs
        )

        return new_agent

    def from_GeoDataFrame(self, gdf, unique_id="index", set_attributes=True):
        """Create a list of agents from a GeoDataFrame.

        Args:
            unique_id: Column to use for the unique_id.
                If "index" use the GeoDataFrame index
            set_attributes: Set agent attributes from GeoDataFrame columns.
        """

        if unique_id != "index":
            gdf = gdf.set_index(unique_id)

        gdf = gdf.to_crs(self.crs)

        agents = list()

        for index, row in gdf.iterrows():
            shape = row.geometry
            new_agent = self.create_agent(shape=shape, unique_id=index)

            if set_attributes:
                for col in row.index:
                    if not col == "geometry":
                        setattr(new_agent, col, row[col])
            agents.append(new_agent)
        return agents

    def from_file(self, filename, unique_id="index", set_attributes=True):
        """Create agents from vector data files (e.g. Shapefiles).

        Args:
            filename: The filename of the vector data
            unique_id: The field name of the data to use as the agents unique_id
            set_attributes: Set attributes from data records
        """
        gdf = gpd.read_file(filename)
        agents = self.from_GeoDataFrame(
            gdf, unique_id=unique_id, set_attributes=set_attributes
        )
        return agents

    def from_GeoJSON(self, GeoJSON, unique_id="index", set_attributes=True):
        """Create agents from a GeoJSON object or string.

        Args:
            GeoJSON: The GeoJSON object or string
            unique_id: The fieldfeature name of the data to use as the agents unique_id
            set_attributes: Set attributes from features
        """
        if type(GeoJSON) is str:
            gj = json.loads(GeoJSON)
        else:
            gj = GeoJSON

        gdf = gpd.GeoDataFrame.from_features(gj)
        gdf.crs = "epsg:4326"
        agents = self.from_GeoDataFrame(
            gdf, unique_id=unique_id, set_attributes=set_attributes
        )
        return agents
