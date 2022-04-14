import pyproj
from libpysal import weights
from rtree import index
from shapely.geometry import Point
from shapely.prepared import prep

from mesa_geo.geoagent import GeoAgent


class GeoSpace:
    def __init__(self, crs="epsg:3857"):
        """Create a GeoSpace for GIS enabled mesa modeling.

        Args:
            crs: Coordinate reference system of the GeoSpace
                If `crs` is not set, epsg:3857 (Web Mercator) is used as default.
                However, this system is only accurate at the equator and errors
                increase with latitude.

        Properties:
            crs: Coordinate reference system of the GeoSpace
            transformer: A pyproj.Transformer that transforms the GeoSpace into
                         epsg:4326. Mainly used for GeoJSON serialization.
            idx: R-tree index for fast spatial queries
            bbox: Bounding box of all agents within the GeoSpace
            agents: List of all agents in the Geospace

        Methods:
            add_agents: add a list or a single GeoAgent.
            remove_agent: Remove a single agent from GeoSpace
            agents_at: List all agents at a specific position
            distance: Calculate distance between two agents
            get_neighbors: Returns a list of (touching) neighbors
            get_intersecting_agents: Returns list of agents that intersect
            get_agents_within: Returns a list of agents within
            get_agent_contains: Returns a list of agents contained
            get_agents_touches: Returns a list of agents that touch
            update_bbox: Update the bounding box of the GeoSpace
        """
        self._crs = pyproj.CRS.from_user_input(crs)
        self._transformer = pyproj.Transformer.from_crs(
            crs_from=self.crs, crs_to="epsg:4326", always_xy=True
        )

        self.bbox = None
        self._neighborhood = None

        # Set up rtree index
        self.idx = index.Index()
        self.idx.agents = {}

    @property
    def crs(self):
        """
        Return the coordinate reference system of the GeoSpace.
        """
        return self._crs

    @property
    def transformer(self):
        """
        Return the pyproj.Transformer that transforms the GeoSpace into
        epsg:4326. Mainly used for GeoJSON serialization.
        """
        return self._transformer

    def add_agents(self, agents, auto_convert_crs=False):
        """Add a list of GeoAgents to the Geospace.

        GeoAgents must have a geometry attribute. This function may also be called
        with a single GeoAgent.

        Args:
            agents: List of GeoAgents, or a single GeoAgent, to be added into GeoSpace.
            auto_convert_crs: Whether to automatically convert GeoAgent of different
                crs into the crs of the GeoSpace. Default to False.

        Raises:
            ValueError: If GeoAgent of different crs is added into the GeoSpace, while
                `self.auto_convert_crs` is set to False.
        """
        if isinstance(agents, GeoAgent):
            agent = agents
            if hasattr(agent, "geometry"):
                if not self.crs.is_exact_same(agent.crs):
                    if auto_convert_crs:
                        agent.to_crs(self.crs)
                    else:
                        raise ValueError(
                            f"Inconsistent crs: {agent.__class__.__name__} is of crs {agent.crs.to_string()}, "
                            f"different from the crs of {self.__class__.__name__} - {self.crs.to_string()}. "
                            "Please check your crs settings, or set `auto_convert_crs` to `True` to allow "
                            "automatic crs conversion of GeoAgents to GeoSpace."
                        )
                self.idx.insert(id(agent), agent.geometry.bounds, None)
                self.idx.agents[id(agent)] = agent
            else:
                raise AttributeError("GeoAgents must have a geometry attribute")
        else:
            for agent in agents:
                if not self.crs.is_exact_same(agent.crs):
                    if auto_convert_crs:
                        agent.to_crs(self.crs)
                    else:
                        raise ValueError(
                            f"Inconsistent crs: {agent.__class__.__name__} is of crs {agent.crs.to_string()}, "
                            f"different from the crs of {self.__class__.__name__} - {self.crs.to_string()}. "
                            "Please check your crs settings, or set `auto_convert_crs` to `True` to allow "
                            "automatic crs conversion of GeoAgents to GeoSpace."
                        )
            self._recreate_rtree(agents)

        self.update_bbox()

    def remove_agent(self, agent):
        """Remove an agent from the GeoSpace."""
        self.idx.delete(id(agent), agent.geometry.bounds)
        del self.idx.agents[id(agent)]
        self.update_bbox()

    def get_relation(self, agent, relation):
        """Return a list of related agents.

        Args:
            agent: the agent for which to compute the relation
            relation: must be one of 'intersects', 'within', 'contains',
                'touches'
            other_agents: A list of agents to compare against.
                Omit to compare against all other agents of the GeoSpace
        """
        possible_agents = self._get_rtree_intersections(agent.geometry)
        for other_agent in possible_agents:
            if getattr(agent.geometry, relation)(other_agent.geometry):
                yield other_agent

    def _get_rtree_intersections(self, geometry):
        """Calculate rtree intersections for candidate agents."""
        return (self.idx.agents[i] for i in self.idx.intersection(geometry.bounds))

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
            geometry = agent.geometry.center().buffer(distance)
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

    def _create_neighborhood(self):
        """Create a neighborhood graph of all agents."""
        agents = self.agents
        geometries = [agent.geometry for agent in agents]
        self._neighborhood = weights.contiguity.Queen.from_iterable(geometries)
        self._neighborhood.agents = agents
        self._neighborhood.idx = {}
        for agent, key in zip(agents, self._neighborhood.neighbors.keys()):
            self._neighborhood.idx[agent] = key

    def get_neighbors(self, agent):
        """Get (touching) neighbors of an agent."""
        if not self._neighborhood or self._neighborhood.agents != self.agents:
            self._create_neighborhood()

        idx = self._neighborhood.idx[agent]
        neighbors_idx = self._neighborhood.neighbors[idx]
        neighbors = [self.agents[i] for i in neighbors_idx]
        return neighbors

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

    def update_bbox(self, bbox=None):
        """Update bounding box of the GeoSpace."""
        if bbox:
            self.bbox = bbox
        elif not self.agents:
            self.bbox = None
        else:
            self.bbox = self.idx.bounds

    @property
    def agents(self):
        """
        Return a list of all agents in the Geospace.
        """
        return list(self.idx.agents.values())

    @property
    def __geo_interface__(self):
        """Return a GeoJSON FeatureCollection."""
        features = [a.__geo_interface__() for a in self.agents]
        return {"type": "FeatureCollection", "features": features}
