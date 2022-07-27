Release History
---------------

## 0.3.0 (2022-07-27)

### Special Notes

- BREAKING: rename model.grid to model.space [#40](https://github.com/projectmesa/mesa-geo/pull/40)
- BREAKING: rename GeoAgent's shape attribute to geometry [#57](https://github.com/projectmesa/mesa-geo/pull/57)

### Improvements

- feat/crs [#58](https://github.com/projectmesa/mesa-geo/pull/58)
  - add GeoAgent.crs attribute
  - update GeoSpace with GeoAgent.crs
- extract an _AgentLayer from GeoSpace [#62](https://github.com/projectmesa/mesa-geo/pull/62)
- add layers into geospace [#67](https://github.com/projectmesa/mesa-geo/pull/67)
- implement RasterLayer [#75](https://github.com/projectmesa/mesa-geo/pull/75)
- create raster layer from file [#92](https://github.com/projectmesa/mesa-geo/pull/92)

- ***Front-end updates***
  - implement LeafletPortrayal dataclass for GeoAgent portrayal [#84](https://github.com/projectmesa/mesa-geo/pull/84)

- ***CI updates***
  - ci: Replace Travis with GH Actions [#47](https://github.com/projectmesa/mesa-geo/pull/47)
  - ci: Disable PyPy tests for now [#56](https://github.com/projectmesa/mesa-geo/pull/56)

- ***Dependency updates***
  - Frontend dependencies [#54](https://github.com/projectmesa/mesa-geo/pull/54)
    - remove all frontend dependencies available from mesa
    - create setup.cfg and pyproject.toml from setup.py
  - download leaflet during install [#59](https://github.com/projectmesa/mesa-geo/pull/59)
  - remove version number from leaflet filenames [#61](https://github.com/projectmesa/mesa-geo/pull/61)
  - update for Mesa v1.0.0 [#78](https://github.com/projectmesa/mesa-geo/pull/78)
    - specify mesa 1.x dependency
    - update for mesa css includes
    - remove jQuery usage in MapModule.js
    - use Slider instead of UserSettableParameter in examples

- ***Example updates***
  - update examples [#74](https://github.com/projectmesa/mesa-geo/pull/74)
    - change examples folder structure
    - add test for examples
    - add geo_schelling_points example
  - add rainfall and urban growth examples [#80](https://github.com/projectmesa/mesa-geo/pull/80)
  - add uganda example [#90](https://github.com/projectmesa/mesa-geo/pull/90)

- ***Other improvements***
  - add github issue templates [#38](https://github.com/projectmesa/mesa-geo/pull/38)
  - apply Black to all Python files [#50](https://github.com/projectmesa/mesa-geo/pull/50)
  - add code of conduct and contributing guide [#69](https://github.com/projectmesa/mesa-geo/pull/69)
  - update license with year and contributors [#86](https://github.com/projectmesa/mesa-geo/pull/86)
  - rename master branch to main [#89](https://github.com/projectmesa/mesa-geo/pull/89)

### Fixes

- fix remove_agent in GeoSpace [#34](https://github.com/projectmesa/mesa-geo/pull/34)
- remove deprecated skip_equivalent from pyproj [#43](https://github.com/projectmesa/mesa-geo/pull/43)
- flake8: Fix errors [#51](https://github.com/projectmesa/mesa-geo/pull/51)
- rename InstallCommand to BuildCommand [#55](https://github.com/projectmesa/mesa-geo/pull/55)
- fix codecov and README.md [#71](https://github.com/projectmesa/mesa-geo/pull/71)
- use shape.centroid instead of shape.center() [#73](https://github.com/projectmesa/mesa-geo/pull/73)
- fix unique id exception for raster cells [#83](https://github.com/projectmesa/mesa-geo/pull/83)
- fix total_bounds check in GeoSpace [#88](https://github.com/projectmesa/mesa-geo/pull/88)
