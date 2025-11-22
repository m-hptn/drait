import { Node, Edge, MarkerType } from 'reactflow';
import { Project, Package, Class, RelationshipType } from '../types/metamodel';

/**
 * Convert DRAIT metamodel to React Flow nodes and edges
 */

const GRID_WIDTH = 300;
const GRID_HEIGHT = 400;

export interface FlowData {
  nodes: Node[];
  edges: Edge[];
}

/**
 * Calculate auto-layout positions for classes
 */
function calculateLayout(classes: Class[]): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>();

  const columns = Math.ceil(Math.sqrt(classes.length));

  classes.forEach((cls, index) => {
    // Use stored position if available
    if (cls.position) {
      positions.set(cls.id, cls.position);
    } else {
      // Auto-layout in grid
      const col = index % columns;
      const row = Math.floor(index / columns);
      positions.set(cls.id, {
        x: col * GRID_WIDTH + 50,
        y: row * GRID_HEIGHT + 50
      });
    }
  });

  return positions;
}

/**
 * Get edge style and markers based on relationship type
 */
function getEdgeStyle(relType: RelationshipType) {
  switch (relType) {
    case RelationshipType.INHERITANCE:
      return {
        stroke: '#374151',
        strokeWidth: 2,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#374151'
        },
        style: { strokeDasharray: '0' }
      };

    case RelationshipType.REALIZATION:
      return {
        stroke: '#6b7280',
        strokeWidth: 2,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#6b7280'
        },
        style: { strokeDasharray: '5 5' }
      };

    case RelationshipType.COMPOSITION:
      return {
        stroke: '#111827',
        strokeWidth: 2,
        markerEnd: {
          type: MarkerType.Arrow,
          width: 20,
          height: 20,
          color: '#111827'
        },
        markerStart: {
          type: MarkerType.Arrow,
          width: 15,
          height: 15,
          color: '#111827'
        },
        style: { strokeDasharray: '0' }
      };

    case RelationshipType.AGGREGATION:
      return {
        stroke: '#374151',
        strokeWidth: 2,
        markerEnd: {
          type: MarkerType.Arrow,
          width: 20,
          height: 20,
          color: '#374151'
        },
        markerStart: {
          type: MarkerType.Arrow,
          width: 15,
          height: 15,
          color: '#374151'
        },
        style: { strokeDasharray: '0' }
      };

    case RelationshipType.DEPENDENCY:
      return {
        stroke: '#9ca3af',
        strokeWidth: 1.5,
        markerEnd: {
          type: MarkerType.Arrow,
          width: 15,
          height: 15,
          color: '#9ca3af'
        },
        style: { strokeDasharray: '5 5' }
      };

    case RelationshipType.ASSOCIATION:
    default:
      return {
        stroke: '#6b7280',
        strokeWidth: 2,
        markerEnd: {
          type: MarkerType.Arrow,
          width: 18,
          height: 18,
          color: '#6b7280'
        },
        style: { strokeDasharray: '0' }
      };
  }
}

/**
 * Convert a Package to React Flow nodes and edges
 */
export function packageToFlow(pkg: Package): FlowData {
  const positions = calculateLayout(pkg.classes);

  // Create nodes for each class
  const nodes: Node[] = pkg.classes.map((cls) => {
    const pos = positions.get(cls.id) || { x: 0, y: 0 };

    return {
      id: cls.id,
      type: 'classNode',
      position: pos,
      data: {
        classData: cls
      }
    };
  });

  // Create edges for each relationship
  const edges: Edge[] = pkg.relationships.map((rel) => {
    const edgeStyle = getEdgeStyle(rel.type);

    return {
      id: rel.id,
      source: rel.source_id,
      target: rel.target_id,
      type: 'smoothstep',
      animated: false,
      label: rel.source_role || rel.target_role || undefined,
      labelStyle: { fontSize: 10, fill: '#6b7280' },
      labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
      ...edgeStyle
    };
  });

  return { nodes, edges };
}

/**
 * Calculate layout for packages and their classes
 */
