# Migration to ESM (ECMAScript Modules)

## Context
The CJS (CommonJS) build of Vite's Node API was deprecated and will be removed in Vite 6. We migrated the project to use ESM to follow current best practices and avoid future compatibility issues.

## Changes Made

### 1. Package Configuration
**File**: `package.json`
- Added `"type": "module"` to specify that all `.js` files should be treated as ESM modules

### 2. Config Files Renamed to .cjs
**Files**:
- `postcss.config.js` → `postcss.config.cjs`
- `tailwind.config.js` → `tailwind.config.cjs`
- `electron/preload.js` → `electron/preload.cjs`

**Reason**: These files use CommonJS (`module.exports` or `require()`) syntax, so we explicitly marked them with `.cjs` extension to indicate they're CommonJS modules in an ESM project.

### 3. Electron Main Process
**File**: `electron/main.js`

**Before (CommonJS)**:
```javascript
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
```

**After (ESM)**:
```javascript
import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

**Note**: In ESM, `__dirname` and `__filename` are not automatically available, so we recreate them from `import.meta.url`.

### 4. Electron Preload Script
**File**: `electron/preload.js` → `electron/preload.cjs`

**IMPORTANT**: Preload scripts **must remain in CommonJS** format because Electron does not support ESM in the preload context yet.

**Action taken**:
- Kept the `require()` syntax in preload script
- Renamed file to `.cjs` extension to explicitly mark it as CommonJS in an ESM project
- Updated reference in `main.js` to point to `preload.cjs`

```javascript
// preload.cjs - MUST use CommonJS
const { contextBridge, ipcRenderer } = require('electron');
```

## Verification
All builds now complete without the CJS deprecation warning:

```bash
npm run build          # ✅ No CJS warning
npm run dev:vite       # ✅ No CJS warning
```

## Benefits
1. **Future-proof**: Compatible with Vite 6 and beyond
2. **Modern JavaScript**: Uses current ECMAScript standards
3. **Better tree-shaking**: ESM enables better optimization by bundlers
4. **Cleaner syntax**: `import`/`export` is more explicit than `require`/`module.exports`

## References
- [Vite Migration Guide](https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated)
- [Node.js ESM Documentation](https://nodejs.org/api/esm.html)
