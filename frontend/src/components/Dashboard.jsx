import React from 'react';
import { FileText, Calendar, Users, AlertCircle, Clock, CheckCircle } from 'lucide-react';

const Dashboard = ({ contracts, onSelectContract, setView }) => {
  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Contracts Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">Overview of all processed and processing contracts.</p>
        </div>
        <div className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full shadow-sm border border-gray-100 flex items-center gap-2">
           <FileText size={16} className="text-blue-500" />
           <span className="font-medium text-gray-700">{contracts.length}</span> Total Contracts
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {contracts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <FileText className="w-16 h-16 mb-4 text-gray-300" />
            <p className="text-lg font-medium text-gray-500">No contracts available</p>
            <p className="text-sm mt-2">Upload some contracts to get started.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg shadow-sm overflow-hidden">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filename
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vendor
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dates
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {contracts.map((contract) => (
                  <tr key={contract.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="flex-shrink-0 h-5 w-5 text-gray-400 mr-3" />
                        <div className="text-sm font-medium text-gray-900 truncate max-w-[200px]" title={contract.filename}>
                          {contract.filename}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-[250px] truncate" title={contract.metadata?.title || 'N/A'}>
                        {contract.metadata?.title || <span className="text-gray-400 italic">Not available</span>}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900">
                        {contract.metadata?.vendor ? (
                           <>
                             <Users className="flex-shrink-0 h-4 w-4 text-gray-400 mr-2" />
                             <span className="truncate max-w-[150px]" title={contract.metadata.vendor}>{contract.metadata.vendor}</span>
                           </>
                        ) : (
                           <span className="text-gray-400 italic">N/A</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                       <div className="flex flex-col gap-1 text-sm text-gray-600">
                         {contract.metadata?.start_date && (
                           <div className="flex items-center gap-1" title="Start Date">
                             <Calendar size={12} className="text-green-500" /> {contract.metadata.start_date}
                           </div>
                         )}
                         {contract.metadata?.end_date && (
                           <div className="flex items-center gap-1" title="End Date">
                             <Calendar size={12} className="text-red-500" /> {contract.metadata.end_date}
                           </div>
                         )}
                         {(!contract.metadata?.start_date && !contract.metadata?.end_date) && (
                            <span className="text-gray-400 italic text-xs">Dates unavailable</span>
                         )}
                       </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {contract.status === 'processing' ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <Clock className="w-3 h-3 mr-1" /> Processing
                        </span>
                      ) : contract.status === 'failed' ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                           <AlertCircle className="w-3 h-3 mr-1" /> Failed
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                           <CheckCircle className="w-3 h-3 mr-1" /> Processed
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => {
                          onSelectContract(contract);
                          setView('chat');
                        }}
                        disabled={contract.status !== 'processed'}
                        className={`text-blue-600 hover:text-blue-900 transition-colors ${contract.status !== 'processed' ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        Chat
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
