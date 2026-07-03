import numpy as np


class SoftBody:
    def __init__(self, mass, pts, r, springs, stiff, damp, outline):
        self.ptPos = pts
        self.velocity = np.zeros((len(pts), 3))
        self.force = np.zeros((len(pts), 3))
        self.ptMass = mass / len(pts)
        self.r = r
        self.springPts = springs
        self.stiff = stiff
        self.restLength = [self.distance(self.ptPos[spring[0]], self.ptPos[spring[1]]) for spring in self.springPts]
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

    def springForce(self, s):
        return (
            self.distance(self.ptPos[self.springPts[s][0]], self.ptPos[self.springPts[s][1]]) - self.restLength[s]
        ) * self.stiff + np.dot(
            self.normalize(self.directionVector(self.ptPos[self.springPts[s][0]], self.ptPos[self.springPts[s][1]])),
            self.velocity[self.springPts[s][1]] - self.velocity[self.springPts[s][0]],
        ) * self.damp

    def calculateForces(self):
        self.force = [[0.0, 0.0, 0.0] for _ in self.ptPos]
        for i in range(len(self.force)):
            self.force[i][1] -= 0.01

        for j in range(len(self.springPts)):
            p0 = self.ptPos[self.springPts[j][0]]
            p1 = self.ptPos[self.springPts[j][1]]
            v0 = self.normalize(self.directionVector(p0, p1))
            v1 = self.normalize(self.directionVector(p1, p0))
            springForce = self.springForce(j)
            self.force[self.springPts[j][0]][0] += v0[0] * springForce
            self.force[self.springPts[j][0]][1] += v0[1] * springForce
            self.force[self.springPts[j][0]][2] += v0[2] * springForce
            self.force[self.springPts[j][1]][0] += v1[0] * springForce
            self.force[self.springPts[j][1]][1] += v1[1] * springForce
            self.force[self.springPts[j][1]][2] += v1[2] * springForce

        for i in range(len(self.velocity)):
            self.velocity[i][0] += self.force[i][0]
            self.velocity[i][1] += self.force[i][1]
            self.velocity[i][2] += self.force[i][2]
            self.velocity[i][0] = round(self.velocity[i][0], 5)
            self.velocity[i][1] = round(self.velocity[i][1], 5)
            self.velocity[i][2] = round(self.velocity[i][2], 5)

        for i in range(len(self.ptPos)):
            self.ptPos[i][0] += self.velocity[i][0]
            self.ptPos[i][1] += self.velocity[i][1]
            self.ptPos[i][2] += self.velocity[i][2]
            self.ptPos[i][0] = round(self.ptPos[i][0], 5)
            self.ptPos[i][1] = round(self.ptPos[i][1], 5)
            self.ptPos[i][2] = round(self.ptPos[i][2], 5)

    def wallCollide(self):
        for i in range(len(self.ptPos)):
            if self.ptPos[i][1] > 50:
                self.ptPos[i][1] = 50
                self.velocity[i] = self.reflect(self.velocity[i], [0, -1, 0], 0.8)
            elif self.ptPos[i][1] < -50:
                self.ptPos[i][1] = -50
                self.velocity[i] = self.reflect(self.velocity[i], [0, 1, 0], 0.8)
            if self.ptPos[i][0] > 50:
                self.ptPos[i][0] = 50
                self.velocity[i] = self.reflect(self.velocity[i], [-1, 0, 0], 0.8)
            elif self.ptPos[i][0] < -50:
                self.ptPos[i][0] = -50
                self.velocity[i] = self.reflect(self.velocity[i], [1, 0, 0], 0.8)

    def selfCollide(self):
        for i in range(len(self.ptPos)):
            for j in range(len(self.ptPos)):
                p0 = self.ptPos[i]
                p1 = self.ptPos[j]
                if p0 != p1:
                    d = self.distance(p0, p1)
                    if d < 2 * self.r:
                        v0 = self.normalize(self.directionVector(p0, p1))
                        v1 = self.normalize(self.directionVector(p1, p0))
                        self.ptPos[i][0] += v1[0] * (2 * self.r - d) / 2
                        self.ptPos[i][1] += v1[1] * (2 * self.r - d) / 2
                        self.ptPos[i][2] += v1[2] * (2 * self.r - d) / 2
                        self.ptPos[j][0] += v0[0] * (2 * self.r - d) / 2
                        self.ptPos[j][1] += v0[1] * (2 * self.r - d) / 2
                        self.ptPos[j][2] += v0[2] * (2 * self.r - d) / 2

    def directionVector(self, p1, p2):
        return [p2[i] - p1[i] for i in range(len(p1))]
