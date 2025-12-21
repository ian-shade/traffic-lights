# Traffic Simulation Web Interface

## Directory Structure

```
web/
├── index.html                 # Main HTML file
├── js/                        # JavaScript modules
│   ├── CanvasManager.js       # Handles canvas setup and responsive behavior
│   ├── IntersectionRenderer.js # Renders traffic intersection and cars
│   ├── SocketManager.js       # WebSocket communication with backend
│   ├── UIController.js        # UI updates and user interactions
│   └── TrafficSimulationClient.js # Main coordinator class
├── css/                       # Stylesheet modules
│   ├── variables.css          # CSS variables and theme colors
│   ├── base.css               # Reset and base layout styles
│   ├── header.css             # Header component styles
│   ├── sidebar.css            # Sidebar component styles
│   ├── buttons.css            # Button components (controller, VIP, standard)
│   ├── controls.css           # Control inputs (sliders)
│   ├── stats.css              # Statistics display components
│   ├── canvas.css             # Canvas area and loading overlay
│   └── responsive.css         # Responsive design breakpoints
└── [DEPRECATED]
    ├── app.js                 # Old monolithic JavaScript (keep for reference)
    └── style.css              # Old monolithic CSS (keep for reference)
```

## JavaScript Modules

### CanvasManager.js
- Manages canvas element and context
- Handles responsive canvas sizing
- Listens to window resize and orientation change events

### IntersectionRenderer.js
- Renders the traffic intersection
- Draws roads, lane markings, and stop lines
- Renders traffic lights with proper states
- Draws regular and VIP cars with animations
- Handles compass labels

### SocketManager.js
- Establishes WebSocket connection with Flask backend
- Handles connect/disconnect events
- Emits user actions (start, pause, reset, controller changes)
- Receives state updates from backend
- Manages update loop at 60 FPS

### UIController.js
- Initializes all UI control event listeners
- Updates UI elements based on backend state
- Handles controller buttons, sliders, and VIP spawn buttons
- Syncs UI with backend state

### TrafficSimulationClient.js
- Main coordinator class
- Initializes and connects all other modules
- Manages application lifecycle
- Coordinates state updates between components

## CSS Modules

### variables.css
- CSS custom properties (color palette, theme variables)

### base.css
- Global reset and base styles
- Main layout container structure

### header.css
- Header bar with title and controller badge

### sidebar.css
- Sidebar container and control sections
- Scrollbar styling

### buttons.css
- Controller type buttons with grid layout
- Standard action buttons (start/pause, reset)
- VIP spawn buttons

### controls.css
- Slider components for spawn rate and speed

### stats.css
- Statistics display in sidebar
- Floating stats box overlay on canvas

### canvas.css
- Canvas area container
- Loading overlay with spinner animation

### responsive.css
- Media queries for different screen sizes
- Mobile and tablet optimizations

## Loading Order

**CSS**: Variables → Base → Components → Responsive

**JavaScript**: CanvasManager → IntersectionRenderer → SocketManager → UIController → TrafficSimulationClient

The order ensures dependencies are loaded before components that use them.

## Development Notes

- All JavaScript classes are in the global scope for simplicity
- For production, consider using ES6 modules or a bundler
- The old `app.js` and `style.css` are kept for reference but are no longer used
- All functionality remains identical to the original implementation
