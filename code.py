import numpy as np
import time
import math
from progress.bar import Bar
import random

# Функции для расчетов
def tsialkovsky_velocity(M0, Mf, Isp, g0):
    """Формула Циолковского для расчета delta-V"""
    return g0 * Isp * math.log(M0 / Mf)

def atmospheric_density(altitude):
    """Плотность атмосферы в зависимости от высоты"""
    if altitude < 80000:
        return 1.225 * math.exp(-altitude / 7500)
    else:
        return 0.0

def aerodynamic_drag(density, velocity, Cd, A):
    """Аэродинамическое сопротивление"""
    return 0.5 * density * velocity**2 * Cd * A

def gravity(altitude, g0=9.81):
    """Гравитация в зависимости от высоты"""
    R_earth = 6371000  # радиус Земли в метрах
    return g0 * (R_earth / (R_earth + altitude))**2

#------------- ПОДГОТОВКА СИМУЛЯЦИИ ------------
print("Выбор режима:")
print("0 - Скоростной")
print("1 - Медленный")
mode = input()

if mode == '1':
    print('Подготавливаю симмуляцию Луна-17...')
    bar = Bar('Инициализация систем', max=25)
    for i in range(25):
        time.sleep(random.uniform(0.1, 0.3))
        bar.next()
    bar.finish()
    
    bar = Bar('Загрузка телеметрии', max=18)
    for i in range(18):
        time.sleep(random.uniform(0.1, 0.3))
        bar.next()
    bar.finish()
    
    bar = Bar('Калибровка приборов', max=15)
    for i in range(15):
        time.sleep(random.uniform(0.1, 0.3))
        bar.next()
    bar.finish()

# Параметры миссии Луна-17
print("\n" + "="*50)
print("МИССИЯ ЛУНА-17 - СИМУЛЯЦИЯ ЗАПУСКА")
print("="*50)

# Конфигурация ракеты-носителя
g0 = 9.81
M0_total = 305000  # стартовая масса, кг
M_payload = 5700   # масса полезной нагрузки (Луноход-1), кг
Isp_stage1 = 280   # удельный импульс 1й ступени, сек
Isp_stage2 = 320   # удельный импульс 2й ступени, сек
Isp_stage3 = 340   # удельный импульс 3й ступени, сек
thrust_stage1 = 4000000  # тяга 1й ступени, Н

time.sleep(3)

#--- ЭТАП 1: СТАРТ И ВЫВОД НА ОПОРНУЮ ОРБИТУ ---
print("\n=== ЭТАП 1: СТАРТ И ВЫВОД НА ОПОРНУЮ ОРБИТУ ===")

altitude = 0
velocity = 0
mass = M0_total
Cd = 0.8
A = 15.0

time_steps = [0, 10, 30, 60, 120, 180, 300, 600]
print("Время(с) | Высота(км) | Скорость(м/с) | Масса(т)")
print("-" * 50)

for t in time_steps:
    if t == 0:
        continue
    
    dt = t - time_steps[time_steps.index(t)-1]
    
    # Расход топлива
    fuel_consumption = 1200 * dt  # кг/сек
    mass -= fuel_consumption
    
    # Расчет сил
    density = atmospheric_density(altitude)
    drag = aerodynamic_drag(density, velocity, Cd, A)
    g = gravity(altitude)
    
    # Ускорение
    thrust = thrust_stage1
    net_force = thrust - drag - mass * g
    acceleration = net_force / mass
    
    # Обновление параметров
    velocity += acceleration * dt
    altitude += velocity * dt
    
    print(f"{t:8.0f} | {altitude/1000:10.1f} | {velocity:13.0f} | {mass/1000:8.1f}")
    
    if altitude > 80000 and t > 100:
        print("★ Достигнута граница атмосферы!")
        break

# Отделение 1й ступени
mass *= 0.4  # сброс первой ступени
print(f"\n★ ОТДЕЛЕНИЕ 1Й СТУПЕНИ - Масса: {mass/1000:.1f} т")

time.sleep(3)

#--- ЭТАП 2: ВЫВОД НА ТРАЕКТОРИЮ ПОЛЕТА К ЛУНЕ ---
print("\n=== ЭТАП 2: ВЫВОД НА ТРАЕКТОРИЮ ПОЛЕТА К ЛУНЕ ===")

time_steps = [0, 300, 600, 900, 1200, 1500]
velocity_orbit = 7800  # орбитальная скорость

for t in time_steps:
    if t == 0:
        continue
    
    dt = t - time_steps[time_steps.index(t)-1]
    
    fuel_consumption = 200 * dt
    mass -= fuel_consumption
    
    # Разгон до второй космической скорости
    velocity = velocity_orbit + (11200 - velocity_orbit) * (t / 1500)
    altitude = 200000 + t * 50  # постепенный набор высоты
    
    print(f"Время: {t:4.0f}с - Высота: {altitude/1000:6.1f}км - Скорость: {velocity:6.0f}м/с")

print("★ Достигнута вторая космическая скорость!")

time.sleep(3)

#--- ЭТАП 3: ПОЛЕТ К ЛУНЕ ---
print("\n=== ЭТАП 3: ПОЛЕТ К ЛУНЕ ===")

print("Коррекция траектории...")
time.sleep(1)
print("Полет по трансфертной орбите...")
time.sleep(1)
print("Подготовка к торможению...")

# Торможение для выхода на орбиту Луны
delta_v_moon = 900  # м/с для торможения
print(f"★ Выполнен тормозной импульс: {delta_v_moon} м/с")

time.sleep(3)

#--- ЭТАП 4: ПОСАДКА НА ЛУНУ ---
print("\n=== ЭТАП 4: ПОСАДКА НА ЛУНУ ===")

mass_lander = 1900  # масса посадочной ступени
velocity_approach = 1700
altitude_moon = 15000
g_moon = 1.62

print("Начало посадки...")
time_steps = [0, 10, 20, 30, 40, 50, 55]

for t in time_steps:
    if t == 0:
        continue
    
    # Торможение двигателем
    thrust_landing = 8000  # Н
    fuel_consumption = 5 * t
    mass_lander -= fuel_consumption
    
    # Расчет скорости снижения
    velocity_approach = max(0, 1700 - t * 30)
    altitude_moon = max(0, 15000 - t * 270)
    
    if altitude_moon > 0:
        print(f"Высота: {altitude_moon:5.0f}м - Скорость: {velocity_approach:4.0f}м/с - Топливо: {mass_lander:4.0f}кг")
    else:
        print("★ ПОСАДКА! Луноход-1 доставлен на поверхность Луны!")
        break

time.sleep(3)

#--- РЕЗУЛЬТАТЫ МИССИИ ---
print("\n" + "="*50)
print("МЕССИЯ ЛУНА-17 УСПЕШНО ЗАВЕРШЕНА!")
print("="*50)
print("Достигнутые цели:")
print("✓ Успешный запуск с Земли")
print("✓ Вывод на опорную орбиту") 
print("✓ Перелет по траектории Земля-Луна")
print("✓ Выход на орбиту Луны")
print("✓ Мягкая посадка в Море Дождей")
print("✓ Развертывание Лунохода-1")
print(f"✓ Масса доставленного груза: {M_payload} кг")
print("\nЛуноход-1 готов к исследованиям!")
print("="*50)