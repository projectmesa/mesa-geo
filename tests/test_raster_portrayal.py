"""Tests for the vectorized raster portrayal path.

Covers pixel-exact correctness, vmin/vmax handling, NaN transparency,
callable/bare-style dispatch, band z-order, multi-layer selective styling,
and legacy-path byte-identity.
"""

import base64
import warnings
from io import BytesIO

import matplotlib
import matplotlib.colors
import mesa
import numpy as np
import pytest
import xyzservices.providers as xyz
from mesa.visualization.components import PropertyLayerStyle
from PIL import Image

import mesa_geo as mg
import mesa_geo.visualization.components.geospace_component as gc
from mesa_geo.raster_layers import RasterLayer
from mesa_geo.visualization.components.geospace_component import MapModule

# ---- Helpers ----


@pytest.fixture(autouse=True)
def _reset_colorbar_state():
    """Reset module-level colorbar warning state before each test."""
    gc._COLORBAR_STATE["warned"] = False
    yield


def _make_model_with_raster(data, *, crs="epsg:4326", band_name="band0"):
    """Create a Model+GeoSpace+RasterLayer with a single band, CRS 4326 so
    to_crs('epsg:4326') is an identity transform."""
    model = mesa.Model()
    model.space = mg.GeoSpace(crs=crs, warn_crs_conversion=False)
    h, w = data.shape
    layer = RasterLayer(w, h, crs=crs, total_bounds=[0, 0, 1, 1], model=model)
    layer.set_band(band_name, data)
    model.space.add_layer(layer, name="test_layer")
    return model, layer


def _decode_data_url_to_rgba(data_url):
    """Decode a data:image/png;base64,... URL into a (H, W, 4) uint8 array."""
    _, b64 = data_url.split(",", 1)
    raw = base64.b64decode(b64)
    img = Image.open(BytesIO(raw)).convert("RGBA")
    return np.array(img)


def _render_rasters(model, raster_portrayal):
    """Shortcut: render via MapModule and return the rasters list."""
    mm = MapModule(
        portrayal_method=None,
        tiles=xyz.OpenStreetMap.Mapnik,
        raster_portrayal=raster_portrayal,
    )
    result = mm.render(model)
    return result["layers"]["rasters"]


# ---- Tests ----


