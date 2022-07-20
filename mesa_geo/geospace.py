from __future__ import annotations

import warnings
from typing import List

import geopandas as gpd
import numpy as np
import pyproj
from libpysal import weights
from rtree import index
from shapely.geometry import Point
from shapely.prepared import prep

from mesa_geo.geo_base import GeoBase
from mesa_geo.geoagent import GeoAgent
from mesa_geo.raster_layers import ImageLayer, RasterLayer


class GeoSpace(GeoBase):
    def __init__(self, crs="epsg:3857", *, warn_crs_conversion=True):
        """Create a GeoSpace for GIS enabled mesa modeling.

        Args:
            crs: Coordinate reference system of the GeoSpace
                If `crs` is not set, epsg:3857 (Web Mercator) is used as default.
                However, this system is only accurate at the equator and errors
                increase with latitude.
            warn_crs_conversion: Whether to receive warning messages about
                converting layers and GeoAgents of different crs into the crs of
                GeoSpace. Default to True.

        Properties:
            crs: Coordinate reference system of the GeoSpace
            warn_crs_conversion: Whether to receive warning messages about
                                 converting layers and GeoAgents of different crs
                                 into the crs of GeoSpace.
            transformer: A pyproj.Transformer that transforms the GeoSpace into
                         epsg:4326. Mainly used for GeoJSON serialization.
            agents: List of all agents in the GeoSpace.
            layers: List of all layers in the GeoSpace.
            total_bounds: Bounds of the GeoSpace in [min_x, min_y, max_x, max_y] format.

        Methods:
            add_agents: Add a list or a single GeoAgent.
            remove_agent: Remove a single agent from GeoSpace
            agents_at: List all agents at a specific position
            distance: Calculate distance between two agents
            get_neighbors: Returns a list of (touching) neighbors
            get_intersecting_agents: Returns list of agents that intersect
            get_relation: Return a list of related agents
            get_neighbors_within_distance: Return a list of agents within `distance` of `agent`
            add_layer: Add an ImageLayer, RasterLayer or a geopandas.GeoDataFrame
        """
        super().__init__(crs)
        self._transformer = pyproj.Transformer.from_crs(
            crs_from=self.crs, crs_to="epsg:4326", always_xy=True
        )
        self.warn_crs_conversion = warn_crs_conversion
        self._agent_layer = _AgentLayer()
        self._static_layers = []
        self._total_bounds = None  # [min_x, min_y, max_x, max_y]

    def to_crs(self, crs, inplace=False) -> GeoSpace | None:
        super()._to_crs_check(crs)

        if inplace:
            for agent in self.agents:
                agent.to_crs(crs, inplace=True)
            for layer in self.layers:
                layer.to_crs(crs, inplace=True)
        else:
            geospace = GeoSpace(
                crs=self.crs.to_string(), warn_crs_conversion=self.warn_crs_conversion
            )
            for agent in self.agents:
                geospace.add_agents(agent.to_crs(crs, inplace=False))
            for layer in self.layers:
                geospace.add_layer(layer.to_crs(crs, inplace=False))
            return geospace

    @property
    def transformer(self):
        """
        Return the pyproj.Transformer that transforms the GeoSpace into
        epsg:4326. Mainly used for GeoJSON serialization.
        """
        return self._transformer

    @property
    def agents(self):
        """
        Return a list of all agents in the Geospace.
        """
        return self._agent_layer.agents

    @property
    def layers(self) -> List[ImageLayer | RasterLayer | gpd.GeoDataFrame]:
        """
        Return a list of all layers in the Geospace.
        """
        return self._static_layers

    @property
    def total_bounds(self) -> np.ndarray | None:
        """
        Return the bounds of the GeoSpace in [min_x, min_y, max_x, max_y] format.
        """
        return self._total_bounds

    def _update_bounds(self, new_bounds: np.ndarray) -> None:
        if new_bounds is not None:
            if self._total_bounds is not None:
                new_min_x = min(self.total_bounds[0], new_bounds[0])
                new_min_y = min(self.total_bounds[1], new_bounds[1])
                new_max_x = max(self.total_bounds[2], new_bounds[2])
                new_max_y = max(self.total_bounds[3], new_bounds[3])
                self._total_bounds = np.array(
                    [new_min_x, new_min_y, new_max_x, new_max_y]
                )
            else:
                self._total_bounds = new_bounds

    @property
    def __geo_interface__(self):
        """Return a GeoJSON FeatureCollection."""
        features = [a.__geo_interface__() for a in self.agents]
        return {"type": "FeatureCollection", "features": features}

    def add_layer(self, layer: ImageLayer | RasterLayer | gpd.GeoDataFrame) -> None:
        """Add a layer to the Geospace.

        Args:
            layer: An ImageLayer, RasterLayer or a geopandas.GeoDataFrame, to be added into GeoSpace.
        """
        if not self.crs.is_exact_same(layer.crs):
            if self.warn_crs_conversion:
                warnings.warn(
                    f"Converting {layer.__class__.__name__} from crs {layer.crs.to_string()} "
                    f"to the crs of {self.__class__.__name__} - {self.crs.to_string()}. "
                    "Please check your crs settings if this is unintended, or set `GeoSpace.warn_crs_conversion` "
                    "to `False` to suppress this warning message."
                )
            layer.to_crs(self.crs, inplace=True)
        self._update_bounds(layer.total_bounds)
        self._static_layers.append(layer)

    def _check_agent(self, agent):
        if hasattr(agent, "geometry"):
            if not self.crs.is_exact_same(agent.crs):
                if self.warn_crs_conversion:
                    warnings.warn(
                        f"Converting {agent.__class__.__name__} from crs {agent.crs.to_string()} "
                        f"to the crs of {self.__class__.__name__} - {self.crs.to_string()}. "
                        "Please check your crs settings if this is unintended, or set `GeoSpace.warn_crs_conversion` "
                        "to `False` to suppress this warning message."
                    )
                agent.to_crs(self.crs, inplace=True)
        else:
            raise AttributeError("GeoAgents must have a geometry attribute")

    def add_agents(self, agents):
        """Add a list of GeoAgents to the Geospace.

        GeoAgents must have a geometry attribute. This function may also be called
        with a single GeoAgent.

        Args:
            agents: List of GeoAgents, or a single GeoAgent, to be added into GeoSpace.

        Raises:
            AttributeError: If GeoAgent doesn't have a geometry attribute.
        """
        if isinstance(agents, GeoAgent):
            agent = agents
            self._check_agent(agent)
        else:
            for agent in agents:
                self._check_agent(agent)
        self._agent_layer.add_agents(agents)
        self._update_bounds(new_bounds=self._agent_layer.total_bounds)

    def _recreate_rtree(self, new_agents=None):
        """Create a new rtree index from agents geometries."""
        self._agent_layer._recreate_rtree(new_agents)

    def remove_agent(self, agent):
        """Remove an agent from the GeoSpace."""
        self._agent_layer.remove_agent(agent)

    def get_relation(self, agent, relation):
        """Return a list of related agents.

        Args:
            agent: the agent for which to compute the relation
            relation: must be one of 'intersects', 'within', 'contains',
                'touches'
            other_agents: A list of agents to compare against.
                Omit to compare against all other agents of the GeoSpace
        """
        yield from self._agent_layer.get_relation(agent, relation)

    def get_intersecting_agents(self, agent, other_agents=None):
        return self._agent_layer.get_intersecting_agents(agent, other_agents)

    def get_neighbors_within_distance(
        self, agent, distance, center=False, relation="intersects"
    ):
        """Return a list of agents within `distance` of `agent`.

        Distance is measured as a buffer around the agent's geometry,
        set center=True to calculate distance from center.
        """
        yield from self._agent_layer.get_neighbors_within_distance(
            agent, distance, center, relation
        )

    def agents_at(self, pos):
        """Return a list of agents at given pos."""
        return self._agent_layer.agents_at(pos)

    def distance(self, agent_a, agent_b):
        """Return distance of two agents."""
        return self._agent_layer.distance(agent_a, agent_b)

    def get_neighbors(self, agent):
        """Get (touching) neighbors of an agent."""
        return self._agent_layer.get_neighbors(agent)


