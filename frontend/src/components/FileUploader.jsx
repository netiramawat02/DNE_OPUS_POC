import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Check, AlertCircle, X } from 'lucide-react';

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
    <div className="p-4 border border-dashed border-gray-300 rounded-lg bg-gray-50 text-center flex flex-col items-center">
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={handleFileChange}
        className="hidden"
        id="file-upload"
        disabled={uploading}
      />
      <label
        htmlFor="file-upload"
        className={`cursor-pointer flex flex-col items-center justify-center w-full p-4 hover:bg-gray-100 transition-colors ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <Upload className="w-8 h-8 text-blue-500 mb-2" />
        <span className="text-sm text-gray-600 font-medium">
          Click to Select Contract PDFs
        </span>
      </label>

      {selectedFiles.length > 0 && (
        <div className="w-full mt-4 text-left">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Selected Files:</h4>
          <ul className="space-y-2 max-h-32 overflow-y-auto pr-2">
            {selectedFiles.map((file, index) => (
              <li key={`${file.name}-${index}`} className="flex items-center justify-between text-sm text-gray-600 bg-white p-2 rounded border border-gray-200">
                <div className="flex items-center gap-2 truncate">
                  <FileText size={16} className="text-blue-400 flex-shrink-0" />
                  <span className="truncate">{file.name}</span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  disabled={uploading}
                  className="text-gray-400 hover:text-red-500 transition-colors ml-2 flex-shrink-0"
                  title="Remove file"
                >
                  <X size={16} />
                </button>
              </li>
            ))}
          </ul>

          <button
            onClick={handleUpload}
            disabled={uploading}
            className={`mt-4 w-full py-2 px-4 rounded font-medium text-white transition-colors ${
              uploading ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading ? "Uploading..." : `Upload ${selectedFiles.length} File${selectedFiles.length > 1 ? 's' : ''}`}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-2 text-red-500 text-xs flex items-center justify-center gap-1">
          <AlertCircle size={12} /> {error}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
