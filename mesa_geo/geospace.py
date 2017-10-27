from mesa_geo.geoagent import GeoAgent
from mesa_geo.shapes import as_shape, Point
import pyproj
from rtree import index
from shapely.ops import transform as s_transform
from functools import partial


class GeoSpace:
    def __init__(self, bbox=None, crs=None):
        """Base class for GIS enabled mesa modeling.

        mesa-geo provides an easy way to add agents from a GeoJSON objects.
        Shapefiles are not yet supported by mesa-geo and should be converted
        to GeoJSON format prior to usage.
        Please note that the GeoJSON specifications require all shapes to be
        in the geographic system WGS84. Therefore you should consider setting
        a coordinate reference system via the `crs` keyword. All agents added
        from GeoJSON objects are then automatically transformed into that
        system and all calculations take place in that system.
        If `crs` is not set, epsg:3857 (Web Mercator) is used as default.
        However, this system is only accurate at the equator and errors
        increase with latitude.

        Properties:
            crs: Project crs that is used for all calculations
            idx: R-tree index for fast spatial queries
            bbox: Bounding box of all agents within the GeoSpace
            agents: List of all agents in the Geospace

        Methods:
            add_agent: add single agent to the GeoSpace.
            remove_agent: Remove agent from GeoSpace
            create_agents_from_GeoJSON: Create agents from GeoJSON object
            transform: Transforms a shape from one crs to another
            agents_at: List all agents at a specific position
            distance: Calculate distance between to agents
            get_intersecting_agents: Get agents that intersect with an agent
            get_agents_within: Get agents of which the agent is within
            get_agent_contains: Get agents who are contained by an agent
            get_agents_touches: Get agents that that an agent
            update_bbox: Update the bounding box of the GeoSpace
            create_rtree: Recalculate the R-tree of the GeoSpace
        """
        self.agents = []
        self.bbox = bbox
        if not crs:
            crs = 'epsg:3857'
            # TODO raise a warning
        self.crs = pyproj.Proj(init=crs)
        self.WGS84 = pyproj.Proj(init='epsg:4326')
        self.idx = index.Index()
        self.idx.maxid = 0

    def add_agent(self, agent):
        """Add a single GeoAgent to the Geospace."""
        if issubclass(agent, GeoAgent):
            if hasattr(agent, "shape"):
                self.agents.append(agent)
                self.idx.insert(self.idx.maxid + 1, agent.shape.bounds)
                self.idx.maxid += 1
            else:
                raise AttributeError("GeoSpace agents must have a shape")
        else:
            raise TypeError("Agent is not a subclass of GeoAgent")

    def remove_agent(self, agent):
        """Remove an agent from the GeoSpace."""
        self.agents.remove(agent)
        self.idx.delete(agent.idx_id, agent.shape.bounds)

    def create_agents_from_GeoJSON(self, GeoJSON, agent, set_attributes=True,
                                   **kwargs):
        """Create agents from a GeoJSON object.

        Args:
            GeoJSON: A GeoJSON object
            agent: GeoAgent class of the agent.
                   kwargs will be passed to this Class.
                   !! unique_id must be a string indicating the name of a
                   GeoJSON attribute that is used for the unique_id.
                   TODO: Allow iterators as unique_id or create unique_id
                   automatically (e.g. for GeoJSON geometries)
            set_attributes: If True set GeoAgent properties from GeoJSON
                            attributes
            kwargs: Additional parameters passed to GeoAgent.
                    Can be strings that indicate GeoJSON attributes to be used.
        """
        gj = GeoJSON
        geometries = ["Point", "MultiPoint", "LineString",
                      "MultiLineString", "Polygon", "MultiPolygon"]
        agents = []

        def create_agent(shape, kwargs):
            shape = self.transform(from_crs=pyproj.Proj(init='epsg:4326'),
                                   to_crs=self.crs,
                                   shape=shape)
            new_agent = agent(shape=shape, **kwargs)
            agents.append(new_agent)
            return new_agent

        def _set_attributes(new_agent, attributes):
            for key, value in attributes.items():
                setattr(new_agent, key, value)

        def create_agent_with_attributes(agent, shape, attributes, kwargs):
            new_agent = create_agent(shape, kwargs)
            if set_attributes:
                if isinstance(set_attributes, list):
                    new_attributes = dict.fromkeys(set_attributes &
                                                   attributes.keys())
                    for key in set_attributes:
                        new_attributes[key] = attributes[key]
                    attributes = new_attributes
                _set_attributes(new_agent, attributes)

        def update_kwargs(kwargs, attributes):
            for key, value in kwargs.items():
                if isinstance(value, str) and value in attributes.keys():
                    kwargs[key] = attributes.pop(value)
            return kwargs

        if gj['type'] in geometries:
            shape = as_shape(gj)
            create_agent(shape, kwargs)

        if gj['type'] == 'GeometryCollection':
            shapes = as_shape(gj)
            for shape in shapes:
                create_agent(shape, kwargs)

        if gj['type'] == 'Feature':
            shape, attributes = as_shape(gj)
            kwargs = update_kwargs(kwargs, attributes)
            create_agent_with_attributes(agent, shape, attributes, kwargs)

        if gj['type'] == "FeatureCollection":
            features = as_shape(gj)
            for shape, attributes in zip(*features):
                out_kwargs = kwargs.copy()
                out_kwargs = update_kwargs(out_kwargs, attributes)
                create_agent_with_attributes(agent, shape, attributes,
                                             out_kwargs)

        self.agents.extend(agents)
        self.create_rtree()

    def transform(self, from_crs, to_crs, shape):
        """Transform a shape from one crs to another."""
        project = partial(pyproj.transform,
                          from_crs,
                          to_crs)
        return s_transform(project, shape)

    def get_neighbors_within_distance(self, agent, distance,
                                      center=False,
                                      relation='intersects'):
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

    def get_relation(self, relation, agent, other_agents=None):
        """Return a list of related agents.

        relation: must be one of 'intersects', 'within', 'contains', 'touches'
        agent: the agent for which to compute the relation
        other_agents: A list of agents to compare against. Can be ommited to
                      compare against all other agents of the GeoSpace
        """
        related_agents = []
        possible_agents = self.get_rtree_intersections(agent, other_agents)
        if possible_agents:
            for other_agent in possible_agents:
                if getattr(agent.shape, relation)(other_agent.shape):
                    related_agents.append(other_agent)
        return related_agents

    def get_rtree_intersections(self, agent, other_agents=None):
        """Calculate rtree intersections for candidate agents."""
        intersections = []
        if not other_agents:
            other_agents = [a for a in self.agents if a != agent]
        intersect_ids = list(self.idx.intersection(agent.shape.bounds))
        for agent in other_agents:
            if agent.idx_id in intersect_ids:
                intersections.append(agent)
        return intersections

    def agents_at(self, pos):
        """Return a list of agents at given pos."""
        if not isinstance(pos, Point):
            pos = Point(pos)
        return self.get_relation('within', pos)

    def distance(self, agent_a, agent_b):
        """Return distance of two agents.

        Note: You can also use agent.shape.distance directly
        """
        return agent_a.shape.distance(agent_b.shape)

    def create_rtree(self):
        """Create a new rtree index from agents shapes."""
        shapes = []
        i = 0
        for i, agent in enumerate(self.agents):
            agent.idx_id = i
            shapes.append(agent.shape)

        index_ids = range(i)

        # Bulk load the shapes
        def data_gen():
            for index_id, shape in zip(index_ids, shapes):
                yield (index_id, shape.bounds, shape)

        self.idx = index.Index(data_gen())
        self.idx.maxid = i

    def update_bbox(self, bbox=None):
        """Update bounding box of the GeoSpace."""
        if bbox:
            self.bbox = bbox
        elif not self.agents:
            self.bbox = None
        else:
            self.bbox = self.idx.bounds

    def __geo_interface__(self):
        """Return a GeoJSON FeatureCollection."""
        features = [a.__geo_interface__() for a in self.agents]
        return {'type': 'FeatureCollection',
                'features': features}
