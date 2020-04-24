from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from model import InfectedModel, PersonAgent
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
    "pop_size": UserSettableParameter("slider", "Population size", 10, 10, 100, 10),
    "minority_pc": UserSettableParameter(
        "slider", "Fraction minority", 0.2, 0.00, 1.0, 0.05
    ),
}


def infected_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, PersonAgent):
        # portrayal["Shape"] = 'Triangle'
        portrayal["radius"] = '2'
    if agent.atype in ['hotspot', 'infected']:
        portrayal["color"] = "Red"
    else:
        portrayal["color"] = "Green"
    return portrayal


infected_text = InfectedText()
map_element = MapModule(infected_draw, InfectedModel.MAP_COORDS, 10, 500, 500)
infected_chart = ChartModule([{"Label": "infected", "Color": "Black"}])
server = ModularServer(
    InfectedModel, [map_element, infected_text, infected_chart], "Infected", model_params
)
server.launch()
