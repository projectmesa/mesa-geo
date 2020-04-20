from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from model import InfectedModel
from mesa_geo.visualization.MapModule import MapModule


class InfectedText(TextElement):
    """
    Display a text count of how many infected agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Infected agents: " + str(model.infected)


model_params = {
    "density": UserSettableParameter("slider", "Agent density", 0.6, 0.1, 1.0, 0.1),
    "minority_pc": UserSettableParameter(
        "slider", "Fraction minority", 0.2, 0.00, 1.0, 0.05
    ),
}


def infected_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    portrayal["Shape"] = 'Circle'
    portrayal["radius"] = '2'
    portrayal["x"] = '0'
    portrayal["y"] = '0'
    portrayal["color"] = "Green"
    if agent.atype in ['hotspot', 'infected']:
        portrayal["color"] = "Red"
    else:
        portrayal["color"] = "Blue"
    return portrayal


infected_element = InfectedText()
map_element = MapModule(infected_draw, [43.741667, -79.373333], 10, 500, 500)
#map_element = MapModule(infected_draw, [43.547899,-96.735894], 4, 500, 500)
infected_chart = ChartModule([{"Label": "infected", "Color": "Black"}])
server = ModularServer(
    InfectedModel, [map_element, infected_element, infected_chart], "Infected", model_params
)
server.launch()
