# DRAIT Desktop Application

Electron-based desktop application for DRAIT UML Class Diagram Editor.

## Technology Stack

- **Electron**: Desktop application framework
- **React 18**: UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Flow**: Diagram rendering library (to be integrated)
- **Zustand**: State management (to be integrated)

## Project Structure

```
src/desktop/
├── electron/              # Electron main process
│   ├── main.js           # Main process entry point
│   └── preload.js        # Preload script (security bridge)
├── renderer/             # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   ├── types/        # TypeScript types
│   │   ├── styles/       # CSS files
│   │   ├── App.tsx       # Main App component
│   │   └── main.tsx      # React entry point
│   └── index.html        # HTML template
├── package.json          # Dependencies and scripts
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
└── tailwind.config.js    # Tailwind CSS configuration
```

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ with DRAIT installed
- uv (Python package manager)

### Install Dependencies

```bash
cd src/desktop
npm install
```

### Development Mode

Run the app in development mode with hot-reload:

```bash
npm run dev
```

This will:
1. Start Vite dev server on http://localhost:5173
2. Launch Electron with dev tools open
3. Enable hot-reload for React components

### Build

Build the React app for production:

```bash
npm run build
```

### Package

Create distributable packages:

```bash
npm run build:electron
```

This creates platform-specific packages in `dist-electron/`:
- **macOS**: `.dmg` file
- **Windows**: `.exe` installer
- **Linux**: `.AppImage` and `.deb` packages

## Architecture

### Electron Main Process

- Manages application window
- Handles native menus and dialogs
- Communicates with Python backend (subprocess)
- Provides IPC handlers for renderer

### Renderer Process (React)

- UI components
- Diagram editor
- Communicates with main process via IPC

### Python Backend

- Runs as subprocess or embedded server
- Handles parsing and code generation
- Uses existing DRAIT core (metamodel, parser, generator)

### Communication Flow

```
React (Renderer) ←→ IPC ←→ Electron Main ←→ Python Subprocess
```

## Available Scripts

- `npm run dev` - Start development mode
- `npm run build` - Build React app
- `npm run build:electron` - Package for distribution
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Current Status

✅ Basic Electron + React setup
✅ TypeScript configuration
✅ Tailwind CSS integration
✅ Python subprocess bridge (placeholder)
✅ File dialog integration
⏳ React Flow diagram rendering
⏳ Full Python parser integration
⏳ Code generator integration
⏳ Interactive diagram editing

## Next Steps

1. Integrate React Flow for diagram rendering
2. Implement metamodel TypeScript types
3. Create diagram components (Class, Relationship, etc.)
4. Build toolbar and property panel
5. Complete Python bridge implementation
6. Add code generation UI

## Notes

- The Python backend currently uses `uv run drait-parse` command
- Need to add `--format=json` flag to drait-parse for JSON output
- React components are ready for diagram library integration
