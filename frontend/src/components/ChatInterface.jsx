import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, FileText, Loader2, Info } from 'lucide-react';

const ChatInterface = ({ selectedContract }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, loading]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const payload = {
        query: userMsg.content,
        contract_id: selectedContract?.id
      };
      const response = await axios.post('/api/chat', payload);
      const botMsg = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error. Please try again later." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {selectedContract ? (
        <div className="bg-blue-50 px-6 py-3 border-b border-blue-100 flex items-center justify-between">
           <div className="flex items-center gap-2 text-sm text-blue-800">
             <FileText size={18} className="text-blue-500" />
             <span className="font-medium">Context:</span>
             <span className="font-semibold truncate max-w-md" title={selectedContract.filename}>{selectedContract.filename}</span>
           </div>
           <span className="text-xs bg-white text-blue-600 px-2 py-1 rounded-full border border-blue-200 font-medium shadow-sm">
             Single Document Search
           </span>
        </div>
      ) : (
        <div className="bg-gray-50 px-6 py-3 border-b border-gray-200 flex items-center gap-2 text-sm text-gray-700">
           <Info size={18} className="text-gray-400" />
           <span className="font-medium">Context:</span> All uploaded documents (Global Search)
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-white">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto">
            <div className="bg-blue-50 p-4 rounded-full mb-4">
              <Bot className="w-10 h-10 text-blue-500" />
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">How can I help you today?</h3>
            <p className="text-sm text-gray-500">
              {selectedContract
                ? `Ask me anything about "${selectedContract.filename}". I'll analyze the document and provide answers.`
                : "Ask questions across all your processed contracts. To focus on a specific document, select it from the dashboard."}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
               <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                  <Bot size={18} className="text-blue-600" />
               </div>
            )}
            <div
              className={`max-w-[75%] p-4 rounded-2xl ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-sm shadow-md'
                  : 'bg-gray-50 text-gray-800 rounded-tl-sm border border-gray-100 shadow-sm'
              }`}
            >
              <div className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
                  <div className="font-medium flex items-center gap-1 mb-1 text-gray-700">
                    <FileText size={12} /> Sources used:
                  </div>
                  <ul className="list-disc list-inside space-y-0.5 ml-1">
                    {msg.sources.map((s, i) => (
                      <li key={i} className="truncate" title={s}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
           <div className="flex justify-start">
             <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                  <Bot size={18} className="text-blue-600" />
             </div>
             <div className="bg-gray-50 border border-gray-100 p-4 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-2 text-gray-500 text-sm">
               <Loader2 size={16} className="animate-spin text-blue-500" /> Analyzing documents...
             </div>
           </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={sendMessage} className="relative max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={selectedContract ? `Ask about ${selectedContract.filename}...` : "Ask a question about your contracts..."}
            className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="absolute right-2 top-2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            <Send size={18} className="ml-0.5" />
          </button>
        </form>
        <div className="text-center mt-2 text-[10px] text-gray-400">
           AI can make mistakes. Verify important information from the source documents.
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
