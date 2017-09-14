# -*- coding: utf-8 -*-
"""
GeoMesa Agent-Based Modeling Framework

Core Objects: GeoSpace, GeoAgent

"""
import datetime

from .geospace import GeoSpace
from .geoagent import GeoAgent


__all__ = ["GeoSpace", "GeoAgent"]

__title__ = 'mesa-geo'
__version__ = 'pre-release'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright %s Project GeoMesa Team' % datetime.date.today().year
