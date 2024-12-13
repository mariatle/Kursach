import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from swarm_x2 import SwarmX2
from utils import printResult

# Глобальные переменные для управления вращением
rotation_x = 0
rotation_y = 0
last_mouse_x = 0
last_mouse_y = 0
mouse_dragging = False
camera_distance = 80  # Расстояние камеры от сцены

# Параметры оптимизации
iterCount = 500
dimension = 2  # Для 3D визуализации выбираем 2 измерения
swarmsize = 5000

minvalues = [-100.0] * dimension
maxvalues = [100.0] * dimension
currentVelocityRatio = 0.1
localVelocityRatio = 1.0
globalVelocityRatio = 5.0

# Функция (для параболоида)
def rastrigin_function(x, y):
    return x**2 + y**2

# Класс для роя частиц
class Particle:
    def __init__(self, dimension=2, bounds=(-100.0, 100.0)):
        self.position = np.random.uniform(bounds[0], bounds[1], dimension)
        self.velocity = np.random.uniform(-1, 1, dimension)
        self.best_position = np.copy(self.position)
        self.best_value = rastrigin_function(*self.position)

    def update_velocity(self, global_best_position, w=0.5, c1=1.5, c2=1.5):
        r1 = np.random.rand(len(self.position))
        r2 = np.random.rand(len(self.position))
        cognitive_velocity = c1 * r1 * (self.best_position - self.position)
        social_velocity = c2 * r2 * (global_best_position - self.position)
        self.velocity = w * self.velocity + cognitive_velocity + social_velocity

    def update_position(self, bounds=(-100.0, 100.0)):
        self.position += self.velocity
        self.position = np.clip(self.position, bounds[0], bounds[1])
        value = rastrigin_function(*self.position)
        if value < self.best_value:
            self.best_value = value
            self.best_position = np.copy(self.position)

class SwarmX2:
    def __init__(self, swarmsize, minvalues, maxvalues, currentVelocityRatio, localVelocityRatio, globalVelocityRatio):
        self.particles = [Particle(dimension=dimension, bounds=(minvalues[0], maxvalues[0])) for _ in range(swarmsize)]
        self.global_best_position = np.copy(self.particles[0].best_position)
        self.global_best_value = self.particles[0].best_value
        self.minvalues = minvalues
        self.maxvalues = maxvalues
        self.currentVelocityRatio = currentVelocityRatio
        self.localVelocityRatio = localVelocityRatio
        self.globalVelocityRatio = globalVelocityRatio

    def nextIteration(self):
        for particle in self.particles:
            particle.update_velocity(self.global_best_position)
            particle.update_position(bounds=(self.minvalues[0], self.maxvalues[0]))

            if particle.best_value < self.global_best_value:
                self.global_best_value = particle.best_value
                self.global_best_position = np.copy(particle.best_position)

def draw_2d_particles(swarm):
    """Рисует частицы в 2D на плоскости X-Y."""
    positions = np.array([particle.position for particle in swarm.particles])
    glColor3f(1.0, 0.0, 0.0)  # Красный цвет для частиц

    glPointSize(5)
    glBegin(GL_POINTS)
    for pos in positions:
        glVertex2f(pos[0], pos[1])  # Отображаем только X и Y
    glEnd()

# Отрисовка параболоидной поверхности
def draw_surface(X, Y, Z):
    glBegin(GL_QUADS)
    for i in range(len(X) - 1):
        for j in range(len(Y) - 1):
            glColor3f(0.8, 0.8, 0.1)  # Цвет параболоида
            glVertex3f(X[i, j], Y[i, j], Z[i, j])
            glVertex3f(X[i + 1, j], Y[i + 1, j], Z[i + 1, j])
            glVertex3f(X[i + 1, j + 1], Y[i + 1, j + 1], Z[i + 1, j + 1])
            glVertex3f(X[i, j + 1], Y[i, j + 1], Z[i, j + 1])
    glEnd()

