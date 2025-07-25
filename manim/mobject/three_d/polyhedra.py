"""General polyhedral class and platonic solids."""

from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING, Any

import numpy as np

from manim.mobject.geometry.polygram import Polygon
from manim.mobject.graph import Graph
from manim.mobject.three_d.three_dimensions import Dot3D
from manim.mobject.types.vectorized_mobject import VGroup
from manim.utils.qhull import QuickHull

if TYPE_CHECKING:
    from manim.mobject.mobject import Mobject
    from manim.typing import Point3D, Point3DLike_Array

__all__ = [
    "Polyhedron",
    "Tetrahedron",
    "Octahedron",
    "Icosahedron",
    "Dodecahedron",
    "ConvexHull3D",
]


class Polyhedron(VGroup):
    """An abstract polyhedra class.

    In this implementation, polyhedra are defined with a list of vertex coordinates in space, and a list
    of faces. This implementation mirrors that of a standard polyhedral data format (OFF, object file format).

    Parameters
    ----------
    vertex_coords
        A list of coordinates of the corresponding vertices in the polyhedron. Each coordinate will correspond to
        a vertex. The vertices are indexed with the usual indexing of Python.
    faces_list
        A list of faces. Each face is a sublist containing the indices of the vertices that form the corners of that face.
    faces_config
        Configuration for the polygons representing the faces of the polyhedron.
    graph_config
        Configuration for the graph containing the vertices and edges of the polyhedron.

    Examples
    --------
    To understand how to create a custom polyhedra, let's use the example of a rather simple one - a square pyramid.

    .. manim:: SquarePyramidScene
        :save_last_frame:

        class SquarePyramidScene(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                vertex_coords = [
                    [1, 1, 0],
                    [1, -1, 0],
                    [-1, -1, 0],
                    [-1, 1, 0],
                    [0, 0, 2]
                ]
                faces_list = [
                    [0, 1, 4],
                    [1, 2, 4],
                    [2, 3, 4],
                    [3, 0, 4],
                    [0, 1, 2, 3]
                ]
                pyramid = Polyhedron(vertex_coords, faces_list)
                self.add(pyramid)

    In defining the polyhedron above, we first defined the coordinates of the vertices.
    These are the corners of the square base, given as the first four coordinates in the vertex list,
    and the apex, the last coordinate in the list.

    Next, we define the faces of the polyhedron. The triangular surfaces of the pyramid are polygons
    with two adjacent vertices in the base and the vertex at the apex as corners. We thus define these
    surfaces in the first four elements of our face list. The last element defines the base of the pyramid.

    The graph and faces of polyhedra can also be accessed and modified directly, after instantiation.
    They are stored in the `graph` and `faces` attributes respectively.

    .. manim:: PolyhedronSubMobjects
        :save_last_frame:

        class PolyhedronSubMobjects(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                octahedron = Octahedron(edge_length = 3)
                octahedron.graph[0].set_color(RED)
                octahedron.faces[2].set_color(YELLOW)
                self.add(octahedron)
    """

    def __init__(
        self,
        vertex_coords: Point3DLike_Array,
        faces_list: list[list[int]],
        faces_config: dict[str, str | int | float | bool] = {},
        graph_config: dict[str, Any] = {},
    ):
        super().__init__()
        self.faces_config = dict(
            {"fill_opacity": 0.5, "shade_in_3d": True}, **faces_config
        )
        self.graph_config = dict(
            {
                "vertex_type": Dot3D,
                "edge_config": {
                    "stroke_opacity": 0,  # I find that having the edges visible makes the polyhedra look weird
                },
            },
            **graph_config,
        )
        self.vertex_coords = vertex_coords
        self.vertex_indices = list(range(len(self.vertex_coords)))
        self.layout: dict[Hashable, Any] = dict(enumerate(self.vertex_coords))
        self.faces_list = faces_list
        self.face_coords = [[self.layout[j] for j in i] for i in faces_list]
        self.edges = self.get_edges(self.faces_list)
        self.faces = self.create_faces(self.face_coords)
        self.graph = Graph(
            self.vertex_indices, self.edges, layout=self.layout, **self.graph_config
        )
        self.add(self.faces, self.graph)
        self.add_updater(self.update_faces)

    def get_edges(self, faces_list: list[list[int]]) -> list[tuple[int, int]]:
        """Creates list of cyclic pairwise tuples."""
        edges: list[tuple[int, int]] = []
        for face in faces_list:
            edges += zip(face, face[1:] + face[:1])
        return edges

    def create_faces(
        self,
        face_coords: Point3DLike_Array,
    ) -> VGroup:
        """Creates VGroup of faces from a list of face coordinates."""
        face_group = VGroup()
        for face in face_coords:
            face_group.add(Polygon(*face, **self.faces_config))
        return face_group

    def update_faces(self, m: Mobject) -> None:
        face_coords = self.extract_face_coords()
        new_faces = self.create_faces(face_coords)
        self.faces.match_points(new_faces)

    def extract_face_coords(self) -> Point3DLike_Array:
        """Extracts the coordinates of the vertices in the graph.
        Used for updating faces.
        """
        new_vertex_coords = []
        for v in self.graph.vertices:
            new_vertex_coords.append(self.graph[v].get_center())
        layout = dict(enumerate(new_vertex_coords))
        return [[layout[j] for j in i] for i in self.faces_list]


