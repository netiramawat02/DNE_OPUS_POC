import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import FileUploader from './components/FileUploader';
import './App.css';

function App() {
  const [contracts, setContracts] = useState([]);
  const [selectedContract, setSelectedContract] = useState(null);

  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async () => {
    try {
      const res = await axios.get('/api/contracts');
      setContracts(res.data);
    } catch (err) {
      console.error("Failed to fetch contracts", err);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar (Left) */}
      <div className="w-80 h-full hidden md:block">
        <Sidebar
          contracts={contracts}
          selectedContract={selectedContract}
          onSelect={setSelectedContract}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col p-6 h-full overflow-hidden">
        <header className="mb-6 flex justify-between items-center">
          <div>
              <h1 className="text-2xl font-bold text-gray-800">AI Contract Chatbot</h1>
              <p className="text-sm text-gray-500">Upload PDF contracts and ask questions.</p>
          </div>
        </header>

        <div className="flex-1 flex flex-col gap-4 overflow-hidden">
          {/* Uploader */}
          <div className="flex-none">
             <FileUploader onUploadSuccess={fetchContracts} />
          </div>

          {/* Chat */}
          <div className="flex-1 overflow-hidden">
             <ChatInterface selectedContract={selectedContract} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
