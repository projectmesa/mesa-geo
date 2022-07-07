import mesa
from mesa.visualization.modules import ChartModule, TextElement

from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa_geo.visualization.modules import MapModule
from .model import GeoSchellingPoints
from .agents import PersonAgent, RegionAgent


class HappyElement(TextElement):
    def render(self, model):
        return f"Happy agents: {model.happy}"


class UnhappyElement(TextElement):
    def render(self, model):
        return f"Unhappy agents: {model.unhappy}"


model_params = {
    "red_percentage": mesa.visualization.Slider("% red", 0.5, 0.00, 1.0, 0.05),
    "similarity_threshold": mesa.visualization.Slider(
        "% similar wanted", 0.5, 0.00, 1.0, 0.05
    ),
}


def schelling_draw(agent):
    portrayal = dict()
    if isinstance(agent, RegionAgent):
        if agent.red_cnt > agent.blue_cnt:
            portrayal["color"] = "Red"
        elif agent.red_cnt < agent.blue_cnt:
            portrayal["color"] = "Blue"
        else:
            portrayal["color"] = "Grey"
    elif isinstance(agent, PersonAgent):
        portrayal["radius"] = 1
        portrayal["shape"] = "circle"
        portrayal["color"] = "Red" if agent.is_red else "Blue"
    return portrayal


happy_element = HappyElement()
unhappy_element = UnhappyElement()
map_element = MapModule(schelling_draw, [52, 12], 4, 500, 500)
happy_chart = ChartModule(
    [
        {"Label": "unhappy", "Color": "Orange"},
        {
            "Label": "happy",
            "Color": "Green",
        },
    ]
)
server = ModularServer(
    GeoSchellingPoints,
    [map_element, happy_element, unhappy_element, happy_chart],
    "Schelling",
    model_params,
)
