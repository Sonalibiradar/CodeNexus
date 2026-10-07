import { useState } from 'react';
import { Zap, AlertTriangle, ShieldCheck, ShieldAlert, Route, FileCode, CheckCircle2, Search } from 'lucide-react';
import type { BlastRadiusResult } from '../types';

interface BlastRadiusViewProps {
  initialTarget?: string;
}

export const BlastRadiusView = ({ initialTarget = '' }: BlastRadiusViewProps) => {
  const [target, setTarget] = useState(initialTarget);
  const [result, setResult] = useState<BlastRadiusResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    if (!target.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/impact?target=${encodeURIComponent(target)}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'CRITICAL':
        return <span className="px-3 py-1 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-bold flex items-center gap-1.5"><ShieldAlert className="w-4 h-4" /> CRITICAL RISK</span>;
      case 'HIGH':
        return <span className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-bold flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" /> HIGH RISK</span>;
      case 'MODERATE':
        return <span className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-bold flex items-center gap-1.5"><Zap className="w-4 h-4" /> MODERATE RISK</span>;
      default:
        return <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5"><ShieldCheck className="w-4 h-4" /> LOW RISK</span>;
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div>
          <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            Pull Request & Diff Blast Radius Simulator
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Traverse reverse-call and import dependency chains to calculate every upstream file, symbol, and API endpoint affected by a change.
          </p>
        </div>

        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="Enter file path or symbol name (e.g. app/graph/builder.py or CodeKnowledgeGraph)"
              className="w-full pl-9 pr-4 py-2.5 bg-slate-900/90 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400/50"
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={loading || !target.trim()}
            className="px-6 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-sm rounded-xl flex items-center gap-2 transition cursor-pointer"
          >
            {loading ? 'Analyzing Impact...' : 'Simulate Impact'}
          </button>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-l-4 border-amber-400">
            <div>
              <span className="text-xs text-slate-400 uppercase font-semibold">Analyzed Target</span>
              <h4 className="text-lg font-mono font-bold text-slate-100">{result.target}</h4>
              <p className="text-xs text-slate-400 mt-1">
                Total Affected Components: <strong className="text-cyan-400">{result.total_impacted}</strong>
              </p>
            </div>
            <div>
              {getRiskBadge(result.risk_level)}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-panel p-5 rounded-2xl space-y-3">
              <h5 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Route className="w-4 h-4 text-rose-400" />
                Affected API Endpoints ({result.impacted_endpoints.length})
              </h5>
              {result.impacted_endpoints.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No external API routes directly depend on this component.</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {result.impacted_endpoints.map((ep, idx) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs font-mono text-rose-300">
                      {ep}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="glass-panel p-5 rounded-2xl space-y-3">
              <h5 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <FileCode className="w-4 h-4 text-cyan-400" />
                Impacted Files ({result.impacted_files.length})
              </h5>
              {result.impacted_files.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No other files import this module.</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {result.impacted_files.map((f, idx) => (
                    <div key={idx} className="p-2 rounded-lg bg-slate-900/60 border border-white/5 text-xs font-mono text-slate-300 truncate" title={f}>
                      {f}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="glass-panel p-5 rounded-2xl space-y-3">
              <h5 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-indigo-400" />
                Impacted Functions/Symbols ({result.impacted_symbols.length})
              </h5>
              {result.impacted_symbols.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No downstream symbols identified.</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {result.impacted_symbols.map((s, idx) => (
                    <div key={idx} className="p-2 rounded-lg bg-slate-900/60 border border-white/5 text-xs font-mono text-indigo-300 truncate" title={s}>
                      {s}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
