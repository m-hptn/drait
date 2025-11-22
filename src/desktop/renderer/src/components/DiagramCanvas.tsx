import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  BackgroundVariant,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';

import ClassNode from './ClassNode';
import PackageNode from './PackageNode';
import './ClassNode.css';
import './PackageNode.css';
import { Project } from '../types/metamodel';
import { projectToFlow } from '../utils/metamodelToFlow';

interface DiagramCanvasProps {
  project: Project;
}

const nodeTypes = {
  classNode: ClassNode,
  packageNode: PackageNode
};

export default function DiagramCanvas({ project }: DiagramCanvasProps) {
  // Convert metamodel to React Flow format
  const initialFlow = useMemo(() => projectToFlow(project), [project]);

  const [nodes, , onNodesChange] = useNodesState(initialFlow.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialFlow.edges);

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
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
        </Panel>
      </ReactFlow>
    </div>
  );
}
