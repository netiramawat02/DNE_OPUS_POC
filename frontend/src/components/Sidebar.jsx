import React from 'react';
import { FileText, Calendar, Users, Hash } from 'lucide-react';

const Sidebar = ({ contracts, selectedContract, onSelect }) => {
  return (
    <div className="h-full bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5" /> Processed Contracts
      </h2>

      {contracts.length === 0 ? (
        <p className="text-sm text-gray-500 italic">No contracts uploaded yet.</p>
      ) : (
        <div className="space-y-4">
          {contracts.map((contract) => (
            <div
              key={contract.id}
              className={`p-3 rounded shadow-sm border cursor-pointer transition-colors ${
                selectedContract?.id === contract.id
                  ? 'bg-blue-50 border-blue-300 ring-1 ring-blue-300'
                  : 'bg-white border-gray-100 hover:bg-gray-100'
              }`}
              onClick={() => onSelect(contract)}
            >
              <div className="font-medium text-blue-700 text-sm mb-2 truncate" title={contract.filename}>
                {contract.filename}
              </div>

              {contract.metadata && (
                <div className="space-y-1">
                  {contract.metadata.title && (
                     <div className="text-xs text-gray-800 font-semibold">{contract.metadata.title}</div>
                  )}
                  <div className="grid grid-cols-2 gap-1 text-xs text-gray-500">
                    {contract.metadata.start_date && (
                        <div className="flex items-center gap-1" title="Start Date">
                           <Calendar size={10} /> {contract.metadata.start_date}
                        </div>
                    )}
                    {contract.metadata.end_date && (
                        <div className="flex items-center gap-1" title="End Date">
                           <Calendar size={10} /> {contract.metadata.end_date}
                        </div>
                    )}
                  </div>
                   {contract.metadata.vendor && (
                        <div className="text-xs text-gray-600 flex items-center gap-1 mt-1">
                           <Users size={10} /> {contract.metadata.vendor}
                        </div>
                    )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Sidebar;
