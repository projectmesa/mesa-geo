"""Utility functions used by mesa_geo."""

from functools import partial
import pyproj
from shapely.ops import transform as s_transform


def transform(shape, from_crs, to_crs):
    """Transform a shape from one crs to another."""
    project = partial(pyproj.transform, from_crs, to_crs)
    return s_transform(project, shape)
