// Canvas Manager - Handles canvas setup and responsive behavior
class CanvasManager {
    constructor() {
        this.canvas = document.getElementById('canvas');
        if (!this.canvas) {
            console.error('Canvas not found!');
            return;
        }
        this.ctx = this.canvas.getContext('2d');
        this.setupResponsiveCanvas();
    }

    setupResponsiveCanvas() {
        const resizeCanvas = () => {
            const container = this.canvas.parentElement;
            const containerRect = container.getBoundingClientRect();

            // Account for padding (2rem = 32px on each side)
            const padding = 64;
            const maxWidth = containerRect.width - padding;
            const maxHeight = containerRect.height - padding;

            // Make canvas size based on the smaller dimension to keep it square
            const size = Math.min(maxWidth, maxHeight);

            this.canvas.width = size;
            this.canvas.height = size;
        };

        // Initial resize
        resizeCanvas();

        // Resize on window resize
        window.addEventListener('resize', resizeCanvas);

        // Also resize when sidebar might change (like on mobile)
        window.addEventListener('orientationchange', () => {
            setTimeout(resizeCanvas, 100);
        });
    }

    getContext() {
        return this.ctx;
    }

    getCanvas() {
        return this.canvas;
    }
}
