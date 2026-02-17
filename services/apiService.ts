
import { VideoMetadata } from "../types";

export const apiService = {
  /**
   * Calls the Python backend to extract real metadata using yt-dlp
   */
  async extractMetadata(url: string): Promise<VideoMetadata> {
    const response = await fetch('/api/extract', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to extract metadata');
    }

    return await response.json();
  },

  /**
   * Generates a conceptual download URL for the backend
   */
  getDownloadUrl(videoId: string, format: string): string {
    return `/api/download?id=${videoId}&format=${encodeURIComponent(format)}`;
  }
};
