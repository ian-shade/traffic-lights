// Intersection Renderer - Handles all intersection and traffic rendering
class IntersectionRenderer {
    constructor(canvasManager) {
        this.canvasManager = canvasManager;
        this.ctx = canvasManager.getContext();
        this.canvas = canvasManager.getCanvas();
    }

    render(state) {
        if (!state) return;

        const ctx = this.ctx;
        const canvas = this.canvas;

        // Clear canvas with gradient
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, '#1e293b');
        gradient.addColorStop(1, '#334155');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Use full canvas with some padding
        const padding = 0;
        const intersectionSize = Math.min(canvas.width, canvas.height) - padding * 2;
        const centerX = (canvas.width - intersectionSize) / 2;
        const centerY = (canvas.height - intersectionSize) / 2;

        // Scale all positions relative to intersection size (base size was 600)
        const scale = intersectionSize / 600;

        this.drawRoad(centerX, centerY, intersectionSize, scale);
        this.drawTrafficLights(state, centerX, centerY, scale);
        this.drawCars(state, centerX, centerY, intersectionSize);
        this.drawCompassLabels(centerX, centerY, intersectionSize, scale);
    }

    drawRoad(centerX, centerY, intersectionSize, scale) {
        const ctx = this.ctx;

        // Draw road base
        ctx.fillStyle = '#374151';
        ctx.fillRect(centerX, centerY, intersectionSize, intersectionSize);

        // Draw vertical road
        ctx.fillStyle = '#4b5563';
        ctx.fillRect(centerX + 250 * scale, centerY, 100 * scale, intersectionSize);

        // Draw horizontal road
        ctx.fillRect(centerX, centerY + 250 * scale, intersectionSize, 100 * scale);

        // Draw lane dividers (yellow)
        ctx.fillStyle = '#fbbf24';
        ctx.fillRect(centerX + 295 * scale, centerY, 10 * scale, 240 * scale);
        ctx.fillRect(centerX + 295 * scale, centerY + 360 * scale, 10 * scale, 240 * scale);
        ctx.fillRect(centerX, centerY + 295 * scale, 240 * scale, 10 * scale);
        ctx.fillRect(centerX + 360 * scale, centerY + 295 * scale, 240 * scale, 10 * scale);

        // Draw stop lines (white)
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(centerX + 250 * scale, centerY + 248 * scale, 100 * scale, 4 * scale);
        ctx.fillRect(centerX + 250 * scale, centerY + 348 * scale, 100 * scale, 4 * scale);
        ctx.fillRect(centerX + 248 * scale, centerY + 250 * scale, 4 * scale, 100 * scale);
        ctx.fillRect(centerX + 348 * scale, centerY + 250 * scale, 4 * scale, 100 * scale);
    }

    drawTrafficLights(state, centerX, centerY, scale) {
        // East (right side, vertical light)
        this.drawTrafficLight(centerX + 360 * scale, centerY + 245 * scale, state.lights.east, false, scale);

        // West (left side, vertical light)
        this.drawTrafficLight(centerX + 220 * scale, centerY + 245 * scale, state.lights.west, false, scale);

        // North (bottom, horizontal light)
        this.drawTrafficLight(centerX + 255 * scale, centerY + 360 * scale, state.lights.north, true, scale);

        // South (top, horizontal light)
        this.drawTrafficLight(centerX + 265 * scale, centerY + 220 * scale, state.lights.south, true, scale);
    }

    drawTrafficLight(x, y, state, horizontal, scale = 1) {
        const ctx = this.ctx;
        const redColor = state === 'red' ? '#ef4444' : '#7f1d1d';
        const yellowColor = state === 'yellow' ? '#fbbf24' : '#78350f';
        const greenColor = state === 'green' ? '#10b981' : '#064e3b';

        if (!horizontal) {
            // Vertical light
            ctx.fillStyle = '#1f2937';
            ctx.fillRect(x, y, 20 * scale, 70 * scale);

            if (state === 'red') { ctx.shadowBlur = 15 * scale; ctx.shadowColor = redColor; }
            ctx.beginPath();
            ctx.arc(x + 10 * scale, y + 10 * scale, 6 * scale, 0, Math.PI * 2);
            ctx.fillStyle = redColor;
            ctx.fill();
            ctx.shadowBlur = 0;

            if (state === 'yellow') { ctx.shadowBlur = 15 * scale; ctx.shadowColor = yellowColor; }
            ctx.beginPath();
            ctx.arc(x + 10 * scale, y + 35 * scale, 6 * scale, 0, Math.PI * 2);
            ctx.fillStyle = yellowColor;
            ctx.fill();
            ctx.shadowBlur = 0;

            if (state === 'green') { ctx.shadowBlur = 15 * scale; ctx.shadowColor = greenColor; }
            ctx.beginPath();
            ctx.arc(x + 10 * scale, y + 60 * scale, 6 * scale, 0, Math.PI * 2);
            ctx.fillStyle = greenColor;
            ctx.fill();
            ctx.shadowBlur = 0;
        } else {
            // Horizontal light
            ctx.fillStyle = '#1f2937';
            ctx.fillRect(x, y, 70 * scale, 20 * scale);

            if (state === 'red') { ctx.shadowBlur = 15 * scale; ctx.shadowColor = redColor; }
            ctx.beginPath();
            ctx.arc(x + 10 * scale, y + 10 * scale, 6 * scale, 0, Math.PI * 2);
            ctx.fillStyle = redColor;
            ctx.fill();
            ctx.shadowBlur = 0;

            if (state === 'yellow') { ctx.shadowBlur = 15 * scale; ctx.shadowColor = yellowColor; }
            ctx.beginPath();
            ctx.arc(x + 35 * scale, y + 10 * scale, 6 * scale, 0, Math.PI * 2);
            ctx.fillStyle = yellowColor;
            ctx.fill();
            ctx.shadowBlur = 0;

            if (state === 'green') { ctx.shadowBlur = 15 * scale; ctx.shadowColor = greenColor; }
            ctx.beginPath();
            ctx.arc(x + 60 * scale, y + 10 * scale, 6 * scale, 0, Math.PI * 2);
            ctx.fillStyle = greenColor;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    drawCars(state, centerX, centerY, intersectionSize) {
        for (const car of state.cars) {
            this.drawCar(car, centerX, centerY, intersectionSize);
        }
    }

    drawCar(car, centerX, centerY, intersectionSize) {
        const ctx = this.ctx;
        const roadScale = intersectionSize / 600; // Scale relative to base 600px size
        // Car positions come from backend in range 0-800, need to map to our 600px base
        const s = (car.position / 900) * intersectionSize;

        let x, y, width, height, rotation;

        // Correct lane positioning - cars stay in their lanes (scaled)
        if (car.direction === 'north') {
            // North-bound cars (bottom to top) - right lane
            x = centerX + 310 * roadScale;
            y = centerY + intersectionSize - s;
            width = 16 * roadScale;
            height = 28 * roadScale;
            rotation = 0;
        } else if (car.direction === 'south') {
            // South-bound cars (top to bottom) - left lane
            x = centerX + 290 * roadScale;
            y = centerY + s;
            width = 16 * roadScale;
            height = 28 * roadScale;
            rotation = Math.PI;
        } else if (car.direction === 'east') {
            // East-bound cars (left to right) - bottom lane
            x = centerX + s;
            y = centerY + 310 * roadScale;
            width = 28 * roadScale;
            height = 16 * roadScale;
            rotation = 0;
        } else {
            // West-bound cars (right to left) - top lane
            x = centerX + intersectionSize - s;
            y = centerY + 290 * roadScale;
            width = 28 * roadScale;
            height = 16 * roadScale;
            rotation = Math.PI;
        }

        // Save context and rotate for proper car orientation
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);

        if (car.isVip) {
            // VIP Car - Emergency Vehicle Design
            this.drawVIPCar(ctx, width, height, car.color);
        } else {
            // Regular Car Design
            this.drawRegularCar(ctx, width, height, car.color);
        }

        ctx.restore();
    }

    drawRegularCar(ctx, width, height, color) {
        const carColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
        const detailScale = Math.min(width, height) / 16; // Scale details relative to car size

        // Car body with rounded edges
        ctx.fillStyle = carColor;
        ctx.beginPath();
        ctx.roundRect(-width/2, -height/2, width, height, 3 * detailScale);
        ctx.fill();

        // Windshield
        ctx.fillStyle = 'rgba(100, 150, 200, 0.6)';
        ctx.beginPath();
        ctx.roundRect(-width/2 + 2 * detailScale, -height/2 + 3 * detailScale, width - 4 * detailScale, height * 0.3, 2 * detailScale);
        ctx.fill();

        // Rear window
        ctx.beginPath();
        ctx.roundRect(-width/2 + 2 * detailScale, height/2 - 3 * detailScale - height * 0.25, width - 4 * detailScale, height * 0.25, 2 * detailScale);
        ctx.fill();

        // Headlights
        ctx.fillStyle = '#ffffcc';
        ctx.fillRect(-width/2 + 1 * detailScale, -height/2, 3 * detailScale, 2 * detailScale);
        ctx.fillRect(width/2 - 4 * detailScale, -height/2, 3 * detailScale, 2 * detailScale);

        // Shadow/outline
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.lineWidth = 0.5 * detailScale;
        ctx.beginPath();
        ctx.roundRect(-width/2, -height/2, width, height, 3 * detailScale);
        ctx.stroke();
    }

    drawVIPCar(ctx, width, height, color) {
        const detailScale = Math.min(width, height) / 16; // Scale details relative to car size

        // VIP car base (usually white or bright colors)
        ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
        ctx.beginPath();
        ctx.roundRect(-width/2, -height/2, width, height, 3 * detailScale);
        ctx.fill();

        // Emergency stripe
        ctx.fillStyle = '#ff0000';
        ctx.fillRect(-width/2 + 3 * detailScale, -height/2 + height * 0.4, width - 6 * detailScale, 3 * detailScale);

        // Windshield (darker for emergency vehicles)
        ctx.fillStyle = 'rgba(50, 50, 80, 0.8)';
        ctx.beginPath();
        ctx.roundRect(-width/2 + 2 * detailScale, -height/2 + 3 * detailScale, width - 4 * detailScale, height * 0.3, 2 * detailScale);
        ctx.fill();

        // Animated light bar on top
        const pulse = Math.sin(Date.now() / 150) * 0.5 + 0.5;

        // Blue light (left)
        ctx.shadowBlur = 8 * pulse * detailScale;
        ctx.shadowColor = '#0080ff';
        ctx.fillStyle = `rgba(0, 128, 255, ${0.7 + pulse * 0.3})`;
        ctx.beginPath();
        ctx.arc(-width/4, -height/2 + 2 * detailScale, 2.5 * detailScale, 0, Math.PI * 2);
        ctx.fill();

        // Red light (right)
        ctx.shadowColor = '#ff0000';
        ctx.fillStyle = `rgba(255, 0, 0, ${0.7 + pulse * 0.3})`;
        ctx.beginPath();
        ctx.arc(width/4, -height/2 + 2 * detailScale, 2.5 * detailScale, 0, Math.PI * 2);
        ctx.fill();

        ctx.shadowBlur = 0;

        // VIP badge/text
        ctx.fillStyle = '#ffffff';
        ctx.font = `bold ${6 * detailScale}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText('VIP', 0, height/2 - 4 * detailScale);

        // Outline
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5 * detailScale;
        ctx.beginPath();
        ctx.roundRect(-width/2, -height/2, width, height, 3 * detailScale);
        ctx.stroke();
    }

    drawCompassLabels(centerX, centerY, intersectionSize, scale) {
        const ctx = this.ctx;
        ctx.shadowColor = 'rgba(99, 102, 241, 0.5)';
        ctx.shadowBlur = 10 * scale;
        ctx.fillStyle = '#f1f5f9';
        ctx.font = `bold ${24 * scale}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText('N', centerX + 300 * scale, centerY + 30 * scale);
        ctx.fillText('S', centerX + 300 * scale, centerY + intersectionSize - 10 * scale);
        ctx.fillText('E', centerX + intersectionSize - 20 * scale, centerY + 310 * scale);
        ctx.fillText('W', centerX + 30 * scale, centerY + 310 * scale);
        ctx.shadowBlur = 0;
    }
}
