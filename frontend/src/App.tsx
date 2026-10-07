import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewView } from './components/OverviewView';
import { GraphCanvas } from './components/GraphCanvas';
import { BlastRadiusView } from './components/BlastRadiusView';
import { ChatAssistant } from './components/ChatAssistant';
import { MetricsView } from './components/MetricsView';
import { FileViewerModal } from './components/FileViewerModal';
import type { ScanResponse, FileMetadata } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [repoPath, setRepoPath] = useState<string>('');
  const [scanData, setScanData] = useState<ScanResponse | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isIndexing, setIsIndexing] = useState<boolean>(false);
  const [isIndexed, setIsIndexed] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [blastTarget, setBlastTarget] = useState<string>('');

  useEffect(() => {
    fetch('/api/status')
      .then(res => res.json())
      .then(data => {
        if (data.active_repo) {
          setRepoPath(data.active_repo);
          setIsIndexed(data.is_indexed);
        }
      })
      .catch(() => {});
  }, []);

  const handleScan = async () => {
    if (!repoPath.trim()) return;
    setIsScanning(true);
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setScanData(data);
        setIsIndexed(false);
      } else {
        alert(data.detail || 'Scan failed');
      }
    } catch (err: any) {
      alert(`Error scanning repository: ${err.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const handleIndex = async () => {
    setIsIndexing(true);
    try {
      const res = await fetch('/api/index', { method: 'POST' });
      const data = await res.json();
      if (res.ok && data.success) {
        setIsIndexed(true);
      } else {
        alert(data.detail || 'Indexing failed');
      }
    } catch (err: any) {
      alert(`Error indexing repository: ${err.message}`);
    } finally {
      setIsIndexing(false);
    }
  };

  const handleExploreBlastRadius = (target: string) => {
    setBlastTarget(target);
    setActiveTab('impact');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        repoPath={repoPath}
        setRepoPath={setRepoPath}
        onScan={handleScan}
        onIndex={handleIndex}
        isScanning={isScanning}
        isIndexing={isIndexing}
        isIndexed={isIndexed}
        hasScanData={!!scanData}
      />

      <main className="flex-1 overflow-auto">
        {activeTab === 'overview' && (
          <OverviewView
            data={scanData}
            onOpenFile={(file: FileMetadata) => setSelectedFile(file.relative_path)}
            onExploreBlastRadius={handleExploreBlastRadius}
          />
        )}

        {activeTab === 'graph' && (
          <GraphCanvas
            onSelectNode={(nodeId: string) => setSelectedFile(nodeId)}
            onExploreBlastRadius={handleExploreBlastRadius}
          />
        )}

        {activeTab === 'impact' && (
          <BlastRadiusView initialTarget={blastTarget} />
        )}

        {activeTab === 'chat' && (
          <ChatAssistant
            onOpenFile={(filePath: string) => setSelectedFile(filePath)}
            isIndexed={isIndexed}
          />
        )}

        {activeTab === 'metrics' && (
          <MetricsView
            metrics={scanData ? scanData.metrics : null}
            onExploreFile={(filePath: string) => setSelectedFile(filePath)}
          />
        )}
      </main>

      <FileViewerModal
        filePath={selectedFile}
        onClose={() => setSelectedFile(null)}
      />
    </div>
  );
}

export default App;
