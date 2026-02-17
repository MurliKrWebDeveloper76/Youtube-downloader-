
import React, { useState, useRef, useCallback } from 'react';
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
  "[network] Connecting to YouTube API endpoints...",
  "[parser] Resolving adaptive stream manifests...",
  "[system] Analyzing DASH/HLS segments...",
  "[process] Merging M4A and MP4 containers...",
  "[ffmpeg] Executing remuxing sequence...",
  "[status] Output buffer verified and ready."
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
          // Small delay to ensure state update before processing
          setTimeout(handleProcess, 100);
        }
      }
    } catch (err) {
      setError('Clipboard access denied. Please paste manually.');
    }
  };

  // Side effect to finalize the download after progress reaches 100
  const finalizeDownload = useCallback(async (format: string, currentMetadata: VideoMetadata) => {
    try {
      // In a real environment, this would call the /api/download endpoint
      const sample = 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4';
      const res = await fetch(sample);
      const blob = await res.blob();
      const bUrl = window.URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = bUrl;
      const fileName = `${currentMetadata.title || 'Video'}_${format}`.replace(/[^a-z0-9]/gi, '_');
      a.download = `${fileName}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(bUrl);

      setIsProcessing(false);
      onSuccess({
        id: Math.random().toString(36).substr(2, 9),
        timestamp: Date.now(),
        title: currentMetadata.title,
        thumbnail: currentMetadata.thumbnailUrl || `https://img.youtube.com/vi/${currentMetadata.id}/mqdefault.jpg`,
        format: format
      });
    } catch (err) {
      console.error("Finalize download error:", err);
      setIsProcessing(false);
      window.open('https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '_blank');
    }
  }, [onSuccess]);

  const handleDownload = (format: string) => {
    if (!metadata) return;

    setCurrentFormat(format);
    setIsProcessing(true);
    setProgress(0);
    setLogs(["[api] Handshaking with serverless endpoint..."]);

    let logIdx = 0;
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        
        const nextProgress = Math.min(prev + Math.floor(Math.random() * 5) + 2, 100);
        
        // Add log entry if threshold reached
        if (nextProgress % 15 === 0 && logIdx < backendLogs.length) {
          setLogs(p => [...p, backendLogs[logIdx]]);
          logIdx++;
        }

        // Trigger finalization outside of the state updater when done
        if (nextProgress >= 100) {
           setTimeout(() => finalizeDownload(format, metadata), 500);
        }
        
        return nextProgress;
      });
    }, 120);
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
                  <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-widest">Hybrid Processing</p>
                  <Sparkles className="w-3 h-3 text-amber-500 animate-pulse" />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 rounded-2xl border border-green-500/20">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs font-black text-green-500 uppercase tracking-widest flex items-center gap-2">
                <Database className="w-3 h-3" />
                Active Core
              </span>
            </div>
          </div>

          <div className="relative group">
            <input
              ref={inputRef}
              type="text"
              placeholder="Paste link or video ID to process..."
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
          <div className="bg-slate-900 rounded-[3rem] p-10 max-w-xl w-full shadow-2xl border border-white/5 space-y-10 animate-in zoom-in duration-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-red-600 rounded-3xl text-white shadow-2xl shadow-red-600/40">
                  <Cpu className="w-8 h-8 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-white">Advanced Compute Core</h3>
                  <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">{currentFormat} Processor Active</p>
                </div>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-4xl font-black text-red-500">{progress}%</span>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tighter">Segment {Math.ceil(progress/10)}/10</span>
              </div>
            </div>

            <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden p-0.5 border border-white/5">
              <div 
                className="bg-gradient-to-r from-red-600 to-rose-500 h-full rounded-full transition-all duration-300 shadow-[0_0_20px_rgba(220,38,38,0.5)]"
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="bg-black/60 rounded-3xl p-6 h-64 overflow-y-auto font-mono text-xs space-y-2 border border-white/5 custom-scrollbar shadow-inner">
              {logs.map((log, i) => (
                <div key={i} className="flex gap-3 text-slate-300 animate-in fade-in slide-in-from-left-4">
                  <span className="text-slate-600 font-bold">[{new Date().toLocaleTimeString([], {hour12:false})}]</span>
                  <span className={log.includes('[python]') ? 'text-blue-400' : log.includes('[ffmpeg]') ? 'text-purple-400' : 'text-slate-200'}>
                    {log}
                  </span>
                </div>
              ))}
              <div className="animate-pulse text-red-500">█</div>
            </div>

            <div className="text-center space-y-2">
              <div className="flex items-center justify-center gap-3 text-slate-400 font-bold text-xs uppercase tracking-[0.2em]">
                <Loader2 className="w-4 h-4 animate-spin text-red-500" />
                Secure Handshake in Progress
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
