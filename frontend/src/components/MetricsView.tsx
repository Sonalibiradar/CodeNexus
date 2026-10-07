import { Activity, AlertTriangle, CheckCircle2, Ghost } from 'lucide-react';
import type { GraphMetrics } from '../types';

interface MetricsViewProps {
  metrics: GraphMetrics | null;
  onExploreFile: (filePath: string) => void;
}

export const MetricsView = ({ metrics, onExploreFile }: MetricsViewProps) => {
  if (!metrics) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] text-center px-4">
        <Activity className="w-12 h-12 text-slate-500 mb-2 animate-pulse" />
        <h4 className="text-slate-300 font-bold">No Metrics Available</h4>
        <p className="text-xs text-slate-500">Scan a repository to see architecture health insights.</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 rounded-2xl border-l-4 border-cyan-400">
          <p className="text-xs text-slate-400 uppercase font-semibold">Graph Completeness</p>
          <p className="text-2xl font-bold text-slate-100 mt-1">{metrics.total_files} Files</p>
          <p className="text-xs text-slate-400 mt-1">{metrics.total_import_edges} cross-module connections</p>
        </div>

        <div className={`glass-card p-5 rounded-2xl border-l-4 ${metrics.cycles_count > 0 ? 'border-amber-400' : 'border-emerald-400'}`}>
          <p className="text-xs text-slate-400 uppercase font-semibold">Circular Dependencies</p>
          <p className="text-2xl font-bold text-slate-100 mt-1">{metrics.cycles_count} Cycles</p>
          <p className="text-xs text-slate-400 mt-1">
            {metrics.cycles_count === 0 ? 'Clean modular DAG structure' : 'Coupling warning: cycles detected'}
          </p>
        </div>

        <div className="glass-card p-5 rounded-2xl border-l-4 border-indigo-400">
          <p className="text-xs text-slate-400 uppercase font-semibold">Dead Code Warnings</p>
          <p className="text-2xl font-bold text-slate-100 mt-1">{metrics.dead_symbols_count} Candidates</p>
          <p className="text-xs text-slate-400 mt-1">Internal functions with 0 callers</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Circular Dependency Groups
            </h4>
            <span className="text-xs text-slate-400">{metrics.cycles_count} detected</span>
          </div>

          {metrics.cycles.length === 0 ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>Great! No circular dependencies found across the codebase graph.</span>
            </div>
          ) : (
            <div className="space-y-3 max-h-72 overflow-y-auto">
              {metrics.cycles.map((cycle, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs space-y-1">
                  <span className="font-semibold text-amber-400">Cycle #{idx + 1} ({cycle.length} files)</span>
                  <div className="font-mono text-slate-300 pl-2 space-y-0.5">
                    {cycle.map((f, fi) => (
                      <p key={fi}>↳ {f}</p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Ghost className="w-4 h-4 text-purple-400" />
              Dead / Uncalled Symbol Candidates
            </h4>
            <span className="text-xs text-slate-400">{metrics.dead_symbols_count} found</span>
          </div>

          {metrics.dead_symbols.length === 0 ? (
            <div className="p-4 rounded-xl bg-slate-900/50 border border-white/5 text-slate-400 text-xs">
              No dead code candidates detected.
            </div>
          ) : (
            <div className="space-y-2 max-h-72 overflow-y-auto">
              {metrics.dead_symbols.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-white/5 text-xs hover:border-purple-500/30 transition"
                >
                  <div>
                    <span className="font-mono font-semibold text-purple-300">{item.symbol}()</span>
                    <p className="text-[11px] text-slate-400 font-mono truncate">{item.file} (Lines {item.lines})</p>
                  </div>
                  <button
                    onClick={() => onExploreFile(item.file)}
                    className="px-2 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:bg-slate-700 transition cursor-pointer"
                  >
                    Inspect
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