class TestPixelExactColormap:
    """Asymmetric raster, colormap="viridis", vmin=0, vmax=100."""

    def test_viridis_pixel_exact(self):
        # Asymmetric: 3 rows by 5 cols, distinct values
        data = np.array(
            [
                [0, 25, 50, 75, 100],
                [10, 30, 60, 80, 90],
                [5, 15, 45, 65, 95],
            ],
            dtype=float,
        )

        model, _ = _make_model_with_raster(data, band_name="elev")
        style = PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100, alpha=1.0)
        rasters = _render_rasters(model, lambda ln, bn: style)

        assert len(rasters) == 1
        decoded = _decode_data_url_to_rgba(rasters[0]["url"])

        # Compute expected via the same matplotlib pipeline
        norm = matplotlib.colors.Normalize(vmin=0, vmax=100)
        cmap = matplotlib.colormaps["viridis"]
        expected = (cmap(norm(data)) * 255).astype(np.uint8)

        # The CRS is epsg:4326 -> epsg:4326, so the transform is identity.
        np.testing.assert_array_equal(decoded, expected)

    def test_bare_style_default_alpha(self):
        """PropertyLayerStyle defaults alpha=0.8, rendered output should reflect it."""
        data = np.array([[10, 20], [30, 40]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="elev")
        style = PropertyLayerStyle(colormap="viridis")
        rasters = _render_rasters(model, style)

        assert len(rasters) == 1
        decoded = _decode_data_url_to_rgba(rasters[0]["url"])
        assert decoded[0, 0, 3] == int(0.8 * 255)


class TestVminZeroRespected:
    """vmin=0 is honoured rather than being treated as unset."""

    def test_vmin_zero_not_autoranged(self):
        data = np.array([[50, 100], [75, 25]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="b")

        style_explicit = PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100)
        style_auto = PropertyLayerStyle(colormap="viridis", vmin=None, vmax=None)

        rasters_explicit = _render_rasters(model, lambda ln, bn: style_explicit)
        rasters_auto = _render_rasters(model, lambda ln, bn: style_auto)

        px_explicit = _decode_data_url_to_rgba(rasters_explicit[0]["url"])
        px_auto = _decode_data_url_to_rgba(rasters_auto[0]["url"])

        # With vmin=0, the 25 pixel should map differently than with
        # vmin=25 (auto-ranged). The images should differ.
        assert not np.array_equal(px_explicit, px_auto)


class TestAutoRange:
    """vmin/vmax of None auto-range with nan-aware min/max."""

    def test_auto_range_nan_aware(self):
        data = np.array([[np.nan, 20], [40, 60]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="b")

        style = PropertyLayerStyle(colormap="viridis", vmin=None, vmax=None, alpha=1.0)
        rasters = _render_rasters(model, lambda ln, bn: style)

        assert len(rasters) == 1
        decoded = _decode_data_url_to_rgba(rasters[0]["url"])

        # Auto-range should be nanmin=20, nanmax=60
        norm = matplotlib.colors.Normalize(vmin=20, vmax=60)
        cmap = matplotlib.colormaps["viridis"]
        expected = (cmap(norm(data)) * 255).astype(np.uint8)
        # NaN pixel should be alpha=0
        expected[0, 0, 3] = 0
        np.testing.assert_array_equal(decoded, expected)


class TestUniformColor:
    """A uniform color= style produces a constant RGBA."""

    def test_uniform_red(self):
        data = np.array([[50, 100], [0.1, 75]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="b")

        style = PropertyLayerStyle(color="red", alpha=1.0, vmin=0, vmax=100)
        rasters = _render_rasters(model, lambda ln, bn: style)

        assert len(rasters) == 1
        decoded = _decode_data_url_to_rgba(rasters[0]["url"])

        red_rgba = matplotlib.colors.to_rgba("red")
        # RGB channels should all be (255, 0, 0)
        assert np.all(decoded[..., 0] == int(red_rgba[0] * 255))
        assert np.all(decoded[..., 1] == int(red_rgba[1] * 255))
        assert np.all(decoded[..., 2] == int(red_rgba[2] * 255))
        # Alpha should be proportional to normalized data value
        # data=100 -> norm=1.0 -> alpha=255; data=0.1 -> norm~0.001 -> alpha~0
        assert decoded[0, 1, 3] == 255  # data=100, fully opaque


class TestNanTransparency:
    """A NaN cell is fully transparent."""

    def test_nan_alpha_zero(self):
        data = np.array([[np.nan, 50], [25, 75]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="b")

        style = PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100)
        rasters = _render_rasters(model, lambda ln, bn: style)

        decoded = _decode_data_url_to_rgba(rasters[0]["url"])
        assert decoded[0, 0, 3] == 0  # NaN pixel is fully transparent


class TestCallableReturnsNone:
    """A callable returning None for a band produces no overlay."""

    def test_none_skips_band(self):
        data = np.array([[10, 20], [30, 40]], dtype=float)
        model, layer = _make_model_with_raster(data, band_name="visible")
        layer.set_band("hidden", np.ones((2, 2)))

        def selective(layer_name, band_name):
            if band_name == "hidden":
                return None
            return PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100)

        rasters = _render_rasters(model, selective)
        # Only 'visible' should produce an overlay
        assert len(rasters) == 1


class TestBareStyleAllBands:
    """A bare style object applies to every band."""

    def test_bare_style_covers_all(self):
        data1 = np.array([[10, 20], [30, 40]], dtype=float)
        data2 = np.array([[50, 60], [70, 80]], dtype=float)
        model, layer = _make_model_with_raster(data1, band_name="a")
        layer.set_band("b", data2)

        style = PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100)
        rasters = _render_rasters(model, style)
        assert len(rasters) == 2


class TestSelectiveMultiLayer:
    """With two raster layers, only the styled one is drawn."""

    def test_two_layers_one_styled(self):
        model = mesa.Model()
        model.space = mg.GeoSpace(crs="epsg:4326", warn_crs_conversion=False)

        layer1 = RasterLayer(
            2, 2, crs="epsg:4326", total_bounds=[0, 0, 1, 1], model=model
        )
        layer1.set_band("elev", np.array([[10, 20], [30, 40]], dtype=float))
        model.space.add_layer(layer1, name="styled")

        layer2 = RasterLayer(
            2, 2, crs="epsg:4326", total_bounds=[0, 0, 1, 1], model=model
        )
        layer2.set_band("temp", np.array([[5, 6], [7, 8]], dtype=float))
        model.space.add_layer(layer2, name="unstyled")

        def portrayal(layer_name, band_name):
            if layer_name == "styled":
                return PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100)
            return None

        rasters = _render_rasters(model, portrayal)
        # Only the "styled" layer produced an overlay
        assert len(rasters) == 1


