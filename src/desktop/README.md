# DRAIT Desktop Application

Electron-based desktop application for DRAIT UML Class Diagram Editor with interactive visual diagram editing.

## Technology Stack

- **Electron**: Desktop application framework
- **React 18**: UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **React Flow**: Interactive diagram rendering and editing
- **Python (drait)**: Backend parser and metamodel

## Features

✅ **Visual UML Diagram Rendering**
- Interactive class diagram visualization
- Package grouping with visual containers
- Relationship rendering (inheritance, composition, etc.)
- Drag-and-drop node positioning

✅ **Package Management**
- Visual package containers for multi-package projects
- Nested package support (e.g., `services.auth`)
- Resizable package containers with minimum size constraints
- Package header showing class count

✅ **Layout Persistence**
- Auto-save layout on diagram changes (2-second debounce)
- Manual save via "Save Layout" button
- Layouts stored in `~/.drait/layouts/`
- Deterministic class IDs for reliable save/load

✅ **Python Integration**
- Folder and file import
- Automatic exclusion of virtual environments (`.venv`, `venv`, etc.)
- Real-time parsing with JSON output

✅ **Interactive Editing**
- Move classes within and between packages
- Resize package containers
- Dynamic minimum size based on content
- Parent-child node relationships

## Project Structure

```
src/desktop/
├── electron/                    # Electron main process
│   ├── main.js                 # Main process with IPC handlers
│   └── preload.cjs             # Security bridge to renderer
├── renderer/                    # React application
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── DiagramCanvas.tsx      # Main diagram component
│   │   │   ├── ClassNode.tsx          # Class node component
│   │   │   ├── PackageNode.tsx        # Package container component
│   │   │   └── *.css                  # Component styles
│   │   ├── types/              # TypeScript definitions
│   │   │   ├── metamodel.ts           # DRAIT metamodel types
│   │   │   ├── electron.d.ts          # Electron API types
│   │   │   └── layout.ts              # Layout persistence types
│   │   ├── utils/              # Utility functions
│   │   │   └── metamodelToFlow.ts     # Convert metamodel to React Flow
│   │   ├── App.tsx             # Main App component
│   │   └── main.tsx            # React entry point
│   └── index.html              # HTML template
├── package.json                # Dependencies and scripts
├── vite.config.ts              # Vite configuration
└── tsconfig.json               # TypeScript configuration
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

### Electron Main Process (`electron/main.js`)

**Responsibilities:**
- Window management and lifecycle
- Native file/folder dialogs
- Python subprocess execution
- Layout file persistence

**IPC Handlers:**
- `dialog:openFile` - Open file picker
- `dialog:openFolder` - Open folder picker
- `python:parse` - Parse single Python file
- `python:parseFolder` - Parse Python folder/project
- `layout:save` - Save diagram layout to disk
- `layout:load` - Load saved diagram layout

### Renderer Process (React)

**Main Components:**

1. **DiagramCanvas** (`components/DiagramCanvas.tsx`)
   - React Flow integration
   - Layout loading on project open
   - Auto-save with debouncing
   - Node change validation for package constraints

2. **ClassNode** (`components/ClassNode.tsx`)
   - Renders individual class with attributes and methods
   - Shows stereotypes (abstract, dataclass)
   - Displays source file information

3. **PackageNode** (`components/PackageNode.tsx`)
   - Package container with header
   - Dynamic minimum size calculation
   - Resize validation based on child positions
   - Visual grouping of classes

4. **Metamodel Conversion** (`utils/metamodelToFlow.ts`)
   - Converts DRAIT metamodel to React Flow format
   - Multi-package layout algorithm
   - Package and class positioning
   - Relationship edge generation

### Python Backend

**Integration:**
- Uses `uv run drait-parse` with `--format json`
- Parser excludes common directories (`.venv`, `__pycache__`, etc.)
- Deterministic UUID generation for classes (uuid5 based on name + file)
- Nested package support with dot notation

### Layout Persistence

**Storage Location:** `~/.drait/layouts/`

**File Format:**
```json
{
  "version": "1.0",
  "projectPath": "/absolute/path/to/project",
  "savedAt": "2025-11-28T20:00:00.000Z",
  "nodes": [
    {
      "id": "package-name",
      "position": { "x": 50, "y": 50 },
      "dimensions": { "width": 800, "height": 600 }
    },
    {
      "id": "class-uuid",
      "position": { "x": 100, "y": 150 }
    }
  ]
}
```

**File Naming:** `{project-path-with-dashes}.layout.json`

**Example:** `/home/user/myproject` → `home-user-myproject.layout.json`

## Communication Flow

```
User Action
    ↓
