import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Глобальные переменные для управления камерой
rotation_x = 0
rotation_y = 0
last_mouse_x = 0
last_mouse_y = 0
mouse_dragging = False
camera_distance = 800  # Начальная дистанция камеры

# Функция Швефеля
def schwefel_function(x, y):
    return -x * np.sin(np.sqrt(np.abs(x))) - y * np.sin(np.sqrt(np.abs(y)))

# Создание сетки для вычислений
def generate_schwefel_mesh(step=20, range_limit=500):
    x = np.arange(-range_limit, range_limit, step)
    y = np.arange(-range_limit, range_limit, step)
    X, Y = np.meshgrid(x, y)
    Z = schwefel_function(X, Y)
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
    axis_length = 1000  # Длина осей
    tick_spacing = 50  # Расстояние между отметками

    glLineWidth(2)
    glBegin(GL_LINES)

    # Ось X (красная)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-axis_length, 0, 0)
    glVertex3f(axis_length, 0, 0)

    # Ось Y (зеленая)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0, -axis_length, 0)
    glVertex3f(0, axis_length, 0)

    # Ось Z (синяя)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0, 0, -axis_length)
    glVertex3f(0, 0, axis_length)

    glEnd()

    # Разметка осей
    glPointSize(5)
    glBegin(GL_POINTS)
    for i in range(-axis_length, axis_length + tick_spacing, tick_spacing):
        glColor3f(1.0, 1.0, 1.0)
        glVertex3f(i, 0, 0)  # Точки на оси X
        glVertex3f(0, i, 0)  # Точки на оси Y
        glVertex3f(0, 0, i)  # Точки на оси Z
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

# Обработчик прокрутки колесика мыши
def scroll_callback(window, xoffset, yoffset):
    global camera_distance
    camera_distance -= yoffset * 20  # Увеличение/уменьшение дистанции
    camera_distance = max(100, min(camera_distance, 2000))  # Ограничение диапазона

# Обработчик клавиш
def key_callback(window, key, scancode, action, mods):
    global rotation_x, rotation_y
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_UP:      # Вращение вверх
            rotation_x -= 5
        elif key == glfw.KEY_DOWN:  # Вращение вниз
            rotation_x += 5
        elif key == glfw.KEY_LEFT:  # Вращение влево
            rotation_y -= 5
        elif key == glfw.KEY_RIGHT: # Вращение вправо
            rotation_y += 5

# Основная функция
def main():
    if not glfw.init():
        print("Не удалось инициализировать GLFW")
        return

    window = glfw.create_window(800, 600, "Schwefel Function with Keyboard Controls", None, None)
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
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)

    # Генерация сетки функции Швефеля
    X, Y, Z = generate_schwefel_mesh()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Камера
        gluPerspective(45, 800 / 600, 0.1, 2000)
        gluLookAt(camera_distance, camera_distance, camera_distance, 0, 0, 0, 0, 1, 0)

        # Применение вращения
        glRotatef(rotation_x, 1, 0, 0)  # Вращение вокруг X
        glRotatef(rotation_y, 0, 1, 0)  # Вращение вокруг Y

        # Рисуем оси с разметкой
        draw_axes_with_ticks()

        # Рисуем поверхность
        draw_surface(X, Y, Z)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
