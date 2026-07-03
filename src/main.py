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
from rendering import draw_floor
from sphere import Sphere


def main():
    soft_bodies = []
    soft_bodies += [Rect((-20, 0, 0), 1000, (3, 3, 3), 5, 1, 0.1, 0.05)]
    soft_bodies += [Sphere((20, 0, 0), 1000, 8, 1, 1, 0.1, 0.05)]

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

        for i in range(len(soft_bodies)):
            soft_bodies[i].calculate_forces()

        for i in range(len(soft_bodies)):
            soft_bodies[i].wall_collide()
            soft_bodies[i].self_collide()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # pyright: ignore[reportOperatorIssue]
        glEnable(GL_DEPTH_TEST)

        draw_floor(12, 12, 10)

        for i in range(len(soft_bodies)):
            glBegin(GL_LINES)
            glColor3fv((1, 1, 1))
            for spring in soft_bodies[i].outline:
                glVertex3fv(
                    (
                        soft_bodies[i].pt_pos[spring[0]][0],
                        soft_bodies[i].pt_pos[spring[0]][1],
                        soft_bodies[i].pt_pos[spring[0]][2],
                    )
                )
                glVertex3fv(
                    (
                        soft_bodies[i].pt_pos[spring[1]][0],
                        soft_bodies[i].pt_pos[spring[1]][1],
                        soft_bodies[i].pt_pos[spring[1]][2],
                    )
                )
            glEnd()

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