React Component (DiagramCanvas, ClassNode, etc.)
    ↓
IPC via window.electron API
    ↓
Electron Main Process (main.js)
    ↓
Python Subprocess (uv run drait-parse)
    ↓
JSON Output
    ↓
Electron Main Process
    ↓
IPC Response
    ↓
React Component Updates State
    ↓
React Flow Re-renders Diagram
```

## Available Scripts

- `npm run dev` - Start development mode
- `npm run dev:vite` - Start only Vite dev server
- `npm run dev:electron` - Start only Electron (requires Vite running)
- `npm run build` - Build React app for production
- `npm run build:electron` - Package for distribution
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Key Implementation Details

### Deterministic Class IDs

Classes now have deterministic UUIDs based on their name and source file:

```python
# src/drait/metamodel.py
def generate_deterministic_uuid(name: str, namespace_str: str = "drait") -> UUID:
    return uuid5(NAMESPACE_DNS, f"{namespace_str}:{name}")

class Class:
    def __post_init__(self):
        source_file = self.metadata.get("source_file", "")
        namespace = f"{source_file}:{self.name}" if source_file else self.name
        self.id = generate_deterministic_uuid(namespace)
```

This ensures the same class always has the same ID across parser runs, enabling layout persistence.

### Package Resize Constraints

Package containers enforce minimum size based on child node positions:

```typescript
// Dynamic calculation in PackageNode.tsx
const { minWidth, minHeight } = useStore((state) => {
  const childNodes = state.nodes.filter(node => node.parentNode === id);
  const maxX = Math.max(...childNodes.map(node => node.position.x));
  const maxY = Math.max(...childNodes.map(node => node.position.y));
  return {
    minWidth: maxX + GRID_WIDTH + 5,
    minHeight: maxY + GRID_HEIGHT + 5
  };
});
```

### Virtual Environment Exclusion

The Python parser excludes common directories:

```python
# src/drait/parsers/python_parser.py
EXCLUDED_DIRS = {
    '.venv', 'venv', '__pycache__', '.git',
    'node_modules', '.tox', 'build', 'dist',
    '.eggs', '*.egg-info', '.pytest_cache',
    '.mypy_cache', '.ruff_cache'
}
```

## Current Status

✅ Electron + React setup
✅ TypeScript configuration
✅ Python subprocess bridge
✅ File/folder dialog integration
✅ React Flow diagram rendering
✅ Full Python parser integration
✅ Interactive diagram editing
✅ Package visualization and grouping
✅ Layout persistence (save/load)
✅ Deterministic class IDs
✅ Dynamic resize constraints
✅ Auto-save functionality
✅ Virtual environment exclusion

## Future Enhancements

- Export diagrams as images (PNG/SVG)
- Export to PlantUML format
- Code generation UI
- Filter and search functionality
- Theme customization
- Cross-package relationship visualization improvements
- Undo/redo support
- Keyboard shortcuts
- Toolbar with editing tools

## Troubleshooting

### Layout not persisting

Ensure the parser is generating deterministic IDs:
```bash
uv run drait-parse /path/to/project --format json | grep '"id"'
```

The IDs should be identical across multiple runs.

### Virtual environment being parsed

Check that excluded directories are working:
```bash
uv run drait-parse /path/to/project --stats
```

Should not show packages from `.venv` or `venv` directories.

### Changes not auto-saving

Check browser console for auto-save logs:
- "Layout saved successfully to: ..." should appear 2 seconds after changes
- Verify `~/.drait/layouts/` directory exists and is writable
