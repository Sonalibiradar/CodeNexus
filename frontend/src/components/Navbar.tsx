import React from 'react';
import { 
  Network, 
  Layers, 
  Zap, 
  MessageSquare, 
  Activity, 
  FolderGit2, 
  Sparkles,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  repoPath: string;
  setRepoPath: (path: string) => void;
  onScan: () => void;
  onIndex: () => void;
  isScanning: boolean;
  isIndexing: boolean;
  isIndexed: boolean;
  hasScanData: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  repoPath,
  setRepoPath,
  onScan,
  onIndex,
  isScanning,
  isIndexing,
  isIndexed,
  hasScanData
}) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'graph', label: 'Architecture Map', icon: Network },
    { id: 'impact', label: 'Blast Radius', icon: Zap },
    { id: 'chat', label: 'Ask CodeNexus', icon: MessageSquare },
    { id: 'metrics', label: 'Health & Insights', icon: Activity },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-3">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-cyan-500 to-emerald-400 p-[2px] flex items-center justify-center glow-cyan">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Network className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
                CodeNexus
              </span>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                v1.0 Pro
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Codebase Intelligence Engine</p>
          </div>
        </div>

        {/* Path Input & Scan Action */}
        <div className="flex items-center gap-2 w-full md:w-auto flex-1 max-w-xl">
          <div className="relative flex-1">
            <FolderGit2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="Paste absolute path to repository (e.g. C:\Users\...)"
              className="w-full pl-9 pr-4 py-2 bg-slate-900/80 border border-white/10 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition"
            />
          </div>
          <button
            onClick={onScan}
            disabled={isScanning || !repoPath.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-medium text-sm rounded-lg flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition cursor-pointer"
          >
            {isScanning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Scanning...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                <span>Scan Repo</span>
              </>
            )}
          </button>

          {hasScanData && (
            <button
              onClick={onIndex}
              disabled={isIndexing}
              className={`px-3 py-2 text-sm font-medium rounded-lg flex items-center gap-1.5 transition cursor-pointer ${
                isIndexed
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-500/20'
              }`}
            >
              {isIndexing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Indexing...</span>
                </>
              ) : isIndexed ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Indexed</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Index RAG</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-white/5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                  isActive
                    ? 'bg-indigo-600/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

      </div>
    </header>
  );
};
