import React, { useState, useEffect } from 'react';
import { X, FileCode, Copy, Check } from 'lucide-react';

interface FileViewerModalProps {
  filePath: string | null;
  onClose: () => void;
}

export const FileViewerModal: React.FC<FileViewerModalProps> = ({ filePath, onClose }) => {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!filePath) return;
    setLoading(true);
    fetch(`/api/file/content?path=${encodeURIComponent(filePath)}`)
      .then(res => res.json())
      .then(data => {
        setContent(data.content || '');
        setLoading(false);
      })
      .catch(() => {
        setContent('// Failed to load file content.');
        setLoading(false);
      });
  }, [filePath]);

  if (!filePath) return null;

  const lines = content.split('\n');

  const copyCode = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="w-full max-w-4xl max-h-[85vh] glass-panel rounded-2xl border border-white/10 shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-white/10 bg-slate-900/90">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-mono font-semibold text-slate-200">{filePath}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={copyCode}
              className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white text-xs flex items-center gap-1 transition cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Code Content */}
        <div className="flex-1 overflow-auto p-4 bg-slate-950 text-xs font-mono">
          {loading ? (
            <div className="flex items-center justify-center h-48 text-slate-500">
              Loading source file...
            </div>
          ) : (
            <div className="table w-full">
              {lines.map((line, idx) => (
                <div key={idx} className="table-row hover:bg-slate-900/50">
                  <span className="table-cell pr-4 text-right select-none text-slate-600 font-mono w-10">
                    {idx + 1}
                  </span>
                  <span className="table-cell whitespace-pre text-slate-200 pl-2">
                    {line || ' '}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
