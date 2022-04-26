import unittest

import numpy as np
import rasterio as rio

from mesa_geo.geospace import RasterLayer


class TestRasterLayer(unittest.TestCase):
    def setUp(self) -> None:
        self.src_shape = (3, 500, 500)
        self.dst_shape = (3, 400, 583)
        self.src_crs = "epsg:4326"
        self.dst_crs = "epsg:3857"
        self.src_transform = rio.transform.Affine(
            0.0011111111111859,
            0.00,
            -122.26638888878,
            0.00,
            -0.0011111111111859,
            43.01472222189958,
        )
        self.dst_transform = rio.transform.Affine(
            60.43686114587856,
            0.00,
            -13610632.15223135,
            0.00,
            -60.43686114587856,
            5314212.987773206,
        )
        self.src_bounds = [
            -122.26638888878,
            42.855833333,
            -121.94972222209202,
            43.01472222189958,
        ]
        self.dst_bounds = [
            -13610632.15223135,
            5290053.890954778,
            -13575380.980144441,
            5314212.987773206,
        ]
        self.src_resolution = (0.0011111, 0.0011111)
        self.dst_resolution = (60.43686114587856, 60.43686114587856)
        self.raster_layer = RasterLayer(
            values=np.random.uniform(low=0, high=255, size=self.src_shape),
            crs=self.src_crs,
            transform=self.src_transform,
            bounds=self.src_bounds,
        )

    def tearDown(self) -> None:
        pass

    def test_to_crs(self):
        transformed_raster_layer = self.raster_layer.to_crs(self.dst_crs)
        self.assertEqual(transformed_raster_layer.crs, self.dst_crs)
        self.assertEqual(transformed_raster_layer.shape, self.dst_shape)
        self.assertTrue(
            transformed_raster_layer.transform.almost_equals(self.dst_transform)
        )
        np.testing.assert_almost_equal(transformed_raster_layer.bounds, self.dst_bounds)
        np.testing.assert_almost_equal(
            transformed_raster_layer.resolution, self.dst_resolution
        )

        # no change to original layer
        self.assertEqual(self.raster_layer.crs, self.src_crs)
        self.assertEqual(self.raster_layer.shape, self.src_shape)
        self.assertTrue(self.raster_layer.transform.almost_equals(self.src_transform))
        np.testing.assert_almost_equal(self.raster_layer.bounds, self.src_bounds)
        np.testing.assert_almost_equal(
            self.raster_layer.resolution, self.src_resolution
        )

    def test_to_crs_inplace(self):
        self.raster_layer.to_crs(self.dst_crs, inplace=True)
        self.assertEqual(self.raster_layer.crs, self.dst_crs)
        self.assertEqual(self.raster_layer.shape, self.dst_shape)
        self.assertTrue(self.raster_layer.transform.almost_equals(self.dst_transform))
        np.testing.assert_almost_equal(self.raster_layer.bounds, self.dst_bounds)
        np.testing.assert_almost_equal(
            self.raster_layer.resolution, self.dst_resolution
        )
