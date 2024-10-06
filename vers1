import vtk
import numpy as np


# Функция для построения графика
def create_surface(equation, x_range, y_range):
    # Создаем точки для сетки
    x_vals = np.linspace(x_range[0], x_range[1], 100)
    y_vals = np.linspace(y_range[0], y_range[1], 100)
    x, y = np.meshgrid(x_vals, y_vals)

    # Вычисляем значения z
    z = eval(equation)

    # Создаем массив точек
    points = vtk.vtkPoints()
    for i in range(len(x_vals)):
        for j in range(len(y_vals)):
            points.InsertNextPoint(x[i, j], y[i, j], z[i, j])

    # Создаем полигональную поверхность
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)

    # Создаем ячейки для треугольников
    triangles = vtk.vtkCellArray()
    for i in range(len(x_vals) - 1):
        for j in range(len(y_vals) - 1):
            id1 = i * len(y_vals) + j
            id2 = id1 + 1
            id3 = id1 + len(y_vals)
            id4 = id3 + 1

            triangles.InsertNextCell(3)
            triangles.InsertCellPoint(id1)
            triangles.InsertCellPoint(id2)
            triangles.InsertCellPoint(id3)

            triangles.InsertNextCell(3)
            triangles.InsertCellPoint(id2)
            triangles.InsertCellPoint(id4)
            triangles.InsertCellPoint(id3)

    poly_data.SetPolys(triangles)

    return poly_data


# Уравнение функции
equation = "np.sin(x**2 + y**2) / (x**2 + y**2 + 1e-10)"  # Добавляем небольшое значение для избежания деления на ноль
x_range = (-4, 4)
y_range = (-4, 4)

# Создаем график
surface_data = create_surface(equation, x_range, y_range)

# Создание маппера и актора
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(surface_data)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Создание рендерера, окна и интерактора
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.1)  # Цвет фона

# Запуск визуализации
render_window.Render()
render_window_interactor.Start()
