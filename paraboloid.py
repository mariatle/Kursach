import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Глобальные переменные для управления вращением
rotation_x = 0
rotation_y = 0
last_mouse_x = 0
last_mouse_y = 0
mouse_dragging = False

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

# Отрисовка осей с разметкой
def draw_axes_with_ticks():
    glLineWidth(2)
    glBegin(GL_LINES)

    # Ось X (красная)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-50, 0, 0)
    glVertex3f(50, 0, 0)

    # Ось Y (зеленая)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0, -50, 0)
    glVertex3f(0, 50, 0)

    # Ось Z (синяя)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0, 0, -50)
    glVertex3f(0, 0, 50)

    glEnd()

    # Разметка осей (точки с шагом 5)
    glPointSize(5)
    glBegin(GL_POINTS)
    for i in range(-50, 55, 5):  # Разметка на X и Z
        glColor3f(1.0, 1.0, 1.0)  # Белые точки
        glVertex3f(i, 0, 0)  # Точки на оси X
        glVertex3f(0, 0, i)  # Точки на оси Z
    for i in range(-50, 55, 5):  # Разметка на Y
        glVertex3f(0, i, 0)  # Точки на оси Y
    glEnd()

# Обработчик движения мыши
def mouse_motion_callback(window, xpos, ypos):
    global last_mouse_x, last_mouse_y, rotation_x, rotation_y, mouse_dragging

    if mouse_dragging:
        dx = xpos - last_mouse_x
        dy = ypos - last_mouse_y
        rotation_x += dy * 0.5  # Изменение угла вращения по X
        rotation_y += dx * 0.5  # Изменение угла вращения по Y
        last_mouse_x = xpos
        last_mouse_y = ypos

# Обработчик кнопок мыши
def mouse_button_callback(window, button, action, mods):
    global last_mouse_x, last_mouse_y, mouse_dragging

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_dragging = True
            last_mouse_x, last_mouse_y = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            mouse_dragging = False

# Основная функция
def main():
    if not glfw.init():
        print("Не удалось инициализировать GLFW")
        return

    window = glfw.create_window(800, 600, "Paraboloid with Mouse Rotation", None, None)
    if not window:
        glfw.terminate()
        print("Не удалось создать окно")
        return

    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)  # Включить тест глубины
    glClearColor(0.1, 0.1, 0.1, 1.0)  # Темно-серый фон

    # Установка обработчиков событий
    glfw.set_cursor_pos_callback(window, mouse_motion_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    X, Y, Z = generate_paraboloid_mesh(step=1, range_limit=10)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Камера
        gluPerspective(45, 800 / 600, 0.1, 200)
        gluLookAt(30, 30, 30, 0, 0, 0, 0, 1, 0)

        # Применение вращения
        glRotatef(rotation_x, 1, 0, 0)  # Вращение вокруг X
        glRotatef(rotation_y, 0, 1, 0)  # Вращение вокруг Y

        # Рисуем оси с разметкой
        draw_axes_with_ticks()

        # Рисуем параболоид
        draw_surface(X, Y, Z)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
