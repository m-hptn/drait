import { useState } from 'react';
import './App.css';
import DiagramCanvas from './components/DiagramCanvas';
import { Project } from './types/metamodel';

const MAX_CLASSES_WARNING = 50;
const MAX_CLASSES_LIMIT = 100;

function App() {
  const [message, setMessage] = useState('');
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleOpenFile = async () => {
    try {
      const filePath = await window.electron.dialog.openFile([
        { name: 'Python Files', extensions: ['py'] },
        { name: 'All Files', extensions: ['*'] }
      ]);

      if (filePath) {
        setIsLoading(true);
        setMessage(`Parsing file: ${filePath}...`);

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
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenFolder = async () => {
    try {
      const folderPath = await window.electron.dialog.openFolder();

      if (folderPath) {
        setIsLoading(true);
        setMessage(`Parsing folder: ${folderPath}...`);

        // Parse the Python folder
        const result = await window.electron.python.parseFolder(folderPath);

        if (result.success && result.metamodel) {
          const pkg = result.metamodel.packages[0];
          const classCount = pkg.classes.length;

          // Check if too many classes
          if (classCount > MAX_CLASSES_LIMIT) {
            setMessage(
              `⚠️ Warning: Found ${classCount} classes. This is too many to visualize efficiently.\n` +
              `Only the first ${MAX_CLASSES_LIMIT} classes will be displayed.\n` +
              `Consider selecting a smaller folder or specific Python files instead.`
            );

            // Limit the classes
            const limitedProject = {
              ...result.metamodel,
              packages: [{
                ...pkg,
                classes: pkg.classes.slice(0, MAX_CLASSES_LIMIT)
              }]
            };
            setProject(limitedProject as Project);
          } else if (classCount > MAX_CLASSES_WARNING) {
            setMessage(
              `⚠️ Successfully parsed ${classCount} classes from: ${folderPath}\n` +
              `Note: Large diagrams may be slow to render and navigate.`
            );
            setProject(result.metamodel as Project);
          } else {
            setMessage(`Successfully parsed ${classCount} classes from: ${folderPath}`);
            setProject(result.metamodel as Project);
          }
        } else {
          setMessage(`Error: ${result.message || 'Unknown error'}`);
        }
      }
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
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
          <button
            onClick={handleOpenFolder}
            className="btn btn-primary btn-sm"
          >
            Import Python Folder
          </button>
        </div>
      </header>

      <main className="app-main">
        {isLoading ? (
          <div className="welcome-section">
            <h2>Loading...</h2>
            <p>Parsing Python code and generating diagram...</p>
            {message && (
              <div className="message">
                {message}
              </div>
            )}
          </div>
        ) : project ? (
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
              <button
                onClick={handleOpenFolder}
                className="btn btn-primary"
                style={{ marginLeft: '10px' }}
              >
                Import Python Folder
              </button>
            </div>

            {message && (
              <div className="message" style={{ whiteSpace: 'pre-line' }}>
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
