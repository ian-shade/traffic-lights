// Main Traffic Simulation Client - Coordinates all components
class TrafficSimulationClient {
    constructor() {
        this.state = null;

        // Initialize all components
        this.canvasManager = new CanvasManager();
        if (!this.canvasManager.getCanvas()) {
            console.error('Failed to initialize canvas manager');
            return;
        }

        this.renderer = new IntersectionRenderer(this.canvasManager);
        this.socketManager = new SocketManager((state) => this.handleStateUpdate(state));
        this.uiController = new UIController(this.socketManager);

        this.startRenderLoop();
    }

    handleStateUpdate(state) {
        this.state = state;
        this.uiController.updateUI(state);
    }

    startRenderLoop() {
        const render = () => {
            if (this.state) {
                this.renderer.render(this.state);
            }
            requestAnimationFrame(render);
        };
        render();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TrafficSimulationClient();
});
