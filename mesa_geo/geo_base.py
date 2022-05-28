from __future__ import annotations

from abc import abstractmethod

import numpy as np
import pyproj


class GeoBase:
    _crs: pyproj.CRS | None

    def __init__(self, crs=None):
        self.crs = crs

    @property
    @abstractmethod
    def total_bounds(self) -> np.ndarray | None:
        raise NotImplementedError

    @property
    def crs(self) -> pyproj.CRS | None:
        return self._crs

    @crs.setter
    def crs(self, crs):
        self._crs = pyproj.CRS.from_user_input(crs) if crs else None

    @abstractmethod
    def to_crs(self, crs, inplace=False) -> GeoBase | None:
        raise NotImplementedError

    def _to_crs_check(self, crs) -> None:
        if self.crs is None:
            raise TypeError("Need a valid crs to transform from.")
        if crs is None:
            raise TypeError("Need a valid crs to transform to.")
