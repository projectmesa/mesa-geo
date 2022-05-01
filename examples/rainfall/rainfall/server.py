from typing import Tuple

import mesa

from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa_geo.visualization.modules import MapModule
from .model import Rainfall
from .space import LakeCell

model_params = {
    "rain_rate": mesa.visualization.Slider("rain rate", 500, 0, 500, 5),
    "water_height": mesa.visualization.Slider("water height", 5, 1, 5, 1),
}


def cell_portrayal(cell: LakeCell) -> Tuple[float, float, float, float]:
    if cell.water_level == 0:
        return cell.elevation, cell.elevation, cell.elevation, 1
    else:
        return 0, 0, 255, 1


map_module = MapModule(
    portrayal_method=cell_portrayal,
    view=[42.935329021940994, -122.10805555543601],
    zoom=11.1,
    map_height=341,
    map_width=498,
)
water_chart = mesa.visualization.ChartModule(
    [
        {"Label": "Total Amount of Water", "Color": "Black"},
        {"Label": "Total Contained", "Color": "Blue"},
        {"Label": "Total Outflow", "Color": "Orange"},
    ]
)

server = ModularServer(
    Rainfall, [map_module, water_chart], "Rainfall Model", model_params
)
