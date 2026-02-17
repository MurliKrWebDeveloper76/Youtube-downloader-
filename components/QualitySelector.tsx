import React from 'react';
import { Video, Music, Download, ShieldCheck } from 'lucide-react';

interface QualitySelectorProps {
  onDownload: (format: string, res: string) => void;
  availableResolutions: string[];
  availableAudio: string[];
}

export const QualitySelector: React.FC<QualitySelectorProps> = ({ onDownload, availableResolutions, availableAudio }) => {
  return (
    <div className="space-y-6">
      <div className="glass rounded-3xl p-6 shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <Video className="w-6 h-6 text-red-500" />
          <h3 className="text-xl font-bold">Video (MP4)</h3>
        </div>
        <div className="space-y-3">
          {availableResolutions.map((res) => (
            <button
              key={res}
              onClick={() => onDownload('MP4', res)}
              className="w-full flex items-center justify-between p-4 rounded-2xl bg-white/40 dark:bg-slate-800/40 hover:bg-white/60 dark:hover:bg-slate-700/60 transition-all group"
            >
              <div className="flex items-center gap-3">
                <span className="font-bold">{res}</span>
                {['720p', '1080p', '4K'].includes(res) && (
                  <span className="text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">HD</span>
                )}
              </div>
              <Download className="w-5 h-5 text-red-500 group-hover:translate-y-0.5 transition-transform" />
            </button>
          ))}
        </div>
      </div>

      <div className="glass rounded-3xl p-6 shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <Music className="w-6 h-6 text-rose-500" />
          <h3 className="text-xl font-bold">Audio (MP3)</h3>
        </div>
        <div className="space-y-3">
          {availableAudio.map((res) => (
            <button
              key={res}
              onClick={() => onDownload('MP3', res)}
              className="w-full flex items-center justify-between p-4 rounded-2xl bg-white/40 dark:bg-slate-800/40 hover:bg-white/60 dark:hover:bg-slate-700/60 transition-all group"
            >
              <div className="flex items-center gap-3">
                <span className="font-bold">{res}</span>
                {res === '320kbps' && <ShieldCheck className="w-4 h-4 text-rose-500" />}
              </div>
              <Download className="w-5 h-5 text-rose-500 group-hover:translate-y-0.5 transition-transform" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