class TestLegacyPathUntouched:
    """raster_portrayal=None keeps the original to_image path."""

    def test_legacy_renders(self):
        """When raster_portrayal is None the old to_image codepath runs."""
        model = mesa.Model()
        model.space = mg.GeoSpace(crs="epsg:4326", warn_crs_conversion=False)
        layer = RasterLayer(
            2, 2, crs="epsg:4326", total_bounds=[0, 0, 1, 1], model=model
        )
        layer.apply_raster(np.array([[[10, 20], [30, 40]]]))
        model.space.add_layer(layer)

        def old_portrayal(cell):
            # apply_raster with no attr_name generates "attribute_0"
            v = cell.attribute_0
            return (min(v * 2, 255), v, 0, 255)

        mm_legacy = MapModule(
            portrayal_method=old_portrayal, tiles=xyz.OpenStreetMap.Mapnik
        )
        result = mm_legacy.render(model)
        rasters = result["layers"]["rasters"]
        assert len(rasters) == 1
        assert rasters[0]["url"].startswith("data:image/png;base64,")


class TestBandZOrder:
    """Band overlays follow _data insertion order."""

    def test_overlay_order_matches_insertion(self):
        """Bands added as a, b, c must produce overlays in that order."""
        model = mesa.Model()
        model.space = mg.GeoSpace(crs="epsg:4326", warn_crs_conversion=False)
        layer = RasterLayer(
            2, 2, crs="epsg:4326", total_bounds=[0, 0, 1, 1], model=model
        )
        layer.set_band("alpha_band", np.array([[10, 20], [30, 40]], dtype=float))
        layer.set_band("beta_band", np.array([[50, 60], [70, 80]], dtype=float))
        model.space.add_layer(layer, name="ordered")

        call_order = []

        def tracking_portrayal(layer_name, band_name):
            call_order.append(band_name)
            return PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100)

        _render_rasters(model, tracking_portrayal)
        assert call_order == ["alpha_band", "beta_band"]


class TestAllNanBandSkipped:
    """An all-NaN band is skipped, without warning or overlay."""

    def test_all_nan_no_overlay(self):
        data = np.full((3, 3), np.nan)
        model, _ = _make_model_with_raster(data, band_name="nan_band")

        style = PropertyLayerStyle(colormap="viridis")
        rasters = _render_rasters(model, lambda ln, bn: style)
        assert len(rasters) == 0


