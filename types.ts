export interface VideoMetadata {
  id: string;
  title: string;
  channel: string;
  duration: string;
  thumbnailUrl: string;
  views: string;
  url: string;
  directUrl?: string;
}

export interface Format {
  quality: string;
  type: 'video' | 'audio';
  size: string;
  hd?: boolean;
}

export interface HistoryItem {
  id: string;
  timestamp: number;
  title: string;
  thumbnail: string;
  format: string;
}

export enum Theme {
  LIGHT = 'light',
  DARK = 'dark'
}