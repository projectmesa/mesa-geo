# Mesa-Geo: GIS Extension for Mesa Agent-Based Modeling

[![GitHub CI](https://github.com/projectmesa/mesa-geo/workflows/build/badge.svg)](https://github.com/projectmesa/mesa-geo/actions)
[![Read the Docs](https://readthedocs.org/projects/mesa-geo/badge/?version=main)](https://mesa-geo.readthedocs.io/en/main)
[![Codecov](https://codecov.io/gh/projectmesa/mesa-geo/branch/main/graph/badge.svg)](https://codecov.io/gh/projectmesa/mesa-geo)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/mesa-geo.svg)](https://pypi.org/project/mesa-geo)
[![PyPI - License](https://img.shields.io/pypi/l/mesa-geo)](https://pypi.org/project/mesa-geo/)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/mesa-geo)](https://pypistats.org/packages/mesa-geo)
[![Matrix Chat](https://img.shields.io/matrix/mesa-geo:matrix.org?label=chat&logo=Matrix)](https://matrix.to/#/#mesa-geo:matrix.org)

Mesa-Geo implements a `GeoSpace` that can host GIS-based `GeoAgents`, which are like normal Agents, except they have a `geometry` attribute that is a [Shapely object](https://shapely.readthedocs.io/en/latest/manual.html) and a `crs` attribute for its Coordinate Reference System. You can use `Shapely` directly to create arbitrary geometries, but in most cases you will want to import your geometries from a file. Mesa-Geo allows you to create GeoAgents from any vector data file (e.g. shapefiles), valid GeoJSON objects or a GeoPandas GeoDataFrame.

## Using Mesa-Geo

To install Mesa-Geo on linux or macOS run

```shell
pip install mesa-geo
```

On windows you should first use Anaconda to install some of the requirements with

```shell
conda install fiona pyproj rtree shapely
pip install mesa-geo
```

Since Mesa-Geo is in early development you could also install the latest version directly from Github via

```shell
pip install -e git+https://github.com/projectmesa/mesa-geo.git#egg=mesa-geo
```

Take a look at the [examples](https://github.com/projectmesa/mesa-geo/tree/main/examples) folder for sample models demonstrating Mesa-Geo features.

For more help on using Mesa-Geo, check out the following resources:

- [Introductory Tutorial](http://mesa-geo.readthedocs.org/en/main/tutorials/intro_tutorial.html)
- [Docs](http://mesa-geo.readthedocs.org/en/main/)
- [Mesa-Geo Discussions](https://github.com/projectmesa/mesa-geo/discussions)
- [PyPI](https://pypi.org/project/mesa-geo/)

## Contributing to Mesa-Geo

Want to join the team or just curious about what is happening with Mesa & Mesa-Geo? You can...

  * Join our [Matrix chat room](https://matrix.to/#/#mesa-geo:matrix.org) in which questions, issues, and ideas can be (informally) discussed.
  * Come to a monthly dev session (you can find dev session times, agendas and notes at [Mesa discussions](https://github.com/projectmesa/mesa/discussions).
  * Just check out the code at [GitHub](https://github.com/projectmesa/mesa-geo/).

If you run into an issue, please file a [ticket](https://github.com/projectmesa/mesa-geo/issues) for us to discuss. If possible, follow up with a pull request.

If you would like to add a feature, please reach out via [ticket](https://github.com/projectmesa/mesa-geo/issues) or join a dev session (see [Mesa discussions](https://github.com/projectmesa/mesa/discussions)).
A feature is most likely to be added if you build it!

Don't forget to check out the [Contributors guide](https://github.com/projectmesa/mesa-geo/blob/main/CONTRIBUTING.md).
