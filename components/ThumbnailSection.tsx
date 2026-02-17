
import React, { useState } from 'react';
import { Image as ImageIcon, Download, Maximize2, Check, Loader2, AlertCircle } from 'lucide-react';
import { VideoMetadata } from '../types';

interface ThumbnailSectionProps {
  metadata: VideoMetadata;
}

export const ThumbnailSection: React.FC<ThumbnailSectionProps> = ({ metadata }) => {
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const thumbResolutions = [
    { label: 'SD', suffix: 'sddefault' },
    { label: 'HD', suffix: 'hqdefault' },
    { label: 'Max', suffix: 'maxresdefault' },
  ];

  const triggerDownload = async (label: string, url: string) => {
    setDownloading(label);
    setError(null);
    try {
      // Use a proxy-free method for public thumbnails where possible,
      // or rely on standard fetch if headers are permissive.
      const response = await fetch(url, { mode: 'no-cors' });
      
      // Since no-cors gives opaque response, we try standard fetch first
      const corsResponse = await fetch(url).catch(() => null);
      
      if (corsResponse && corsResponse.ok) {
        const blob = await corsResponse.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = `yt-ultra-thumb-${metadata.id}-${label.toLowerCase()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);
      } else {
        // If CORS fails, open in a way the user can save
        const win = window.open(url, '_blank');
        if (win) {
          win.focus();
        } else {
          setError('Popup blocked. Click resolution to open.');
        }
      }
    } catch (err) {
      console.error('Download failed:', err);
      setError('Download restricted by browser security.');
    } finally {
      setTimeout(() => setDownloading(null), 2000);
    }
  };

  return (
    <div className="glass rounded-3xl p-6 shadow-xl border border-white/10">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-amber-500/20 rounded-lg">
            <ImageIcon className="w-5 h-5 text-amber-500" />
          </div>
          <h3 className="text-xl font-bold">HQ Thumbnails</h3>
        </div>
        {error && (
          <div className="flex items-center gap-1 text-[10px] text-red-500 font-bold uppercase">
            <AlertCircle className="w-3 h-3" />
            {error}
          </div>
        )}
      </div>
      <div className="grid grid-cols-3 gap-3">
        {thumbResolutions.map((r) => {
          const imgUrl = `https://img.youtube.com/vi/${metadata.id}/${r.suffix}.jpg`;
          const isDownloading = downloading === r.label;

          return (
            <div key={r.label} className="relative group rounded-2xl overflow-hidden bg-slate-100 dark:bg-slate-800/50 p-1.5 border border-slate-200 dark:border-slate-700/50 transition-all hover:border-amber-500/50">
              <div className="relative h-20 overflow-hidden rounded-xl bg-slate-200 dark:bg-slate-900">
                <img 
                  src={imgUrl} 
                  alt={r.label}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  onError={(e) => {
                    if (r.suffix === 'maxresdefault') {
                      (e.target as HTMLImageElement).src = `https://img.youtube.com/vi/${metadata.id}/hqdefault.jpg`;
                    }
                  }}
                />
              </div>
              <div className="mt-2 flex items-center justify-between px-1">
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{r.label}</span>
                <button 
                  onClick={() => triggerDownload(r.label, imgUrl)}
                  disabled={isDownloading}
                  className="p-1.5 hover:bg-amber-500 hover:text-white dark:hover:bg-amber-500 rounded-lg transition-all active:scale-90 disabled:opacity-50"
                >
                  {isDownloading ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Download className="w-3 h-3 text-amber-500 group-hover:text-white" />
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
      <p className="mt-4 text-[10px] text-slate-400 font-medium text-center italic">
        *If download doesn't start, thumbnail will open in a new tab.
      </p>
    </div>
  );
};