class Tetrahedron(Polyhedron):
    """A tetrahedron, one of the five platonic solids. It has 4 faces, 6 edges, and 4 vertices.

    Parameters
    ----------
    edge_length
        The length of an edge between any two vertices.

    Examples
    --------

    .. manim:: TetrahedronScene
        :save_last_frame:

        class TetrahedronScene(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                obj = Tetrahedron()
                self.add(obj)
    """

    def __init__(self, edge_length: float = 1, **kwargs: Any):
        unit = edge_length * np.sqrt(2) / 4
        super().__init__(
            vertex_coords=[
                np.array([unit, unit, unit]),
                np.array([unit, -unit, -unit]),
                np.array([-unit, unit, -unit]),
                np.array([-unit, -unit, unit]),
            ],
            faces_list=[[0, 1, 2], [3, 0, 2], [0, 1, 3], [3, 1, 2]],
            **kwargs,
        )


class Octahedron(Polyhedron):
    """An octahedron, one of the five platonic solids. It has 8 faces, 12 edges and 6 vertices.

    Parameters
    ----------
    edge_length
        The length of an edge between any two vertices.

    Examples
    --------

    .. manim:: OctahedronScene
        :save_last_frame:

        class OctahedronScene(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                obj = Octahedron()
                self.add(obj)
    """

    def __init__(self, edge_length: float = 1, **kwargs: Any):
        unit = edge_length * np.sqrt(2) / 2
        super().__init__(
            vertex_coords=[
                np.array([unit, 0, 0]),
                np.array([-unit, 0, 0]),
                np.array([0, unit, 0]),
                np.array([0, -unit, 0]),
                np.array([0, 0, unit]),
                np.array([0, 0, -unit]),
            ],
            faces_list=[
                [2, 4, 1],
                [0, 4, 2],
                [4, 3, 0],
                [1, 3, 4],
                [3, 5, 0],
                [1, 5, 3],
                [2, 5, 1],
                [0, 5, 2],
            ],
            **kwargs,
        )


class Icosahedron(Polyhedron):
    """An icosahedron, one of the five platonic solids. It has 20 faces, 30 edges and 12 vertices.

    Parameters
    ----------
    edge_length
        The length of an edge between any two vertices.

    Examples
    --------

    .. manim:: IcosahedronScene
        :save_last_frame:

        class IcosahedronScene(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                obj = Icosahedron()
                self.add(obj)
    """

    def __init__(self, edge_length: float = 1, **kwargs: Any):
        unit_a = edge_length * ((1 + np.sqrt(5)) / 4)
        unit_b = edge_length * (1 / 2)
        super().__init__(
            vertex_coords=[
                np.array([0, unit_b, unit_a]),
                np.array([0, -unit_b, unit_a]),
                np.array([0, unit_b, -unit_a]),
                np.array([0, -unit_b, -unit_a]),
                np.array([unit_b, unit_a, 0]),
                np.array([unit_b, -unit_a, 0]),
                np.array([-unit_b, unit_a, 0]),
                np.array([-unit_b, -unit_a, 0]),
                np.array([unit_a, 0, unit_b]),
                np.array([unit_a, 0, -unit_b]),
                np.array([-unit_a, 0, unit_b]),
                np.array([-unit_a, 0, -unit_b]),
            ],
            faces_list=[
                [1, 8, 0],
                [1, 5, 7],
                [8, 5, 1],
                [7, 3, 5],
                [5, 9, 3],
                [8, 9, 5],
                [3, 2, 9],
                [9, 4, 2],
                [8, 4, 9],
                [0, 4, 8],
                [6, 4, 0],
                [6, 2, 4],
                [11, 2, 6],
                [3, 11, 2],
                [0, 6, 10],
                [10, 1, 0],
                [10, 7, 1],
                [11, 7, 3],
                [10, 11, 7],
                [10, 11, 6],
            ],
            **kwargs,
        )


