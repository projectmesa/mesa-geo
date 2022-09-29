from __future__ import annotations

import dataclasses
import os
from dataclasses import dataclass
from typing import Union

import geopandas as gpd
from folium.utilities import image_to_url
from mesa.visualization.ModularVisualization import VisualizationElement
from shapely.geometry import mapping, Point

from mesa_geo.raster_layers import RasterLayer, RasterBase

LeafletOption = Union[str, bool, int, float]


@dataclass
class LeafletPortrayal:
    """A dataclass defining the portrayal of a GeoAgent in Leaflet map.

    The fields are defined to be consistent with GeoJSON options in
    Leaflet.js: https://leafletjs.com/reference.html#geojson
    """

    style: dict[str, LeafletOption] | None = None
    pointToLayer: dict[str, LeafletOption] | None = None
    popupProperties: dict[str, LeafletOption] | None = None


class MapModule(VisualizationElement):
    """A MapModule for Leaflet maps that uses a user-defined portrayal method
    to generate a portrayal of a raster Cell or a GeoAgent.

    For a raster Cell, the portrayal method should return a (r, g, b, a) tuple.

    For a GeoAgent, the portrayal method should return a dictionary.
        For a Line or a Polygon, the available options can be found at: https://leafletjs.com/reference.html#path-option
        For a Point, the available options can be found at: https://leafletjs.com/reference.html#circlemarker-option
        In addition, the portrayal dictionary can contain a "description" key, which will be used as the popup text.
    """

    local_includes = [
        "js/MapModule.js",
        "css/external/leaflet.css",
        "js/external/leaflet.js",
    ]
    local_dir = os.path.dirname(__file__) + "/../templates"

    def __init__(
        self,
        portrayal_method=None,
        view=None,
        zoom=None,
        map_width=500,
        map_height=500,
    ):
        """
        Create a new MapModule.

        :param portrayal_method: A method that takes a GeoAgent (or a Cell) and returns
            a dictionary of options (or a (r, g, b, a) tuple) for Leaflet.js.
        :param view: The initial view of the map. Must be set together with zoom.
            If both view and zoom are None, the map will be centered on the total bounds
            of the space. Default is None.
        :param zoom: The initial zoom level of the map. Must be set together with view.
            If both view and zoom are None, the map will be centered on the total bounds
            of the space. Default is None.
        :param map_width: The width of the map in pixels. Default is 500.
        :param map_height: The height of the map in pixels. Default is 500.
        """
        self.portrayal_method = portrayal_method
        self._crs = "epsg:4326"

        if view is None and zoom is None:
            new_element = f"new MapModule(null, null, {map_width}, {map_height})"
        else:
            new_element = f"new MapModule({view}, {zoom}, {map_width}, {map_height})"
        self.js_code = f"elements.push({new_element});"

    def render(self, model):
        return {
            "layers": self._render_layers(model),
            "agents": self._render_agents(model),
        }

    def _render_layers(self, model):
        layers = {"rasters": [], "vectors": [], "total_bounds": []}
        for layer in model.space.layers:
            if isinstance(layer, RasterBase):
                if isinstance(layer, RasterLayer):
                    layer = layer.to_image(colormap=self.portrayal_method)
                layers["rasters"].append(
                    image_to_url(layer.to_crs(self._crs).values.transpose([1, 2, 0]))
                )
            elif isinstance(layer, gpd.GeoDataFrame):
                layers["vectors"].append(
                    layer.to_crs(self._crs)[["geometry"]].__geo_interface__
                )
        # longlat [min_x, min_y, max_x, max_y] to latlong [min_y, min_x, max_y, max_x]
        if model.space.total_bounds is not None:
            transformed_xx, transformed_yy = model.space.transformer.transform(
                xx=[model.space.total_bounds[0], model.space.total_bounds[2]],
                yy=[model.space.total_bounds[1], model.space.total_bounds[3]],
            )
            layers["total_bounds"] = [
                [transformed_yy[0], transformed_xx[0]],  # min_y, min_x
                [transformed_yy[1], transformed_xx[1]],  # max_y, max_x
            ]
        return layers

    def _render_agents(self, model):
        feature_collection = {"type": "FeatureCollection", "features": []}
        for agent in model.space.agents:
            transformed_geometry = agent.get_transformed_geometry(
                model.space.transformer
            )
            agent_portrayal = {}
            if self.portrayal_method:
                properties = self.portrayal_method(agent)
                agent_portrayal = LeafletPortrayal(
                    popupProperties=properties.pop("description", None)
                )
                if isinstance(agent.geometry, Point):
                    agent_portrayal.pointToLayer = properties
                else:
                    agent_portrayal.style = properties
                agent_portrayal = dataclasses.asdict(
                    agent_portrayal,
                    dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
                )
            feature_collection["features"].append(
                {
                    "type": "Feature",
                    "geometry": mapping(transformed_geometry),
                    "properties": agent_portrayal,
                }
            )
        return feature_collection
