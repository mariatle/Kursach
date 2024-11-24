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
swarmsize = 200

minvalues = [-100.0] * dimension
maxvalues = [100.0] * dimension
currentVelocityRatio = 0.1
localVelocityRatio = 1.0
globalVelocityRatio = 5.0

# Функция Растригина (для параболоида)
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

def plotSwarm(swarm, iteration, ax):
    """Визуализирует текущее состояние роя с использованием OpenGL."""
    ax.clear()

    # Параболоид
    x = np.linspace(-100, 100, 100)
    y = np.linspace(-100, 100, 100)
    X, Y = np.meshgrid(x, y)
    Z = X ** 2 + Y ** 2
    ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.6, edgecolor='none')

    # Позиции частиц
    positions = np.array([particle.position for particle in swarm.particles])
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 0] ** 2 + positions[:, 1] ** 2, color='red', label='Particles')

    ax.set_title(f"Swarm Optimization - Iteration {iteration}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()

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

# Отрисовка осей
def draw_axes():
    glLineWidth(2)
    glBegin(GL_LINES)

    # Ось X (красная)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-500, 0, 0)
    glVertex3f(500, 0, 0)

    # Ось Y (зеленая)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0, -500, 0)
    glVertex3f(0, 500, 0)

    # Ось Z (синяя)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0, 0, -500)
    glVertex3f(0, 0, 500)

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

    window = glfw.create_window(800, 600, "Particle Swarm Optimization", None, None)
    if not window:
        glfw.terminate()
        print("Не удалось создать окно")
        return

    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Установка обработчиков событий
    glfw.set_cursor_pos_callback(window, mouse_motion_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

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
    for n in range(iterCount):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Камера
        gluPerspective(45, 800 / 600, 0.1, 500)

        # Расстояние камеры и её вращение
        camera_position = np.array([np.sin(np.radians(rotation_y)) * camera_distance,
                                    np.sin(np.radians(rotation_x)) * camera_distance,
                                    camera_distance])

        # Устанавливаем позицию камеры
        gluLookAt(camera_position[0], camera_position[1], camera_position[2], 0, 0, 0, 0, 1, 0)

        # Вращение сцены
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        # Рисуем оси
        draw_axes()

        # Рисуем параболоид
        x = np.linspace(-30, 100, 100)
        y = np.linspace(-30, 100, 100)
        X, Y = np.meshgrid(x, y)
        Z = X**2 + Y**2
        draw_surface(X, Y, Z)

        # Отображаем частицы
        positions = np.array([particle.position for particle in swarm.particles])
        glColor3f(0.0, 1.0, 1.0)  # Зеленый цвет для частиц
        glPointSize(10)
        glBegin(GL_POINTS)
        for pos in positions:
            glVertex3f(pos[0], pos[1], rastrigin_function(pos[0], pos[1]))
        glEnd()

        # Обновление роя
        swarm.nextIteration()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
