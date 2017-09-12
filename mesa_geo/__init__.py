# -*- coding: utf-8 -*-
"""
GeoMesa Agent-Based Modeling Framework

Core Objects: GeoSpace, GeoAgent and Patch.

"""
import datetime

from .geospace import GeoSpace
from .geoagent import GeoAgent


__all__ = ["GeoSpace", "GeoAgent"]

__title__ = 'mesa-geo'
__version__ = '0.0.1'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright %s Project Mesa Team' % datetime.date.today().year