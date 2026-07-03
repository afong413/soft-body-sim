from soft_body import SoftBody


class Rect(SoftBody):
    def __init__(self, position, mass, size, division, radii, stiffness, damping):
        x0, y0, z0 = position[0], position[1], position[2]
        width, height, depth = size[0], size[1], size[2]
        massPoints = []
        for x in range(width + 1):
            for y in range(height + 1):
                for z in range(depth + 1):
                    massPoints += [
                        [
                            x0 + x * division - width * division / 2,
                            y0 + y * division - height * division / 2,
                            z0 + z * division - depth * division / 2,
                        ]
                    ]
        springs = []
        for x in range(width):
            for y in range(height + 1):
                for z in range(depth + 1):
                    springs += [
                        (self.flatten(x, y, z, width, height, depth), self.flatten(x + 1, y, z, width, height, depth))
                    ]
        for x in range(width + 1):
            for y in range(height):
                for z in range(depth + 1):
                    springs += [
                        (self.flatten(x, y, z, width, height, depth), self.flatten(x, y + 1, z, width, height, depth))
                    ]
        for x in range(width + 1):
            for y in range(height + 1):
                for z in range(depth):
                    springs += [
                        (self.flatten(x, y, z, width, height, depth), self.flatten(x, y, z + 1, width, height, depth))
                    ]
        for x in range(width):
            for y in range(height):
                for z in range(depth):
                    springs += [
                        (
                            self.flatten(x, y, z, width, height, depth),
                            self.flatten(x + 1, y + 1, z + 1, width, height, depth),
                        )
                    ]
                    springs += [
                        (
                            self.flatten(x + 1, y, z, width, height, depth),
                            self.flatten(x, y + 1, z + 1, width, height, depth),
                        )
                    ]
                    springs += [
                        (
                            self.flatten(x, y + 1, z, width, height, depth),
                            self.flatten(x + 1, y, z + 1, width, height, depth),
                        )
                    ]
        for x in range(width):
            for y in range(height):
                for z in range(depth + 1):
                    springs += [
                        (
                            self.flatten(x, y, z, width, height, depth),
                            self.flatten(x + 1, y + 1, z, width, height, depth),
                        )
                    ]
                    springs += [
                        (
                            self.flatten(x + 1, y, z, width, height, depth),
                            self.flatten(x, y + 1, z, width, height, depth),
                        )
                    ]
        for x in range(width):
            for y in range(height + 1):
                for z in range(depth):
                    springs += [
                        (
                            self.flatten(x, y, z, width, height, depth),
                            self.flatten(x + 1, y, z + 1, width, height, depth),
                        )
                    ]
                    springs += [
                        (
                            self.flatten(x + 1, y, z, width, height, depth),
                            self.flatten(x, y, z + 1, width, height, depth),
                        )
                    ]
        for x in range(width + 1):
            for y in range(height):
                for z in range(depth):
                    springs += [
                        (
                            self.flatten(x, y, z, width, height, depth),
                            self.flatten(x, y + 1, z + 1, width, height, depth),
                        )
                    ]
                    springs += [
                        (
                            self.flatten(x, y + 1, z, width, height, depth),
                            self.flatten(x, y, z + 1, width, height, depth),
                        )
                    ]
        outline = []
        for x in range(width):
            outline += [(self.flatten(x, 0, 0, width, height, depth), self.flatten(x + 1, 0, 0, width, height, depth))]
            outline += [
                (self.flatten(x, height, 0, width, height, depth), self.flatten(x + 1, height, 0, width, height, depth))
            ]
            outline += [
                (self.flatten(x, 0, depth, width, height, depth), self.flatten(x + 1, 0, depth, width, height, depth))
            ]
            outline += [
                (
                    self.flatten(x, height, depth, width, height, depth),
                    self.flatten(x + 1, height, depth, width, height, depth),
                )
            ]
        for y in range(height):
            outline += [(self.flatten(0, y, 0, width, height, depth), self.flatten(0, y + 1, 0, width, height, depth))]
            outline += [
                (self.flatten(width, y, 0, width, height, depth), self.flatten(width, y + 1, 0, width, height, depth))
            ]
            outline += [
                (self.flatten(0, y, depth, width, height, depth), self.flatten(0, y + 1, depth, width, height, depth))
            ]
            outline += [
                (
                    self.flatten(width, y, depth, width, height, depth),
                    self.flatten(width, y + 1, depth, width, height, depth),
                )
            ]
        for z in range(depth):
            outline += [(self.flatten(0, 0, z, width, height, depth), self.flatten(0, 0, z + 1, width, height, depth))]
            outline += [
                (self.flatten(width, 0, z, width, height, depth), self.flatten(width, 0, z + 1, width, height, depth))
            ]
            outline += [
                (self.flatten(0, height, z, width, height, depth), self.flatten(0, height, z + 1, width, height, depth))
            ]
            outline += [
                (
                    self.flatten(width, height, z, width, height, depth),
                    self.flatten(width, height, z + 1, width, height, depth),
                )
            ]
        super().__init__(mass, massPoints, radii, springs, stiffness, damping, outline)

    def flatten(self, x, y, z, w, h, d):
        return x * (h + 1) * (d + 1) + y * (d + 1) + z
