from mesa_geo.geoagent import GeoAgent
import pyproj
from rtree import index
from shapely.ops import transform as s_transform
from functools import partial
from pysal.lib import weights
from shapely.geometry import Point


class GeoSpace:
    def __init__(self, crs=None):
        """Base class for GIS enabled mesa modeling.

        mesa-geo provides an easy way to add agents from a GeoJSON object or
        shapfiles. Please note that the GeoJSON specifications require all
        shapes to be in the geographic system WGS84. Therefore you should
        consider setting a coordinate reference system via the `crs` keyword.
        All agents added from GeoJSON objects are then automatically
        transformed into that system.
        If `crs` is not set, epsg:3857 (Web Mercator) is used as default.
        However, this system is only accurate at the equator and errors
        increase with latitude.

        Properties:
            crs: Project ´coordinate reference system
            idx: R-tree index for fast spatial queries
            bbox: Bounding box of all agents within the GeoSpace
            agents: List of all agents in the Geospace

        Methods:
            add_agent: add single agent to the GeoSpace.
            remove_agent: Remove agent from GeoSpace
            create_agents_from_GeoJSON: Create agents from a GeoJSON object
            create_agents_from_shapefile: Create agents from a shapefile
            transform: Transforms a shape from one crs to another
            agents_at: List all agents at a specific position
            distance: Calculate distance between to agents
            get_neighbors: Returns a list of (touching) neighbors
            get_intersecting_agents: Returns list of agents that intersect
            get_agents_within: Returns a list of agents within
            get_agent_contains: Returns a list of agents contained
            get_agents_touches: Returns a list of agents that touch
            update_bbox: Update the bounding box of the GeoSpace
        """
        if not crs:
            crs = "epsg:3857"
            # TODO raise a warning
        self.crs = pyproj.Proj(init=crs)
        self.WGS84 = pyproj.Proj(init="epsg:4326")

        self.agents = []
        self.bbox = None
        self._neighborhood = None

        # Set up rtree index
        self.idx = index.Index()
        self.idx.maxid = 0

    def add_agent(self, agent):
        """Add a single GeoAgent to the Geospace."""
        if isinstance(agent, GeoAgent):
            if hasattr(agent, "shape"):
                self.agents.append(agent)
                self.idx.insert(self.idx.maxid + 1, agent.shape.bounds)
                self.idx.maxid += 1
                self.update_bbox()
            else:
                raise AttributeError("GeoAgents must have a shape attribute")
        else:
            raise TypeError("Agent is not an instance of GeoAgent")

    def remove_agent(self, agent):
        """Remove an agent from the GeoSpace."""
        self.agents.remove(agent)
        self.idx.delete(agent.idx_id, agent.shape.bounds)
        self.update_bbox()

    def transform(self, from_crs, to_crs, shape):
        """Transform a shape from one crs to another."""
        project = partial(pyproj.transform, from_crs, to_crs)
        return s_transform(project, shape)

    def get_relation(self, agent, relation, other_agents=None):
        """Return a list of related agents.

        Args:
            relation: must be one of 'intersects', 'within', 'contains',
                'touches'
            agent: the agent for which to compute the relation
            other_agents: A list of agents to compare against.
                Omit to compare against all other agents of the GeoSpace
        """
        related_agents = []
        possible_agents = self._get_rtree_intersections(agent, other_agents)
        if possible_agents:
            for other_agent in possible_agents:
                if getattr(agent.shape, relation)(other_agent.shape):
                    related_agents.append(other_agent)
        return related_agents

    def _get_rtree_intersections(self, agent, other_agents=None):
        """Calculate rtree intersections for candidate agents."""
        intersections = []
        if not other_agents:
            other_agents = self.agents
        intersect_ids = list(self.idx.intersection(agent.shape.bounds))
        intersections = (a for a in other_agents if a.idx_id in intersect_ids)
        return intersections

    def get_intersecting_agents(self, agent, other_agents=None):
        intersecting_agents = self.get_relation("intersects", agent, other_agents)
        return intersecting_agents

    def get_neighbors_within_distance(
        self, agent, distance, center=False, relation="intersects"
    ):
        """Return a list of agents within `distance` of `agent`.

        Distance is measured as a buffer around the agent's shape,
        set center=True to calculate distance from center.
        """
        old_shape = agent.shape
        if center:
            agent.shape = agent.shape.center().buffer(distance)
        else:
            agent.shape = agent.shape.buffer(distance)
        neighbors = self.get_relation(relation, agent)
        agent.shape = old_shape
        return neighbors

    def agents_at(self, pos):
        """Return a list of agents at given pos."""
        if not isinstance(pos, Point):
            pos = Point(pos)
        return self.get_relation("within", pos)

    def distance(self, agent_a, agent_b):
        """Return distance of two agents."""
        return agent_a.shape.distance(agent_b.shape)

    def _create_neighborhood(self):
        """Create a neighborhood graph of all agents."""
        agents = self.agents
        shapes = [agent.shape for agent in agents]
        self._neighborhood = weights.Contiguity.Queen.from_iterable(shapes)
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

    def create_rtree(self):
        """Create a new rtree index from agents shapes."""
        shapes = []
        for i, agent in enumerate(self.agents):
            agent.idx_id = i
            shapes.append(agent.shape)

        # Bulk load the shapes
        def data_gen():
            for index_id, shape in enumerate(shapes):
                yield (index_id, shape.bounds, shape)

        self.idx = index.Index(data_gen())
        self.idx.maxid = len(shapes)

    def update_bbox(self, bbox=None):
        """Update bounding box of the GeoSpace."""
        if bbox:
            self.bbox = bbox
        elif not self.agents:
            self.bbox = None
        else:
            self.bbox = self.idx.bounds

    @property
    def __geo_interface__(self):
        """Return a GeoJSON FeatureCollection."""
        features = [a.__geo_interface__() for a in self.agents]
        return {"type": "FeatureCollection", "features": features}
