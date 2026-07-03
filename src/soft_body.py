import numpy as np


class SoftBody:
    def __init__(self, mass, pts, r, springs, stiff, damp, outline):
        self.pt_pos = pts
        self.velocity = np.zeros((len(pts), 3))
        self.force = np.zeros((len(pts), 3))
        self.pt_mass = mass / len(pts)
        self.r = r
        self.spring_pts = springs
        self.stiff = stiff
        self.rest_length = [self.distance(self.pt_pos[spring[0]], self.pt_pos[spring[1]]) for spring in self.spring_pts]
        self.damp = damp
        self.outline = outline

    def distance(self, p0, p1):
        return np.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2 + (p1[2] - p0[2]) ** 2)

    def normalize(self, v):
        magnitude = np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        if magnitude != 0:
            return (v[0] / magnitude, v[1] / magnitude, v[2] / magnitude)
        return np.array([0, 0, 0])

    def reflect(self, v, r, loss):
        r = self.normalize(r)
        return np.array([loss * (v[i] - 2 * np.dot(v, r) * r[i]) for i in range(3)])

    def spring_force(self, s):
        return (
            self.distance(self.pt_pos[self.spring_pts[s][0]], self.pt_pos[self.spring_pts[s][1]]) - self.rest_length[s]
        ) * self.stiff + np.dot(
            self.normalize(
                self.direction_vector(self.pt_pos[self.spring_pts[s][0]], self.pt_pos[self.spring_pts[s][1]])
            ),
            self.velocity[self.spring_pts[s][1]] - self.velocity[self.spring_pts[s][0]],
        ) * self.damp

    def calculate_forces(self):
        self.force = [[0.0, 0.0, 0.0] for _ in self.pt_pos]
        for i in range(len(self.force)):
            self.force[i][1] -= 0.01

        for j in range(len(self.spring_pts)):
            p0 = self.pt_pos[self.spring_pts[j][0]]
            p1 = self.pt_pos[self.spring_pts[j][1]]
            v0 = self.normalize(self.direction_vector(p0, p1))
            v1 = self.normalize(self.direction_vector(p1, p0))
            spring_force = self.spring_force(j)
            self.force[self.spring_pts[j][0]][0] += v0[0] * spring_force
            self.force[self.spring_pts[j][0]][1] += v0[1] * spring_force
            self.force[self.spring_pts[j][0]][2] += v0[2] * spring_force
            self.force[self.spring_pts[j][1]][0] += v1[0] * spring_force
            self.force[self.spring_pts[j][1]][1] += v1[1] * spring_force
            self.force[self.spring_pts[j][1]][2] += v1[2] * spring_force

        for i in range(len(self.velocity)):
            self.velocity[i][0] += self.force[i][0]
            self.velocity[i][1] += self.force[i][1]
            self.velocity[i][2] += self.force[i][2]
            self.velocity[i][0] = round(self.velocity[i][0], 5)
            self.velocity[i][1] = round(self.velocity[i][1], 5)
            self.velocity[i][2] = round(self.velocity[i][2], 5)

        for i in range(len(self.pt_pos)):
            self.pt_pos[i][0] += self.velocity[i][0]
            self.pt_pos[i][1] += self.velocity[i][1]
            self.pt_pos[i][2] += self.velocity[i][2]
            self.pt_pos[i][0] = round(self.pt_pos[i][0], 5)
            self.pt_pos[i][1] = round(self.pt_pos[i][1], 5)
            self.pt_pos[i][2] = round(self.pt_pos[i][2], 5)

    def wall_collide(self):
        for i in range(len(self.pt_pos)):
            if self.pt_pos[i][1] > 50:
                self.pt_pos[i][1] = 50
                self.velocity[i] = self.reflect(self.velocity[i], [0, -1, 0], 0.8)
            elif self.pt_pos[i][1] < -50:
                self.pt_pos[i][1] = -50
                self.velocity[i] = self.reflect(self.velocity[i], [0, 1, 0], 0.8)
            if self.pt_pos[i][0] > 50:
                self.pt_pos[i][0] = 50
                self.velocity[i] = self.reflect(self.velocity[i], [-1, 0, 0], 0.8)
            elif self.pt_pos[i][0] < -50:
                self.pt_pos[i][0] = -50
                self.velocity[i] = self.reflect(self.velocity[i], [1, 0, 0], 0.8)

    def self_collide(self):
        for i in range(len(self.pt_pos)):
            for j in range(len(self.pt_pos)):
                p0 = self.pt_pos[i]
                p1 = self.pt_pos[j]
                if p0 != p1:
                    d = self.distance(p0, p1)
                    if d < 2 * self.r:
                        v0 = self.normalize(self.direction_vector(p0, p1))
                        v1 = self.normalize(self.direction_vector(p1, p0))
                        self.pt_pos[i][0] += v1[0] * (2 * self.r - d) / 2
                        self.pt_pos[i][1] += v1[1] * (2 * self.r - d) / 2
                        self.pt_pos[i][2] += v1[2] * (2 * self.r - d) / 2
                        self.pt_pos[j][0] += v0[0] * (2 * self.r - d) / 2
                        self.pt_pos[j][1] += v0[1] * (2 * self.r - d) / 2
                        self.pt_pos[j][2] += v0[2] * (2 * self.r - d) / 2

    def direction_vector(self, p1, p2):
        return [p2[i] - p1[i] for i in range(len(p1))]
