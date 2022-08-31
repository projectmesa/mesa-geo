"""
GeoBase
-------
"""

from __future__ import annotations

from abc import abstractmethod

import numpy as np
import pyproj


class GeoBase:
    """
    Base class for all geo-related classes.
    """

    _crs: pyproj.CRS | None

    def __init__(self, crs=None):
        """
        Create a new GeoBase object.

        :param crs: The coordinate reference system of the object.
        """

        self.crs = crs

    @property
    @abstractmethod
    def total_bounds(self) -> np.ndarray | None:
        """
        Return the bounds of the object in [min_x, min_y, max_x, max_y] format.

        :return: The bounds of the object in [min_x, min_y, max_x, max_y] format.
        :rtype: np.ndarray | None
        """

        raise NotImplementedError

    @property
    def crs(self) -> pyproj.CRS | None:
        """
        Return the coordinate reference system of the object.
        """

        return self._crs

    @crs.setter
    def crs(self, crs):
        """
        Set the coordinate reference system of the object.
        """

        self._crs = pyproj.CRS.from_user_input(crs) if crs else None

    @abstractmethod
    def to_crs(self, crs, inplace=False) -> GeoBase | None:
        """
        Transform the object to a new coordinate reference system.

        :param crs: The coordinate reference system to transform to.
        :param inplace: Whether to transform the object in place or
            return a new object. Defaults to False.

        :return: The transformed object if not inplace.
        :rtype: GeoBase | None
        """
        raise NotImplementedError

    def _to_crs_check(self, crs) -> None:
        """
        Check that the object has a coordinate reference system to
        transform from and to.
        """
        if self.crs is None:
            raise TypeError("Need a valid crs to transform from.")
        if crs is None:
            raise TypeError("Need a valid crs to transform to.")