class _AgentLayer:
    """Layer that contains the GeoAgents. Mainly for internal usage within `GeoSpace`.

    Properties:
        idx: R-tree index for fast spatial queries
        total_bounds: Bounds of the layer in [min_x, min_y, max_x, max_y] format
        agents: List of all agents in the layer

    Methods:
        add_agents: add a list or a single GeoAgent.
        remove_agent: Remove a single agent from the layer
        agents_at: List all agents at a specific position
        distance: Calculate distance between two agents
        get_neighbors: Returns a list of (touching) neighbors
        get_intersecting_agents: Returns list of agents that intersect
        get_relation: Return a list of related agents
        get_neighbors_within_distance: Return a list of agents within `distance` of `agent`
    """

    def __init__(self):
        self._neighborhood = None

        # Set up rtree index
        self.idx = index.Index()
        self.idx.agents = {}

    @property
    def agents(self):
        return list(self.idx.agents.values())

    @property
    def total_bounds(self):
        return self.idx.get_bounds(coordinate_interleaved=True)

    def _get_rtree_intersections(self, geometry):
        """Calculate rtree intersections for candidate agents."""
        return (self.idx.agents[i] for i in self.idx.intersection(geometry.bounds))

    def _create_neighborhood(self):
        """Create a neighborhood graph of all agents."""
        agents = self.agents
        geometries = [agent.geometry for agent in agents]
        self._neighborhood = weights.contiguity.Queen.from_iterable(geometries)
        self._neighborhood.agents = agents
        self._neighborhood.idx = {}
        for agent, key in zip(agents, self._neighborhood.neighbors.keys()):
            self._neighborhood.idx[agent] = key

    def _recreate_rtree(self, new_agents=None):
        """Create a new rtree index from agents geometries."""

        if new_agents is None:
            new_agents = []
        old_agents = list(self.agents)
        agents = old_agents + new_agents

        # Bulk insert agents
        index_data = ((id(agent), agent.geometry.bounds, None) for agent in agents)

        self.idx = index.Index(index_data)
        self.idx.agents = {id(agent): agent for agent in agents}

    def add_agents(self, agents):
        """Add a list of GeoAgents to the layer without checking their crs.

        GeoAgents must have the same crs to avoid incorrect spatial indexing results.
        To change the crs of a GeoAgent, use `GeoAgent.to_crs()` method. Refer to
        `GeoSpace._check_agent()` as an example.
        This function may also be called with a single GeoAgent.

        Args:
            agents: List of GeoAgents, or a single GeoAgent, to be added into the layer.
        """
        if isinstance(agents, GeoAgent):
            agent = agents
            self.idx.insert(id(agent), agent.geometry.bounds, None)
            self.idx.agents[id(agent)] = agent
        else:
            self._recreate_rtree(agents)

    def remove_agent(self, agent):
        """Remove an agent from the layer."""
        self.idx.delete(id(agent), agent.geometry.bounds)
        del self.idx.agents[id(agent)]

    def get_relation(self, agent, relation):
        """Return a list of related agents.

        Args:
            agent: the agent for which to compute the relation
            relation: must be one of 'intersects', 'within', 'contains',
                'touches'
            other_agents: A list of agents to compare against.
                Omit to compare against all other agents of the layer.
        """
        possible_agents = self._get_rtree_intersections(agent.geometry)
        for other_agent in possible_agents:
            if getattr(agent.geometry, relation)(other_agent.geometry):
                yield other_agent

    def get_intersecting_agents(self, agent, other_agents=None):
        intersecting_agents = self.get_relation(agent, "intersects")
        return intersecting_agents

    def get_neighbors_within_distance(
        self, agent, distance, center=False, relation="intersects"
    ):
        """Return a list of agents within `distance` of `agent`.

        Distance is measured as a buffer around the agent's geometry,
        set center=True to calculate distance from center.
        """
        if center:
            geometry = agent.geometry.centroid.buffer(distance)
        else:
            geometry = agent.geometry.buffer(distance)
        possible_neighbors = self._get_rtree_intersections(geometry)
        prepared_geometry = prep(geometry)
        for other_agent in possible_neighbors:
            if getattr(prepared_geometry, relation)(other_agent.geometry):
                yield other_agent

    def agents_at(self, pos):
        """Return a list of agents at given pos."""
        if not isinstance(pos, Point):
            pos = Point(pos)
        return self.get_relation(pos, "within")

    def distance(self, agent_a, agent_b):
        """Return distance of two agents."""
        return agent_a.geometry.distance(agent_b.geometry)

    def get_neighbors(self, agent):
        """Get (touching) neighbors of an agent."""
        if not self._neighborhood or self._neighborhood.agents != self.agents:
            self._create_neighborhood()

        idx = self._neighborhood.idx[agent]
        neighbors_idx = self._neighborhood.neighbors[idx]
        neighbors = [self.agents[i] for i in neighbors_idx]
        return neighbors
