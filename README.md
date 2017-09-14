# GeoMesa - a GIS extension to Mesa Agent-Based Modeling

Currently with limited functionality, but the GeoSchelling example implements a geo version of the Schelling example and demonstrates basic functionality and visualization with leaflet.  

Requires shapely, geojson, pyproj and rtree

This is a pre-release. No functionality guaranteed, bugs included

## Implemented functions
* Add agents with shapes from GeoJSON
* Shapes are Shapely objects (with distance, buffer, etc. functions already )  
* CRS transformations (GeoJSON is always WGS84, unsuitable for accurate calculations)
* compute relation (intersection, within, etc. ) between shapes with speed-up from r-tree indexing
