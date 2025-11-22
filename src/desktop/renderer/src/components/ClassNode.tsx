import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Class, getVisibilitySymbol, formatType } from '../types/metamodel';

interface ClassNodeProps {
  data: {
    classData: Class;
  };
}

function ClassNode({ data }: ClassNodeProps) {
  const { classData } = data;

  // Get source file from metadata
  const sourceFile = classData.metadata?.source_file as string | undefined;

  return (
    <div className="class-node">
      {/* Connection handles */}
      <Handle type="target" position={Position.Top} className="handle" />
      <Handle type="source" position={Position.Bottom} className="handle" />

      {/* Source file indicator */}
      {sourceFile && (
        <div className="class-source-file" title={sourceFile}>
          📄 {sourceFile}
        </div>
      )}

      {/* Class name section */}
      <div className="class-header">
        {classData.is_abstract && <div className="class-stereotype">&lt;&lt;abstract&gt;&gt;</div>}
        {classData.decorators.length > 0 && (
          <div className="class-decorators">
            {classData.decorators.map((dec, idx) => (
              <span key={idx} className="decorator">
                @{dec.name}
              </span>
            ))}
          </div>
        )}
        <div className="class-name">{classData.name}</div>
        {classData.base_classes.length > 0 && (
          <div className="class-bases">
            extends {classData.base_classes.join(', ')}
          </div>
        )}
      </div>

      {/* Attributes section */}
      {classData.attributes.length > 0 && (
        <div className="class-section">
          {classData.attributes.map((attr, idx) => (
            <div key={idx} className="class-member">
              <span className="visibility">{getVisibilitySymbol(attr.visibility)}</span>
              <span className="member-name">{attr.name}</span>
              <span className="member-type">: {formatType(attr.type)}</span>
              {attr.default_value && (
                <span className="default-value"> = {attr.default_value}</span>
              )}
              {attr.is_static && <span className="modifier"> {'{'}static{'}'}</span>}
              {attr.is_class_var && <span className="modifier"> {'{'}class{'}'}</span>}
            </div>
          ))}
        </div>
      )}

      {/* Methods section */}
      {classData.methods.length > 0 && (
        <div className="class-section">
          {classData.methods.map((method, idx) => (
            <div key={idx} className="class-member">
              <span className="visibility">{getVisibilitySymbol(method.visibility)}</span>
              <span className="member-name">{method.name}</span>
              <span className="parameters">
                (
                {method.parameters.map((param, pidx) => (
                  <span key={pidx}>
                    {pidx > 0 && ', '}
                    {param.name}: {formatType(param.type)}
                  </span>
                ))}
                )
              </span>
              {method.return_type && (
                <span className="member-type">: {formatType(method.return_type)}</span>
              )}
              {method.is_static && <span className="modifier"> {'{'}static{'}'}</span>}
              {method.is_class_method && <span className="modifier"> {'{'}classmethod{'}'}</span>}
              {method.is_abstract && <span className="modifier"> {'{'}abstract{'}'}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default memo(ClassNode);
