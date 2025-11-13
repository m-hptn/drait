import { useState } from 'react';
import './App.css';
import DiagramCanvas from './components/DiagramCanvas';
import { Project } from './types/metamodel';

function App() {
  const [message, setMessage] = useState('');
  const [project, setProject] = useState<Project | null>(null);

  const handleOpenFile = async () => {
    try {
      const filePath = await window.electron.dialog.openFile([
        { name: 'Python Files', extensions: ['py'] },
        { name: 'All Files', extensions: ['*'] }
      ]);

      if (filePath) {
        setMessage(`Selected file: ${filePath}`);

        // Parse the Python file
        const result = await window.electron.python.parse(filePath);

        if (result.success && result.metamodel) {
          setProject(result.metamodel as Project);
          setMessage(`Successfully parsed: ${filePath}`);
        } else {
          setMessage(`Error: ${result.message || 'Unknown error'}`);
        }
      }
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>DRAIT</h1>
        <p>UML Class Diagram Editor</p>
        <div className="header-actions">
          <button
            onClick={handleOpenFile}
            className="btn btn-primary btn-sm"
          >
            Import Python File
          </button>
        </div>
      </header>

      <main className="app-main">
        {project ? (
          <DiagramCanvas project={project} />
        ) : (
          <div className="welcome-section">
            <h2>Welcome to DRAIT Desktop</h2>
            <p>Model-Driven Development Tool for Python</p>

            <div className="actions">
              <button
                onClick={handleOpenFile}
                className="btn btn-primary"
              >
                Import Python File
              </button>
            </div>

            {message && (
              <div className="message">
                {message}
              </div>
            )}

            <div className="info">
              <p>Platform: {window.electron.platform}</p>
              <p>Environment: {window.electron.isDev ? 'Development' : 'Production'}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
