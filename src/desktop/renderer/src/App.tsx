import { useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [parsedContent, setParsedContent] = useState('');

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

        if (result.success) {
          setParsedContent(result.output || '');
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
      </header>

      <main className="app-main">
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

          {parsedContent && (
            <div className="parsed-content">
              <h3>Parsed Output:</h3>
              <pre>{parsedContent}</pre>
            </div>
          )}

          <div className="info">
            <p>Platform: {window.electron.platform}</p>
            <p>Environment: {window.electron.isDev ? 'Development' : 'Production'}</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
