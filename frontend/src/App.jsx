import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import FileUploader from './components/FileUploader';
import './App.css';

function App() {
  const [contracts, setContracts] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
        const apiKey = localStorage.getItem('apiKey');
        if (apiKey) {
            axios.defaults.headers.common['X-API-Key'] = apiKey;
            setIsAuthenticated(true);
            fetchContracts();
        } else {
            // Simple prompt for now
            const key = window.prompt("Please enter your API Key to access the Chatbot:");
            if (key) {
                localStorage.setItem('apiKey', key);
                axios.defaults.headers.common['X-API-Key'] = key;
                setIsAuthenticated(true);
                fetchContracts();
            }
        }
    };

    checkAuth();
  }, []);

  const fetchContracts = async () => {
    try {
      const res = await axios.get('/api/contracts');
      setContracts(res.data);
    } catch (err) {
      console.error("Failed to fetch contracts", err);
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
         // Key might be invalid
         alert("Invalid API Key or session expired.");
         localStorage.removeItem('apiKey');
         setIsAuthenticated(false);
         window.location.reload();
      }
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100">
        <div className="text-center p-8 bg-white rounded shadow-md">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">Authentication Required</h1>
            <p className="text-gray-600 mb-4">You need an API Key to access this application.</p>
             <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
             >
                Enter API Key
             </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar (Left) */}
      <div className="w-80 h-full hidden md:block">
        <Sidebar contracts={contracts} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col p-6 h-full overflow-hidden">
        <header className="mb-6 flex justify-between items-center">
          <div>
              <h1 className="text-2xl font-bold text-gray-800">AI Contract Chatbot</h1>
              <p className="text-sm text-gray-500">Upload PDF contracts and ask questions.</p>
          </div>
          <button
            onClick={() => {
                if(window.confirm("Are you sure you want to clear your API Key?")) {
                    localStorage.removeItem('apiKey');
                    window.location.reload();
                }
            }}
            className="text-xs text-red-500 hover:text-red-700 font-semibold"
          >
            Clear API Key
          </button>
        </header>

        <div className="flex-1 flex flex-col gap-4 overflow-hidden">
          {/* Uploader */}
          <div className="flex-none">
             <FileUploader onUploadSuccess={fetchContracts} />
          </div>

          {/* Chat */}
          <div className="flex-1 overflow-hidden">
             <ChatInterface />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
