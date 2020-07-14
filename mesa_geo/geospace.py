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
            crs: Project coordinate reference system
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
        self.crs = pyproj.CRS(crs)
        self.WGS84 = pyproj.CRS("epsg:4326")
        self.Transformer = pyproj.Transformer.from_crs(
            self.crs, self.WGS84, skip_equivalent=True, always_xy=True
        )

        self.bbox = None
        self._neighborhood = None

        # Set up rtree index
        self.idx = index.Index()
        self.idx.agents = {}

    def add_agents(self, agents):
        """Add a list of GeoAgents to the Geospace.

        GeoAgents must have a shape attribute. This function may also be called
        with a single GeoAgent."""
        if isinstance(agents, GeoAgent):
            agent = agents
            if hasattr(agent, "shape"):
                self.idx.insert(id(agent), agent.shape.bounds, None)
                self.idx.agents[id(agent)] = agent
            else:
                raise AttributeError("GeoAgents must have a shape attribute")
        else:
            self._recreate_rtree(agents)

        self.update_bbox()

    def remove_agent(self, agent):
        """Remove an agent from the GeoSpace."""
        self.idx.delete(id(agent), agent.shape.bounds)
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
        related_agents = []
        possible_agents = self._get_rtree_intersections(agent.shape)
        for other_agent in possible_agents:
            if getattr(agent.shape, relation)(other_agent.shape):
                yield other_agent

    def _get_rtree_intersections(self, shape):
        """Calculate rtree intersections for candidate agents."""
        return (self.idx.agents[i] for i in self.idx.intersection(shape.bounds))

    def get_intersecting_agents(self, agent, other_agents=None):
        intersecting_agents = self.get_relation(agent, "intersects")
        return intersecting_agents

    def get_neighbors_within_distance(
        self, agent, distance, center=False, relation="intersects"
    ):
        """Return a list of agents within `distance` of `agent`.

        Distance is measured as a buffer around the agent's shape,
        set center=True to calculate distance from center.
        """
        if center:
            shape = agent.shape.center().buffer(distance)
        else:
            shape = agent.shape.buffer(distance)
        possible_neighbors = self._get_rtree_intersections(shape)
        prepared_shape = prep(shape)
        for other_agent in possible_neighbors:
            if getattr(prepared_shape, relation)(other_agent.shape):
                yield other_agent

    def agents_at(self, pos):
        """Return a list of agents at given pos."""
        if not isinstance(pos, Point):
            pos = Point(pos)
        return self.get_relation(pos, "within")

    def distance(self, agent_a, agent_b):
        """Return distance of two agents."""
        return agent_a.shape.distance(agent_b.shape)

    def _create_neighborhood(self):
        """Create a neighborhood graph of all agents."""
        agents = self.agents
        shapes = [agent.shape for agent in agents]
        self._neighborhood = weights.contiguity.Queen.from_iterable(shapes)
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
        """Create a new rtree index from agents shapes."""

        if new_agents is None:
            new_agents = []
        old_agents = list(self.agents)
        agents = old_agents + new_agents

        # Bulk insert agents
        index_data = ((id(agent), agent.shape.bounds, None) for agent in agents)

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
        return list(self.idx.agents.values())

    @property
    def __geo_interface__(self):
        """Return a GeoJSON FeatureCollection."""
        features = [a.__geo_interface__() for a in self.agents]
        return {"type": "FeatureCollection", "features": features}
