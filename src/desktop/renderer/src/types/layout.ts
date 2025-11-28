/**
 * Layout persistence types for saving and loading diagram layouts
 */

export interface NodeLayout {
  id: string;
  position: {
    x: number;
    y: number;
  };
  // For package nodes, also store dimensions
  dimensions?: {
    width: number;
    height: number;
  };
}

export interface DiagramLayout {
  // Metadata
  version: string;
  projectPath: string; // Absolute path to the source folder
  savedAt: string; // ISO timestamp

  // Layout data
  nodes: NodeLayout[];

  // Viewport state (optional - for future enhancement)
  viewport?: {
    x: number;
    y: number;
    zoom: number;
  };
}

/**
 * Generate a layout file name from a project path
 */
export function getLayoutFileName(projectPath: string): string {
  // Convert path to a safe filename
  // e.g., "/home/user/project" -> "home-user-project.layout.json"
  return projectPath
    .replace(/^\//, '') // Remove leading slash
    .replace(/\//g, '-') // Replace slashes with hyphens
    .replace(/\s+/g, '_') // Replace spaces with underscores
    + '.layout.json';
}
