"""mesa_geo Agent-Based Modeling Framework.

Core Objects: GeoSpace, GeoAgent

"""
import datetime

from mesa_geo import visualization
from mesa_geo.geoagent import AgentCreator, GeoAgent
from mesa_geo.geospace import GeoSpace
from mesa_geo.raster_layers import Cell, ImageLayer, RasterLayer
from mesa_geo.tile_layers import RasterWebTile, WMSWebTile

__all__ = [
    "GeoSpace",
    "GeoAgent",
    "AgentCreator",
    "ImageLayer",
    "Cell",
    "RasterLayer",
    "visualization",
    "RasterWebTile",
    "WMSWebTile",
]

__title__ = "Mesa-Geo"
__version__ = "0.7.1"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.timezone.utc).date().year
__copyright__ = f"Copyright {_this_year} Project Mesa-Geo Team"
