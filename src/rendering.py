from OpenGL.GL import GL_LINES, glBegin, glColor3fv, glEnd, glVertex3fv


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
