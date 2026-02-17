
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Youtube, Search, Clipboard, Loader2, AlertCircle, Cpu, Database, Sparkles } from 'lucide-react';
import { apiService } from '../services/apiService';
import { VideoMetadata, HistoryItem } from '../types';
import { VideoPreview } from './VideoPreview';
import { QualitySelector } from './QualitySelector';
import { ThumbnailSection } from './ThumbnailSection';

interface DownloaderCardProps {
  onSuccess: (item: HistoryItem) => void;
}

const backendLogs = [
  "[python] Initializing yt-dlp engine...",
  "[network] Connecting to YT API...",
  "[parser] Resolving adaptive stream...",
  "[system] Analyzing DASH segments...",
  "[ffmpeg] Executing remuxing...",
  "[status] Buffer ready for streaming."
];

export const DownloaderCard: React.FC<DownloaderCardProps> = ({ onSuccess }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [metadata, setMetadata] = useState<VideoMetadata | null>(null);
  const [error, setError] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentFormat, setCurrentFormat] = useState('');

  const inputRef = useRef<HTMLInputElement>(null);
  
  const onSuccessRef = useRef(onSuccess);
  useEffect(() => {
    onSuccessRef.current = onSuccess;
  }, [onSuccess]);

  const validateUrl = (val: string) => {
    const t = val.trim();
    return t.length > 0 && (t.includes('youtube.com') || t.includes('youtu.be') || t.match(/^[a-zA-Z0-9_-]{11}$/));
  };

  const handleProcess = async () => {
    const cleanUrl = url.trim();
    if (!validateUrl(cleanUrl)) {
      setError('Please provide a valid YouTube URL or Video ID.');
      return;
    }
    
    setError('');
    setIsLoading(true);
    setMetadata(null);

    try {
      const data = await apiService.extractMetadata(cleanUrl);
      setMetadata(data);
    } catch (err: any) {
      console.error('Extraction Error:', err);
      setError(err.message || 'Service is currently under heavy load. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text);
        if (validateUrl(text)) {
          setTimeout(handleProcess, 100);
        }
      }
    } catch (err) {
      setError('Clipboard access denied. Please paste manually.');
    }
  };

  const finalizeDownload = useCallback((format: string, currentMetadata: VideoMetadata) => {
    // 1. Construct the optimized streaming proxy URL
    const downloadUrl = `/api/download?id=${currentMetadata.id}&format=${encodeURIComponent(format)}`;
    
    // 2. Trigger download instantly using direct window location
    window.location.assign(downloadUrl);

    // 3. Close processing overlay almost immediately for a "fast" feel
    setTimeout(() => {
      setIsProcessing(false);
      if (onSuccessRef.current) {
        onSuccessRef.current({
          id: Math.random().toString(36).substr(2, 9),
          timestamp: Date.now(),
          title: currentMetadata.title,
          thumbnail: currentMetadata.thumbnailUrl || `https://img.youtube.com/vi/${currentMetadata.id}/mqdefault.jpg`,
          format: format
        });
      }
    }, 1000);
  }, []);

  const handleDownload = (format: string) => {
    if (!metadata) return;

    setCurrentFormat(format);
    setIsProcessing(true);
    setProgress(0);
    setLogs(["[api] Handshaking with secure proxy..."]);

    // Accelerated progress for "One Click" feel
    let logIdx = 0;
    const interval = setInterval(() => {
      setProgress(prev => {
        // High increment (15-25% per tick)
        const nextProgress = Math.min(prev + Math.floor(Math.random() * 20) + 15, 100);
        
        if (nextProgress % 30 === 0 && logIdx < backendLogs.length) {
          setLogs(p => [...p, backendLogs[logIdx]]);
          logIdx++;
        }

        if (nextProgress >= 100) {
          clearInterval(interval);
          finalizeDownload(format, metadata);
          return 100;
        }
        
        return nextProgress;
      });
    }, 60); // Faster interval (60ms vs 120ms)
  };

  return (
    <div id="downloader" className="w-full max-w-4xl mx-auto p-4 md:p-8 space-y-8">
      <div className="glass rounded-[2.5rem] p-8 md:p-12 shadow-2xl transition-all border border-white/10 dark:hover:border-red-500/20">
        <div className="space-y-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-500 rounded-2xl shadow-lg shadow-red-500/30">
                <Youtube className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-3xl font-black tracking-tight dark:text-white">YT Ultra</h2>
                <div className="flex items-center gap-2">
                  <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-widest">Instant One-Click Engine</p>
                  <Sparkles className="w-3 h-3 text-amber-500 animate-pulse" />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 rounded-2xl border border-green-500/20">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs font-black text-green-500 uppercase tracking-widest flex items-center gap-2">
                <Database className="w-3 h-3" />
                Core Active
              </span>
            </div>
          </div>

          <div className="relative group">
            <input
              ref={inputRef}
              type="text"
              placeholder="Paste link or video ID..."
              value={url}
              onChange={(e) => { setUrl(e.target.value); if (error) setError(''); }}
              onKeyDown={(e) => e.key === 'Enter' && handleProcess()}
              className="w-full h-18 pl-8 pr-44 rounded-3xl bg-white/40 dark:bg-slate-900/40 border-2 border-slate-200 dark:border-slate-800 focus:border-red-500 dark:focus:border-red-500 outline-none transition-all text-xl font-medium shadow-xl backdrop-blur-md dark:text-white"
            />
            <div className="absolute right-3 top-3 bottom-3 flex gap-2">
              <button
                onClick={handlePaste}
                className="flex items-center gap-2 px-6 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-2xl transition-all text-slate-600 dark:text-slate-200 font-bold text-sm"
              >
                <Clipboard className="w-5 h-5" />
                Paste
              </button>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-3 text-red-500 font-bold bg-red-50 dark:bg-red-900/10 p-5 rounded-2xl border border-red-500/20 animate-in fade-in slide-in-from-top-4">
              <AlertCircle className="w-6 h-6 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <button
            onClick={handleProcess}
            disabled={isLoading || !url.trim()}
            className="w-full h-16 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white rounded-3xl font-black text-xl shadow-2xl shadow-red-500/40 transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-4 group overflow-hidden"
          >
            {isLoading ? (
              <Loader2 className="w-8 h-8 animate-spin" />
            ) : (
              <>
                <Search className="w-7 h-7 transition-transform group-hover:scale-110" />
                Initialize Ultra Extraction
              </>
            )}
          </button>
        </div>
      </div>

      {metadata && !isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
          <div className="space-y-8">
            <VideoPreview metadata={metadata} />
            <ThumbnailSection metadata={metadata} />
          </div>
          <QualitySelector onDownload={handleDownload} />
        </div>
      )}

      {isProcessing && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-2xl p-6">
          <div className="bg-slate-900 rounded-[3rem] p-10 max-w-xl w-full shadow-2xl border border-white/5 space-y-10 animate-in zoom-in duration-300">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-red-600 rounded-3xl text-white shadow-2xl shadow-red-600/40">
                  <Cpu className="w-8 h-8 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-white">Advanced Compute</h3>
                  <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">{currentFormat} Processor</p>
                </div>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-4xl font-black text-red-500">{progress}%</span>
              </div>
            </div>

            <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden p-0.5 border border-white/5">
              <div 
                className="bg-gradient-to-r from-red-600 to-rose-500 h-full rounded-full transition-all duration-300 shadow-[0_0_20px_rgba(220,38,38,0.5)]"
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="bg-black/60 rounded-3xl p-6 h-48 overflow-y-auto font-mono text-[10px] space-y-2 border border-white/5 custom-scrollbar shadow-inner">
              {logs.map((log, i) => (
                <div key={i} className="flex gap-3 text-slate-300 animate-in fade-in slide-in-from-left-2">
                  <span className="text-slate-600">[{new Date().toLocaleTimeString([], {hour12:false})}]</span>
                  <span className={log.includes('[python]') ? 'text-blue-400' : 'text-slate-200'}>{log}</span>
                </div>
              ))}
              <div className="animate-pulse text-red-500">█</div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center gap-3 text-slate-400 font-bold text-xs uppercase tracking-[0.2em]">
                <Loader2 className="w-4 h-4 animate-spin text-red-500" />
                Piping stream to browser...
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