function calculatePackageLayout(packages: Package[]): {
  packagePositions: Map<string, { x: number; y: number; width: number; height: number }>;
  classPositions: Map<string, { x: number; y: number }>;
} {
  const packagePositions = new Map<string, { x: number; y: number; width: number; height: number }>();
  const classPositions = new Map<string, { x: number; y: number }>();

  const PACKAGE_PADDING = 60; // Space inside package for classes
  const PACKAGE_SPACING = 50; // Space between packages
  const PACKAGE_HEADER_HEIGHT = 50; // Height of package header

  let currentX = 50;
  let currentY = 50;
  let maxHeightInRow = 0;
  const MAX_ROW_WIDTH = 1400; // Maximum width before wrapping to next row

  packages.forEach((pkg) => {
    const classCount = pkg.classes.length;
    if (classCount === 0) return;

    // Calculate grid dimensions for classes in this package
    const columns = Math.ceil(Math.sqrt(classCount));
    const rows = Math.ceil(classCount / columns);

    // Calculate package dimensions
    const packageWidth = Math.max(400, columns * GRID_WIDTH + PACKAGE_PADDING * 2);
    const packageHeight = PACKAGE_HEADER_HEIGHT + rows * GRID_HEIGHT + PACKAGE_PADDING * 2;

    // Check if we need to wrap to next row
    if (currentX + packageWidth > MAX_ROW_WIDTH && currentX > 50) {
      currentX = 50;
      currentY += maxHeightInRow + PACKAGE_SPACING;
      maxHeightInRow = 0;
    }

    // Store package position
    packagePositions.set(pkg.name, {
      x: currentX,
      y: currentY,
      width: packageWidth,
      height: packageHeight
    });

    // Calculate positions for classes within this package
    // IMPORTANT: Positions must be relative to package position for React Flow parent nodes
    pkg.classes.forEach((cls, index) => {
      const col = index % columns;
      const row = Math.floor(index / columns);

      classPositions.set(cls.id, {
        x: PACKAGE_PADDING + col * GRID_WIDTH,
        y: PACKAGE_HEADER_HEIGHT + PACKAGE_PADDING + row * GRID_HEIGHT
      });
    });

    // Move to next position
    currentX += packageWidth + PACKAGE_SPACING;
    maxHeightInRow = Math.max(maxHeightInRow, packageHeight);
  });

  return { packagePositions, classPositions };
}

/**
 * Convert a Project to React Flow nodes and edges
 * Supports multiple packages with visual grouping
 */
export function projectToFlow(project: Project): FlowData {
  if (project.packages.length === 0) {
    return { nodes: [], edges: [] };
  }

  // If only one package, use simple layout without package containers
  if (project.packages.length === 1) {
    return packageToFlow(project.packages[0]);
  }

  // Multiple packages - create package containers and position classes within them
  const { packagePositions, classPositions } = calculatePackageLayout(project.packages);

  const nodes: Node[] = [];
  const edges: Edge[] = [];

  // Create package background nodes
  project.packages.forEach((pkg) => {
    const pkgPos = packagePositions.get(pkg.name);
    if (!pkgPos) return;

    // Calculate actual minimum dimensions needed for classes
    const classPositionsInPackage = pkg.classes.map(cls => classPositions.get(cls.id)!);
    const maxClassX = Math.max(...classPositionsInPackage.map(pos => pos.x));
    const maxClassY = Math.max(...classPositionsInPackage.map(pos => pos.y));
    const minWidth = maxClassX + GRID_WIDTH + PACKAGE_PADDING;
    const minHeight = maxClassY + GRID_HEIGHT + PACKAGE_PADDING;

    // Add package container node
    nodes.push({
      id: `package-${pkg.name || 'root'}`,
      type: 'packageNode',
      position: { x: pkgPos.x, y: pkgPos.y },
      data: {
        packageName: pkg.name,
        classCount: pkg.classes.length,
        minWidth: minWidth,
        minHeight: minHeight
      },
      style: {
        width: pkgPos.width,
        height: pkgPos.height,
        zIndex: -1
      },
      draggable: true,
      selectable: true
    });

    // Add class nodes
    pkg.classes.forEach((cls) => {
      const pos = classPositions.get(cls.id);
      if (!pos) return;

      nodes.push({
        id: cls.id,
        type: 'classNode',
        position: pos,
        data: {
          classData: cls
        },
        parentNode: `package-${pkg.name || 'root'}`,
        extent: 'parent' as const,
        draggable: true
      });
    });

    // Add edges for this package's relationships
    pkg.relationships.forEach((rel) => {
      const edgeStyle = getEdgeStyle(rel.type);

      edges.push({
        id: rel.id,
        source: rel.source_id,
        target: rel.target_id,
        type: 'smoothstep',
        animated: false,
        label: rel.source_role || rel.target_role || undefined,
        labelStyle: { fontSize: 10, fill: '#6b7280' },
        labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
        ...edgeStyle
      });
    });
  });

  return { nodes, edges };
}
