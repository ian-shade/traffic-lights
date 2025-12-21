// Socket Manager - Handles WebSocket communication with Flask backend
class SocketManager {
    constructor(onStateUpdate) {
        this.socket = null;
        this.onStateUpdate = onStateUpdate;
        this.lastUpdate = Date.now();
        this.initSocket();
    }

    initSocket() {
        // Connect to Flask-SocketIO server
        this.socket = io();

        this.socket.on('connect', () => {
            console.log('Connected to server');
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.classList.add('hidden');
            }
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden');
            }
        });

        this.socket.on('state_update', (state) => {
            if (this.onStateUpdate) {
                this.onStateUpdate(state);
            }
        });

        // Send update requests at 60 FPS
        setInterval(() => {
            if (this.socket && this.socket.connected) {
                const now = Date.now();
                const deltaTime = now - this.lastUpdate;
                this.lastUpdate = now;
                this.socket.emit('update', { delta_time: deltaTime });
            }
        }, 1000 / 60);
    }

    // Controller actions
    changeController(controller) {
        this.socket.emit('change_controller', { controller });
    }

    start() {
        this.socket.emit('start');
    }

    pause() {
        this.socket.emit('pause');
    }

    reset() {
        this.socket.emit('reset');
    }

    updateSpawnRate(spawnRate) {
        this.socket.emit('update_spawn_rate', { spawn_rate: spawnRate });
    }

    updateSpeed(speed) {
        this.socket.emit('update_speed', { speed });
    }

    spawnVIP(direction) {
        this.socket.emit('spawn_vip', { direction });
    }
}
