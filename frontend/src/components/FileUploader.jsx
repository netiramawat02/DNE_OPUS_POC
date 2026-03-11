import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, AlertCircle, X, Loader2 } from 'lucide-react';

const FileUploader = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    setSelectedFiles((prev) => [...prev, ...files]);
    e.target.value = null; // Reset input
  };

  const removeFile = (indexToRemove) => {
    setSelectedFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) return;

    setUploading(true);
    setError(null);

    try {
      for (let i = 0; i < selectedFiles.length; i++) {
        const data = new FormData();
        data.append('file', selectedFiles[i]);
        await axios.post('/api/upload', data);
      }
      onUploadSuccess();
      setSelectedFiles([]); // Clear selected files on success
    } catch (err) {
      setError("Failed to upload file(s).");
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="relative group">
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={handleFileChange}
        className="hidden"
        id="file-upload"
        disabled={uploading}
      />

      {selectedFiles.length === 0 ? (
        <label
          htmlFor="file-upload"
          className={`flex items-center justify-center gap-2 w-full py-2 px-4 border-2 border-dashed border-blue-300 rounded-lg bg-blue-50 text-blue-700 cursor-pointer hover:bg-blue-100 transition-colors ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Upload size={18} />
          <span className="text-sm font-medium">Upload PDF Contracts</span>
        </label>
      ) : (
        <div className="absolute right-0 top-0 w-80 bg-white p-4 rounded-lg shadow-xl border border-gray-200 z-50">
          <div className="flex justify-between items-center mb-3">
             <h4 className="text-sm font-semibold text-gray-800">Selected Files</h4>
             <button onClick={() => setSelectedFiles([])} className="text-gray-400 hover:text-gray-600">
               <X size={16} />
             </button>
          </div>

          <ul className="space-y-2 max-h-48 overflow-y-auto pr-2 mb-4">
            {selectedFiles.map((file, index) => (
              <li key={`${file.name}-${index}`} className="flex items-center justify-between text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-md border border-gray-100">
                <div className="flex items-center gap-2 truncate">
                  <FileText size={14} className="text-blue-500 flex-shrink-0" />
                  <span className="truncate">{file.name}</span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  disabled={uploading}
                  className="text-gray-400 hover:text-red-500 transition-colors ml-2 flex-shrink-0"
                  title="Remove file"
                >
                  <X size={14} />
                </button>
              </li>
            ))}
          </ul>

          <div className="flex gap-2">
            <label
              htmlFor="file-upload"
              className="flex-1 text-center py-2 px-4 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer transition-colors"
            >
              Add More
            </label>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md text-sm font-medium text-white transition-colors ${
                uploading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {uploading ? (
                 <><Loader2 size={16} className="animate-spin" /> Uploading...</>
              ) : (
                 `Upload ${selectedFiles.length}`
              )}
            </button>
          </div>

          {error && (
            <div className="mt-3 text-red-500 text-xs flex items-center justify-center gap-1 bg-red-50 p-2 rounded">
              <AlertCircle size={14} /> {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