class TestConstantBandRendered:
    """A constant band is drawn flat rather than skipped."""

    def test_constant_value_renders_flat_color(self):
        data = np.full((3, 3), 42.0)
        model, _ = _make_model_with_raster(data, band_name="const_band")

        style = PropertyLayerStyle(colormap="viridis", alpha=1.0)
        rasters = _render_rasters(model, lambda ln, bn: style)
        assert len(rasters) == 1
        decoded = _decode_data_url_to_rgba(rasters[0]["url"])

        # Verify it's a uniform flat color and not transparent (alpha=255)
        assert decoded[0, 0, 3] == 255

        # Since vmin==vmax, Normalize maps it to 0 (low end of colormap)
        norm = matplotlib.colors.Normalize(vmin=42.0, vmax=42.0)
        cmap = matplotlib.colormaps["viridis"]
        expected = (cmap(norm(data)) * 255).astype(np.uint8)
        np.testing.assert_array_equal(decoded, expected)

    def test_constant_value_renders_color_path(self):
        data = np.full((3, 3), 42.0)
        model, _ = _make_model_with_raster(data, band_name="const_color_band")

        style = PropertyLayerStyle(color="red", alpha=1.0)
        rasters = _render_rasters(model, lambda ln, bn: style)
        assert len(rasters) == 1
        decoded = _decode_data_url_to_rgba(rasters[0]["url"])

        # In the color path with vmin == vmax, the band must render visibly
        # with full alpha rather than being transparent (alpha=255).
        red_rgba = matplotlib.colors.to_rgba("red")
        assert np.all(decoded[..., 0] == int(red_rgba[0] * 255))
        assert np.all(decoded[..., 1] == int(red_rgba[1] * 255))
        assert np.all(decoded[..., 2] == int(red_rgba[2] * 255))
        assert np.all(decoded[..., 3] == 255)


class TestColorbarWarnsOnce:
    """colorbar=True warns once per render, not once per band."""

    def test_warns_once(self):
        data1 = np.array([[10, 20], [30, 40]], dtype=float)
        data2 = np.array([[50, 60], [70, 80]], dtype=float)
        model, layer = _make_model_with_raster(data1, band_name="a")
        layer.set_band("b", data2)

        style = PropertyLayerStyle(colormap="viridis", vmin=0, vmax=100, colorbar=True)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _render_rasters(model, style)
            colorbar_warnings = [x for x in w if "colorbar" in str(x.message).lower()]
            assert len(colorbar_warnings) == 1

    def test_warns_once_across_multiple_mapmodule_instances(self):
        data = np.array([[10, 20], [30, 40]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="a")
        style = PropertyLayerStyle(colormap="viridis", colorbar=True)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Simulating two render cycles (GeoSpaceLeaflet creates a new MapModule each time)
            _render_rasters(model, style)
            _render_rasters(model, style)
            colorbar_warnings = [x for x in w if "colorbar" in str(x.message).lower()]
            assert len(colorbar_warnings) == 1


class TestPortrayalValidation:
    """Non-callable / invalid raster_portrayal raises TypeError."""

    def test_dict_portrayal_raises_type_error(self):
        data = np.array([[10, 20], [30, 40]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="a")

        with pytest.raises(
            TypeError,
            match=r"'raster_portrayal' must be a callable.*or a PropertyLayerStyle instance",
        ):
            _render_rasters(model, {"colormap": "viridis"})

    def test_callable_returning_dict_raises_type_error(self):
        data = np.array([[10, 20], [30, 40]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="a")

        with pytest.raises(
            TypeError,
            match=r"Portrayal for band 'a' .* must be a PropertyLayerStyle or None",
        ):
            _render_rasters(model, lambda ln, bn: {"colormap": "viridis"})

    def test_property_layer_style_mutually_exclusive(self):
        with pytest.raises(
            ValueError, match="Specify either 'color' or 'colormap', not both"
        ):
            PropertyLayerStyle(color="red", colormap="viridis")

    def test_property_layer_style_requires_at_least_one(self):
        with pytest.raises(ValueError, match="Specify one of 'color' or 'colormap'"):
            PropertyLayerStyle()


class TestAgentPortrayalNoneGuard:
    """When both agent_portrayal and raster_portrayal are None and a RasterLayer exists, raise ValueError."""

    def test_agent_portrayal_none_raises_clear_error(self):
        data = np.array([[10, 20], [30, 40]], dtype=float)
        model, _ = _make_model_with_raster(data, band_name="a")

        mm = MapModule(
            portrayal_method=None,
            tiles=xyz.OpenStreetMap.Mapnik,
            raster_portrayal=None,
        )
        with pytest.raises(
            ValueError,
            match=r"neither 'raster_portrayal' nor 'agent_portrayal' was provided",
        ):
            mm.render(model)
