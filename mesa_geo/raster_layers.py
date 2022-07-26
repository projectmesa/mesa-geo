from __future__ import annotations

import copy
import itertools
import math
import uuid
from typing import (
    Tuple,
    List,
    Dict,
    Any,
    Set,
    cast,
    overload,
    Sequence,
    Iterator,
    Iterable,
    Type,
)

import numpy as np
import rasterio as rio
from affine import Affine
from mesa.agent import Agent
from mesa.space import Coordinate, accept_tuple_argument
from rasterio.warp import (
    calculate_default_transform,
    transform_bounds,
    reproject,
    Resampling,
)

from mesa_geo.geo_base import GeoBase


class RasterBase(GeoBase):
    """
    Base class for raster layers.
    """

    _width: int
    _height: int
    _transform: Affine
    _total_bounds: np.ndarray  # [min_x, min_y, max_x, max_y]

    def __init__(self, width, height, crs, total_bounds):
        super().__init__(crs)
        self._width = width
        self._height = height
        self._total_bounds = total_bounds
        self._update_transform()

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, width: int) -> None:
        self._width = width
        self._update_transform()

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, height: int) -> None:
        self._height = height
        self._update_transform()

    @property
    def total_bounds(self) -> np.ndarray:
        return self._total_bounds

    @total_bounds.setter
    def total_bounds(self, total_bounds: np.ndarray) -> None:
        self._total_bounds = total_bounds
        self._update_transform()

    @property
    def transform(self) -> Affine:
        return self._transform

    @property
    def resolution(self) -> Tuple[float, float]:
        """
        Returns the (width, height) of a cell in the units of CRS.
        """
        a, b, _, d, e, _, _, _, _ = self.transform
        return math.sqrt(a**2 + d**2), math.sqrt(b**2 + e**2)

    def _update_transform(self) -> None:
        self._transform = rio.transform.from_bounds(
            *self.total_bounds, width=self.width, height=self.height
        )

    def to_crs(self, crs, inplace=False) -> RasterBase | None:
        raise NotImplementedError

    def out_of_bounds(self, pos: Coordinate) -> bool:
        """Determines whether position is off the grid."""
        x, y = pos
        return x < 0 or x >= self.width or y < 0 or y >= self.height


class Cell(Agent):
    """
    Cells are containers of raster attributes, and are building blocks of `RasterLayer`.
    """

    pos: Coordinate | None  # (x, y), origin is at lower left corner of the grid
    indices: Coordinate | None  # (row, col), origin is at upper left corner of the grid

    def __init__(self, pos=None, indices=None):
        super().__init__(uuid.uuid4().int, None)
        self.pos = pos
        self.indices = indices

    def step(self):
        pass


