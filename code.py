import time
import math

def atmospheric_density(altitude):
    if altitude < 70000:
        return 1.225 * math.exp(-altitude / 5000)
    else:
        return 0.0

def aerodynamic_drag(density, velocity, Cd, S):
    return 0.5 * density * velocity**2 * Cd * S

def gravity(altitude, g0=9.81):
    R_kerbin = 600000
    return g0 * (R_kerbin / (R_kerbin + altitude))**2

def calculate_delta_v(mass_initial, mass_final, isp, g0=9.81):
    if mass_final <= 0 or mass_initial <= mass_final:
        return 0
    return g0 * isp * math.log(mass_initial / mass_final)

print("\nKSP MISSION LUNA-17")

deltaV_required = {
    "Взлет с Кербина": 3400,
    "Переход к Муне": 860,
    "Захват орбиты Муны": 280,
    "Посадка на Муну": 580
}

total_deltaV_needed = sum(deltaV_required.values())

g0 = 9.81
M0_total = 120000
M_payload = 5000
initial_fuel = M0_total * 0.85

stages = [
    {"name": "1я ступень", "Isp": 290, "thrust": 2000000, "burn_time": 110, "fuel_frac": 0.65},
    {"name": "2я ступень", "Isp": 340, "thrust": 800000, "burn_time": 180, "fuel_frac": 0.20},
    {"name": "3я ступень", "Isp": 350, "thrust": 250000, "burn_time": 300, "fuel_frac": 0.10}
]

print("\nSTAGE 1: TAKEOFF FROM KERBIN (requires Delta-v = 3400 m/s)")
print("="*80)

time_elapsed = 0
altitude = 0
velocity = 0
mass = M0_total
fuel = initial_fuel
Cd = 0.2
S = 10.0
x_position = 0
y_position = 0
pitch_angle = 90
pitch_rad = math.radians(pitch_angle)

stage = stages[0]
target_deltaV = deltaV_required["Взлет с Кербина"]
mass_after_stage1 = mass / math.exp(target_deltaV / (g0 * stage["Isp"]))
fuel_needed_stage1 = mass - mass_after_stage1
fuel_rate = fuel_needed_stage1 / stage["burn_time"]

print("Time(s) | Speed(m/s) | OX(km) | OY(km) | Fuel(t)")
print("-" * 80)

print(f"{time_elapsed:8.1f} | {velocity:13.2f} | {x_position/1000:6.1f} | {y_position/1000:6.1f} | {fuel/1000:8.1f}")

pitch_schedule = [
    (0, 90), (10, 89), (30, 85), (60, 80), (90, 75), (110, 70)
]

time_steps = [10, 30, 60, 90, 110]

for t in time_steps:
    dt = t - time_elapsed
    time_elapsed = t
    
    current_pitch = 90
    for time_point, pitch in pitch_schedule:
        if t >= time_point:
            current_pitch = pitch
    pitch_rad = math.radians(current_pitch)
    
    fuel_used = fuel_rate * dt
    if fuel_used > fuel:
        fuel_used = fuel
    fuel -= fuel_used
    mass -= fuel_used
    
    if fuel <= 0:
        break
    
    density = atmospheric_density(altitude)
    drag_force = aerodynamic_drag(density, velocity, Cd, S)
    g = gravity(altitude)
    gravity_force = mass * g
    thrust = stage["thrust"]
      
    thrust_x = thrust * math.cos(pitch_rad)
    thrust_y = thrust * math.sin(pitch_rad)
    
    drag_x = drag_force * math.cos(pitch_rad)
    drag_y = drag_force * math.sin(pitch_rad)
    
    force_x = thrust_x - drag_x
    force_y = thrust_y - drag_y - gravity_force
    
    acceleration_x = force_x / mass if mass > 0 else 0
    acceleration_y = force_y / mass if mass > 0 else 0
    acceleration_total = math.sqrt(acceleration_x**2 + acceleration_y**2)
    
    current_velocity_x = velocity * math.cos(pitch_rad)
    current_velocity_y = velocity * math.sin(pitch_rad)
    
    new_velocity_x = current_velocity_x + acceleration_x * dt
    new_velocity_y = current_velocity_y + acceleration_y * dt
    velocity = math.sqrt(new_velocity_x**2 + new_velocity_y**2)
    
    x_position += new_velocity_x * dt
    y_position += new_velocity_y * dt
    altitude = y_position
    
    if x_position < 0:
        x_position = 0
    if y_position < 0:
        y_position = 0
        altitude = 0
    
    print(f"{time_elapsed:8.1f} | {velocity:13.2f} | {x_position/1000:6.1f} | {y_position/1000:6.1f} | {fuel/1000:8.1f}")

actual_deltaV_stage1 = calculate_delta_v(M0_total, mass, stage["Isp"], g0)

mass_before_sep = mass
mass *= (1 - stage["fuel_frac"])
fuel *= (1 - stage["fuel_frac"])
print(f"SEPARATION: mass {mass_before_sep/1000:.1f} t -> {mass/1000:.1f} t")

time.sleep(1)

print("\nSTAGE 2: TRANSITION TO MOON (requires Delta-v = 860 m/s)")
print("="*80)

stage = stages[1]
target_deltaV = deltaV_required["Переход к Муне"]

