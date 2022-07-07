import mesa
from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa_geo.visualization.modules import MapModule

from model import GeoSir
from agents import PersonAgent


class InfectedText(TextElement):
    """
    Display a text count of how many steps have been taken
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Steps: " + str(model.steps)


model_params = {
    "pop_size": mesa.visualization.Slider("Population size", 30, 10, 100, 10),
    "init_infected": mesa.visualization.Slider(
        "Fraction initial infection", 0.2, 0.00, 1.0, 0.05
    ),
    "exposure_distance": mesa.visualization.Slider(
        "Exposure distance", 500, 100, 1000, 100
    ),
}


def infected_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, PersonAgent):
        portrayal["radius"] = "2"
    if agent.atype in ["hotspot", "infected"]:
        portrayal["color"] = "Red"
    elif agent.atype in ["safe", "susceptible"]:
        portrayal["color"] = "Green"
    elif agent.atype in ["recovered"]:
        portrayal["color"] = "Blue"
    elif agent.atype in ["dead"]:
        portrayal["color"] = "Black"
    return portrayal


infected_text = InfectedText()
map_element = MapModule(infected_draw, GeoSir.MAP_COORDS, 10, 500, 500)
infected_chart = ChartModule(
    [
        {"Label": "infected", "Color": "Red"},
        {"Label": "susceptible", "Color": "Green"},
        {"Label": "recovered", "Color": "Blue"},
        {"Label": "dead", "Color": "Black"},
    ]
)
server = ModularServer(
    GeoSir,
    [map_element, infected_text, infected_chart],
    "Basic agent-based SIR model",
    model_params,
)
