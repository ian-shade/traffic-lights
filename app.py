"""
Flask API server for Traffic Intersection Simulation
Serves the web frontend and provides WebSocket for real-time simulation
"""
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
from typing import Dict

from models import Direction, LightState, Car
from traffic_controller import TrafficController
from car_manager import CarManager
from controllers import (
    FixedTimeController,
    ActuatedThresholdController,
    MaxPressureController,
    FuzzyController,
    QTableController
)

app = Flask(__name__, static_folder='web', static_url_path='')
app.config['SECRET_KEY'] = 'traffic-simulation-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class SimulationState:
    def __init__(self):
        self.traffic_controller = TrafficController()
        self.car_manager = CarManager()
        self.controller_name = "fixed_time"
        self.spawn_rate = 2.0
        self.last_spawn_time = 0
        self.current_time = 0
        self.running = False
        self.speed_multiplier = 1.0
        self._apply_controller(self.controller_name)

    def _apply_controller(self, name: str):
        name = (name or "fixed_time").lower()
        self.controller_name = name

        if name == "fixed_time":
            self.traffic_controller.set_controller(FixedTimeController(switch_every_s=30))
        elif name == "actuated":
            self.traffic_controller.set_controller(ActuatedThresholdController())
        elif name == "max_pressure":
            self.traffic_controller.set_controller(MaxPressureController())
        elif name == "fuzzy":
            self.traffic_controller.set_controller(FuzzyController())
        elif name == "q_learning":
            self.traffic_controller.set_controller(QTableController("q_table_advanced.json"))
        else:
            self.traffic_controller.set_controller(FixedTimeController(switch_every_s=30))
            self.controller_name = "fixed_time"

    def reset(self):
        self.traffic_controller = TrafficController()
        self._apply_controller(self.controller_name)
        self.car_manager = CarManager()
        self.last_spawn_time = 0
        self.current_time = 0
        self.running = False
        self.spawn_rate = 2.0
        self.speed_multiplier = 1.0

    def update(self, delta_time: float):
        self.current_time += delta_time

        if self.current_time - self.last_spawn_time > self.spawn_rate * 1000 + random.random() * 1000:
            direction = random.choice(list(Direction))
            self.car_manager.spawn_car(direction)
            self.last_spawn_time = self.current_time

        queue_stats = {d: self.car_manager.get_queue_count(d) for d in Direction}
        vip_queue_stats = {d: self.car_manager.get_vip_queue_count(d) for d in Direction}

        self.traffic_controller.update(queue_stats, vip_queue_stats, delta_time)
        self.car_manager.update_cars(
            lambda d: self.traffic_controller.get_light_state(d),
            delta_time
        )

    def get_state_dict(self) -> dict:
        cars_data = []
        for car in self.car_manager.get_cars():
            cars_data.append({
                'id': car.id,
                'direction': car.direction.value,
                'position': car.position,
                'speed': car.speed,
                'color': car.color,
                'isVip': car.is_vip,
                'committed': car.committed
            })

        lights = {
            'north': self.traffic_controller.get_light_state(Direction.NORTH).value,
            'south': self.traffic_controller.get_light_state(Direction.SOUTH).value,
            'east': self.traffic_controller.get_light_state(Direction.EAST).value,
            'west': self.traffic_controller.get_light_state(Direction.WEST).value
        }

        queue_stats = {
            'north': self.car_manager.get_queue_count(Direction.SOUTH),
            'south': self.car_manager.get_queue_count(Direction.NORTH),
            'east': self.car_manager.get_queue_count(Direction.WEST),
            'west': self.car_manager.get_queue_count(Direction.EAST)
        }

        return {
            'cars': cars_data,
            'lights': lights,
            'queues': queue_stats,
            'phase_time': self.traffic_controller.get_phase_time_remaining(),
            'current_phase': self.traffic_controller.current_phase,
            'controller': self.controller_name,
            'total_cars': len(self.car_manager.get_cars()),
            'vip_cars': len([c for c in self.car_manager.get_cars() if c.is_vip]),
            'spawn_rate': self.spawn_rate,
            'speed_multiplier': self.speed_multiplier,
            'running': self.running
        }

sim_state = SimulationState()

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Reset simulation state on new connection (page refresh)
    sim_state.reset()
    emit('state_update', sim_state.get_state_dict())

@socketio.on('start')
def handle_start():
    sim_state.running = True
    emit('state_update', sim_state.get_state_dict(), broadcast=True)

@socketio.on('pause')
def handle_pause():
    sim_state.running = not sim_state.running
    emit('state_update', sim_state.get_state_dict(), broadcast=True)

@socketio.on('reset')
def handle_reset():
    sim_state.reset()
    emit('state_update', sim_state.get_state_dict(), broadcast=True)

@socketio.on('update')
def handle_update(data):
    if sim_state.running:
        delta_time = data.get('delta_time', 16.67) * sim_state.speed_multiplier
        sim_state.update(delta_time)
        emit('state_update', sim_state.get_state_dict(), broadcast=True)

@socketio.on('change_controller')
def handle_change_controller(data):
    controller_name = data.get('controller', 'fixed_time')
    sim_state.controller_name = controller_name
    sim_state.reset()
    emit('state_update', sim_state.get_state_dict(), broadcast=True)

@socketio.on('spawn_vip')
def handle_spawn_vip(data):
    direction_str = data.get('direction', 'NORTH').upper()
    direction = Direction[direction_str]
    sim_state.car_manager.spawn_car(direction, force_vip=True)
    emit('state_update', sim_state.get_state_dict(), broadcast=True)

@socketio.on('update_spawn_rate')
def handle_update_spawn_rate(data):
    spawn_rate = data.get('spawn_rate', 2.0)
    sim_state.spawn_rate = max(0.5, min(5.0, spawn_rate))
    emit('state_update', sim_state.get_state_dict(), broadcast=True)

@socketio.on('update_speed')
def handle_update_speed(data):
    speed = data.get('speed', 1.0)
    sim_state.speed_multiplier = max(0.25, min(3.0, speed))
    emit('state_update', sim_state.get_state_dict(), broadcast=True)

if __name__ == '__main__':
    print("=" * 60)
    print("🚦 Traffic Simulation Web Server")
    print("=" * 60)
    print("📡 Server running at: http://localhost:3003")
    print("🌐 Open this URL in your browser to view the simulation")
    print("=" * 60)
    socketio.run(app, debug=True, host='0.0.0.0', port=3003)