mass_start = mass
target_velocity = velocity + target_deltaV
burn_time = 120

print("Time(s) | Speed(m/s) | OX(km) | OY(km) | Fuel(t)")
print("-" * 80)

current_pitch = 70
pitch_rad = math.radians(current_pitch)

time_steps_2 = [120, 140, 160, 180, 200, 220, 240]

for t in time_steps_2:
    if t == 120:
        print(f"{t:8.1f} | {velocity:13.2f} | {x_position/1000:6.1f} | {y_position/1000:6.1f} | {fuel/1000:8.1f}")
        continue
    
    dt = 20
    time_elapsed = t
    
    fuel_needed = mass_start - (mass_start / math.exp(target_deltaV / (g0 * stage["Isp"])))
    fuel_rate = fuel_needed / burn_time
    
    fuel_used = fuel_rate * dt
    if fuel_used > fuel:
        fuel_used = fuel
    fuel -= fuel_used
    mass -= fuel_used
    
    velocity_increment = target_deltaV * (dt / burn_time)
    velocity += velocity_increment
    
    altitude_increment = 100 * dt
    altitude += altitude_increment
    
    velocity_x = velocity * math.cos(pitch_rad)
    velocity_y = velocity * math.sin(pitch_rad)
    
    x_position += velocity_x * dt
    y_position = altitude
    
    acceleration = stage["thrust"] / mass if mass > 0 else 0
    
    print(f"{time_elapsed:8.1f} | {velocity:13.2f} | {x_position/1000:6.1f} | {y_position/1000:6.1f} | {fuel/1000:8.1f}")

actual_deltaV_stage2 = calculate_delta_v(mass_start, mass, stage["Isp"], g0)

mass *= (1 - stage["fuel_frac"])
fuel *= (1 - stage["fuel_frac"])

time.sleep(1)

print("\nSTAGE 3: CAPTURE OF THE MOON'S ORBIT (requires Delta-v = 280 m/s)")
print("="*80)

stage = stages[2]
target_deltaV = deltaV_required["Захват орбиты Муны"]

print("Time(s) | Speed(m/s) | OX(km) | OY(km) | Fuel(t)")
print("-" * 80)

mass_start_brake = mass
fuel_needed_brake = mass_start_brake - (mass_start_brake / math.exp(target_deltaV / (g0 * stage["Isp"])))

if fuel >= fuel_needed_brake:
    brake_time = 60
    fuel_rate_brake = fuel_needed_brake / brake_time
    
    time_steps_3 = [250, 270, 290, 310]
    
    for t in time_steps_3:
        dt = 20
        time_elapsed = t
        
        fuel_used = fuel_rate_brake * dt
        fuel -= fuel_used
        mass -= fuel_used
        
        velocity_decrement = target_deltaV * (dt / brake_time)
        velocity = max(0, velocity - velocity_decrement)
        
        x_position += velocity * 0.3 * dt
        y_position += velocity * 0.7 * dt
        
        acceleration = -stage["thrust"] / mass if mass > 0 else 0
        
        print(f"{time_elapsed:8.1f} | {velocity:13.2f} | {x_position/1000:6.1f} | {y_position/1000:6.1f} | {fuel/1000:8.1f}")
    
    actual_deltaV_brake = calculate_delta_v(mass_start_brake, mass, stage["Isp"], g0)

time.sleep(1)

print("\nSTAGE 4: MOON LANDING (requires Delta-v = 580 m/s)")
print("="*80)

mass_lander = min(mass, 8000)
fuel_lander = fuel
altitude_landing = 15000
velocity_landing = 300
g_moon = 1.62
isp_landing = 310
thrust_landing = 40000

print("Time(s) | Speed(m/s) | Height(m) | Fuel(kg)")
print("-" * 80)

print(f"{time_elapsed:8.1f} | {velocity_landing:13.0f} | {altitude_landing:9.0f} | {fuel_lander:10.0f}")

time_steps_landing = [320, 330, 340, 350, 360, 370]
current_altitude = altitude_landing
current_velocity = velocity_landing
current_fuel = fuel_lander
current_mass = mass_lander
fuel_rate_landing = 40

for t in time_steps_landing:
    dt = 10
    time_elapsed = t
    
    fuel_used = fuel_rate_landing * dt
    if fuel_used > current_fuel:
        fuel_used = current_fuel
    current_fuel -= fuel_used
    current_mass -= fuel_used
    
    if current_mass <= 0:
        break
    
    thrust = thrust_landing
    net_force = thrust - current_mass * g_moon
    acceleration = net_force / current_mass if current_mass > 0 else -g_moon
    
    if acceleration > 0:
        current_velocity = max(0, current_velocity - acceleration * 0.5 * dt)
    else:
        current_velocity = current_velocity + abs(acceleration) * dt
    
    current_altitude = max(0, current_altitude - current_velocity * dt)
    
    print(f"{time_elapsed:8.1f} | {current_velocity:13.1f} | {current_altitude:9.0f} | {current_fuel:10.0f}")
    
    if current_altitude <= 0:
        print(f"\n*** THE MOON LANDING IS COMPLETED! ***")
        break

print(f"\n The mission has been completed successfully!")
print("="*80)
