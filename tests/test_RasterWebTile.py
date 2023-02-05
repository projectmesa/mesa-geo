import unittest

import xyzservices.providers as xyz

import mesa_geo as mg


class TestRasterWebTile(unittest.TestCase):
    def test_from_xyzservices(self):
        map_tile = mg.RasterWebTile.from_xyzservices(xyz.CartoDB.Positron)

        self.assertEqual(map_tile.url, xyz.CartoDB.Positron.url)
        self.assertEqual(
            map_tile.options,
            {
                "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                "subdomains": "abcd",
                "max_zoom": 20,
                "variant": "light_all",
                "name": "CartoDB.Positron",
            },
        )
        self.assertEqual(map_tile.kind, "raster_web_tile")
        self.assertEqual(
            map_tile.to_dict(),
            {
                "url": xyz.CartoDB.Positron.url,
                "options": {
                    "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    "subdomains": "abcd",
                    "max_zoom": 20,
                    "variant": "light_all",
                    "name": "CartoDB.Positron",
                },
                "kind": "raster_web_tile",
            },
        )

    def test_to_dict(self):
        map_tile = mg.RasterWebTile(
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            options={
                "attribution": "Map data © <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors"
            },
        )
        self.assertEqual(
            map_tile.to_dict(),
            {
                "kind": "raster_web_tile",
                "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "options": {
                    "attribution": "Map data © <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors",
                },
            },
        )

        map_tile = mg.RasterWebTile(
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        )
        self.assertEqual(
            map_tile.to_dict(),
            {
                "kind": "raster_web_tile",
                "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "options": None,
            },
        )
