import { useCallback, useMemo, useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  BackgroundVariant,
  Panel,
  Node
} from 'reactflow';
import 'reactflow/dist/style.css';

import ClassNode from './ClassNode';
import PackageNode from './PackageNode';
import './ClassNode.css';
import './PackageNode.css';
import { Project } from '../types/metamodel';
import { projectToFlow } from '../utils/metamodelToFlow';
import { DiagramLayout } from '../types/layout';

interface DiagramCanvasProps {
  project: Project;
  projectPath: string;
}

const nodeTypes = {
  classNode: ClassNode,
  packageNode: PackageNode
};

export default function DiagramCanvas({ project, projectPath }: DiagramCanvasProps) {
  const [layoutLoaded, setLayoutLoaded] = useState(false);

  // Convert metamodel to React Flow format
  const initialFlow = useMemo(() => {
    console.log('DiagramCanvas: Converting project to flow', {
      projectName: project.name,
      packageCount: project.packages.length,
      packages: project.packages.map(p => ({ name: p.name, classCount: p.classes.length }))
    });
    const flow = projectToFlow(project);
    console.log('DiagramCanvas: Flow generated', {
      nodeCount: flow.nodes.length,
      edgeCount: flow.edges.length,
      nodes: flow.nodes.map(n => ({ id: n.id, type: n.type, position: n.position }))
    });
    return flow;
  }, [project]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialFlow.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialFlow.edges);

  // Load saved layout on mount
  useEffect(() => {
    const loadLayout = async () => {
      if (!projectPath || layoutLoaded || nodes.length === 0) return;

      console.log('Loading layout for project:', projectPath);
      console.log('Current nodes count:', nodes.length);

      try {
        const result = await window.electron.layout.load(projectPath);
        if (result.success && result.layout) {
          const savedLayout = result.layout as DiagramLayout;
          console.log('Loaded layout with', savedLayout.nodes.length, 'nodes');

          // Apply saved positions and dimensions to nodes
          setNodes((currentNodes) => {
            return currentNodes.map((node) => {
              const savedNode = savedLayout.nodes.find((n) => n.id === node.id);
              if (savedNode) {
                console.log(`Restoring position for ${node.id}:`, savedNode.position);
                return {
                  ...node,
                  position: savedNode.position,
                  ...(savedNode.dimensions && {
                    style: {
                      ...node.style,
                      width: savedNode.dimensions.width,
                      height: savedNode.dimensions.height,
                    },
                  }),
                };
              }
              return node;
            });
          });
        } else {
          console.log('No saved layout found, using default layout');
        }
        // Mark as loaded regardless of whether we found a saved layout
        setLayoutLoaded(true);
      } catch (error) {
        console.error('Failed to load layout:', error);
        setLayoutLoaded(true); // Still mark as loaded to enable auto-save
      }
    };

    loadLayout();
  }, [projectPath, setNodes, layoutLoaded, nodes.length]);

  // Save layout function
  const saveLayout = useCallback(async () => {
    if (!projectPath) return;

    try {
      const layoutData: DiagramLayout = {
        version: '1.0',
        projectPath,
        savedAt: new Date().toISOString(),
        nodes: nodes.map((node) => ({
          id: node.id,
          position: node.position,
          ...(node.style?.width &&
            node.style?.height && {
              dimensions: {
                width: node.style.width as number,
                height: node.style.height as number,
              },
            }),
        })),
      };

      const result = await window.electron.layout.save(projectPath, layoutData);
      if (result.success) {
        console.log('Layout saved successfully to:', result.path);
      }
    } catch (error) {
      console.error('Failed to save layout:', error);
    }
  }, [projectPath, nodes]);

  // Auto-save layout after node changes (with debounce)
  useEffect(() => {
    if (!layoutLoaded) return; // Don't auto-save until initial layout is loaded

    const timeoutId = setTimeout(() => {
      saveLayout();
    }, 2000); // Save 2 seconds after last change

    return () => clearTimeout(timeoutId);
  }, [nodes, saveLayout, layoutLoaded]);

  // Custom nodes change handler that enforces minimum size constraints for package nodes
  const handleNodesChange = useCallback(
    (changes: any[]) => {
      const validatedChanges = changes.map((change) => {
        // Check if this is a dimension change for a package node
        if (change.type === 'dimensions' && change.dimensions) {
          const node = nodes.find((n) => n.id === change.id);
          if (node && node.type === 'packageNode') {
            // Calculate minimum dimensions based on child positions
            const childNodes = nodes.filter((n) => n.parentNode === change.id);
            if (childNodes.length > 0) {
              const maxX = Math.max(...childNodes.map((n) => n.position.x));
              const maxY = Math.max(...childNodes.map((n) => n.position.y));
              const minWidth = maxX + 300 + 5; // GRID_WIDTH + minimal margin
              const minHeight = maxY + 400 + 5; // GRID_HEIGHT + minimal margin

              // Enforce minimum dimensions
              return {
                ...change,
                dimensions: {
                  ...change.dimensions,
                  width: Math.max(change.dimensions.width, minWidth),
                  height: Math.max(change.dimensions.height, minHeight),
                },
              };
            }
          }
        }
        return change;
      });
      onNodesChange(validatedChanges);
    },
    [nodes, onNodesChange]
  );

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#e5e7eb" />
        <Controls />
        <MiniMap
          nodeColor={() => '#3b82f6'}
          nodeStrokeWidth={3}
          zoomable
          pannable
        />
        <Panel position="top-left" className="diagram-info">
          <div style={{
            background: 'white',
            padding: '8px 12px',
            borderRadius: '4px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            fontSize: '12px',
            color: '#374151'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
              <div>
                <strong>{project.name}</strong>
                {project.packages.length > 0 && (
                  <>
                    <br />
                    <span style={{ color: '#6b7280' }}>
                      {project.packages.length} package{project.packages.length !== 1 ? 's' : ''},{' '}
                      {project.packages.reduce((sum, pkg) => sum + pkg.classes.length, 0)} classes,{' '}
                      {project.packages.reduce((sum, pkg) => sum + pkg.relationships.length, 0)} relationships
                    </span>
                  </>
                )}
              </div>
              <button
                onClick={saveLayout}
                style={{
                  padding: '4px 8px',
                  fontSize: '11px',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '3px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
                title="Save current layout"
              >
                Save Layout
              </button>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
