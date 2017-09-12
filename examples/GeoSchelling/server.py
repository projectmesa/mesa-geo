from mesa.visualization.ModularVisualization import (ModularServer,
                                                     VisualizationElement)
from mesa.visualization.modules import ChartModule, TextElement
from model import SchellingModel
from mesa.visualization.UserParam import UserSettableParameter


class MapModule(VisualizationElement):
    local_includes = ["Map.js", "leaflet.min.js"]

    def __init__(self, view, zoom, map_height, map_width):
        self.map_height = map_height
        self.map_width = map_width
        self.view = view
        new_element = "new MapModule({}, {}, {}, {})"
        new_element = new_element.format(view,
                                         zoom,
                                         map_width,
                                         map_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        agents = [a.__geo_interface__() for a in model.grid.agents]
        return [agents, model.grid.bbox]


class HappyElement(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''
    def __init__(self):
        pass

    def render(self, model):
        return "Happy agents: " + str(model.happy)


model_params = {
        "density": UserSettableParameter("slider", "Agent density",
                                         0.8, 0.1, 1.0, 0.1),
        "minority_pc": UserSettableParameter("slider", "Fraction minority",
                                             0.2, 0.00, 1.0, 0.05)
    }


happy_element = HappyElement()
map_element = MapModule([52, 12], 4, 500, 500)
happy_chart = ChartModule([{"Label": "happy", "Color": "Black"}])
server = ModularServer(SchellingModel,
                       [map_element, happy_element, happy_chart],
                       "Schelling", model_params)
server.launch()
