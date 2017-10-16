from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from model import SchellingModel
from mesa.visualization.ModularVisualization import VisualizationElement


class MapModule(VisualizationElement):
    """A MapModule for Leaflet maps."""

    package_includes = []
    local_includes = ["leaflet.min.js", "LeafletMap.js"]

    def __init__(self, portrayal_method, view=[0, 0], zoom=10,
                 map_height=500, map_width=500):
        self.portrayal_method = portrayal_method
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
        featurecollection = dict(type='FeatureCollection', features=[])
        for i, agent in enumerate(model.grid.agents):
            shape = agent.__geo_interface__()
            portrayal = self.portrayal_method(agent)
            for key, value in portrayal.items():
                shape['properties'][key] = value
                featurecollection['features'].append(shape)
        return featurecollection


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


def schelling_draw(agent):
    '''
    Portrayal Method for canvas
    '''
    portrayal = dict()
    if agent.atype is None:
        portrayal["color"] = "Grey"
    elif agent.atype == 0:
        portrayal["color"] = "Red"
    else:
        portrayal["color"] = "Blue"
    return portrayal


happy_element = HappyElement()
map_element = MapModule(schelling_draw, [52, 12], 4, 500, 500)
happy_chart = ChartModule([{"Label": "happy", "Color": "Black"}])
server = ModularServer(SchellingModel,
                       [map_element, happy_element, happy_chart],
                       "Schelling", model_params)
server.launch()
