import matplotlib.pyplot as plt
import numpy as np
import math
import json

# Параметры атмосферы Кербина
def atmospheric_density_kerbin(altitude):
    """Атмосферная плотность Кербина"""
    return 1.225  * math.exp(-altitude / 5000)


def aerodynamic_drag(density, velocity, Cd, S):
    """Аэродинамическое сопротивление"""
    return 0.5 * density * velocity**2 * Cd * S

def gravity(altitude, g0=9.81):
    """Гравитация на высоте"""
    R_kerbin = 600000
    return g0 * (R_kerbin / (R_kerbin + altitude)) ** 2

def get_orbital_velocity(altitude, g0=9.81, R=600000):
    """Орбитальная скорость на высоте"""
    return math.sqrt(g0 * R**2 / (R + altitude))

# Константы
g0 = 9.81
R = 600_000
Cd = 0.57
S = 13.56

# Параметры ступеней
stages = [
    {
        'name': 'Первая ступень',
        'dry_mass': 47554,     # Сухая масса ступени (кг)
        'fuel': 108_389,       # Масса топлива (кг)
        'burn_time': 100,      # Время работы (с)
        'thrust': 2_664_700,   # Тяга (Н)
        'Isp': 290             # Удельный импульс (с)
    },
    {
        'name': 'Вторая ступень',
        'dry_mass': 14769,
        'fuel': 18633,
        'burn_time': 117,
        'thrust': 510_630,
        'Isp': 345               
    }
]

# Инициализация переменных
stage_separated = False
current_stage = 0

# Начальные значения для первой ступени
fuel = stages[0]['fuel']
mass = stages[0]['dry_mass'] + stages[0]['fuel'] + stages[1]['dry_mass'] + stages[1]['fuel']
thrust = stages[0]['thrust']
burn_time = stages[0]['burn_time']
Isp = stages[0]['Isp']
fuel_rate = stages[0]['fuel'] / stages[0]['burn_time']

# Переменные для времени работы ступеней
stage_start_time = 0  # Время запуска текущей ступени
stage_elapsed_time = 0  # Время работы текущей ступени

# Начальные условия полета
time_elapsed = 0
altitude = 0
velocity = 0
x_position = 0
y_position = 0

# Программа тангажа (угол от горизонта: 0° = горизонтально, 90° = вертикально)
pitch_schedule = [
    (0, 90),      # Старт вертикально
    (10, 89),     # Очень медленный начальный наклон
    (20, 88),
    (30, 86),
    (40, 83),
    (50, 79),
    (60, 74),     # 74° от горизонта
    (70, 68),
    (80, 60),     # 60° от горизонта
    (90, 50),     # 50° от горизонта
    (100, 40),    # 40° от горизонта (разделение здесь)
    (110, 30),    # 30° от горизонта
    (120, 20),    # 20° от горизонта
    (130, 10),    # 10° от горизонта
    (140, 5),     # Почти горизонтально
    (150, 0),     # Полностью горизонтально
    (300, 0)      # Держим горизонтально
]

# Массивы для данных
time = []
altitudes = []
speeds = []
x_speeds = []
y_speeds = []
accels = []
x_accels = []
y_accels = []
masses = []
thrusts = []
pitch_angles = []
drag_forces = []
stage_info = []  # Для отображения активной ступени

dt = 0.1  # шаг интегрирования

# Инициализация скоростей
current_velocity_x = 0
current_velocity_y = 0

