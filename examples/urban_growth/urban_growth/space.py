from __future__ import annotations
import gzip

import mesa
import rasterio as rio

from mesa_geo import Cell, RasterLayer
from mesa_geo.geospace import GeoSpace


class UrbanCell(Cell):
    urban: bool | None
    slope: int | None
    road_1: int | None
    excluded: int | None
    land_use: int | None

    suitable: bool | None
    road: bool | None
    run_value: int | None
    road_found: bool | None
    road_pixel: UrbanCell | None

    new_urbanized: bool | None

    def __init__(
        self,
        pos: mesa.space.Coordinate | None = None,
        indices: mesa.space.Coordinate | None = None,
    ):
        super().__init__(pos, indices)
        self.urban = None
        self.slope = None
        self.road_1 = None
        self.excluded = None
        self.land_use = None

        self.suitable = None
        self.road = None
        self.run_value = None
        self.road_found = None
        self.road_pixel = None
        self.new_urbanized = None

    def step(self):
        pass


class City(GeoSpace):
    def __init__(self, width, height, crs, total_bounds):
        super().__init__(crs=crs)
        self.add_layer(
            RasterLayer(width, height, crs, total_bounds, cell_cls=UrbanCell)
        )

    def load_datasets(
        self, urban_data, slope_data, road_data, excluded_data, land_use_data
    ):
        data = {
            "urban": urban_data,
            "slope": slope_data,
            "road_1": road_data,
            "excluded": excluded_data,
            "land_use": land_use_data,
        }
        for attribute_name, data_file in data.items():
            with gzip.open(data_file, "rb") as f:
                with rio.open(f, "r") as dataset:
                    values = dataset.read()
            self.raster_layer.apply_raster(values, name=attribute_name)

        for cell in self.raster_layer:
            cell.urban = True if cell.urban == 2 else False

    def check_road(self):
        for cell in self.raster_layer:
            cell.road = True if cell.road_1 > 0 else False

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
