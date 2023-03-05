import unittest

import mesa_geo as mg


class TestWMSWebTile(unittest.TestCase):
    def setUp(self) -> None:
        self.map_tile_url = "https://gis.charttools.noaa.gov/arcgis/rest/services/MCS/NOAAChartDisplay/MapServer/exts/MaritimeChartService/WMSServer/"

    def test_to_dict(self):
        map_tile = mg.WMSWebTile(
            url=self.map_tile_url,
            options={
                "layers": "0,1,2,3,4,5,6,7,8,9,10,11,12",
                "version": "1.3.0",
                "format": "image/png",
            },
        )
        self.assertEqual(
            map_tile.to_dict(),
            {
                "kind": "wms_web_tile",
                "url": self.map_tile_url,
                "options": {
                    "layers": "0,1,2,3,4,5,6,7,8,9,10,11,12",
                    "version": "1.3.0",
                    "format": "image/png",
                },
            },
        )

        map_tile = mg.WMSWebTile(url=self.map_tile_url)
        self.assertEqual(
            map_tile.to_dict(),
            {
                "kind": "wms_web_tile",
                "url": self.map_tile_url,
                "options": None,
            },
        )
