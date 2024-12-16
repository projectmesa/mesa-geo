import dataclasses
import warnings
from dataclasses import dataclass

import geopandas as gpd
import ipyleaflet
import solara
import xyzservices
from folium.utilities import image_to_url
from mesa.visualization.utils import update_counter
from shapely.geometry import Point, mapping

from mesa_geo.raster_layers import RasterBase, RasterLayer
from mesa_geo.tile_layers import LeafletOption, RasterWebTile


def make_geospace_leaflet(
    agent_portrayal,
    view=None,
    tiles=xyzservices.providers.OpenStreetMap.Mapnik,
    **kwargs,
):
    warnings.warn(
        "make_geospace_leaflet is deprecated, use make_geospace_component instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return make_geospace_component(agent_portrayal, view, tiles, **kwargs)


def make_geospace_component(
    agent_portrayal,
    view=None,
    tiles=xyzservices.providers.OpenStreetMap.Mapnik,
    **kwargs,
):
    def MakeSpaceMatplotlib(model):
        return GeoSpaceLeaflet(model, agent_portrayal, view, tiles, **kwargs)

    return MakeSpaceMatplotlib


@solara.component
def GeoSpaceLeaflet(model, agent_portrayal, view, tiles, **kwargs):
    update_counter.get()
    map_drawer = MapModule(portrayal_method=agent_portrayal, tiles=tiles)
    model_view = map_drawer.render(model)

    if view is None:
        # longlat [min_x, min_y, max_x, max_y] to latlong [min_y, min_x, max_y, max_x]
        transformed_xx, transformed_yy = model.space.transformer.transform(
            xx=[model.space.total_bounds[0], model.space.total_bounds[2]],
            yy=[model.space.total_bounds[1], model.space.total_bounds[3]],
        )
        view = [
            (transformed_yy[0] + transformed_yy[1]) / 2,
            (transformed_xx[0] + transformed_xx[1]) / 2,
        ]

    layers = (
        [ipyleaflet.TileLayer.element(url=map_drawer.tiles["url"])] if tiles else []
    )
    for layer in model_view["layers"]["rasters"]:
        layers.append(
            ipyleaflet.ImageOverlay(
                url=layer["url"],
                bounds=layer["bounds"],
            )
        )
    for layer in model_view["layers"]["vectors"]:
        layers.append(ipyleaflet.GeoJSON(element=layer))
    ipyleaflet.Map.element(
        center=view,
        layers=[
            *layers,
            ipyleaflet.GeoJSON.element(data=model_view["agents"][0]),
            *model_view["agents"][1],
        ],
        **kwargs,
    )


@dataclass
class LeafletViz:
    """A dataclass defining the portrayal of a GeoAgent in Leaflet map.

    The fields are defined to be consistent with GeoJSON options in
    Leaflet.js: https://leafletjs.com/reference.html#geojson
    """

    style: dict[str, LeafletOption] | None = None
    popupProperties: dict[str, LeafletOption] | None = None  # noqa: N815


class MapModule:
    """A MapModule for Leaflet maps that uses a user-defined portrayal method
    to generate a portrayal of a raster Cell or a GeoAgent.

    For a raster Cell, the portrayal method should return a (r, g, b, a) tuple.

    For a GeoAgent, the portrayal method should return a dictionary.
        - For a Line or a Polygon, the available options can be found at: https://leafletjs.com/reference.html#path-option
        - For a Point, the available options can be found at: https://leafletjs.com/reference.html#circlemarker-option
        - In addition, the portrayal dictionary can contain a "description" key, which will be used as the popup text.
    """

    def __init__(
        self,
        portrayal_method,
        tiles,
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
        :param scroll_wheel_zoom: Boolean whether not user can scroll on map with mouse wheel
        :param tiles: An optional tile layer to use. Can be a :class:`RasterWebTile` or
            a :class:`xyzservices.TileProvider`. Default is `xyzservices.providers.OpenStreetMap.Mapnik`.

            If the tile provider requires registration, you can pass the API key inside
            the `options` parameter of the :class:`RasterWebTile` constructor.

            For example, to use the `Mapbox` raster tile provider, you can use:

            .. code-block:: python

                import mesa_geo as mg

                mg.RasterWebTile(
                    url="https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token={access_token}",
                    options={
                        "access_token": "my-private-ACCESS_TOKEN",
                        "attribution": '&copy; <a href="https://www.mapbox.com/about/maps/" target="_blank">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors <a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>',
                    },
                )

            Note that `access_token` can have different names depending on the provider,
            e.g., `api_key` or `key`. You can check the documentation of the provider
            for more details.

            `xyzservices` provides a list of providers requiring registration as well:
            https://xyzservices.readthedocs.io/en/stable/registration.html

            For example, you may use the following code to use the `Mapbox` provider:

            .. code-block:: python

                import xyzservices.providers as xyz

                xyz.MapBox(id="<insert map_ID here>", accessToken="my-private-ACCESS_TOKEN")

        :param scale_options: A dictionary of options for the map scale. Default is None
            (no map scale). The available options can be found at: https://leafletjs.com/reference.html#control-scale-option
        """
        self.portrayal_method = portrayal_method
        self._crs = "epsg:4326"

        if isinstance(tiles, xyzservices.TileProvider):
            tiles = RasterWebTile.from_xyzservices(tiles).to_dict()
        self.tiles = tiles

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
                    layer_to_render = layer.to_image(
                        colormap=self.portrayal_method
                    ).to_crs(self._crs)
                else:
                    layer_to_render = layer.to_crs(self._crs)
                layers["rasters"].append(
                    {
                        "url": image_to_url(
                            layer_to_render.values.transpose([1, 2, 0])
                        ),
                        # longlat [min_x, min_y, max_x, max_y] to latlong [[min_y, min_x], [max_y, max_x]]
                        "bounds": [
                            [
                                layer_to_render.total_bounds[1],
                                layer_to_render.total_bounds[0],
                            ],
                            [
                                layer_to_render.total_bounds[3],
                                layer_to_render.total_bounds[2],
                            ],
                        ],
                    }
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

    def _get_marker(self, location, properties):
        """
        takes point objects and transforms them to ipyleaflet marker objects

        allowed marker types are point marker types from ipyleaflet
        https://ipyleaflet.readthedocs.io/en/latest/layers/index.html

        default is circle with radius 5

        Parameters
        ----------
        location: iterable
            iterable of location in models geometry

        properties : dict
            properties passed in through agent portrayal


        Returns
        -------
        ipyleaflet marker element

        """

        if "marker_type" not in properties:  # make circle default marker type
            properties["marker_type"] = "Circle"
            properties["radius"] = 5

        marker = properties["marker_type"]
        if marker == "Circle":
            return ipyleaflet.Circle(location=location, **properties)
        elif marker == "CircleMarker":
            return ipyleaflet.CircleMarker(location=location, **properties)
        elif marker == "Marker":
            return ipyleaflet.Marker(location=location, **properties)
        elif marker == "Icon":
            icon_url = properties["icon_url"]
            icon_size = properties.get("icon_size", [20, 20])
            icon_properties = properties.get("icon_properties", {})
            icon = ipyleaflet.Icon(
                icon_url=icon_url, icon_size=icon_size, **icon_properties
            )
            return ipyleaflet.Marker(location=location, icon=icon, **properties)
        elif marker == "AwesomeIcon":
            name = properties["name"]
            icon_properties = properties.get("icon_properties", {})
            icon = ipyleaflet.AwesomeIcon(name=name, **icon_properties)
            return ipyleaflet.Marker(location=location, icon=icon, **properties)

        else:
            raise ValueError(
                f"Unsupported marker type:{marker}",
            )

    def _render_agents(self, model):
        feature_collection = {"type": "FeatureCollection", "features": []}
        point_markers = []
        agent_portrayal = {}
        for agent in model.space.agents:
            transformed_geometry = agent.get_transformed_geometry(
                model.space.transformer
            )

            if self.portrayal_method:
                properties = self.portrayal_method(agent)
                agent_portrayal = LeafletViz(
                    popupProperties=properties.pop("description", None)
                )
                if isinstance(agent.geometry, Point):
                    location = mapping(transformed_geometry)
                    # for some reason points are reversed
                    location = (location["coordinates"][1], location["coordinates"][0])
                    point_markers.append(self._get_marker(location, properties))
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
        return [feature_collection, point_markers]
