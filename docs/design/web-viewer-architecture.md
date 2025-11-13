# DRAIT Diagram Viewer Architecture

## Overview

A UML class diagram viewer and editor that allows users to:
1. **View** existing diagrams (from Python code or JSON models)
2. **Edit** diagrams interactively (drag-drop, add/remove elements)
3. **Generate** Python code from diagrams
4. Enable real-time bidirectional synchronization (future)

## Deployment Scenarios

As defined in the arc42 architecture documentation, DRAIT supports two deployment scenarios:

### Scenario 1: Desktop Application (Primary Focus) ⭐

**Target Users**: Individual developers and small teams
**Use Case**: Local development, offline work, file-based workflows

**Technology Stack**:
- **Runtime**: Electron (cross-platform desktop)
- **Frontend**: React 18+ with TypeScript
- **Diagram Library**: [React Flow](https://reactflow.dev/)
- **State Management**: Zustand (lightweight, modern)
- **Styling**: Tailwind CSS + Headless UI
- **Build**: Vite (fast dev server and build)
- **Packaging**: electron-builder (.exe, .dmg, .AppImage)
- **Backend**: Python (subprocess or embedded server)

**Benefits**:
- ✅ Native desktop app experience
- ✅ Direct file system access (save diagrams, generate code)
- ✅ Works offline
- ✅ Better performance (no network latency)
- ✅ Single executable distribution
- ✅ Native OS integration (menus, file dialogs, notifications)
- ✅ No server infrastructure needed

**Architecture**: See "Desktop Application Architecture" section below

### Scenario 2: Web-Based Collaborative Tool (Future)

**Target Users**: Distributed teams, enterprise users
**Use Case**: Real-time collaboration, cloud storage, browser-based access

**Technology Stack**:
- **Frontend**: React + TypeScript (same as desktop)
- **Backend**: Python Flask/FastAPI + WebSocket support
- **Database**: PostgreSQL (for multi-user data)
- **Authentication**: OAuth2 / JWT
- **Collaboration**: Operational Transformation or CRDT for real-time sync
- **Hosting**: Docker containers, cloud deployment

**Benefits**:
- ✅ Real-time collaboration (multiple users editing same diagram)
- ✅ No installation required
- ✅ Centralized storage and backup
- ✅ Version history and branching
- ✅ Team permissions and access control
- ✅ Browser-based (works anywhere)

**Architecture**: See "Web Application Architecture" section below

## Current Focus: Desktop Application First

We're starting with **Scenario 1 (Desktop)** because:
1. Simpler deployment (no server infrastructure)
2. Faster to implement and iterate
3. Meets core use case (individual developers)
4. React components can be reused for web version later
5. Aligns with arc42 architecture decision

The web-based collaborative version remains documented for future implementation.

---

## Desktop Application Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Application                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │          Main Process (Node.js)                     │    │
│  │  - Window management                                │    │
│  │  - Native menus & dialogs                          │    │
│  │  - Python subprocess management                     │    │
│  │  - IPC communication                                │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│           ┌───────────────┴──────────────┐                 │
│           │                              │                  │
│           ▼                              ▼                  │
│  ┌─────────────────┐          ┌──────────────────────┐    │
│  │ Renderer        │          │ Python Backend       │    │
│  │ (React App)     │◄────────►│ (Subprocess)         │    │
│  │                 │   IPC    │                      │    │
│  │ Components:     │          │ - Parser             │    │
│  │ - DiagramCanvas │          │ - Generator          │    │
│  │ - Toolbar       │          │ - Metamodel          │    │
│  │ - PropertyPanel │          │ - Exporters          │    │
│  │ - MenuBar       │          │                      │    │
│  │                 │          │ (Existing DRAIT)     │    │
│  │ React Flow      │          └──────────────────────┘    │
│  └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flow

**Electron Main ↔ Renderer (React)**:
- Via Electron IPC (Inter-Process Communication)
- Renderer sends commands: `ipcRenderer.invoke('parse-python', filepath)`
- Main responds with data: `ipcMain.handle('parse-python', async (event, filepath) => {...})`

**Electron Main ↔ Python Backend**:
- Option A: Spawn Python subprocess, communicate via stdin/stdout (JSON)
- Option B: Python runs embedded HTTP server, Electron calls localhost API
- Option C: Use `python-shell` npm package (recommended)

**Example Flow - Parse Python File**:
1. User clicks "Import Python File" → File dialog opens (Main process)
2. User selects `mycode.py`
3. Main process sends file path to Python subprocess
4. Python parses file using existing `PythonParser`
5. Python returns metamodel as JSON
6. Main forwards JSON to Renderer
7. React app renders diagram using React Flow

### Desktop-Specific Architecture

```
┌─────────────────────────────────────────────────┐
│              Web Browser (Client)                │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │         Diagram Editor UI                 │  │
│  │  ┌────────────┐      ┌────────────────┐  │  │
│  │  │  Canvas    │      │  Toolbar       │  │  │
│  │  │  (JointJS) │      │  - Add Class   │  │  │
│  │  │            │      │  - Add Rel.    │  │  │
│  │  │  ┌──────┐  │      │  - Properties  │  │  │
│  │  │  │Class │  │      └────────────────┘  │  │
│  │  │  └──────┘  │                           │  │
│  │  │     │      │      ┌────────────────┐  │  │
│  │  │     ↓      │      │  Property      │  │  │
│  │  │  ┌──────┐  │      │  Panel         │  │  │
│  │  │  │Class2│  │      │  - Edit attrs  │  │  │
│  │  │  └──────┘  │      │  - Edit meths  │  │  │
│  │  └────────────┘      └────────────────┘  │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  JavaScript/TypeScript Application               │
│  - Diagram manipulation                          │
│  - UI interactions                               │
│  - API calls                                     │
└─────────────────────────────────────────────────┘
                      │
                      │ HTTP/REST API
                      │ JSON
                      ↓
┌─────────────────────────────────────────────────┐
│           Python Backend (Flask/FastAPI)         │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │         API Endpoints                     │  │
│  │  - GET  /api/diagram/:id                 │  │
│  │  - POST /api/diagram (save)              │  │
│  │  - POST /api/generate-code               │  │
│  │  - POST /api/parse-code                  │  │
│  └──────────────────────────────────────────┘  │
│                      │                           │
│                      ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │      DRAIT Core (Existing)               │  │
│  │  - Metamodel                             │  │
│  │  - Python Parser                         │  │
│  │  - Code Generator (to be built)         │  │
│  │  - PlantUML Exporter                     │  │
│  └──────────────────────────────────────────┘  │
│                      │                           │
│                      ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │      Storage (Future)                     │  │
│  │  - File system (JSON files)              │  │
│  │  - SQLite (optional)                     │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Component Breakdown

### Frontend Components

#### 1. **DiagramCanvas**
- Renders UML diagram using JointJS/React Flow
- Handles zoom, pan, select
- Displays classes, relationships
- **Responsibilities**:
  - Render metamodel as visual elements
  - Handle user interactions (click, drag)
  - Emit events (element selected, moved, etc.)

#### 2. **Toolbar**
- Add new elements (class, interface, enum)
- Add relationships (inheritance, composition, etc.)
- Layout controls (auto-arrange, zoom)
- **Actions**:
  - Create new class
  - Create new relationship
  - Delete selected
  - Undo/redo

#### 3. **PropertyPanel**
- Edit selected element properties
- Class: name, visibility, abstract
- Attribute: name, type, visibility, default
- Method: name, return type, parameters
- **Form fields** for editing metamodel properties

#### 4. **MenuBar**
- File: New, Open, Save, Export
- Edit: Undo, Redo, Select All
- Generate: Generate Python Code
- Import: Parse Python File
- **Actions**: Save to JSON, load from JSON, export diagram

#### 5. **CodePreview** (Optional)
- Show generated Python code
- Syntax highlighting
- Copy to clipboard
- Download as .py file

### Backend API Endpoints

#### Diagram Management
```python
GET    /api/diagrams          # List all saved diagrams
GET    /api/diagram/:id       # Get diagram by ID (as JSON metamodel)
POST   /api/diagram           # Save/update diagram
DELETE /api/diagram/:id       # Delete diagram
```

#### Code Operations
```python
POST   /api/parse-python      # Upload .py file → return metamodel JSON
POST   /api/generate-code     # Send metamodel JSON → return Python code
POST   /api/export-plantuml   # Send metamodel JSON → return PlantUML
```

#### Validation
```python
POST   /api/validate-diagram  # Validate metamodel consistency
```

## Data Flow

### Scenario 1: User Draws New Diagram → Generate Code

```
1. User clicks "Add Class" in toolbar
   → Frontend creates new Class in local state

2. User edits class properties in PropertyPanel
   → Frontend updates Class object

3. User adds methods/attributes
   → Frontend updates Class.methods, Class.attributes

4. User clicks "Generate Code"
   → Frontend sends metamodel JSON to POST /api/generate-code

5. Backend receives metamodel
   → Deserialize JSON to DRAIT metamodel objects
   → Use Code Generator to create Python code
   → Return Python code as string

6. Frontend displays code in CodePreview
   → User can copy or download
```

### Scenario 2: User Uploads Python Code → View Diagram

```
1. User uploads .py file via "Import Python" button
   → Frontend sends file to POST /api/parse-python

2. Backend receives file
   → Use existing PythonParser
   → Convert to metamodel
   → Serialize to JSON
   → Return JSON

3. Frontend receives metamodel JSON
   → Render diagram on canvas
   → User can now edit the diagram
```

### Scenario 3: Round-Trip (Code → Diagram → Edit → Code)

```
1. Upload Python file → Diagram displayed (Scenario 2)
2. User edits diagram (add new method)
3. User clicks "Generate Code"
4. Backend generates updated Python code
5. User downloads new code
```

## File Structure

```
drait/
├── src/
│   ├── drait/              # Existing Python backend
│   │   ├── metamodel.py
│   │   ├── parsers/
│   │   ├── exporters/
│   │   └── generators/     # NEW: Code generator
│   │       └── python_generator.py
│   └── web/                # NEW: Web application
│       ├── backend/
│       │   ├── app.py      # Flask application
│       │   ├── api/
│       │   │   ├── diagram.py
│       │   │   ├── codegen.py
│       │   │   └── parser.py
│       │   └── models/
│       │       └── storage.py
│       └── frontend/
│           ├── index.html
│           ├── src/
│           │   ├── main.ts
│           │   ├── diagram/
│           │   │   ├── canvas.ts
│           │   │   ├── shapes.ts    # Class/Relationship shapes
│           │   │   └── serializer.ts # Metamodel ↔ JointJS
│           │   ├── components/
│           │   │   ├── toolbar.ts
│           │   │   ├── property-panel.ts
│           │   │   └── menu-bar.ts
│           │   ├── api/
│           │   │   └── client.ts    # API calls
│           │   └── types/
│           │       └── metamodel.ts # TypeScript types
│           ├── styles/
│           │   └── main.css
│           └── package.json
├── examples/
└── tests/
```

## Development Phases

### Phase 1: Basic Viewer (Read-Only) ✅ Start Here
**Goal**: Display existing diagrams from Python code

- [ ] Set up Flask backend with API endpoints
- [ ] Create basic HTML/CSS structure
- [ ] Integrate JointJS for diagram rendering
- [ ] Implement metamodel → JointJS conversion
- [ ] Add "Import Python File" functionality
- [ ] Display classes with attributes/methods
- [ ] Display relationships

**Deliverable**: Can parse Python file and view as UML diagram

### Phase 2: Interactive Editor
**Goal**: Edit diagrams interactively

- [ ] Add toolbar for creating elements
- [ ] Enable drag-and-drop class creation
- [ ] Implement property panel
- [ ] Add/edit/delete classes
- [ ] Add/edit/delete attributes
- [ ] Add/edit/delete methods
- [ ] Create relationships by dragging
- [ ] Undo/redo functionality

**Deliverable**: Can create and edit diagrams visually

### Phase 3: Code Generation
**Goal**: Generate Python code from diagrams

- [ ] Build Python code generator
- [ ] Implement template-based generation
- [ ] Handle type annotations
- [ ] Generate decorators (@dataclass, @property)
- [ ] Add code preview panel
- [ ] Download generated code

**Deliverable**: Can generate Python code from diagrams

### Phase 4: Persistence & Polish
**Goal**: Save/load diagrams, improve UX

- [ ] Save diagrams to JSON files
- [ ] Load saved diagrams
- [ ] Auto-layout algorithm
- [ ] Export to PNG/SVG
- [ ] Keyboard shortcuts
- [ ] Responsive design
- [ ] Error handling & validation

**Deliverable**: Production-ready diagram editor

### Phase 5: Advanced Features (Future)
- Real-time collaboration
- Version control integration
- Bidirectional sync (watch Python files)
- Multiple diagram types (sequence, state)
- Plugin system

## Technology Choices for MVP

### Diagram Library: JointJS vs Mermaid vs React Flow

**JointJS** (Recommended for MVP)
- ✅ Mature, stable
- ✅ Built for UML diagrams
- ✅ Interactive editing out of the box
- ✅ Good documentation
- ❌ Not free for commercial (but open-source for now)

**Mermaid**
- ✅ Simple, text-based
- ✅ Great for static diagrams
- ❌ Limited interactivity
- ❌ Not ideal for editing

**React Flow**
- ✅ Modern, React-based
- ✅ Very flexible
- ✅ Active development
- ❌ Requires React setup
- ❌ More work to build UML-specific features

**Decision**: Start with **JointJS** for quick MVP, can migrate later

### Backend: Flask vs FastAPI

**Flask**
- ✅ Simpler, fewer dependencies
- ✅ Good for small API
- ✅ Easy to learn

**FastAPI**
- ✅ Modern, async support
- ✅ Auto-generated OpenAPI docs
- ✅ Type hints
- ❌ Slightly more complex

**Decision**: Start with **Flask** for simplicity

## Next Steps

1. ✅ Create feature branch
2. ✅ Design architecture (this document)
3. ⏭️ Set up basic Flask backend
4. ⏭️ Create minimal HTML/JS frontend
5. ⏭️ Integrate JointJS
6. ⏭️ Implement first API endpoint (parse Python → JSON)
7. ⏭️ Render diagram from JSON

**Let's start with Phase 1: Basic Viewer!**
