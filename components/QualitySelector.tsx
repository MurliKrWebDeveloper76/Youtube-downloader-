
import React from 'react';
import { Video, Music, Download, ShieldCheck } from 'lucide-react';

interface QualitySelectorProps {
  onDownload: (format: string) => void;
}

export const QualitySelector: React.FC<QualitySelectorProps> = ({ onDownload }) => {
  const videoFormats = [
    { q: '144p', size: '2.4 MB', hd: false },
    { q: '360p', size: '12.8 MB', hd: false },
    { q: '720p', size: '48.2 MB', hd: true },
    { q: '1080p', size: '120.5 MB', hd: true },
    { q: '4K', size: '450.0 MB', hd: true },
  ];

  const audioFormats = [
    { q: '128kbps', size: '4.2 MB' },
    { q: '192kbps', size: '6.8 MB' },
    { q: '320kbps', size: '11.5 MB' },
  ];

  return (
    <div className="space-y-6">
      <div className="glass rounded-3xl p-6 shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <Video className="w-6 h-6 text-red-500" />
          <h3 className="text-xl font-bold">Video Options (MP4)</h3>
        </div>
        <div className="space-y-3">
          {videoFormats.map((f) => (
            <button
              key={f.q}
              onClick={() => onDownload(`MP4 ${f.q}`)}
              className="w-full flex items-center justify-between p-4 rounded-2xl bg-white/40 dark:bg-slate-800/40 hover:bg-white/60 dark:hover:bg-slate-700/60 transition-all group"
            >
              <div className="flex items-center gap-3">
                <span className="font-bold">{f.q}</span>
                {f.hd && (
                  <span className="text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">HD</span>
                )}
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{f.size}</span>
                <Download className="w-5 h-5 text-red-500 group-hover:translate-y-0.5 transition-transform" />
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="glass rounded-3xl p-6 shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <Music className="w-6 h-6 text-rose-500" />
          <h3 className="text-xl font-bold">Audio Options (MP3)</h3>
        </div>
        <div className="space-y-3">
          {audioFormats.map((f) => (
            <button
              key={f.q}
              onClick={() => onDownload(`MP3 ${f.q}`)}
              className="w-full flex items-center justify-between p-4 rounded-2xl bg-white/40 dark:bg-slate-800/40 hover:bg-white/60 dark:hover:bg-slate-700/60 transition-all group"
            >
              <div className="flex items-center gap-3">
                <span className="font-bold">{f.q}</span>
                {f.q === '320kbps' && (
                  /* Fix: ShieldCheck does not support the title prop. Wrapping in a span instead to provide a tooltip. */
                  <span title="High Quality">
                    <ShieldCheck className="w-4 h-4 text-rose-500" />
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{f.size}</span>
                <Download className="w-5 h-5 text-rose-500 group-hover:translate-y-0.5 transition-transform" />
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
