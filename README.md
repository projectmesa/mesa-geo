# mesa-geo - a GIS extension to Mesa Agent-Based Modeling

mesa-geo implements a `GeoSpace` that can host GIS-based `GeoAgents`, which are like normal Agents, except they have a `shape` attribute that is a [Shapely object](https://shapely.readthedocs.io/en/latest/manual.html). You can use `Shapely` directly to create arbitrary shapes, but in most cases you will want to import your shapes from a file. Mesa-geo allows you to create GeoAgents from any vector data file (e.g. shapefiles), valid GeoJSON objects or a GeoPandas GeoDataFrame.

This is the first release of mesa-geo. No functionality guaranteed, bugs included.

## Installation

To install mesa-geo on linux or macOS run

```shell
pip install mesa-geo
```

On windows you should first use Anaconda to install some of the requirements with

```shell
conda install fiona pyproj rtree shapely
pip install mesa-geo
```

Since mesa-geo is in early development you could also install the latest version directly from Github via

```shell
pip install -e git+https://github.com/projectmesa/mesa-geo.git#egg=mesa-geo
```

## Getting started

You should be familiar with how [mesa](https://github.com/projectmesa/mesa) works.

So let's get started with some shapes! We will work with [records of US states](http://eric.clst.org/Stuff/USGeoJSON). We use the `requests` library to retrieve the data, but of course you can work with local data.

```python
from mesa_geo import GeoSpace, GeoAgent, AgentCreator
from mesa import Model
import requests
url = 'http://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_20m.json'
r = requests.get(url)
geojson_states = r.json()
```

First we create a `State` Agent and a `GeoModel`. Both should look familiar if you have worked with mesa before.

```python
class State(GeoAgent):
    def __init__(self, unique_id, model, shape):
        super().__init__(unique_id, model, shape)

class GeoModel(Model):
    def __init__(self):
        self.space = GeoSpace()
        
        state_agent_kwargs = dict(model=self)
        AC = AgentCreator(agent_class=State, agent_kwargs=state_agent_kwargs)
        agents = AC.from_GeoJSON(GeoJSON=geojson_states, unique_id="NAME")
        self.space.add_agents(agents)
```

In the `GeoModel` we first create an instance of AgentCreator, where we provide the Agent class (State) and its required arguments, except shape and unique_id. We then use the `.from_GeoJSON` function to create our agents from the shapes in the GeoJSON file. We provide the feature "name" as the key from which the agents get their unique_ids.
Finally, we add the agents to the GeoSpace

Let's instantiate our model and look at one of the agents:

```python
m = GeoModel()

agent = m.space.agents[0]
print(agent.unique_id)
agent.shape
```

If you work in the Jupyter Notebook your output should give you the name of the state and a visual representation of the shape.

    Arizona

!['Arizona state borders'](output_3_1.svg)

By default the AgentCreator also sets further agent attributes from the Feature properties.

```python
agent.CENSUSAREA
```

    113594.084

Let's start to do some spatial analysis. We can use usual Mesa function names to get neighboring states

```python
neighbors = m.space.get_neighbors(agent)
print([a.unique_id for a in neighbors])
```

    California
    Colorado
    New Mexico
    Utah
    Nevada

To get a list of all states within a certain distance you can use the following

```python
[a.unique_id for a in m.space.get_neighbors_within_distance(agent, 600000)]
```

    ['California',
    'Colorado',
    'New Mexico',
    'Oklahoma',
    'Wyoming',
    'Idaho',
    'Utah',
    'Nevada']

The unit for the distance depends on the coordinate reference system (CRS) of the GeoSpace. Since we did not specify the CRS, mesa-geo defaults to the 'Web Mercator' projection (in meters). If you want to do some serious measurements you should always set an appropriate CRS, since the accuracy of Web Mercator declines with distance from the equator.  We can achieve this by initializing the AgentCreator and the GeoSpace with the `crs` keyword  `crs="epsg:2163"`. Mesa-geo then transforms all coordinates from the GeoJSON geographic coordinates into the set crs.

## Going further

To get a deeper understanding of mesa-geo you should checkout the GeoSchelling example. It implements a Leaflet visualization which is similar to use as the CanvasGridVisualization of Mesa.

To add further functionality, I need feedback on which functionality is desired by users. Please post a message [here](https://groups.google.com/forum/#!topic/projectmesa-dev/qEf2XBFZYnI) or open an issue if you have any ideas or recommendations.