def draw_axes():
    glLineWidth(2)

    # Рисуем оси
    glBegin(GL_LINES)
    glColor3f(1.0, 1.0, 1.0)  # Белый цвет для осей

    # Ось X
    glVertex3f(-200, 0, 0)  # Начало оси X
    glVertex3f(200, 0, 0)   # Конец оси X

    # Ось Y
    glVertex3f(0, -200, 0)  # Начало оси Y
    glVertex3f(0, 200, 0)   # Конец оси Y

    # Ось Z
    glVertex3f(0, 0, -200)  # Начало оси Z
    glVertex3f(0, 0, 200)   # Конец оси Z
    glEnd()

    # Рисуем разметку
    glLineWidth(1)
    glBegin(GL_LINES)

    # Разметка оси X
    for i in range(-200, 201, 10):  # Разметка через 10 единичных отрезков
        glVertex3f(i, -2, 0)  # Маленькая отметка ниже оси
        glVertex3f(i, 2, 0)   # Маленькая отметка выше оси

    # Разметка оси Y
    for i in range(-200, 201, 10):  # Разметка через 10 единичных отрезков
        glVertex3f(-2, i, 0)  # Маленькая отметка слева от оси
        glVertex3f(2, i, 0)   # Маленькая отметка справа от оси

    # Разметка оси Z
    for i in range(-200, 201, 10):  # Разметка через 10 единичных отрезков
        glVertex3f(0, -2, i)  # Маленькая отметка ниже оси
        glVertex3f(0, 2, i)   # Маленькая отметка выше оси

    glEnd()

# Обработчик движения мыши
def mouse_motion_callback(window, xpos, ypos):
    global last_mouse_x, last_mouse_y, rotation_x, rotation_y, mouse_dragging

    if mouse_dragging:
        dx = xpos - last_mouse_x
        dy = ypos - last_mouse_y
        rotation_x += dy * 0.5  # Регулируем скорость вращения по вертикали
        rotation_y += dx * 0.5  # Регулируем скорость вращения по горизонтали
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

    # Создание окна для 3D-визуализации
    window_3d = glfw.create_window(800, 600, "3D Particle Swarm Optimization", None, None)
    if not window_3d:
        glfw.terminate()
        print("Не удалось создать 3D окно")
        return

    # Создание окна для 2D-визуализации
    window_2d = glfw.create_window(800, 600, "2D Particle Swarm Optimization", None, None)
    if not window_2d:
        glfw.terminate()
        print("Не удалось создать 2D окно")
        return

    # Установка контекста OpenGL для первого окна
    glfw.make_context_current(window_3d)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Инициализация роя частиц
    swarm = SwarmX2(
        swarmsize,
        minvalues,
        maxvalues,
        currentVelocityRatio,
        localVelocityRatio,
        globalVelocityRatio,
    )

    # Основной цикл оптимизации
    while not glfw.window_should_close(window_3d) and not glfw.window_should_close(window_2d):
        # ======= Отрисовка 3D =======
        glfw.make_context_current(window_3d)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Камера и вращение для 3D
        gluPerspective(45, 800 / 600, 0.1, 500)
        camera_position = np.array([
            np.sin(np.radians(rotation_y)) * camera_distance,
            np.sin(np.radians(rotation_x)) * camera_distance,
            camera_distance
        ])
        gluLookAt(camera_position[0], camera_position[1], camera_position[2], 0, 0, 0, 0, 1, 0)
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        draw_axes()

        # Рисуем параболоид
        x = np.linspace(-30, 100, 100)
        y = np.linspace(-30, 100, 100)
        X, Y = np.meshgrid(x, y)
        Z = X**2 + Y**2
        draw_surface(X, Y, Z)

        # Отображаем частицы в 3D
        positions = np.array([particle.position for particle in swarm.particles])
        glColor3f(0.0, 1.0, 1.0)
        glPointSize(10)
        glBegin(GL_POINTS)
        for pos in positions:
            glVertex3f(pos[0], pos[1], rastrigin_function(pos[0], pos[1]))
        glEnd()

        # ======= Отрисовка 2D =======
        glfw.make_context_current(window_2d)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # 2D ортографическая проекция
        glOrtho(-110, 110, -110, 110, -1, 1)
        draw_2d_particles(swarm)

        # Обновляем рой
        swarm.nextIteration()

        # Обновляем оба окна
        glfw.swap_buffers(window_3d)
        glfw.swap_buffers(window_2d)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