class RasterLayer(RasterBase):
    """
    Some methods in `RasterLayer` are copied from `mesa.space.Grid`, including:

    __getitem__
    __iter__
    coord_iter
    iter_neighborhood
    get_neighborhood
    iter_neighbors
    get_neighbors  # copied and renamed to `get_neighboring_cells`
    out_of_bounds  # copied into `RasterBase`
    iter_cell_list_contents
    get_cell_list_contents

    Methods from `mesa.space.Grid` that are not copied over:

    torus_adj
    neighbor_iter
    move_agent
    place_agent
    _place_agent
    remove_agent
    is_cell_empty
    move_to_empty
    find_empty
    exists_empty_cells

    Another difference is that `mesa.space.Grid` has `self.grid: List[List[Agent | None]]`,
    whereas it is `self.cells: List[List[Cell]]` here in `RasterLayer`.
    """

    cells: List[List[Cell]]
    _neighborhood_cache: Dict[Any, List[Coordinate]]

    def __init__(self, width, height, crs, total_bounds, cell_cls: Type[Cell] = Cell):
        super().__init__(width, height, crs, total_bounds)
        self.cell_cls = cell_cls
        self.cells = []
        for x in range(self.width):
            col: List[cell_cls] = []
            for y in range(self.height):
                row_idx, col_idx = self.height - y - 1, x
                col.append(self.cell_cls(pos=(x, y), indices=(row_idx, col_idx)))
            self.cells.append(col)

        self._neighborhood_cache = {}

    @overload
    def __getitem__(self, index: int) -> List[Cell]:
        ...

    @overload
    def __getitem__(self, index: Tuple[int | slice, int | slice]) -> Cell | List[Cell]:
        ...

    @overload
    def __getitem__(self, index: Sequence[Coordinate]) -> List[Cell]:
        ...

    def __getitem__(
        self, index: int | Sequence[Coordinate] | Tuple[int | slice, int | slice]
    ) -> Cell | List[Cell]:
        """Access contents from the grid."""

        if isinstance(index, int):
            # cells[x]
            return self.cells[index]

        if isinstance(index[0], tuple):
            # cells[(x1, y1), (x2, y2)]
            index = cast(Sequence[Coordinate], index)

            cells = []
            for pos in index:
                x1, y1 = pos
                cells.append(self.cells[x1][y1])
            return cells

        x, y = index

        if isinstance(x, int) and isinstance(y, int):
            # cells[x, y]
            x, y = cast(Coordinate, index)
            return self.cells[x][y]

        if isinstance(x, int):
            # cells[x, :]
            x = slice(x, x + 1)

        if isinstance(y, int):
            # grid[:, y]
            y = slice(y, y + 1)

        # cells[:, :]
        x, y = (cast(slice, x), cast(slice, y))
        cells = []
        for rows in self.cells[x]:
            for cell in rows[y]:
                cells.append(cell)
        return cells

    def __iter__(self) -> Iterator[Cell]:
        """Create an iterator that chains the rows of the cells together
        as if it is one list"""
        return itertools.chain(*self.cells)

    def coord_iter(self) -> Iterator[Tuple[Cell, int, int]]:
        """An iterator that returns coordinates as well as cell contents."""
        for row in range(self.width):
            for col in range(self.height):
                yield self.cells[row][col], row, col  # cell, x, y

    def apply_raster(self, data: np.ndarray, attr_name: str = None) -> None:
        assert data.shape == (1, self.height, self.width)
        if attr_name is None:
            attr_name = f"attribute_{len(self.cell_cls.__dict__)}"
        for x in range(self.width):
            for y in range(self.height):
                setattr(self.cells[x][y], attr_name, data[0, self.height - y - 1, x])

    def iter_neighborhood(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> Iterator[Coordinate]:
        """Return an iterator over cell coordinates that are in the
        neighborhood of a certain point.
        Args:
            pos: Coordinate tuple for the neighborhood to get.
            moore: If True, return Moore neighborhood
                        (including diagonals)
                   If False, return Von Neumann neighborhood
                        (exclude diagonals)
            include_center: If True, return the (x, y) cell as well.
                            Otherwise, return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.
        Returns:
            A list of coordinate tuples representing the neighborhood. For
            example with radius 1, it will return list with number of elements
            equals at most 9 (8) if Moore, 5 (4) if Von Neumann (if not
            including the center).
        """
        yield from self.get_neighborhood(pos, moore, include_center, radius)

    def iter_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> Iterator[Cell]:
        """Return an iterator over neighbors to a certain point.
        Args:
            pos: Coordinates for the neighborhood to get.
            moore: If True, return Moore neighborhood
                    (including diagonals)
                   If False, return Von Neumann neighborhood
                     (exclude diagonals)
            include_center: If True, return the (x, y) cell as well.
                            Otherwise,
                            return surrounding cells only.
            radius: radius, in cells, of neighborhood to get.
        Returns:
            An iterator of non-None objects in the given neighborhood;
            at most 9 if Moore, 5 if Von-Neumann
            (8 and 4 if not including the center).
        """
        neighborhood = self.get_neighborhood(pos, moore, include_center, radius)
        return self.iter_cell_list_contents(neighborhood)

    @accept_tuple_argument
    def iter_cell_list_contents(
        self, cell_list: Iterable[Coordinate]
    ) -> Iterator[Cell]:
        """Returns an iterator of the contents of the cells
        identified in cell_list.
        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.
        Returns:
            An iterator of the contents of the cells identified in cell_list
        """
        # Note: filter(None, iterator) filters away an element of iterator that
        # is falsy. Hence, iter_cell_list_contents returns only non-empty
        # contents.
        return filter(None, (self.cells[x][y] for x, y in cell_list))

    @accept_tuple_argument
    def get_cell_list_contents(self, cell_list: Iterable[Coordinate]) -> List[Cell]:
        """Returns a list of the contents of the cells
        identified in cell_list.
        Note: this method returns a list of cells.
        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.
        Returns:
            A list of the contents of the cells identified in cell_list
        """
        return list(self.iter_cell_list_contents(cell_list))

    def get_neighborhood(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> List[Coordinate]:
        cache_key = (pos, moore, include_center, radius)
        neighborhood = self._neighborhood_cache.get(cache_key, None)

        if neighborhood is None:
            coordinates: Set[Coordinate] = set()

            x, y = pos
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx == 0 and dy == 0 and not include_center:
                        continue
                    # Skip coordinates that are outside manhattan distance
                    if not moore and abs(dx) + abs(dy) > radius:
                        continue

                    coord = (x + dx, y + dy)

                    if self.out_of_bounds(coord):
                        continue
                    coordinates.add(coord)

            neighborhood = sorted(coordinates)
            self._neighborhood_cache[cache_key] = neighborhood

        return neighborhood

    def get_neighboring_cells(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> List[Cell]:
        neighboring_cell_idx = self.get_neighborhood(pos, moore, include_center, radius)
        return [self.cells[idx[0]][idx[1]] for idx in neighboring_cell_idx]

    def to_crs(self, crs, inplace=False) -> RasterLayer | None:
        super()._to_crs_check(crs)
        layer = self if inplace else copy.copy(self)

        src_crs = rio.crs.CRS.from_user_input(layer.crs)
        dst_crs = rio.crs.CRS.from_user_input(crs)
        if not layer.crs.is_exact_same(crs):
            transform, dst_width, dst_height = calculate_default_transform(
                src_crs,
                dst_crs,
                self.width,
                self.height,
                *layer.total_bounds,
            )
            layer._total_bounds = [
                *transform_bounds(src_crs, dst_crs, *layer.total_bounds)
            ]
            layer.crs = crs
            layer._transform = transform

        if not inplace:
            return layer

    def to_image(self, colormap) -> ImageLayer:
        """
        Returns an ImageLayer colored by the provided colormap.
        """
        values = np.empty(shape=(4, self.height, self.width))
        for cell in self:
            row, col = cell.indices
            values[:, row, col] = colormap(cell)
        return ImageLayer(values=values, crs=self.crs, total_bounds=self.total_bounds)

    @classmethod
    def from_file(
        cls, raster_file, cell_cls: Type[Cell] = Cell, attr_name: str = None
    ) -> RasterLayer:
        with rio.open(raster_file, "r") as dataset:
            values = dataset.read()
            _, height, width = values.shape
            total_bounds = [
                dataset.bounds.left,
                dataset.bounds.bottom,
                dataset.bounds.right,
                dataset.bounds.top,
            ]
            obj = cls(width, height, dataset.crs, total_bounds, cell_cls)
            obj._transform = dataset.transform
            obj.apply_raster(values, attr_name=attr_name)
            return obj


class ImageLayer(RasterBase):
    _values: np.ndarray

    def __init__(self, values, crs, total_bounds):
        super().__init__(
            width=values.shape[2],
            height=values.shape[1],
            crs=crs,
            total_bounds=total_bounds,
        )
        self._values = values.copy()

    @property
    def values(self) -> np.ndarray:
        return self._values

    @values.setter
    def values(self, values: np.ndarray) -> None:
        self._values = values
        self._width = values.shape[2]
        self._height = values.shape[1]
        self._update_transform()

    def to_crs(self, crs, inplace=False) -> ImageLayer | None:
        super()._to_crs_check(crs)
        layer = self if inplace else copy.copy(self)

        src_crs = rio.crs.CRS.from_user_input(layer.crs)
        dst_crs = rio.crs.CRS.from_user_input(crs)
        if not layer.crs.is_exact_same(crs):
            num_bands, src_height, src_width = self.values.shape
            transform, dst_width, dst_height = calculate_default_transform(
                src_crs,
                dst_crs,
                src_width,
                src_height,
                *layer.total_bounds,
            )
            dst = np.empty(shape=(num_bands, dst_height, dst_width))
            for i, band in enumerate(layer.values):
                reproject(
                    source=band,
                    destination=dst[i],
                    src_transform=layer.transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                )
            layer._total_bounds = [
                *transform_bounds(src_crs, dst_crs, *layer.total_bounds)
            ]
            layer._values = dst
            layer._height = layer._values.shape[1]
            layer._width = layer._values.shape[2]
            layer.crs = crs
            layer._transform = transform
        if not inplace:
            return layer

    @classmethod
    def from_file(cls, image_file) -> ImageLayer:
        with rio.open(image_file, "r") as dataset:
            values = dataset.read()
            total_bounds = [
                dataset.bounds.left,
                dataset.bounds.bottom,
                dataset.bounds.right,
                dataset.bounds.top,
            ]
            obj = cls(values=values, crs=dataset.crs, total_bounds=total_bounds)
            obj._transform = dataset.transform
            return obj

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(crs={self.crs}, total_bounds={self.total_bounds}, values={repr(self.values)})"
