import unittest
from unittest.mock import MagicMock, patch

import solara

from mesa_geo.visualization.geojupyter_viz import Card, GeoJupyterViz


class TestGeoViz(unittest.TestCase):
    @patch("mesa_geo.visualization.geojupyter_viz.rv.CardTitle")
    @patch("mesa_geo.visualization.geojupyter_viz.rv.Card")
    @patch("mesa_geo.visualization.geojupyter_viz.components_matplotlib.PlotMatplotlib")
    @patch("mesa_geo.visualization.geojupyter_viz.leaflet_viz.map")
    def test_card_function(
        self,
        mock_map,
        mock_PlotMatplotlib,  # noqa: N803
        mock_Card,  # noqa: N803
        mock_CardTitle,  # noqa: N803
    ):
        model = MagicMock()
        measures = {"Measure1": lambda x: x}
        agent_portrayal = MagicMock()
        map_drawer = (MagicMock(),)
        zoom = (10,)
        scroll_wheel_zoom = (True,)
        center_default = ([0, 0],)
        current_step = MagicMock()
        current_step.value = 0
        color = "white"
        layout_type = {"Map": "default", "Measure": "Measure1"}

        with patch(
            "mesa_geo.visualization.geojupyter_viz.rv.Card", return_value=MagicMock()
        ) as mock_rv_card:
            _ = Card(
                model,
                measures,
                agent_portrayal,
                map_drawer,
                center_default,
                zoom,
                scroll_wheel_zoom,
                current_step,
                color,
                layout_type,
            )

        mock_rv_card.assert_called_once()
        mock_CardTitle.assert_any_call(children=["Map"])
        mock_map.assert_called_once_with(
            model, map_drawer, zoom, center_default, scroll_wheel_zoom
        )
        # mock_PlotMatplotlib.assert_called_once()

    @patch("mesa_geo.visualization.geojupyter_viz.solara.GridDraggable")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.Sidebar")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.Card")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.Markdown")
    @patch("mesa_geo.visualization.geojupyter_viz.jv.ModelController")
    @patch("mesa_geo.visualization.geojupyter_viz.jv.UserInputs")
    @patch("mesa_geo.visualization.geojupyter_viz.jv.split_model_params")
    @patch("mesa_geo.visualization.geojupyter_viz.jv.make_initial_grid_layout")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.use_memo")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.use_reactive")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.use_state")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.AppBarTitle")
    @patch("mesa_geo.visualization.geojupyter_viz.solara.AppBar")
    @patch("mesa_geo.visualization.geojupyter_viz.leaflet_viz.MapModule")
    @patch("mesa_geo.visualization.geojupyter_viz.rv.Card")
    def test_geojupyterviz_function(
        self,
        mock_rv_Card,  # noqa: N803
        mock_MapModule,  # noqa: N803
        mock_AppBar,  # noqa: N803
        mock_AppBarTitle,  # noqa: N803
        mock_use_state,
        mock_use_reactive,
        mock_use_memo,
        mock_make_initial_grid_layout,
        mock_split_model_params,
        mock_UserInputs,  # noqa: N803
        mock_ModelController,  # noqa: N803
        mock_Markdown,  # noqa: N803
        mock_Card,  # noqa: N803
        mock_Sidebar,  # noqa: N803
        mock_GridDraggable,  # noqa: N803
    ):
        model_class = MagicMock()
        model_params = MagicMock()
        measures = [lambda x: x]
        name = "TestModel"
        agent_portrayal = MagicMock()
        play_interval = 150
        view = [0, 0]
        zoom = 10
        center_point = [0, 0]

        mock_use_reactive.side_effect = [MagicMock(value=0), MagicMock(value=0)]
        mock_split_model_params.return_value = ({}, {})
        mock_use_state.return_value = ({}, MagicMock())
        mock_use_memo.return_value = MagicMock()
        mock_make_initial_grid_layout.return_value = {}

        mock_rv_Card.return_value.__enter__ = MagicMock()
        mock_rv_Card.return_value.__exit__ = MagicMock()

        solara.render(
            GeoJupyterViz(
                model_class=model_class,
                model_params=model_params,
                measures=measures,
                name=name,
                agent_portrayal=agent_portrayal,
                play_interval=play_interval,
                view=view,
                zoom=zoom,
                center_point=center_point,
            )
        )

        mock_AppBar.assert_called_once()
        mock_AppBarTitle.assert_called_once_with(name)
        mock_split_model_params.assert_called_once_with(model_params)
        mock_use_memo.assert_called_once()
        mock_UserInputs.assert_called_once()
        mock_ModelController.assert_called_once()
        mock_Markdown.assert_called()
        mock_Card.assert_called()
        mock_Sidebar.assert_called_once()
        mock_GridDraggable.assert_called_once()
        mock_MapModule.assert_called_once()
