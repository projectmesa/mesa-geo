from __future__ import annotations

import gzip
import uuid

import geopandas as gpd
import mesa
import rasterio as rio

from mesa_geo.geoagent import GeoAgent
from mesa_geo.geospace import GeoSpace
from mesa_geo.raster_layers import Cell, RasterLayer


class UgandaCell(Cell):
    population: float | None

    def __init__(
        self,
        pos: mesa.space.Coordinate | None = None,
        indices: mesa.space.Coordinate | None = None,
    ):
        super().__init__(pos, indices)
        self.population = None

    def step(self):
        pass


class Lake(GeoAgent):
    pass


class UgandaArea(GeoSpace):
    def __init__(self, crs):
        super().__init__(crs=crs)

    def load_data(self, population_gzip_file, lake_zip_file, world_zip_file):
        world_size = gpd.GeoDataFrame.from_file(world_zip_file)
        with gzip.open(population_gzip_file, "rb") as population_file:
            with rio.open(population_file, "r") as population_data:
                values = population_data.read()
                _, height, width = values.shape
        self.add_layer(
            RasterLayer(
                width,
                height,
                world_size.crs,
                world_size.total_bounds,
                cell_cls=UgandaCell,
            )
        )
        self.population_layer.apply_raster(values, name="population")

        self.lake = gpd.GeoDataFrame.from_file(lake_zip_file).geometry[0]
        self.add_agents(GeoAgent(uuid.uuid4().int, None, self.lake, self.crs))

    @property
    def population_layer(self):
        return self.layers[0]
