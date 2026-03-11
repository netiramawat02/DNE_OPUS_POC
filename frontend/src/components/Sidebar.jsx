import React from 'react';
import { FileText, LayoutDashboard, MessageSquare, Clock, AlertCircle } from 'lucide-react';

const Sidebar = ({ contracts, selectedContract, onSelect, view, setView }) => {
  return (
    <div className="h-full flex flex-col bg-white">
      <div className="p-4 border-b border-gray-200">
         <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
           <FileText className="w-5 h-5 text-blue-600" /> Contract AI
         </h2>
      </div>

      <div className="p-3">
         <nav className="space-y-1">
           <button
             onClick={() => setView('dashboard')}
             className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
               view === 'dashboard' ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
             }`}
           >
             <LayoutDashboard size={18} /> Dashboard
           </button>
           <button
             onClick={() => {
                 onSelect(null);
                 setView('chat');
             }}
             className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
               view === 'chat' && !selectedContract ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
             }`}
           >
             <MessageSquare size={18} /> Global Chat
           </button>
         </nav>
      </div>

      <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Your Contracts</h3>
        <span className="bg-gray-200 text-gray-600 py-0.5 px-2 rounded-full text-xs font-medium">{contracts.length}</span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-gray-50">
        {contracts.length === 0 ? (
          <p className="text-sm text-gray-400 italic text-center mt-4">No contracts yet.</p>
        ) : (
          contracts.map((contract) => (
            <div
              key={contract.id}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${
                selectedContract?.id === contract.id && view === 'chat'
                  ? 'bg-blue-50 border-blue-400 shadow-sm ring-1 ring-blue-400'
                  : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-sm'
              }`}
              onClick={() => {
                 onSelect(contract);
                 setView('chat');
              }}
            >
              <div className="flex items-start gap-2">
                 <FileText className={`w-4 h-4 mt-0.5 flex-shrink-0 ${contract.status === 'processed' ? 'text-blue-500' : 'text-gray-400'}`} />
                 <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-800 truncate" title={contract.filename}>
                      {contract.filename}
                    </p>
                    {contract.status === 'processing' && (
                       <p className="text-xs text-yellow-600 flex items-center gap-1 mt-1">
                          <Clock size={12} /> Processing...
                       </p>
                    )}
                    {contract.status === 'failed' && (
                       <p className="text-xs text-red-600 flex items-center gap-1 mt-1">
                          <AlertCircle size={12} /> Failed
                       </p>
                    )}
                    {contract.status === 'processed' && contract.metadata?.vendor && (
                       <p className="text-xs text-gray-500 truncate mt-1" title={contract.metadata.vendor}>
                         {contract.metadata.vendor}
                       </p>
                    )}
                 </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;
