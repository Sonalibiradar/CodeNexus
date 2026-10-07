export interface FileMetadata {
  path: string;
  relative_path: string;
  extension: string;
  language: string;
  category: string;
  size_bytes: number;
  loc: number;
  content_hash: string;
}

export interface HubMetric {
  file: string;
  score: number;
}

export interface DeadSymbol {
  symbol: string;
  file: string;
  lines: string;
}

export interface GraphMetrics {
  total_files: number;
  total_import_edges: number;
  density: number;
  cycles: string[][];
  cycles_count: number;
  top_hubs: HubMetric[];
  roots: string[];
  leaves: string[];
  isolated: string[];
  dead_symbols: DeadSymbol[];
  dead_symbols_count: number;
}

export interface ScanResponse {
  success: boolean;
  repo_path: string;
  total_files: number;
  total_symbols: number;
  metrics: GraphMetrics;
  files: FileMetadata[];
}

export interface BlastRadiusResult {
  target: string;
  found: boolean;
  risk_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | "UNKNOWN";
  total_impacted: number;
  impacted_files: string[];
  impacted_symbols: string[];
  impacted_endpoints: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  citations?: string[];
  diagnostics?: string[];
  isStreaming?: boolean;
}
