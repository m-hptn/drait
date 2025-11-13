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
 * Convert a Project to React Flow nodes and edges
 * For now, we'll just use the first package
 */
export function projectToFlow(project: Project): FlowData {
  if (project.packages.length === 0) {
    return { nodes: [], edges: [] };
  }

  // For now, render just the first package
  // In the future, we could support multiple packages with tabs or sections
  return packageToFlow(project.packages[0]);
}
