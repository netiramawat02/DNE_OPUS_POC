import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import FileUploader from './components/FileUploader';
import './App.css'; // Assuming we might add some basic CSS or use Tailwind via CDN in index.html for simplicity if build process is complex

function App() {
  const [contracts, setContracts] = useState([]);

  const fetchContracts = async () => {
    try {
      const res = await axios.get('/api/contracts');
      setContracts(res.data);
    } catch (err) {
      console.error("Failed to fetch contracts", err);
    }
  };

  useEffect(() => {
    fetchContracts();
  }, []);

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar (Left) */}
      <div className="w-80 h-full hidden md:block">
        <Sidebar contracts={contracts} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col p-6 h-full overflow-hidden">
        <header className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Jules AI Contract Chatbot</h1>
          <p className="text-sm text-gray-500">Upload PDF contracts and ask questions.</p>
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
