import { 
  FileCode2, 
  Code2, 
  Network, 
  Boxes, 
  TrendingUp, 
  Eye, 
  FileText, 
  Binary 
} from 'lucide-react';
import type { ScanResponse, FileMetadata } from '../types';

interface OverviewViewProps {
  data: ScanResponse | null;
  onOpenFile: (file: FileMetadata) => void;
  onExploreBlastRadius: (path: string) => void;
}

export const OverviewView = ({
  data,
  onOpenFile,
  onExploreBlastRadius
}: OverviewViewProps) => {
  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] text-center px-4">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4 glow-indigo">
          <Network className="w-8 h-8 text-indigo-400 animate-pulse" />
        </div>
        <h3 className="text-xl font-bold text-slate-200 mb-2">No Repository Loaded</h3>
        <p className="text-sm text-slate-400 max-w-md">
          Paste the absolute path to your repository in the header above and click <strong className="text-cyan-400">Scan Repo</strong> to generate the Code Knowledge Graph.
        </p>
      </div>
    );
  }

  let totalLoc = 0;
  data.files.forEach(f => {
    totalLoc += f.loc;
  });

  const stats = [
    { label: 'Scanned Files', value: data.total_files, icon: FileCode2, color: 'text-cyan-400' },
    { label: 'Parsed AST Symbols', value: data.total_symbols, icon: Code2, color: 'text-indigo-400' },
    { label: 'Total Lines of Code', value: totalLoc.toLocaleString(), icon: Boxes, color: 'text-emerald-400' },
    { label: 'Graph Density', value: `${(data.metrics.density * 100).toFixed(1)}%`, icon: TrendingUp, color: 'text-purple-400' },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="glass-card p-4 rounded-xl flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-slate-900/80 border border-white/5 flex items-center justify-center">
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">{stat.label}</p>
                <p className="text-2xl font-bold text-slate-100">{stat.value}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Network className="w-4 h-4 text-cyan-400" />
              Central Architectural Hubs (PageRank)
            </h4>
            <span className="text-[11px] text-slate-500">Most imported</span>
          </div>

          <div className="space-y-2">
            {data.metrics.top_hubs.slice(0, 7).map((hub, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/50 border border-white/5 hover:border-cyan-500/30 transition group"
              >
                <div className="flex items-center gap-2.5 overflow-hidden">
                  <span className="text-xs font-mono text-slate-500 w-4">{idx + 1}</span>
                  <span className="text-xs font-medium text-slate-300 truncate group-hover:text-cyan-300">
                    {hub.file}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono text-cyan-400/80 bg-cyan-500/10 px-2 py-0.5 rounded">
                    {(hub.score * 100).toFixed(1)}%
                  </span>
                  <button
                    onClick={() => onExploreBlastRadius(hub.file)}
                    title="Simulate Blast Radius"
                    className="p-1 rounded bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 text-xs transition cursor-pointer"
                  >
                    Impact
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Scanned File Inventory & Categories
            </h4>
            <span className="text-xs text-slate-400">{data.files.length} active files</span>
          </div>

          <div className="overflow-x-auto max-h-[380px] rounded-lg border border-white/5">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 sticky top-0 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="p-3">File Path</th>
                  <th className="p-3">Language</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">LOC</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {data.files.map((f, i) => (
                  <tr key={i} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-mono text-slate-200 flex items-center gap-2">
                      <Binary className="w-3.5 h-3.5 text-slate-500" />
                      <span className="truncate max-w-[280px]" title={f.relative_path}>{f.relative_path}</span>
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 capitalize text-[10px]">
                        {f.language}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-semibold ${
                        f.category === 'source' ? 'bg-cyan-500/10 text-cyan-400' :
                        f.category === 'test' ? 'bg-amber-500/10 text-amber-400' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {f.category}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-slate-400">{f.loc}</td>
                    <td className="p-3 text-right space-x-1">
                      <button
                        onClick={() => onOpenFile(f)}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] transition cursor-pointer"
                      >
                        <Eye className="w-3 h-3 inline mr-1" />
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