while time_elapsed <= 300:  # симулируем до 300 секунд
    # Управление тангажом
    current_pitch = 90
    for time_point, pitch in pitch_schedule:
        if time_elapsed >= time_point:
            current_pitch = pitch
    
    pitch_rad = math.radians(current_pitch)
    
    # Определяем, работает ли двигатель
    if current_stage == 0:
        # Первая ступень: работает до исчерпания топлива или времени
        if fuel > 0 and stage_elapsed_time < burn_time:
            engine_on = True
        else:
            engine_on = False
            # Автоматическое разделение при выключении двигателя
            if not stage_separated:
                
                # Переход ко второй ступени
                current_stage = 1
                stage_separated = True
                stage_start_time = time_elapsed
                stage_elapsed_time = 0
                
                # Параметры второй ступени
                mass = stages[1]['dry_mass'] + stages[1]['fuel']
                fuel = stages[1]['fuel']
                thrust = stages[1]['thrust']
                burn_time = stages[1]['burn_time']
                Isp = stages[1]['Isp']
                fuel_rate = stages[1]['fuel'] / stages[1]['burn_time']
    else:
        # Вторая ступень: работает до исчерпания топлива или времени
        if fuel > 0 and stage_elapsed_time < burn_time:
            engine_on = True
        else:
            engine_on = False
    
    # Расход топлива
    if engine_on:
        fuel_used = fuel_rate * dt
        if fuel_used > fuel:
            fuel_used = fuel
        fuel -= fuel_used
        mass -= fuel_used
    else:
        fuel_used = 0
    
    # Физические расчеты
    density = atmospheric_density_kerbin(altitude)
    drag_force = aerodynamic_drag(density, velocity, Cd, S)
    g = gravity(altitude)
    
    # Вектор тяги (угол от горизонта)
    if engine_on:
        thrust_x = thrust * math.cos(pitch_rad)  # Горизонтальная компонента
        thrust_y = thrust * math.sin(pitch_rad)  # Вертикальная компонента
    else:
        thrust_x = 0
        thrust_y = 0
    
    # Вектор сопротивления (противоположен скорости)
    if velocity > 0.01:
        dir_x = current_velocity_x / velocity
        dir_y = current_velocity_y / velocity
        drag_x = -drag_force * dir_x
        drag_y = -drag_force * dir_y
    else:
        drag_x = 0
        drag_y = 0
    
    # Суммарные силы
    force_x = thrust_x + drag_x
    force_y = thrust_y + drag_y - mass * g
    
    # Ускорения
    if mass > 0.1:
        acceleration_x = force_x / mass
        acceleration_y = force_y / mass
        acceleration_total = math.sqrt(acceleration_x**2 + acceleration_y**2)
    else:
        acceleration_x = 0
        acceleration_y = 0
        acceleration_total = 0
    
    # Интегрирование скорости (метод Эйлера)
    new_velocity_x = current_velocity_x + acceleration_x * dt
    new_velocity_y = current_velocity_y + acceleration_y * dt
    
    # Не допускаем отрицательной высоты
    if y_position + new_velocity_y * dt < 0 and new_velocity_y < 0:
        new_velocity_y = 0
    
    # Обновление скорости
    velocity = math.sqrt(new_velocity_x**2 + new_velocity_y**2)
    
    # Интегрирование положения
    x_position += new_velocity_x * dt
    y_position += new_velocity_y * dt
    altitude = y_position
    
    # Сохранение данных
    time.append(time_elapsed)
    altitudes.append(altitude)
    speeds.append(velocity)
    x_speeds.append(new_velocity_x)
    y_speeds.append(new_velocity_y)
    accels.append(acceleration_total)
    x_accels.append(acceleration_x)
    y_accels.append(acceleration_y)
    masses.append(mass)
    thrusts.append(thrust if engine_on else 0)
    pitch_angles.append(current_pitch)
    drag_forces.append(drag_force)
    stage_info.append(current_stage)
    
    # Обновление переменных для следующего шага
    current_velocity_x = new_velocity_x
    current_velocity_y = new_velocity_y
    stage_elapsed_time += dt
    time_elapsed += dt
    
    # Проверка на достижение орбиты
    if altitude > 70000 and velocity > 1000:
        orbital_velocity = get_orbital_velocity(altitude)
        if velocity >= orbital_velocity * 0.95 and new_velocity_y >= 0:
            break



if altitude > 70000:
    orbital_v = get_orbital_velocity(altitude)
\


# Загрузка данных KSP
with open("data_for_ksp.json", 'r', encoding='UTF-8') as file:
    data_ksp = json.load(file)

time_ksp = np.array(data_ksp[0]["pastime"])
altitude_ksp = np.array(data_ksp[0]["height"]) 
speed_ksp = np.array(data_ksp[0]["velocity"]) 
ox_speed_ksp = np.array(data_ksp[0]["ox_velocity"])
oy_speed_ksp = np.array(data_ksp[0]["oy_velocity"]) 
acceleration_ksp = np.array(data_ksp[0]["acc"])
ox_acceleration_ksp = np.array(data_ksp[0]["ox_ac"]) 
oy_acceleration_ksp = np.array(data_ksp[0]["oy_ac"])

# Построение графиков
plt.figure(figsize=(15, 10))

# 1. Высота от времени
plt.subplot(2, 3, 1)
plt.plot(time, altitudes, label='Мат. модель', color='blue', linewidth=2)
plt.plot(time_ksp, altitude_ksp, label='KSP', color='orange', linestyle='--')
plt.xlabel('Время, с')
plt.ylabel('Высота, м')
plt.title('Высота от времени')
plt.legend()
plt.grid(True)

# 2. Скорость от времени
plt.subplot(2, 3, 2)
plt.plot(time, speeds, label='Мат. модель', color='blue', linewidth=2)
plt.plot(time_ksp, speed_ksp, label='KSP', color='orange', linestyle='--')
plt.xlabel('Время, с')
plt.ylabel('Скорость, м/с')
plt.title('Скорость от времени')
plt.legend()
plt.grid(True)

# 3. Горизонтальная скорость
plt.subplot(2, 3, 3)
plt.plot(time, x_speeds, label='Мат. модель', color='blue', linewidth=2)
plt.plot(time_ksp, ox_speed_ksp, label='KSP', color='orange', linestyle='--')
plt.xlabel('Время, с')
plt.ylabel('Скорость, м/с')
plt.title('Горизонтальная скорость')
plt.legend()
plt.grid(True)

# 4. Вертикальная скорость
plt.subplot(2, 3, 4)
plt.plot(time, y_speeds, label='Мат. модель', color='blue', linewidth=2)
plt.plot(time_ksp, oy_speed_ksp, label='KSP', color='orange', linestyle='--')
plt.xlabel('Время, с')
plt.ylabel('Скорость, м/с')
plt.title('Вертикальная скорость')
plt.legend()
plt.grid(True)

# 5. Ускорение
plt.subplot(2, 3, 5)
plt.plot(time, accels, label='Мат. модель', color='blue', linewidth=2)
plt.plot(time_ksp[::13], acceleration_ksp[::13], label='KSP', color='orange', linestyle='--')
plt.xlabel('Время, с')
plt.ylabel('Ускорение, м/с²')
plt.title('Полное ускорение')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
