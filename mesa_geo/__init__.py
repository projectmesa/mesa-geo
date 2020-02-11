"""mesa_geo Agent-Based Modeling Framework.

Core Objects: GeoSpace, GeoAgent

"""
import datetime

from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo.geospace import GeoSpace

__all__ = ["GeoSpace", "GeoAgent", "AgentCreator"]

__title__ = "mesa-geo"
__version__ = "0.1.2"
__license__ = "Apache 2.0"
__copyright__ = "Copyright %s Project mesa-geo Team" % datetime.date.today().year
