import math
import random
import uuid

import mesa
import mesa_geo as mg
import numpy as np
from shapely.geometry import Point


from .space import UgandaArea


class Person(mg.GeoAgent):
    MOBILITY_RANGE_X = 0.0
    MOBILITY_RANGE_Y = 0.0

    def __init__(self, unique_id, model, geometry, crs, img_coord):
        super().__init__(unique_id, model, geometry, crs)
        self.img_coord = img_coord

    def set_random_world_coord(self):
        world_coord_point = Point(
            self.model.space.population_layer.transform * self.img_coord
        )
        random_world_coord_x = world_coord_point.x + np.random.uniform(
            -self.MOBILITY_RANGE_X, self.MOBILITY_RANGE_X
        )
        random_world_coord_y = world_coord_point.y + np.random.uniform(
            -self.MOBILITY_RANGE_Y, self.MOBILITY_RANGE_Y
        )
        self.geometry = Point(random_world_coord_x, random_world_coord_y)

    def step(self):
        neighborhood = self.model.space.population_layer.get_neighborhood(
            self.img_coord, moore=True
        )
        found = False
        while neighborhood and not found:
            next_img_coord = random.choice(neighborhood)
            world_coord_point = Point(
                self.model.space.population_layer.transform * next_img_coord
            )
            if world_coord_point.within(self.model.space.lake):
                neighborhood.remove(next_img_coord)
                continue
            else:
                found = True
                self.img_coord = next_img_coord
                self.set_random_world_coord()


class Population(mesa.Model):
    def __init__(
        self,
        population_gzip_file="data/popu.asc.gz",
        lake_zip_file="data/lake.zip",
        world_zip_file="data/clip.zip",
    ):
        super().__init__()
        self.space = UgandaArea(crs="epsg:4326")
        self.space.load_data(population_gzip_file, lake_zip_file, world_zip_file)
        pixel_size_x, pixel_size_y = self.space.population_layer.resolution
        Person.MOBILITY_RANGE_X = pixel_size_x / 2.0
        Person.MOBILITY_RANGE_Y = pixel_size_y / 2.0

        self.schedule = mesa.time.RandomActivation(self)
        self._create_agents()

    def _create_agents(self):
        num_agents = 0
        for cell in self.space.population_layer:
            popu_round = math.ceil(cell.population)
            if popu_round > 0:
                for _ in range(popu_round):
                    num_agents += 1
                    point = Point(self.space.population_layer.transform * cell.indices)
                    if not point.within(self.space.lake):
                        person = Person(
                            unique_id=uuid.uuid4().int,
                            model=self,
                            crs=self.space.crs,
                            geometry=point,
                            img_coord=cell.indices,
                        )
                        person.set_random_world_coord()
                        self.space.add_agents(person)
                        self.schedule.add(person)

    def step(self):
        self.schedule.step()
