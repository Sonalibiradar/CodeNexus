import { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  CheckCircle, 
  FileCode, 
  AlertCircle, 
  Copy, 
  Check 
} from 'lucide-react';
import type { ChatMessage } from '../types';

interface ChatAssistantProps {
  onOpenFile: (filePath: string) => void;
  isIndexed: boolean;
}

export const ChatAssistant = ({ onOpenFile }: ChatAssistantProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I'm **CodeNexus AI**. I have mapped your codebase's AST symbols, call graphs, and architecture. Ask me anything about how this code works, execution flows, or specific functions!",
      confidence: 100,
      citations: []
    }
  ]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const starterQuestions = [
    "Where does execution start and how is the project structured?",
    "Which files are the central architectural hubs?",
    "Explain how the graph builder and analyzers connect.",
    "Are there any dead code or unreferenced symbols?"
  ];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (queryText?: string) => {
    const q = queryText || input;
    if (!q.trim() || isGenerating) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: q
    };

    const assistantMsgId = (Date.now() + 1).toString();
    const initAssistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      isStreaming: true
    };

    setMessages(prev => [...prev, userMsg, initAssistantMsg]);
    setInput('');
    setIsGenerating(true);

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });

      if (!response.ok) {
        throw new Error('Failed to start streaming');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';

      if (reader) {
        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const payload = JSON.parse(line.slice(6));
                if (payload.type === 'token') {
                  accumulatedText += payload.content;
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === assistantMsgId
                        ? { ...m, content: accumulatedText }
                        : m
                    )
                  );
                } else if (payload.type === 'final') {
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === assistantMsgId
                        ? {
                            ...m,
                            confidence: payload.confidence,
                            citations: payload.citations,
                            diagnostics: payload.diagnostics,
                            isStreaming: false
                          }
                        : m
                    )
                  );
                }
              } catch (e) {
                // Ignore parse errors
              }
            }
          }
        }
      }
    } catch (err: any) {
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMsgId
            ? {
                ...m,
                content: `*Error generating answer: ${err.message}. Please make sure you have scanned the repository first.*`,
                isStreaming: false
              }
            : m
        )
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] max-w-5xl mx-auto p-4 md:p-6">
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 pb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-1 shadow-md shadow-cyan-500/20">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}

            <div
              className={`max-w-3xl rounded-2xl p-4.5 text-sm space-y-3 shadow-xl ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white ml-12 rounded-tr-sm'
                  : 'glass-panel text-slate-200 mr-12 rounded-tl-sm border border-white/10'
              }`}
            >
              <div className="whitespace-pre-wrap leading-relaxed font-sans">
                {msg.content}
                {msg.isStreaming && (
                  <span className="inline-block w-2 h-4 ml-1 bg-cyan-400 animate-pulse" />
                )}
              </div>

              {msg.role === 'assistant' && !msg.isStreaming && (
                <div className="pt-3 border-t border-white/10 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    {msg.confidence !== undefined && (
                      <div className="flex items-center gap-1.5 text-xs">
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-slate-400">Confidence:</span>
                        <span className="font-semibold text-emerald-400">{msg.confidence}%</span>
                      </div>
                    )}

                    <button
                      onClick={() => copyToClipboard(msg.id, msg.content)}
                      className="text-slate-400 hover:text-slate-200 text-xs flex items-center gap-1 cursor-pointer transition"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>

                  {msg.citations && msg.citations.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[11px] text-slate-400 font-semibold mr-1">Sources:</span>
                      {msg.citations.map((c, idx) => (
                        <button
                          key={idx}
                          onClick={() => onOpenFile(c)}
                          className="px-2 py-0.5 rounded-md bg-slate-900 border border-white/10 hover:border-cyan-500/50 text-cyan-300 text-[11px] font-mono flex items-center gap-1 transition cursor-pointer"
                        >
                          <FileCode className="w-3 h-3 text-cyan-400" />
                          <span>{c}</span>
                        </button>
                      ))}
                    </div>
                  )}

                  {msg.diagnostics && msg.diagnostics.length > 0 && (
                    <div className="p-2 rounded bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      <div>
                        {msg.diagnostics.map((d, i) => (
                          <p key={i}>{d}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-slate-800 border border-white/10 flex items-center justify-center flex-shrink-0 mt-1">
                <User className="w-4 h-4 text-slate-300" />
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {messages.length <= 1 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3">
          {starterQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              className="p-2.5 rounded-xl glass-card text-left text-xs text-slate-300 hover:text-cyan-300 hover:border-cyan-500/30 transition cursor-pointer"
            >
              💡 {q}
            </button>
          ))}
        </div>
      )}

      <div className="glass-panel p-2 rounded-2xl border border-white/10 flex items-center gap-2 shadow-2xl">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Ask CodeNexus about codebase structure, call chains, or functions..."
          rows={1}
          className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none resize-none max-h-24"
        />
        <button
          onClick={() => handleSend()}
          disabled={isGenerating || !input.trim()}
          className="p-2.5 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 disabled:opacity-40 text-white rounded-xl transition cursor-pointer shadow-lg shadow-indigo-500/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
