#!/usr/local/bin/python3

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

from rect import Rect
from rendering import drawFloor


def main():
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


if __name__ == '__main__':
    main()
