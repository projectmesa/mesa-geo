from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from model import InfectedModel
from mesa_geo.visualization.MapModule import MapModule


class InfectedElement(TextElement):
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
    if agent.atype == 'infected':
        portrayal["color"] = "Red"
    else:
        portrayal["color"] = "Blue"
    return portrayal


infected_element = InfectedElement()
map_element = MapModule(infected_draw, [43.741667, -79.373333], 11, 500, 500)
#map_element = MapModule(infected_draw, [43.547899,-96.735894], 4, 500, 500)
infected_chart = ChartModule([{"Label": "infected", "Color": "Black"}])
server = ModularServer(
    InfectedModel, [map_element, infected_element, infected_chart], "Infected", model_params
)
server.launch()
