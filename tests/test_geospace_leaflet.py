import mesa
import solara
import xyzservices
from mesa.visualization.solara_viz import SolaraViz

import mesa_geo.visualization as mgv
from mesa_geo.visualization import make_geospace_leaflet


def test_geospace_leaflet(mocker):
    mock_geospace_leaflet = mocker.spy(
        mgv.components.geospace_leaflet, "GeoSpaceLeaflet"
    )

    model = mesa.Model()
    mocker.patch.object(mesa.Model, "__new__", return_value=model)
    mocker.patch.object(mesa.Model, "__init__", return_value=None)

    agent_portrayal = {
        "Shape": "circle",
        "color": "gray",
    }
    # initialize with space drawer unspecified (use default)
    # component must be rendered for code to run
    solara.render(SolaraViz(model, components=[make_geospace_leaflet(agent_portrayal)]))
    # should call default method with class instance and agent portrayal
    mock_geospace_leaflet.assert_called_with(
        model, agent_portrayal, None, xyzservices.providers.OpenStreetMap.Mapnik
    )
