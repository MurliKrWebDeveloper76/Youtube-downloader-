
import React from 'react';
import { VideoMetadata } from '../types';
import { Clock, Eye, User } from 'lucide-react';

interface VideoPreviewProps {
  metadata: VideoMetadata;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({ metadata }) => {
  return (
    <div className="glass rounded-3xl overflow-hidden group shadow-xl">
      <div className="relative aspect-video">
        <img 
          src={metadata.thumbnailUrl} 
          alt={metadata.title}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      <div className="p-6 space-y-4">
        <h3 className="text-xl font-bold line-clamp-2 leading-tight dark:text-white">
          {metadata.title}
        </h3>
        
        <div className="grid grid-cols-1 gap-3 text-sm font-medium text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-red-500" />
            <span>{metadata.channel}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-red-500" />
              <span>{metadata.duration}</span>
            </div>
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-red-500" />
              <span>{metadata.views} views</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
