import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import FileUploader from './components/FileUploader';
import Dashboard from './components/Dashboard';

function App() {
  const [contracts, setContracts] = useState([]);
  const [selectedContract, setSelectedContract] = useState(null);
  const [view, setView] = useState('dashboard'); // 'dashboard' or 'chat'

  useEffect(() => {
    fetchContracts();
    // Refresh contracts periodically to check processing status
    const interval = setInterval(fetchContracts, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchContracts = async () => {
    try {
      const res = await axios.get('/api/contracts');
      setContracts(res.data);
    } catch (err) {
      console.error("Failed to fetch contracts", err);
    }
  };

  const handleSelectContract = (contract) => {
    setSelectedContract(contract);
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar (Left) */}
      <div className="w-72 h-full flex-shrink-0 hidden md:block bg-white border-r border-gray-200">
        <Sidebar
          contracts={contracts}
          selectedContract={selectedContract}
          onSelect={handleSelectContract}
          view={view}
          setView={setView}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center shadow-sm z-10">
          <div>
              <h1 className="text-2xl font-bold text-gray-800">AI Contract Chatbot</h1>
              <p className="text-sm text-gray-500">Upload PDF contracts and analyze them instantly.</p>
          </div>
          <div className="flex-none w-1/3 min-w-[300px]">
             <FileUploader onUploadSuccess={fetchContracts} />
          </div>
        </header>

        <main className="flex-1 overflow-hidden p-6 bg-gray-50">
          {view === 'dashboard' ? (
             <Dashboard contracts={contracts} onSelectContract={handleSelectContract} setView={setView} />
          ) : (
             <ChatInterface selectedContract={selectedContract} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
