// UI Controller - Manages all UI updates and interactions
class UIController {
    constructor(socketManager) {
        this.socketManager = socketManager;
        this.state = null;
        this.initControls();
    }

    initControls() {
        // Controller buttons
        document.querySelectorAll('.controller-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const controller = e.currentTarget.dataset.controller;
                document.querySelectorAll('.controller-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.socketManager.changeController(controller);
            });
        });

        // Start/Pause button
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                if (!this.state || !this.state.running) {
                    this.socketManager.start();
                } else {
                    this.socketManager.pause();
                }
            });
        }

        // Reset button
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.socketManager.reset();
            });
        }

        // Spawn rate slider
        const spawnRate = document.getElementById('spawnRate');
        if (spawnRate) {
            const spawnRateValue = document.getElementById('spawnRateValue');
            spawnRate.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                if (spawnRateValue) {
                    spawnRateValue.textContent = `${value.toFixed(1)}s`;
                }
                this.socketManager.updateSpawnRate(value);
            });
        }

        // Speed slider
        const simSpeed = document.getElementById('simSpeed');
        if (simSpeed) {
            const speedValue = document.getElementById('speedValue');
            simSpeed.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                if (speedValue) {
                    speedValue.textContent = `${value.toFixed(2)}x`;
                }
                this.socketManager.updateSpeed(value);
            });
        }

        // VIP spawn buttons
        document.querySelectorAll('.vip-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const direction = e.currentTarget.dataset.direction;
                this.socketManager.spawnVIP(direction);
            });
        });
    }

    updateUI(state) {
        if (!state) return;

        this.state = state;

        const updateElement = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        // Update queues
        updateElement('queueNorth', state.queues.north);
        updateElement('queueSouth', state.queues.south);
        updateElement('queueEast', state.queues.east);
        updateElement('queueWest', state.queues.west);

        // Update phase info
        updateElement('phaseTime', `${(state.phase_time / 1000).toFixed(1)}s`);
        updateElement('totalCars', state.total_cars);
        updateElement('vipCars', state.vip_cars);

        // Update controller badge
        const controllerNames = {
            'fixed_time': 'Fixed Time',
            'actuated': 'Actuated',
            'max_pressure': 'Max Pressure',
            'fuzzy': 'Fuzzy Logic',
            'q_learning': 'Q-Learning'
        };
        updateElement('controllerBadge', controllerNames[state.controller] || state.controller);

        // Update start/pause button
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            startBtn.textContent = state.running ? '⏸️ Pause' : '▶️ Start';
        }

        // Update active controller button
        document.querySelectorAll('.controller-btn').forEach(btn => {
            if (btn.dataset.controller === state.controller) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update sliders to match backend state
        if (state.spawn_rate !== undefined) {
            const spawnRateSlider = document.getElementById('spawnRate');
            const spawnRateValue = document.getElementById('spawnRateValue');
            if (spawnRateSlider && parseFloat(spawnRateSlider.value) !== state.spawn_rate) {
                spawnRateSlider.value = state.spawn_rate;
                if (spawnRateValue) {
                    spawnRateValue.textContent = `${state.spawn_rate.toFixed(1)}s`;
                }
            }
        }

        if (state.speed_multiplier !== undefined) {
            const speedSlider = document.getElementById('simSpeed');
            const speedValue = document.getElementById('speedValue');
            if (speedSlider && parseFloat(speedSlider.value) !== state.speed_multiplier) {
                speedSlider.value = state.speed_multiplier;
                if (speedValue) {
                    speedValue.textContent = `${state.speed_multiplier.toFixed(2)}x`;
                }
            }
        }
    }
}
