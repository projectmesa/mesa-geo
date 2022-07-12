from __future__ import annotations
import gzip

import mesa
import numpy as np
import rasterio as rio

from mesa_geo import Cell, RasterLayer
from mesa_geo.geospace import GeoSpace


class LakeCell(Cell):
    elevation: int | None
    water_level: int | None

    def __init__(
        self,
        pos: mesa.space.Coordinate | None = None,
        indices: mesa.space.Coordinate | None = None,
    ):
        super().__init__(pos, indices)
        self.elevation = None
        self.water_level = None

    def step(self):
        pass


class CraterLake(GeoSpace):
    def __init__(self, crs, water_height):
        super().__init__(crs=crs)
        self.water_height = water_height
        self.outflow = 0

    def set_elevation_layer(self, elevation_gzip_file, crs):
        with gzip.open(elevation_gzip_file, "rb") as elevation_file:
            with rio.open(elevation_file, "r") as dataset:
                values = dataset.read()
                _, height, width = values.shape
                total_bounds = dataset.bounds
        raster_layer = RasterLayer(width, height, crs, total_bounds, cell_cls=LakeCell)
        raster_layer.apply_raster(data=values, name="elevation")
        raster_layer.apply_raster(data=np.zeros(values.shape), name="water_level")
        super().add_layer(raster_layer)

    @property
    def raster_layer(self):
        return self.layers[0]

    def is_at_boundary(self, row_idx, col_idx):
        return (
            row_idx == 0
            or row_idx == self.raster_layer.height
            or col_idx == 0
            or col_idx == self.raster_layer.width
        )

    def move_raindrop(self, raindrop, new_pos):
        self.remove_raindrop(raindrop)
        raindrop.pos = new_pos
        self.add_raindrop(raindrop)

    def add_raindrop(self, raindrop):
        x, y = raindrop.pos
        row_ind, col_ind = raindrop.indices
        if self.is_at_boundary(row_ind, col_ind):
            raindrop.is_at_boundary = True
            self.outflow += 1
        else:
            self.raster_layer.cells[x][y].water_level += self.water_height

    def remove_raindrop(self, raindrop):
        x, y = raindrop.pos
        self.raster_layer.cells[x][y].water_level -= self.water_height
