import numpy as np

from soft_body import SoftBody

_PHI = (1 + 5**0.5) / 2

_BASE_VERTICES = [
    (-1, _PHI, 0),
    (1, _PHI, 0),
    (-1, -_PHI, 0),
    (1, -_PHI, 0),
    (0, -1, _PHI),
    (0, 1, _PHI),
    (0, -1, -_PHI),
    (0, 1, -_PHI),
    (_PHI, 0, -1),
    (_PHI, 0, 1),
    (-_PHI, 0, -1),
    (-_PHI, 0, 1),
]

_BASE_FACES = [
    (0, 11, 5),
    (0, 5, 1),
    (0, 1, 7),
    (0, 7, 10),
    (0, 10, 11),
    (1, 5, 9),
    (5, 11, 4),
    (11, 10, 2),
    (10, 7, 6),
    (7, 1, 8),
    (3, 9, 4),
    (3, 4, 2),
    (3, 2, 6),
    (3, 6, 8),
    (3, 8, 9),
    (4, 9, 5),
    (2, 4, 11),
    (6, 2, 10),
    (8, 6, 7),
    (9, 8, 1),
]


class Sphere(SoftBody):
    """A geodesic sphere: a subdivided icosahedron, projected onto a sphere."""

    def __init__(self, position, mass, radius, subdivisions, radii, stiffness, damping):
        x0, y0, z0 = position[0], position[1], position[2]

        vertices = [np.array(v) / np.linalg.norm(v) for v in _BASE_VERTICES]
        faces = list(_BASE_FACES)

        for _ in range(subdivisions):
            midpoint_cache = {}

            def midpoint(i, j):
                key = (min(i, j), max(i, j))
                if key not in midpoint_cache:
                    m = (vertices[i] + vertices[j]) / 2
                    vertices.append(m / np.linalg.norm(m))
                    midpoint_cache[key] = len(vertices) - 1
                return midpoint_cache[key]

            new_faces = []
            for a, b, c in faces:
                ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
                new_faces += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
            faces = new_faces

        mass_points = [[x0 + radius * v[0], y0 + radius * v[1], z0 + radius * v[2]] for v in vertices]

        outline = set()
        for a, b, c in faces:
            for i, j in ((a, b), (b, c), (c, a)):
                outline.add((min(i, j), max(i, j)))
        springs = set(outline)

        for i, v in enumerate(vertices):
            j = min(range(len(vertices)), key=lambda k: np.linalg.norm(vertices[k] + v))
            springs.add((min(i, j), max(i, j)))

        super().__init__(mass, mass_points, radii, list(springs), stiffness, damping, list(outline))
