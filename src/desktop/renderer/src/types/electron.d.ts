/**
 * TypeScript definitions for Electron API exposed via preload script
 */

export interface ElectronAPI {
  dialog: {
    openFile: (filters?: FileFilter[]) => Promise<string | undefined>;
    saveFile: (defaultName?: string, filters?: FileFilter[]) => Promise<string | undefined>;
  };

  python: {
    parse: (filePath: string) => Promise<ParseResult>;
    generate: (metamodel: any) => Promise<GenerateResult>;
  };

  platform: string;
  isDev: boolean;
}

export interface FileFilter {
  name: string;
  extensions: string[];
}

export interface ParseResult {
  success: boolean;
  metamodel?: any;  // Project type from metamodel.ts
  output?: string;
  message?: string;
  error?: string;
}

export interface GenerateResult {
  success: boolean;
  code?: string;
  message?: string;
  error?: string;
}

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}

export {};
