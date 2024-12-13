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

        # Отображаем частицы в 3D
        positions = np.array([particle.position for particle in swarm.particles])
        glColor3f(0.0, 1.0, 1.0)  # Зеленый цвет для частиц
        glPointSize(10)
        glBegin(GL_POINTS)
        for pos in positions:
            glVertex3f(pos[0], pos[1], rastrigin_function(pos[0], pos[1]))
        glEnd()

        # Отображаем частицы в 2D
        draw_2d_particles(swarm)

        # Обновление роя
        swarm.nextIteration()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
