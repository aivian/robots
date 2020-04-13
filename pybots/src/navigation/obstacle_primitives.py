import hashlib
import numpy
import pdb

import shapely.geometry
import shapely.ops

import geometry.lines
import geometry.helpers

def _numpy_to_linestring(numpy_array):
    """Convert a number array to a linestring

    Arguments:
        numpy_array: an (n,3) numpy array to convert into a shapely
            linestring instance

    Returns:
        linestring: the shapely linestring with vertices at the points
            given in numpy_array
    """
    path = shapely.geometry.LineString(numpy_array)
    return path

class ShapePrimitive(object):
    """A class to hold a 2d obstacle
    """
    def __init__(self, shape=None, definition=None):
        """Constructor

        Arguments:
            shape: shapely LinearRing, Polygon or numpy (n,2) array defining
                the perimeter of the obstacle in a local North/East coordinate
                frame. optional, if unspecified then definition will be expected
            definition: optional, a dictionary (likely from a yaml file) with
                the perimeter

        Returns:
            class instance
        """
        if definition is None:
            if isinstance(shape, shapely.geometry.LinearRing):
                shape = shapely.geometry.Polygon(shape)
            if isinstance(shape, numpy.ndarray):
                shape = shapely.geometry.Polygon(shape.T)
            definition = {
                'shape': shape}
        self.define_from_dictionary(definition)

    def define_from_dictionary(self, definition):
        """create this from a dictionary

        Arguments:
            definition: optional, a dictionary (likely from a yaml file) with
                the shape as a field. may also have an 'id' field for this shape

        Returns:
            no returns
        """
        self._shape = shapely.geometry.Polygon(definition['shape'])
        # if the obstacle definition doesn't have a name then make one up that
        # should be unique
        if 'id' not in definition:
            hashin = b''
            for obj in [self._shape, numpy.random.randn(), definition]:
                hashin += str(obj).encode()
            self._id = hashlib.md5(hashin).hexdigest()
        else:
            self._id = definition['id']

        # epsilon is the allowance for numerical error when checking if an
        # intersection point is between the top and bottom faces
        if 'epsilon' not in definition:
            self._epsilon = 1.e-6
        else:
            self._epsilon = definition['epsilon']

    @property
    def id(self):
        """Get the name of this shape"""
        return self._id

    def is_point_inside(self, point):
        """ Check if a point is inside the shape.

        determine if a point lies within the region (inside of its
        borders and outside of any holes in it)

        Arguments:
            point: shapely Point object or 3, element numpy array specifying
                a point in ned coordinates

        Returns:
            is_inside: bool specifying if the point is within the shape
        """
        if isinstance(point, numpy.ndarray):
            point = shapely.geometry.Point(point)
        return point.within(self._shape)

    def is_path_inside(self, path):
        """ Determines if a path lies entirely within a shape.

        Arguments:
            path: shapely LineString object or nx3 numpy array defining
                a path

        Returns:
            is_inside: bool specifying if the path lies within the shape
        """
        if type(path) is numpy.ndarray:
            path = _numpy_to_linestring(path)
        return path.within(self._shape)

    def nearest_exterior(self, point):
        """ Compute a vector from a point to the nearest exterior boundary.

        Arguments:
            point: shapely Point object or 3, numpy array defining the ned
                position of a point

        Returns:
            vector_to_boundary: 1x3 numpy array ned vector to boundary
        """
        if type(point) is numpy.ndarray:
            point = shapely.geometry.Point(point)
        return geometry.lines.point_line_distance(
            point, self._shape.exterior)[0]

    def nearest_hole(self, point):
        """ Compute a vector from a point to the nearest interior boundary.

        Arguments:
            point: shapely Point object or 3, numpy array defining the ned
                position of a point

        Returns:
            vector_to_boundary: 1x3 numpy array ned vector to interior boundary
        """
        if type(point) is numpy.ndarray:
            point = shapely.geometry.Point(point)
        vector_to_boundary = numpy.ones((1, 3)) * numpy.inf
        # a shape can have multiple holes so we need to iterate over them
        for shape in self._shape.interiors:
            dist = geometry.lines.point_line_distance(point, shape)[0]
            if numpy.linalg.norm(dist) < numpy.linalg.norm(vector_to_boundary):
                vector_to_boundary = dist
        return vector_to_boundary

    def nearest_boundary(self, point):
        """ Compute a vector from a point to the nearest boundary

        determines vector to the nearest boundary whether hole or exterior

        Arguments:
            point: shapely Point object or numpy array defining the ned
                position of a point

        Returns:
            vector_to_boundary: 1x3 numpy array ned vector to boundary
        """
        r_exterior = self.nearest_exterior(point)
        r_hole = self.nearest_hole(point)
        if numpy.linalg.norm(r_hole) < numpy.linalg.norm(r_exterior):
            return r_hole
        return r_exterior

    def exterior_intersections(self, path):
        """ Finds all of the points where a path intersects the exterior.

        Arguments:
            path: shapely LineString object or nx3 numpy array defining
                the ned positions of vertices in the path

        Returns:
            intersections: tuple of intersection points between the given
                path and the exterior boundary
        """
        if type(path) is numpy.ndarray:
            path = _numpy_to_linestring(path)
        intersection = path.intersection(self._shape.exterior)
        # sometimes we can get a linestring when there is no intersection
        if isinstance(intersections, shapely.geometry.LineString):
            if intersection.is_empty:
                return tuple()
        # we want a tuple regardless of how many intersections there are so if
        # we get one point back then make it a tuple
        if isinstance(intersection, shapely.geometry.Point):
            return (intersection,)
        else:
            return tuple(intersection)

    def hole_intersections(self, path):
        """ Find intersections between a path and holes in the shape.

        Arguments:
            path: shapely LineString object or nx3 numpy array defining
                the ned positions of vertices in the path

        Returns:
            intersections: tuple of tuples: one tuple each for each hole which
                contains the intersection points between the given path
                and the hole
        """
        if type(path) is numpy.ndarray:
            path = _numpy_to_linestring(path)
        intersections = []
        for hole in self._shape.interiors:
            this_hole_intersections = path.intersection(hole)
            if isinstance(this_hole_intersections, shapely.geometry.Point):
                this_hole_intersections = (this_hole_intersections,)
            if isinstance(this_hole_intersections, shapely.geometry.LineString):
                # this seems to happen when the instersection is on a vertex...
                this_intersection = numpy.array(this_hole_intersections)
                this_hole_intersections = (
                    shapely.geometry.Point(this_intersection[0]),)
            intersections.append(tuple(pt for pt in this_hole_intersections))
        return tuple(intersections)

    def intersections(self, path):
        """ Finds all intersections between a path and the boundaries.

        finds all of the points where a path intersects any edge of the shape
        whether a boundary or a hole

        Arguments:
            path: shapely LineString object or nx3 numpy array defining
                the ned positions of vertices in the path

        Returns:
            intersections: tuple of intersection points between the given
                path and the shape
        """
        if type(path) is numpy.ndarray:
            path = _numpy_to_linestring(path)
        intersections = list(self.exterior_intersection(path))
        intersections += list(i for i in self.hole_intersection(path))
        return tuple(intersections)

