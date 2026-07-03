#!/usr/local/bin/python3

import numpy as np
import pygame
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_LINES,
    glBegin,
    glClear,
    glColor3fv,
    glEnable,
    glEnd,
    glVertex3fv,
)
from OpenGL.GLU import gluLookAt, gluPerspective
from pygame.locals import DOUBLEBUF, OPENGL


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
                        self.velocity[i] = self.reflect(self.velocity[i], v1, 0.8)
                        self.velocity[j] = self.reflect(self.velocity[j], v0, 0.8)

    def directionVector(self, p1, p2):
        return [p2[i] - p1[i] for i in range(len(p1))]


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


def drawFloor(width, depth, division):
    glBegin(GL_LINES)
    glColor3fv((0, 1, 0))
    for x in range(width + 1):
        glVertex3fv((x * division - width * division / 2, -50, depth * division / 2))
        glVertex3fv((x * division - width * division / 2, -50, -depth * division / 2))
    for z in range(depth + 1):
        glVertex3fv((width * division / 2, -50, z * division - depth * division / 2))
        glVertex3fv((-width * division / 2, -50, z * division - depth * division / 2))
    glEnd()


softBodies = []
softBodies += [Rect((0, 0, 0), 1000, (3, 3, 3), 5, 1, 0.1, 0.05)]

pygame.init()
pygame.display.set_mode((1280, 720), DOUBLEBUF | OPENGL)
pygame.display.set_caption('Soft Body Simulator 2.1')
gluPerspective(75, 1280 / 720, 0.1, 500)
gluLookAt(0, 30, -80, 0, -50, 0, 0, 1, 0)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        clock.tick(2)
    else:
        clock.tick(120)

    for i in range(len(softBodies)):
        softBodies[i].calculateForces()

    for i in range(len(softBodies)):
        softBodies[i].wallCollide()
        softBodies[i].selfCollide()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # pyright: ignore[reportOperatorIssue]
    glEnable(GL_DEPTH_TEST)

    drawFloor(12, 12, 10)

    for i in range(len(softBodies)):
        glBegin(GL_LINES)
        glColor3fv((1, 1, 1))
        for spring in softBodies[i].outline:
            glVertex3fv(
                (
                    softBodies[i].ptPos[spring[0]][0],
                    softBodies[i].ptPos[spring[0]][1],
                    softBodies[i].ptPos[spring[0]][2],
                )
            )
            glVertex3fv(
                (
                    softBodies[i].ptPos[spring[1]][0],
                    softBodies[i].ptPos[spring[1]][1],
                    softBodies[i].ptPos[spring[1]][2],
                )
            )
        glEnd()

    pygame.display.flip()

pygame.quit()
