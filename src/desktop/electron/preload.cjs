/**
 * Electron Preload Script
 *
 * This script runs in the renderer process before the React app loads.
 * It exposes a safe API for the React app to communicate with Electron.
 *
 * Security: Uses contextBridge to expose only specific functions,
 * preventing the React app from accessing all of Node.js APIs.
 *
 * NOTE: Preload scripts must use CommonJS (require) because Electron
 * does not yet support ESM in preload context.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose safe API to renderer process (React app)
contextBridge.exposeInMainWorld('electron', {
  // File dialog operations
  dialog: {
    openFile: (filters) => ipcRenderer.invoke('dialog:openFile', filters),
    saveFile: (defaultName, filters) => ipcRenderer.invoke('dialog:saveFile', defaultName, filters)
  },

  // Python backend operations
  python: {
    /**
     * Parse a Python file and get metamodel JSON
     * @param {string} filePath - Path to Python file
     * @returns {Promise<Object>} Metamodel JSON
     */
    parse: (filePath) => ipcRenderer.invoke('python:parse', filePath),

    /**
     * Generate Python code from metamodel
     * @param {Object} metamodel - Metamodel JSON object
     * @returns {Promise<string>} Generated Python code
     */
    generate: (metamodel) => ipcRenderer.invoke('python:generate', metamodel)
  },

  // Platform information
  platform: process.platform,

  // Environment
  isDev: process.env.NODE_ENV === 'development'
});

// Log that preload script has loaded
console.log('Preload script loaded successfully');
