from model import SchellingModel
import pyproj


m = SchellingModel(.2, .2)

a = m.grid.agents[3]

a.shape.geom_type

from_crs = pyproj.Proj(init='epsg:4326')
to_crs = m.grid.crs

# m.grid.transform(, a.shape)

a.shape.exterior.coords.xy
