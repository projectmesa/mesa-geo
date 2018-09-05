# mesa-geo - a GIS extension to Mesa Agent-Based Modeling

mesa-geo implements a `GeoSpace` that can host GIS-based `GeoAgents`, which are exactly like normal Agents, except they have a `shape` attribute that is a [Shapely object](https://shapely.readthedocs.io/en/latest/manual.html). You can use `Shapely` directly to create arbitrary shapes, but in most cases you will want to import your shapes from a file. Mesa-geo allows you to load any GeoJSON object, but you can also import shapefiles, which are automatically converted.

This is the first release of mesa-geo. No functionality guaranteed, bugs included

## Installation

You should clone the repository and install it via
```
pip install .
```

On windows you should first use Anaconda to install some of the requirements with
```
conda install shapely rtree pyproj
pip install .
```

## Getting started
You should be familiar with how [mesa](https://github.com/projectmesa/mesa) works.

So let's get started with some shapes! We will work with [records of US states](http://eric.clst.org/Stuff/USGeoJSON). We use the `requests` library to retrieve the data, but you can also use `geojson` to work with local data.

```python
from mesa_geo import GeoSpace, GeoAgent
import requests
url = 'http://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_20m.json'
r = requests.get(url)
```

First we create a `State` Agent and a `SampleModel`. Both should look familiar if you have worked with mesa before.

```python
class State(GeoAgent):
    def __init__(self, unique_id, model, shape):
        super().__init__(unique_id, model, shape)

class SampleModel:
    def __init__(self, states):
        self.grid = GeoSpace()

        agent_kwargs = dict(model=self, unique_id='name')
        self.grid.create_agents_from_GeoJSON(GeoJSON=states, agent=State, **agent_kwargs)
```

In the `SampleModel` we create agents from the GeoJSON file. Note that we need to tell `create_agents_from_GeoJSON` the class of the agents to be created and provide the agents keyword arguments (kwargs). 

Let's instantiate our model and look at one of the agents:

```python
m = GeoModel(r.json())

agent = m.grid.agents[0]
print(agent.unique_id)
agent.shape
```

If you work in the Jupyter Notebook your output should give you the name of the state and a visual representation of the shape.

    Arizona

![](output_3_1.svg)

You might realize some magic is going on here. We used "name" for the "unique_id" and since this is the name of a Feature property of the GeoJSON it got translated to the property value. By default `GeoSpace.create_agents_from_GeoJSON` also sets further agent attributes from the Feature properties.

```python
agent.CENSUSAREA
```

    113594.084

Let's start to do some spatial analysis. We can use usual Mesa function names to get neighboring states

```python
neighbors = m.grid.get_neighbors(self)
print([a.unique_id for a in neighbors])
```

    California
    Colorado
    New Mexico
    Utah
    Nevada

To get a list of all states within a certain distance you can use the following

```python
[a.unique_id for a in m.grid.get_neighbors_within_distance(agent, 600000)]
```

    ['California',
    'Colorado',
    'New Mexico',
    'Oklahoma',
    'Wyoming',
    'Idaho',
    'Utah',
    'Nevada']

The unit for the distance depends on the coordinate reference system (CRS) of the GeoSpace. Since we did not specify the CRS, mesa-geo defaults to the 'Web Mercator' projection (in meters). However, it's only appropriate for measurements near the equator. If you want to do some serious measurements you should always set an appropriate CRS. This is easily enough done by initializing you GeoSpace with for example `GeoSpace(crs='epsg:2163')`. All transformations from the GeoJSON geographical coordinates is done automatically.

## Going further

To get a deeper understanding of mesa-geo you should checkout the GeoSchelling example. It implements a Leaflet visualization which is similar to use as the CanvasGridVisualization of Mesa.

To implement further functions I need feedback on which functionality is desired by users. Please post a message [here](https://groups.google.com/forum/#!topic/projectmesa-dev/qEf2XBFZYnI) or open an issue if you have any ideas or recommendations.
