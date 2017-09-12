from shapely.geometry import Point, LineString, Polygon, shape, LinearRing


class Point(Point):
    """ A single point """
    def __init__(self, pos):
        super().__init__(pos)


class Line(LineString):
    def __init__(self, pos):
        super().__init__(pos)


class Polygon(Polygon):
    def __init__(self, pos):
        super().__init__(pos)

class LinearRing(LinearRing):
    def __init__(self, pos):
        super().__init__(pos)


def as_shape(GeoJSON):
    """ as_shape takes any valid GeoJSON object and turns it into a
    shapely.geometry object. The return value depends on the type of the
    GeoJSON object:
    For Geometry returns only the shape
    For GeometryCollection return a list of shapes
    For Feature return the shape and the properties members
    For FeatureCollection return a list of shapes and a list of properties
    members.
    """
    gj = GeoJSON
    geometries = ["Point", "MultiPoint", "LineString",
                  "MultiLineString", "Polygon", "MultiPolygon"]
    if gj['type'] in geometries:
        return shape(gj)

    if gj['type'] == 'GeometryCollection':
        shapes = []
        for geometry in gj['geometries']:
            shapes.append(shape(geometry))
        return shapes

    if gj['type'] == 'Feature':
        attributes = gj['properties']
        return shape(gj['geometry']), attributes

    if gj['type'] == "FeatureCollection":
        shapes, attributes = ([], [])
        for feature in gj['features']:
            shapes.append(shape(feature['geometry']))
            attributes.append(feature['properties'])
        return shapes, attributes
