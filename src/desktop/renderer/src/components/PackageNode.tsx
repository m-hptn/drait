import { memo, useCallback } from 'react';
import { NodeResizer, useStore, NodeProps, NodeResizeControl } from 'reactflow';
import './PackageNode.css';

interface PackageNodeData {
  packageName: string;
  classCount: number;
  minWidth: number;
  minHeight: number;
}

const GRID_WIDTH = 300;
const GRID_HEIGHT = 400;
const PACKAGE_PADDING = 60;
const PACKAGE_HEADER_HEIGHT = 50;

function PackageNode({ id, data, selected }: NodeProps<PackageNodeData>) {
  const { packageName, classCount } = data;

  // Get child nodes and calculate dynamic minimum size
  const { minWidth, minHeight } = useStore((state) => {
    if (!state.nodes) {
      return { minWidth: 400, minHeight: 200 };
    }

    const childNodes = state.nodes.filter(node => node.parentNode === id);

    if (childNodes.length === 0) {
      return { minWidth: 400, minHeight: 200 };
    }

    // Find the maximum x and y positions of child nodes
    const maxX = Math.max(...childNodes.map(node => node.position.x));
    const maxY = Math.max(...childNodes.map(node => node.position.y));

    // Calculate minimum dimensions to contain all children
    // Minimal margin - just enough to see the container edge
    const calculatedMinWidth = maxX + GRID_WIDTH + 5;
    const calculatedMinHeight = maxY + GRID_HEIGHT + 5;

    return {
      minWidth: calculatedMinWidth,
      minHeight: calculatedMinHeight
    };
  });

  // Display name: use "(root)" for empty package names
  const displayName = packageName || '(root)';

  // Validate resize to ensure it doesn't go below minimum
  const shouldResize = useCallback(
    (event: any, params: any) => {
      // Only allow resize if new dimensions are >= minimum
      return params.width >= minWidth && params.height >= minHeight;
    },
    [minWidth, minHeight]
  );

  return (
    <div className="package-node">
      <NodeResizer
        color="#3b82f6"
        isVisible={selected}
        minWidth={minWidth}
        minHeight={minHeight}
        shouldResize={shouldResize}
        keepAspectRatio={false}
      />
      <div className="package-header">
        <div className="package-name">{displayName}</div>
        <div className="package-info">{classCount} class{classCount !== 1 ? 'es' : ''}</div>
      </div>
    </div>
  );
}

export default memo(PackageNode);
