"""
Tile Layers
-----------
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Union

import xyzservices

LeafletOption = Union[str, bool, int, float]


@dataclass
class RasterWebTile:
    """
    A class for the background tile layer of Leaflet map that uses a raster
    tile server as the source of the tiles.

    The available options can be found at: https://leafletjs.com/reference.html#tilelayer
    """

    url: str
    options: dict[str, LeafletOption] | None = None
    kind: str = "raster_web_tile"

    @classmethod
    def from_xyzservices(cls, provider: xyzservices.TileProvider) -> RasterWebTile:
        """
        Create a RasterWebTile from an xyzservices TileProvider.

        :param provider: The xyzservices TileProvider to use.
        :return: A RasterWebTile instance.
        """
        provider_dict = dict(provider)
        url = provider_dict.pop("url")
        attribution = provider_dict.pop("html_attribution")
        provider_dict.update({"attribution": attribution})
        return cls(url=url, options=provider_dict)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class WMSWebTile(RasterWebTile):
    """
    A class for the background tile layer of Leaflet map that uses a WMS
    service as the source of the tiles.

    The available options can be found at: https://leafletjs.com/reference.html#tilelayer-wms
    """

    kind: str = "wms_web_tile"
