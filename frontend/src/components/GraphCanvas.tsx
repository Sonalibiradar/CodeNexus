import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  BackgroundVariant
} from '@xyflow/react';
import type { NodeProps, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Search, Code2, Binary, Zap } from 'lucide-react';

interface FileNodeData {
  id: string;
  label: string;
  language: string;
  category: string;
  loc: number;
  size_bytes: number;
  symbols_count: number;
  [key: string]: unknown;
}

const FileNodeComponent = ({ data, selected }: NodeProps<Node<FileNodeData>>) => {
  const nodeData = data;
  return (
    <div className={`p-3 rounded-xl min-w-[200px] max-w-[240px] bg-slate-900/90 border transition-all shadow-xl backdrop-blur-md ${
      selected 
        ? 'border-cyan-400 ring-2 ring-cyan-500/40 glow-cyan' 
        : 'border-white/10 hover:border-indigo-400/50'
    }`}>
      <Handle type="target" position={Position.Top} className="!bg-cyan-400 !w-2.5 !h-2.5 !border-slate-950" />
      
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 overflow-hidden">
          <Binary className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
          <span className="text-xs font-semibold text-slate-100 truncate font-mono">
            {nodeData.label}
          </span>
        </div>
        <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
          {nodeData.language}
        </span>
      </div>

      <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-white/5">
        <span>{nodeData.loc} LOC</span>
        <span className="text-indigo-400 font-medium">{nodeData.symbols_count} symbols</span>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-indigo-500 !w-2.5 !h-2.5 !border-slate-950" />
    </div>
  );
};

interface GraphCanvasProps {
  onSelectNode: (nodeId: string) => void;
  onExploreBlastRadius: (nodeId: string) => void;
}

export const GraphCanvas = ({
  onSelectNode,
  onExploreBlastRadius
}: GraphCanvasProps) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<FileNodeData>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNodeData, setSelectedNodeData] = useState<FileNodeData | null>(null);

  const nodeTypes = useMemo(() => ({ fileNode: FileNodeComponent }), []);

  useEffect(() => {
    fetch('/api/graph')
      .then(res => res.json())
      .then(data => {
        if (data && data.nodes) {
          setNodes(data.nodes);
          setEdges(data.edges);
        }
      })
      .catch(() => {});
  }, [setNodes, setEdges]);

  const handleNodeClick = useCallback((_: React.MouseEvent, node: Node<FileNodeData>) => {
    setSelectedNodeData(node.data);
    onSelectNode(node.id);
  }, [onSelectNode]);

  const filteredNodes = useMemo(() => {
    if (!searchQuery.trim()) return nodes;
    const query = searchQuery.toLowerCase();
    return nodes.map(n => ({
      ...n,
      selected: n.id.toLowerCase().includes(query) || (n.data?.label as string)?.toLowerCase().includes(query)
    }));
  }, [nodes, searchQuery]);

  return (
    <div className="relative w-full h-[calc(100vh-80px)] overflow-hidden bg-slate-950">
      <div className="absolute top-4 left-4 z-20 flex items-center gap-3 glass-panel p-2 rounded-xl border border-white/10 shadow-2xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search nodes or files..."
            className="pl-9 pr-3 py-1.5 bg-slate-900/90 border border-white/10 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-56"
          />
        </div>
        <span className="text-xs text-slate-400 px-2 border-l border-white/10 font-mono">
          {nodes.length} Nodes • {edges.length} Edges
        </span>
      </div>

      {selectedNodeData && (
        <div className="absolute top-4 right-4 z-20 w-80 glass-panel p-4 rounded-2xl border border-white/10 shadow-2xl space-y-3">
          <div className="flex items-center justify-between">
            <h5 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Code2 className="w-4 h-4 text-cyan-400" />
              Node Inspector
            </h5>
            <button
              onClick={() => setSelectedNodeData(null)}
              className="text-slate-400 hover:text-slate-200 text-xs cursor-pointer"
            >
              ✕
            </button>
          </div>

          <div className="p-3 bg-slate-900/80 rounded-xl border border-white/5 space-y-2 text-xs">
            <div>
              <span className="text-[10px] text-slate-500 uppercase">Path</span>
              <p className="font-mono text-slate-200 break-all">{selectedNodeData.id}</p>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-white/5">
              <div>
                <span className="text-[10px] text-slate-500 uppercase">Language</span>
                <p className="text-slate-300 capitalize">{selectedNodeData.language}</p>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase">Category</span>
                <p className="text-slate-300 capitalize">{selectedNodeData.category}</p>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase">LOC</span>
                <p className="font-mono text-slate-300">{selectedNodeData.loc}</p>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase">Symbols</span>
                <p className="font-mono text-indigo-400">{selectedNodeData.symbols_count}</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onExploreBlastRadius(selectedNodeData.id)}
              className="flex-1 py-1.5 px-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition cursor-pointer"
            >
              <Zap className="w-3.5 h-3.5" />
              Simulate Blast Radius
            </button>
          </div>
        </div>
      )}

      <ReactFlow
        nodes={filteredNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="#1e293b" gap={20} size={1} variant={BackgroundVariant.Dots} />
        <Controls />
        <MiniMap
          nodeColor={() => '#6366f1'}
          maskColor="rgba(9, 13, 22, 0.7)"
          className="rounded-xl overflow-hidden shadow-2xl"
        />
      </ReactFlow>
    </div>
  );
};
