import { memo } from 'react';
import { NodeResizer } from 'reactflow';
import './PackageNode.css';

interface PackageNodeProps {
  data: {
    packageName: string;
    classCount: number;
    minWidth: number;
    minHeight: number;
  };
  selected?: boolean;
}

function PackageNode({ data, selected }: PackageNodeProps) {
  const { packageName, classCount, minWidth, minHeight } = data;

  // Display name: use "(root)" for empty package names
  const displayName = packageName || '(root)';

  return (
    <div className="package-node">
      <NodeResizer
        color="#3b82f6"
        isVisible={selected}
        minWidth={minWidth}
        minHeight={minHeight}
      />
      <div className="package-header">
        <div className="package-name">{displayName}</div>
        <div className="package-info">{classCount} class{classCount !== 1 ? 'es' : ''}</div>
      </div>
    </div>
  );
}

export default memo(PackageNode);
