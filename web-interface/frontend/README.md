# MCP Android Web Interface - Frontend

A modern React application for controlling and automating Android devices through the MCP Android server with Claude AI integration.

## Features

- **Device Management**: Connect and select from multiple Android devices
- **Live Screen View**: Real-time device screenshot with auto-refresh
- **Click-to-Coordinate**: Click on device screen to get exact coordinates
- **Claude Integration**: Chat with Claude to automate device interactions
- **Action History**: Track all executed MCP tool calls with parameters and results
- **Modern UI**: Built with React 19, TypeScript, and TailwindCSS

## Tech Stack

- **React 19.1.1** - Latest React with hooks
- **TypeScript 5.9** - Type safety
- **Vite 7** - Fast build tool and dev server
- **TailwindCSS 4** - Utility-first CSS framework
- **WebSockets** - Real-time Claude streaming

## Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:3001`
- Android device connected with MCP Android server

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser
http://localhost:3000
```

## Development

### Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── DeviceSelector.tsx    # Device picker dropdown
│   │   ├── DeviceViewer.tsx      # Screenshot viewer with click detection
│   │   ├── ClaudeChat.tsx        # Chat interface with WebSocket
│   │   └── ActionHistory.tsx     # Action log display
│   ├── services/            # API clients
│   │   ├── api.ts               # REST API client
│   │   └── websocket.ts         # WebSocket client
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles (Tailwind)
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
└── package.json
```

### Available Scripts

```bash
# Development server (http://localhost:3000)
npm run dev

# Type check
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Backend API Integration

The frontend connects to the backend via:

**REST API (proxied through Vite):**
- `GET /api/devices` - List connected devices
- `POST /api/screenshot` - Capture device screenshot
- `GET /api/screenshot/:filename` - Get screenshot image
- `GET /api/actions/history` - Get action history
- `POST /api/actions/record` - Record new action
- `POST /api/mcp/tool` - Execute MCP tool

**WebSocket (direct connection):**
- `ws://localhost:3001/ws/claude` - Claude streaming chat

### Configuration

Edit `vite.config.ts` to change backend URL:

```typescript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:3001', // Change backend URL here
        changeOrigin: true,
      },
    },
  },
})
```

## Component Usage

### DeviceSelector

Select and manage connected Android devices.

```tsx
import { DeviceSelector } from './components/DeviceSelector';

<DeviceSelector
  selectedDevice={deviceId}
  onDeviceChange={(id) => setDeviceId(id)}
/>
```

### DeviceViewer

Display device screenshot with click detection.

```tsx
import { DeviceViewer } from './components/DeviceViewer';

<DeviceViewer
  deviceId={selectedDevice}
  onClickCoordinates={(x, y) => console.log(`Clicked: ${x}, ${y}`)}
/>
```

Features:
- Auto-refresh every 2 seconds (toggleable)
- Click-to-coordinate with visual feedback
- Screenshot download
- Coordinate scaling for different screen sizes

### ClaudeChat

Chat interface with Claude for device automation.

```tsx
import { ClaudeChat } from './components/ClaudeChat';

<ClaudeChat deviceId={selectedDevice} />
```

Features:
- Real-time streaming responses via WebSocket
- Message history with timestamps
- Auto-scroll to latest message
- Connection status indicator

### ActionHistory

Display log of all MCP tool executions.

```tsx
import { ActionHistory } from './components/ActionHistory';

<ActionHistory />
```

Features:
- Auto-refresh every 3 seconds (toggleable)
- Expandable parameter/result details
- Success/failure indicators
- Clear history

## Styling

Uses TailwindCSS utility classes. Key design decisions:

- **Color Scheme**: Blue primary, gray neutrals
- **Layout**: Responsive grid with mobile support
- **Typography**: System fonts for performance
- **Components**: Card-based with shadows and borders

To customize colors, edit `tailwind.config.js`:

```js
export default {
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6', // blue-500
      },
    },
  },
}
```

## Troubleshooting

### WebSocket Connection Failed

- Ensure backend is running on `http://localhost:3001`
- Check backend logs for WebSocket errors
- Verify no firewall blocking port 3001

### Screenshot Not Loading

- Check device is connected via ADB
- Verify backend `/api/screenshot` endpoint is working
- Check browser console for CORS errors

### Click Coordinates Wrong

- Click coordinates are automatically scaled
- Check console for actual device coordinates
- Ensure screenshot dimensions match device resolution

### Type Errors

```bash
# Regenerate types
npm run build
```

## Building for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview

# Deploy dist/ folder to your hosting service
```

Output goes to `dist/` directory.

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- **Bundle Size**: ~150KB gzipped
- **First Load**: < 1s on broadband
- **Lighthouse Score**: 95+ on all metrics

## License

Same as parent project (see root LICENSE file)

## Contributing

This is part of the MCP Android Server project. See main README for contribution guidelines.

## Related

- [Backend Server](../backend/README.md)
- [MCP Android Server](../../README.md)
