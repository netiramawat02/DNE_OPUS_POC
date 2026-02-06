import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Check, AlertCircle } from 'lucide-react';

const FileUploader = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    // Assuming backend handles one at a time or we loop.
    // The current backend endpoint takes one file at 'file' key.
    // Let's loop for multiple support in UI

    try {
      for (let i = 0; i < files.length; i++) {
        const data = new FormData();
        data.append('file', files[i]);
        await axios.post('/api/upload', data);
      }
      onUploadSuccess();
    } catch (err) {
      setError("Failed to upload file(s).");
      console.error(err);
    } finally {
      setUploading(false);
      // Reset input
      e.target.value = null;
    }
  };

  return (
    <div className="p-4 border border-dashed border-gray-300 rounded-lg bg-gray-50 text-center">
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={handleFileChange}
        className="hidden"
        id="file-upload"
      />
      <label
        htmlFor="file-upload"
        className="cursor-pointer flex flex-col items-center justify-center"
      >
        <Upload className="w-8 h-8 text-blue-500 mb-2" />
        <span className="text-sm text-gray-600 font-medium">
          {uploading ? "Uploading..." : "Click to Upload Contract PDFs"}
        </span>
      </label>
      {error && (
        <div className="mt-2 text-red-500 text-xs flex items-center justify-center gap-1">
          <AlertCircle size={12} /> {error}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
