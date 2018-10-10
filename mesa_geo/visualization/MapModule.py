from mesa_geo.visualization.ModularVisualization import VisualizationElement


class MapModule(VisualizationElement):
    """A MapModule for Leaflet maps."""

    package_includes = ["leaflet.js", "LeafletMap.js"]
    local_includes = []

    def __init__(
        self, portrayal_method, view=[0, 0], zoom=10, map_height=500, map_width=500
    ):
        self.portrayal_method = portrayal_method
        self.map_height = map_height
        self.map_width = map_width
        self.view = view
        new_element = "new MapModule({}, {}, {}, {})"
        new_element = new_element.format(view, zoom, map_width, map_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        featurecollection = dict(type="FeatureCollection", features=[])
        for _, agent in enumerate(model.grid.agents):
            shape = agent.__geo_interface__()
            portrayal = self.portrayal_method(agent)
            for key, value in portrayal.items():
                shape["properties"][key] = value
                featurecollection["features"].append(shape)
        return featurecollection
