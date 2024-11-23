import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pygame

# Функция параболоида
def paraboloid_function(x, y):
    return x**2 + y**2

# Создание сетки для вычислений
def generate_paraboloid_mesh(step=1, range_limit=10):
    x = np.arange(-range_limit, range_limit, step)
    y = np.arange(-range_limit, range_limit, step)
    X, Y = np.meshgrid(x, y)
    Z = paraboloid_function(X, Y)
    return X, Y, Z

# Отрисовка поверхности
def draw_surface(X, Y, Z):
    glBegin(GL_QUADS)
    for i in range(len(X) - 1):
        for j in range(len(Y) - 1):
            z_color = (Z[i, j] - Z.min()) / (Z.max() - Z.min())  # Нормализация Z для цвета
            glColor3f(0.2, z_color, 1.0 - z_color)

            glVertex3f(X[i, j], Y[i, j], Z[i, j])
            glVertex3f(X[i + 1, j], Y[i + 1, j], Z[i + 1, j])
            glVertex3f(X[i + 1, j + 1], Y[i + 1, j + 1], Z[i + 1, j + 1])
            glVertex3f(X[i, j + 1], Y[i, j + 1], Z[i, j + 1])
    glEnd()

# Отрисовка осей
# Отрисовка осей
def draw_axes():
    glLineWidth(2)
    glBegin(GL_LINES)

    # Ось X (красная)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-50, 0, 0)  # Удлиненная ось X
    glVertex3f(50, 0, 0)

    # Ось Y (зеленая)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0, -50, 0)  # Удлиненная ось Y
    glVertex3f(0, 50, 0)

    # Ось Z (синяя)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0, 0, -50)  # Удлиненная ось Z
    glVertex3f(0, 0, 50)

    glEnd()

# Основная функция
def main():
    if not glfw.init():
        print("Не удалось инициализировать GLFW")
        return

    # Создаем окно
    window = glfw.create_window(800, 600, "Paraboloid with Axes", None, None)
    if not window:
        glfw.terminate()
        print("Не удалось создать окно")
        return

    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)  # Включить тест глубины
    glClearColor(0.1, 0.1, 0.1, 1.0)  # Темно-серый фон

    # Инициализация данных для параболоида
    X, Y, Z = generate_paraboloid_mesh(step=0.5, range_limit=10)

    # Камера
    camera_angle_x = 0
    camera_angle_y = 0
    zoom = 30

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Управление камерой
        gluPerspective(45, 800 / 600, 0.1, 200)
        gluLookAt(zoom * np.sin(np.radians(camera_angle_y)), zoom * np.sin(np.radians(camera_angle_x)),
                  zoom * np.cos(np.radians(camera_angle_y)),
                  0, 0, 0, 0, 1, 0)

        # Отрисовка осей
        draw_axes()

        # Отрисовка параболоида
        draw_surface(X, Y, Z)

        # Обработка ввода
        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            camera_angle_y -= 1
        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            camera_angle_y += 1
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            camera_angle_x -= 1
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            camera_angle_x += 1
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            zoom -= 1
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            zoom += 1

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()