class Dodecahedron(Polyhedron):
    """A dodecahedron, one of the five platonic solids. It has 12 faces, 30 edges and 20 vertices.

    Parameters
    ----------
    edge_length
        The length of an edge between any two vertices.

    Examples
    --------

    .. manim:: DodecahedronScene
        :save_last_frame:

        class DodecahedronScene(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                obj = Dodecahedron()
                self.add(obj)
    """

    def __init__(self, edge_length: float = 1, **kwargs: Any):
        unit_a = edge_length * ((1 + np.sqrt(5)) / 4)
        unit_b = edge_length * ((3 + np.sqrt(5)) / 4)
        unit_c = edge_length * (1 / 2)
        super().__init__(
            vertex_coords=[
                np.array([unit_a, unit_a, unit_a]),
                np.array([unit_a, unit_a, -unit_a]),
                np.array([unit_a, -unit_a, unit_a]),
                np.array([unit_a, -unit_a, -unit_a]),
                np.array([-unit_a, unit_a, unit_a]),
                np.array([-unit_a, unit_a, -unit_a]),
                np.array([-unit_a, -unit_a, unit_a]),
                np.array([-unit_a, -unit_a, -unit_a]),
                np.array([0, unit_c, unit_b]),
                np.array([0, unit_c, -unit_b]),
                np.array([0, -unit_c, -unit_b]),
                np.array([0, -unit_c, unit_b]),
                np.array([unit_c, unit_b, 0]),
                np.array([-unit_c, unit_b, 0]),
                np.array([unit_c, -unit_b, 0]),
                np.array([-unit_c, -unit_b, 0]),
                np.array([unit_b, 0, unit_c]),
                np.array([-unit_b, 0, unit_c]),
                np.array([unit_b, 0, -unit_c]),
                np.array([-unit_b, 0, -unit_c]),
            ],
            faces_list=[
                [18, 16, 0, 12, 1],
                [3, 18, 16, 2, 14],
                [3, 10, 9, 1, 18],
                [1, 9, 5, 13, 12],
                [0, 8, 4, 13, 12],
                [2, 16, 0, 8, 11],
                [4, 17, 6, 11, 8],
                [17, 19, 5, 13, 4],
                [19, 7, 15, 6, 17],
                [6, 15, 14, 2, 11],
                [19, 5, 9, 10, 7],
                [7, 10, 3, 14, 15],
            ],
            **kwargs,
        )


class ConvexHull3D(Polyhedron):
    """A convex hull for a set of points

    Parameters
    ----------
    points
        The points to consider.
    tolerance
        The tolerance used for quickhull.
    kwargs
        Forwarded to the parent constructor.

    Examples
    --------
    .. manim:: ConvexHull3DExample
        :save_last_frame:
        :quality: high

        class ConvexHull3DExample(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                points = [
                    [ 1.93192757,  0.44134585, -1.52407061],
                    [-0.93302521,  1.23206983,  0.64117067],
                    [-0.44350918, -0.61043677,  0.21723705],
                    [-0.42640268, -1.05260843,  1.61266094],
                    [-1.84449637,  0.91238739, -1.85172623],
                    [ 1.72068132, -0.11880457,  0.51881751],
                    [ 0.41904805,  0.44938012, -1.86440686],
                    [ 0.83864666,  1.66653337,  1.88960123],
                    [ 0.22240514, -0.80986286,  1.34249326],
                    [-1.29585759,  1.01516189,  0.46187522],
                    [ 1.7776499,  -1.59550796, -1.70240747],
                    [ 0.80065226, -0.12530398,  1.70063977],
                    [ 1.28960948, -1.44158255,  1.39938582],
                    [-0.93538943,  1.33617705, -0.24852643],
                    [-1.54868271,  1.7444399,  -0.46170734]
                ]
                hull = ConvexHull3D(
                    *points,
                    faces_config = {"stroke_opacity": 0},
                    graph_config = {
                        "vertex_type": Dot3D,
                        "edge_config": {
                            "stroke_color": BLUE,
                            "stroke_width": 2,
                            "stroke_opacity": 0.05,
                        }
                    }
                )
                dots = VGroup(*[Dot3D(point) for point in points])
                self.add(hull)
                self.add(dots)
    """

    def __init__(self, *points: Point3D, tolerance: float = 1e-5, **kwargs: Any):
        # Build Convex Hull
        array = np.array(points)
        hull = QuickHull(tolerance)
        hull.build(array)

        # Setup Lists
        vertices = []
        faces = []

        # Extract Faces
        c = 0
        d = {}
        facets = set(hull.facets) - hull.removed
        for facet in facets:
            tmp = set()
            for subfacet in facet.subfacets:
                for point in subfacet.points:
                    if point not in d:
                        vertices.append(point.coordinates)
                        d[point] = c
                        c += 1
                    tmp.add(point)
            faces.append([d[point] for point in tmp])

        # Call Polyhedron
        super().__init__(
            vertex_coords=vertices,
            faces_list=faces,
            **kwargs,
        )