class PrismaticShape(ShapePrimitive):
    def __init__(self, shape=None, z0=None, zt=None, definition=None):
        """Constructor

        Arguments:
            shape: shapely LinearRing, Polygon or numpy (n,2) array defining
                the perimeter of the obstacle in a local North/East coordinate
                frame. optional, if unspecified then definition will be expected
            definition: optional, a dictionary (likely from a yaml file) with
                the perimeter

        Returns:
            class instance
        """
        if definition is None:
            if z0 is None:
                z0 = numpy.inf
            if zt is None:
                zt = -numpy.inf
            definition = {
                'shape': shape,
                'z0': z0,
                'zt': zt}
        self.define_from_dictionary(definition)

    def define_from_dictionary(self, definition):
        """Get the stuff we need to define this shape from a dictionary

        Arguments:
            definition: dictionary with
                shape:
                    N: north position
                    E: east position
                z0: down position of base of shape
                zt: down position of top of shape

        Returns:
            sets the shape and z extents internall
        """
        super(PrismaticShape, self).define_from_dictionary(definition)
        self._z0 = float(definition['z0'])
        self._zt = float(definition['zt'])

    def is_point_inside(self, point):
        """ Check if a point is inside the shape.

        determine if a point lies within the region (inside of its
        borders and outside of any holes in it)

        Arguments:
            point: shapely Point object or 3, element numpy array specifying
                a point in ned coordinates

        Returns:
            is_inside: bool specifying if the point is within the shape
        """
        if isinstance(point, numpy.ndarray):
            point = shapely.geometry.Point(point)
        is_inside = super(PrismaticShape, self).is_point_inside(point)
        # we need to check if the point is inside the lateral boundaries and
        # that it's z coordinate is between the extents of this shape
        return is_inside and (point.z > self._zt) and (point.z < self._z0)

    def is_path_inside(self, path):
        """ Determines if a path lies entirely within a shape.

        Arguments:
            path: shapely LineString object or nx3 numpy array defining
                a path

        Returns:
            is_inside: bool specifying if the path lies within the shape
        """
        if type(path) is numpy.ndarray:
            path = _numpy_to_linestring(path)
        assert path.has_z, 'path must have xyz coordinates'
        is_inside = super(PrismaticShape, self).is_path_inside(path)
        z = numpy.array(path)[:,2]
        # we need to check if the path is inside the lateral boundaries and
        # that z coordinates of all points are between the extents of this shape
        return is_inside and numpy.all(z > self._zt) and numpy.all(z < self._z0)

    def nearest_exterior(self, point):
        """ Compute a vector from a point to the nearest exterior boundary.

        Arguments:
            point: shapely Point object or 3, numpy array defining the ned
                position of a point

        Returns:
            vector_to_boundary: 1x3 numpy array ned vector to boundary
        """
        if type(point) is numpy.ndarray:
            point = shapely.geometry.Point(point)
        if point.within(self._shape):
            vector_to_boundary = numpy.zeros((1,3))
        else:
            vector_to_boundary = super(PrismaticShape, self).nearest_exterior(
                point)
        # after we have the vector in a 2-d plane, compute the z difference
        return self._z_difference(point, vector_to_boundary)

    def nearest_hole(self, point):
        """ Compute a vector from a point to the nearest interior boundary.

        Arguments:
            point: shapely Point object or 3, numpy array defining the ned
                position of a point

        Returns:
            vector_to_boundary: 1x3 numpy array ned vector to interior boundary
        """
        if type(point) is numpy.ndarray:
            point = shapely.geometry.Point(point)
        vector_to_boundary = super(PrismaticShape, self).nearest_hole(point)
        # after we have the vector in a 2-d plane, compute the z difference
        return self._z_difference(point, vector_to_boundary)

    def nearest_boundary(self, point):
        """ Compute a vector from a point to the nearest boundary

        determines vector to the nearest boundary whether hole or exterior

        Arguments:
            point: shapely Point object or numpy array defining the ned
                position of a point

        Returns:
            vector_to_boundary: 1x3 numpy array ned vector to boundary
        """
        if type(point) is numpy.ndarray:
            point = shapely.geometry.Point(point)
        vector_to_boundary = super(PrismaticShape, self).nearest_boundary(point)
        # after we have the vector in a 2-d plane, compute the z difference
        return self._z_difference(point, vector_to_boundary)

    def exterior_intersections(self, path):
        """ Finds all of the points where a path intersects the exterior.

        Arguments:
            path: shapely LineString object or nx3 numpy array defining
                the ned positions of vertices in the path

        Returns:
            intersections: tuple of intersection points between the given
                path and the exterior boundary
        """
        if type(path) is numpy.ndarray:
            path = _numpy_to_linestring(path)
        # compute intersection points with the 2-d shapes
        flat_intersections = list(
            super(PrismaticShape, self).exterior_intersections(path))
        # add intersections with the top and bottom
        flat_intersections += self._z_intersection(path)
        # remove any paths which don't actually intersect because they pass
        # above or below the obstacles
        return self._check_z_intersection(path, flat_intersections)

    def intersections(self, path):
        """ Finds all intersections between a path and the boundaries.

        finds all of the points where a path intersects any edge of the shape
        whether a boundary or a hole

        Arguments:
            path: shapely LineString object or nx3 numpy array defining
                the ned positions of vertices in the path

        Returns:
            intersections: tuple of intersection points between the given
                path and the shape
        """
        if type(path) is numpy.ndarray:
            path = _numpy_to_linestring(path)
        intersections = list(self.exterior_intersections(path))
        intersections += list(i for i in self.hole_intersections(path))
        return tuple(intersections)

    def _z_difference(self, point, vector):
        """Compute the z component of a vector from a pont to the shape

        Arguments:
            point: the point location
            vector: vector from point to shape

        Returns:
            vector: the vector but with the z component computed to give the
                appropriate z component to the point on the shape nearest the
                point
        """
        dz = numpy.clip(point.z, self._zt, self._z0) - point.z
        vector[0,2] = dz
        return vector

    def _check_z_intersection(self, path, flat_intersections):
        """Check intersections points to see if they would intersect in z

        Arguments:
            path: the path that we're checking on
            flat_intersections: candidate 2d intersection points to check

        Returns:
            intersections: intersection points filtered to only those where the
                intersection point satisfies the z extent of the shape
        """
        intersections = []
        for i in flat_intersections:
            ip = path.interpolate(path.project(i))
            # there is some numerical error that can happen so we allow a small
            # amount of wiggle room for the intersection point to lie between
            # the top and bottom planes
            if (
                (ip.z - self._epsilon) <= self._z0 and
                (ip.z + self._epsilon) >= self._zt):
                intersections.append(ip)
        return tuple(intersections)

    def _z_intersection(self, path):
        """Compute the points of intersection between a path and the z-normal
        faces of a prismatic shape

        Arguments:
            path: the path we're checking on

        Returns:
            intersections: list of intersection points
        """
        intersections = []
        vertices = shapely.geometry.MultiPoint(
            [shapely.geometry.Point(x,y,z) for x,y,z in path.coords[1:]])
        segments = shapely.ops.split(path, vertices)
        for s in segments:
            if not (s.within(self._shape) or s.intersects(self._shape)):
                continue
            s_z = numpy.array(s)[:,2]
            # compute the point along the line which crosses the plane defining
            # the bottom of the object
            f_0 = (self._z0 - s_z[0]) / numpy.diff(s_z)
            bottom_intersection = s.interpolate(f_0, normalized=True)
            # compute the point along the line which crosses the plane defining
            # the top of the object
            f_t = (self._zt - s_z[0]) / numpy.diff(s_z)
            top_intersection = s.interpolate(f_t, normalized=True)
            # if the point of intersection with the top or bottom is within the
            # line segment and lies within the area defining the cross-section
            # of the shape then the point is a valid intersection
            if (
                f_0 > 0.0 and
                f_0 < 1.0 and
                bottom_intersection.within(self._shape)):
                intersections.append(s.interpolate(f_0, normalized=True))
            if f_t > 0.0 and f_t < 1.0 and top_intersection.within(self._shape):
                intersections.append(s.interpolate(f_t, normalized=True))
        return intersections

