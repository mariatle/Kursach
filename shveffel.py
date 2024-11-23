import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

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
            # Нормализация Z для цвета
            z_color = (Z[i, j] - Z.min()) / (Z.max() - Z.min())

            # Цвет зависит от высоты
            glColor3f(0.2, z_color, 1.0 - z_color)

            # Отрисовка четырехугольников
            glVertex3f(X[i, j], Y[i, j], Z[i, j])  # Точка 1
            glVertex3f(X[i + 1, j], Y[i + 1, j], Z[i + 1, j])  # Точка 2
            glVertex3f(X[i + 1, j + 1], Y[i + 1, j + 1], Z[i + 1, j + 1])  # Точка 3
            glVertex3f(X[i, j + 1], Y[i, j + 1], Z[i, j + 1])  # Точка 4
    glEnd()

# Класс камеры для управления
class Camera:
    def __init__(self):
        self.angle_x = 0  # Угол вращения вокруг оси X
        self.angle_y = 0  # Угол вращения вокруг оси Y
        self.zoom = 1000  # Расстояние от камеры до сцены
        self.last_x = None
        self.last_y = None

    def process_mouse_motion(self, x, y):
        if self.last_x is None or self.last_y is None:
            self.last_x = x
            self.last_y = y
            return

        dx = x - self.last_x
        dy = y - self.last_y

        self.angle_x += dy * 0.5  # Скорость вращения
        self.angle_y += dx * 0.5

        self.last_x = x
        self.last_y = y

    def process_scroll(self, y_offset):
        self.zoom -= y_offset * 20  # Скорость масштабирования
        self.zoom = max(300, min(2000, self.zoom))  # Ограничение масштабирования

# Основная функция
def main():
    # Инициализация GLFW
    if not glfw.init():
        print("Не удалось инициализировать GLFW")
        return

    # Создание окна
    window = glfw.create_window(800, 600, "Schwefel Function", None, None)
    if not window:
        glfw.terminate()
        print("Не удалось создать окно")
        return

    glfw.make_context_current(window)

    # Настройка OpenGL
    glEnable(GL_DEPTH_TEST)  # Включение теста глубины
    glClearColor(0.1, 0.1, 0.1, 1.0)  # Установить фоновый цвет (темно-серый)

    # Генерация сетки функции
    X, Y, Z = generate_schwefel_mesh()

    # Создание камеры
    camera = Camera()

    # Обработчики событий
    def cursor_position_callback(window, xpos, ypos):
        camera.process_mouse_motion(xpos, ypos)

    def scroll_callback(window, xoffset, yoffset):
        camera.process_scroll(yoffset)

    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # Основной цикл
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Камера
        gluPerspective(45, 800 / 600, 0.1, 2000)
        gluLookAt(0, 0, camera.zoom, 0, 0, 0, 0, 1, 0)

        # Вращение сцены
        glRotatef(camera.angle_x, 1, 0, 0)  # Вращение вокруг оси X
        glRotatef(camera.angle_y, 0, 1, 0)  # Вращение вокруг оси Y

        # Отрисовка поверхности
        draw_surface(X, Y, Z)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
