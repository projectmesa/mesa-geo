# GeoSchelling Segregation Model

## Summary

This is a geoversion of a simplified Schelling example. For the original implementation details please see the Schelling examples.
Instead of a regular grid it uses European NUTS-2 regions as location for majority and minority opinions.
For a region to be happy it only needs to have more similar neighbors than unsimilar ones.

This example needs the python packages shapely and geojson which are not in the basic requirements of Mesa.
