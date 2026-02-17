
import React from 'react';
import { History, Trash2, Calendar, FileType } from 'lucide-react';
import { HistoryItem } from '../types';

interface DownloadHistoryProps {
  items: HistoryItem[];
  onClear: () => void;
  onDelete: (id: string) => void;
}

export const DownloadHistory: React.FC<DownloadHistoryProps> = ({ items, onClear, onDelete }) => {
  if (items.length === 0) return null;

  return (
    <section className="py-20 px-6 max-w-4xl mx-auto space-y-10">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-2xl text-red-500">
            <History className="w-6 h-6" />
          </div>
          <h2 className="text-3xl font-black">Recent Activity</h2>
        </div>
        <button 
          onClick={onClear}
          className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-500 hover:text-red-500 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {items.map((item) => (
          <div key={item.id} className="glass rounded-3xl p-5 flex gap-4 group hover:shadow-xl transition-all">
            <img 
              src={item.thumbnail} 
              alt={item.title} 
              className="w-24 h-24 object-cover rounded-2xl"
            />
            <div className="flex-1 space-y-2 relative">
              <h4 className="font-bold line-clamp-2 text-sm leading-tight pr-6">
                {item.title}
              </h4>
              <div className="flex items-center gap-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(item.timestamp).toLocaleDateString()}
                </span>
                <span className="flex items-center gap-1 text-red-500">
                  <FileType className="w-3 h-3" />
                  {item.format}
                </span>
              </div>
              <button 
                onClick={() => onDelete(item.id)}
                className="absolute top-0 right-0 p-1 text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
