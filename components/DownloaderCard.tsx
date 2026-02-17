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

interface AvailableResolutions {
  progressive: string[];
  audio: string[];
}

const backendLogs = [
  "[system] Spawning binary extractor...",
  "[network] Initializing SSL handshake...",
  "[proxy] Tunneling through high-speed node...",
  "[yt-dlp] Resolved DASH manifest...",
  "[io] Piping raw bitstream to browser..."
];

export const DownloaderCard: React.FC<DownloaderCardProps> = ({ onSuccess }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [metadata, setMetadata] = useState<VideoMetadata | null>(null);
  const [resolutions, setResolutions] = useState<AvailableResolutions | null>(null);
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
      setError('Please provide a valid YouTube link.');
      return;
    }
    
    setError('');
    setIsLoading(true);
    setMetadata(null);
    setResolutions(null);

    try {
      const response = await fetch('/api/video_info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: cleanUrl })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Extraction failed');
      setMetadata(data);

      const resResponse = await fetch('/api/available_resolutions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: cleanUrl })
      });
      const resData = await resResponse.json();
      setResolutions(resData);
      
    } catch (err: any) {
      setError(err.message || 'The video extractor encountered an issue.');
    } finally {
      setIsLoading(false);
    }
  };

  const triggerNativeDownload = useCallback((format: string, res: string, currentMetadata: VideoMetadata) => {
    const type = format.toLowerCase().includes('mp3') ? 'mp3' : 'mp4';
    // This URL hits the direct pipe in api/index.py
    const downloadUrl = `/api/download?id=${currentMetadata.id}&resolution=${res}&type=${type}`;
    
    // Create hidden anchor to trigger browser download manager
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.target = '_self'; 
    link.style.display = 'none';
    link.setAttribute('download', ''); 
    document.body.appendChild(link);
    link.click();
    
    // Simulate cleanup and update history
    setTimeout(() => {
      if (document.body.contains(link)) document.body.removeChild(link);
      setIsProcessing(false);
      if (onSuccessRef.current) {
        onSuccessRef.current({
          id: Math.random().toString(36).substr(2, 9),
          timestamp: Date.now(),
          title: currentMetadata.title,
          thumbnail: currentMetadata.thumbnailUrl,
          format: `${type.toUpperCase()} ${res}`
        });
      }
    }, 3000);
  }, []);

  const handleDownloadRequest = (format: string, res: string) => {
    if (!metadata) return;
    setCurrentFormat(`${format} ${res}`);
    setIsProcessing(true);
    setProgress(0);
    setLogs(["[init] Engaging bypass logic..."]);

    let logIdx = 0;
    const interval = setInterval(() => {
      setProgress(prev => {
        const next = Math.min(prev + Math.floor(Math.random() * 20) + 10, 100);
        if (next % 20 === 0 && logIdx < backendLogs.length) {
          setLogs(p => [...p, backendLogs[logIdx]]);
          logIdx++;
        }
        if (next >= 100) {
          clearInterval(interval);
          triggerNativeDownload(format, res, metadata);
          return 100;
        }
        return next;
      });
    }, 120);
  };

  return (
    <div id="downloader" className="w-full max-w-4xl mx-auto p-4 md:p-8 space-y-8">
      <div className="glass rounded-[2.5rem] p-8 md:p-12 shadow-2xl border border-white/10 transition-all hover:border-red-500/20">
        <div className="space-y-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-600 rounded-2xl shadow-lg shadow-red-600/30">
                <Youtube className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-3xl font-black tracking-tight dark:text-white">YT Ultra</h2>
                <div className="flex items-center gap-2">
                  <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-widest">Vercel Proxy Edge</p>
                  <Sparkles className="w-3 h-3 text-amber-500 animate-pulse" />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 rounded-2xl border border-green-500/20">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs font-black text-green-500 uppercase tracking-widest flex items-center gap-2">
                <Database className="w-3 h-3" />
                No-Storage Stream
              </span>
            </div>
          </div>

          <div className="relative group">
            <input
              ref={inputRef}
              type="text"
              placeholder="Paste YouTube link or ID..."
              value={url}
              onChange={(e) => { setUrl(e.target.value); if (error) setError(''); }}
              onKeyDown={(e) => e.key === 'Enter' && handleProcess()}
              className="w-full h-18 pl-8 pr-12 rounded-3xl bg-white/40 dark:bg-slate-900/40 border-2 border-slate-200 dark:border-slate-800 focus:border-red-600 dark:focus:border-red-600 outline-none transition-all text-xl font-medium shadow-xl backdrop-blur-md dark:text-white"
            />
            <div className="absolute right-3 top-3 bottom-3 flex gap-2">
              <button
                onClick={async () => {
                  try {
                    const text = await navigator.clipboard.readText();
                    if (text) { setUrl(text); if (validateUrl(text)) handleProcess(); }
                  } catch (e) { setError('Clipboard access denied.'); }
                }}
                className="flex items-center gap-2 px-6 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-2xl transition-all text-slate-600 dark:text-slate-200 font-bold text-sm"
              >
                <Clipboard className="w-5 h-5" />
                Paste
              </button>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-3 text-red-500 font-bold bg-red-50 dark:bg-red-900/10 p-5 rounded-2xl border border-red-500/20 animate-in fade-in slide-in-from-top-2">
              <AlertCircle className="w-6 h-6 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <button
            onClick={handleProcess}
            disabled={isLoading || !url.trim()}
            className="w-full h-16 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white rounded-3xl font-black text-xl shadow-2xl transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-4 group"
          >
            {isLoading ? <Loader2 className="w-8 h-8 animate-spin" /> : <><Search className="w-7 h-7" /> Extract Media</>}
          </button>
        </div>
      </div>

      {metadata && !isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-8 duration-500">
          <div className="space-y-8">
            <VideoPreview metadata={metadata} />
            <ThumbnailSection metadata={metadata} />
          </div>
          <QualitySelector 
            onDownload={handleDownloadRequest} 
            availableResolutions={resolutions?.progressive || ['360p', '480p', '720p']}
            availableAudio={resolutions?.audio || ['128kbps', '192kbps', '320kbps']}
          />
        </div>
      )}

      {isProcessing && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-2xl p-6">
          <div className="bg-slate-900 rounded-[3rem] p-10 max-w-xl w-full shadow-2xl border border-white/5 space-y-8 animate-in zoom-in duration-300">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-red-600 rounded-3xl text-white shadow-2xl shadow-red-600/40">
                  <Cpu className="w-8 h-8 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-white">Direct-Pipe Stream</h3>
                  <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">{currentFormat} Output</p>
                </div>
              </div>
              <span className="text-4xl font-black text-red-500">{progress}%</span>
            </div>
            <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden border border-white/5">
              <div className="bg-gradient-to-r from-red-600 to-rose-500 h-full rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
            <div className="bg-black/40 rounded-3xl p-6 h-40 overflow-y-auto font-mono text-[10px] space-y-2 border border-white/5 custom-scrollbar">
              {logs.map((log, i) => (
                <div key={i} className="flex gap-3 text-slate-200">
                  <span className="text-slate-600">[{new Date().toLocaleTimeString()}]</span>
                  <span>{log}</span>
                </div>
              ))}
              <div className="animate-pulse text-red-500">█</div>
            </div>
            <div className="text-center text-slate-400 font-bold text-xs uppercase tracking-widest">Handshaking finished. Your browser will start the download shortly.</div>
          </div>
        </div>
      )}
    </div>
  );
};
