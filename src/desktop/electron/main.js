/**
 * Electron Main Process
 *
 * Handles window management, native menus, file dialogs,
 * and communication with Python backend.
 */

// Electron ESM workaround - use default import
import electron from 'electron';
const { app, BrowserWindow, ipcMain, dialog } = electron;

import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let mainWindow = null;
let pythonProcess = null;

// Development mode check
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

/**
 * Create the main application window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    },
    title: 'DRAI - UML2 Class Diagram Editor',
    backgroundColor: '#1f2937', // Dark gray background
    show: false // Don't show until ready
  });

  // Load the app
  if (isDev) {
    // Development: load from Vite dev server
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // Production: load from built files
    mainWindow.loadFile(path.join(__dirname, '../renderer/dist/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Start Python backend process
 */
function startPythonBackend() {
  // TODO: Implement Python subprocess
  // For now, we'll use the installed drait package via CLI
  console.log('Python backend initialization: Using installed drait package');
}

/**
 * Stop Python backend process
 */
function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}

// ============================================================================
// IPC Handlers - Communication between Renderer and Main
// ============================================================================

/**
 * Handle file open dialog
 */
ipcMain.handle('dialog:openFile', async (_event, filters) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: filters || [
      { name: 'Python Files', extensions: ['py'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  return result.filePaths[0]; // Return first selected file
});

/**
 * Handle folder open dialog
 */
ipcMain.handle('dialog:openFolder', async (_event) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });

  if (result.canceled) {
    return undefined;
  }

  console.log('Selected folder:', result.filePaths[0]);
  return result.filePaths[0]; // Return selected folder
});

/**
 * Handle save file dialog
 */
ipcMain.handle('dialog:saveFile', async (_event, defaultName, filters) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: filters || [
      { name: 'Python Files', extensions: ['py'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  return result.filePath;
});

/**
 * Parse Python file and return metamodel JSON
 */
ipcMain.handle('python:parse', async (_event, filePath) => {
  return new Promise((resolve, reject) => {
    // Use drait-parse CLI with JSON output
    const pythonCmd = spawn('uv', ['run', 'drait-parse', filePath, '--format', 'json'], {
      cwd: path.join(__dirname, '../../../') // Project root
    });

    let output = '';
    let errorOutput = '';

    pythonCmd.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonCmd.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonCmd.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python parse failed: ${errorOutput}`));
      } else {
        try {
          // Parse JSON output from drait-parse
          const metamodel = JSON.parse(output);
          resolve({
            success: true,
            metamodel: metamodel,
            message: 'Parsed successfully'
          });
        } catch (error) {
          reject(new Error(`Failed to parse JSON: ${error.message}\nOutput: ${output}`));
        }
      }
    });
  });
});

/**
 * Parse Python folder and return merged metamodel JSON
 */
ipcMain.handle('python:parseFolder', async (_event, folderPath) => {
  console.log('Parsing folder:', folderPath);

  return new Promise((resolve, reject) => {
    // Use drait-parse CLI with folder path and JSON output
    const pythonCmd = spawn('uv', ['run', 'drait-parse', folderPath, '--format', 'json'], {
      cwd: path.join(__dirname, '../../../') // Project root
    });

    let output = '';
    let errorOutput = '';

    pythonCmd.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonCmd.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error('Python stderr:', data.toString());
    });

    pythonCmd.on('close', (code) => {
      console.log('Python parse exit code:', code);
      if (code !== 0) {
        console.error('Parse failed:', errorOutput);
        reject(new Error(`Python parse failed: ${errorOutput}`));
      } else {
        try {
          // Parse JSON output from drait-parse
          const metamodel = JSON.parse(output);
          console.log('Successfully parsed folder, found', metamodel.packages[0].classes.length, 'classes');
          resolve({
            success: true,
            metamodel: metamodel,
            message: 'Parsed successfully'
          });
        } catch (error) {
          console.error('JSON parse failed:', error);
          reject(new Error(`Failed to parse JSON: ${error.message}\nOutput: ${output}`));
        }
      }
    });
  });
});

/**
 * Generate Python code from metamodel JSON
 */
ipcMain.handle('python:generate', async (_event, _metamodelJson) => {
  // TODO: Implement code generation
  // Will call Python generator when it's built
  return {
    success: true,
    code: '# Generated Python code will appear here',
    message: 'Code generator not yet implemented'
  };
});

/**
 * Save diagram layout to disk
 */
ipcMain.handle('layout:save', async (_event, projectPath, layoutData) => {
  const fs = await import('fs/promises');
  const os = await import('os');

  try {
    // Create layouts directory in user's home directory
    const layoutsDir = path.join(os.homedir(), '.drait', 'layouts');
    await fs.mkdir(layoutsDir, { recursive: true });

    // Generate filename from project path
    const fileName = projectPath
      .replace(/^\//, '')
      .replace(/\//g, '-')
      .replace(/\s+/g, '_')
      + '.layout.json';

    const layoutPath = path.join(layoutsDir, fileName);

    // Write layout file
    await fs.writeFile(layoutPath, JSON.stringify(layoutData, null, 2), 'utf-8');

    console.log('Layout saved to:', layoutPath);
    return {
      success: true,
      path: layoutPath
    };
  } catch (error) {
    console.error('Failed to save layout:', error);
    return {
      success: false,
      error: error.message
    };
  }
});

/**
 * Load diagram layout from disk
 */
ipcMain.handle('layout:load', async (_event, projectPath) => {
  const fs = await import('fs/promises');
  const os = await import('os');

  try {
    // Generate filename from project path
    const fileName = projectPath
      .replace(/^\//, '')
      .replace(/\//g, '-')
      .replace(/\s+/g, '_')
      + '.layout.json';

    const layoutPath = path.join(os.homedir(), '.drait', 'layouts', fileName);

    // Read layout file
    const data = await fs.readFile(layoutPath, 'utf-8');
    const layoutData = JSON.parse(data);

    console.log('Layout loaded from:', layoutPath);
    return {
      success: true,
      layout: layoutData
    };
  } catch (error) {
    // File not found is expected for new projects
    if (error.code === 'ENOENT') {
      return {
        success: false,
        error: 'No saved layout found'
      };
    }
    console.error('Failed to load layout:', error);
    return {
      success: false,
      error: error.message
    };
  }
});

// ============================================================================
// App Lifecycle
// ============================================================================

app.whenReady().then(() => {
  startPythonBackend();
  createWindow();

  // macOS: Re-create window when dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopPythonBackend();
    app.quit();
  }
});

// Cleanup before quit
app.on('before-quit', () => {
  stopPythonBackend();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  stopPythonBackend();
});
