"""mesa_geo Agent-Based Modeling Framework.

Core Objects: GeoSpace, GeoAgent

"""
import datetime

from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo.geospace import GeoSpace, ImageLayer

__all__ = ["GeoSpace", "GeoAgent", "AgentCreator", "ImageLayer"]

__title__ = "Mesa-Geo"
__version__ = "0.2.0"
__license__ = "Apache 2.0"
__copyright__ = "Copyright %s Project Mesa-Geo Team" % datetime.date.today().year
