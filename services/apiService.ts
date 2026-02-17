import { VideoMetadata } from "../types";
import { extractMetadata as geminiFallback } from "./geminiService";

export const apiService = {
  /**
   * Primary Extractor:
   * Uses the unified Python backend at /api/video_info
   */
  async extractMetadata(url: string): Promise<VideoMetadata> {
    try {
      const response = await fetch('/api/video_info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const contentType = response.headers.get("content-type");
      
      if (contentType && contentType.includes("text/html")) {
        console.warn("Backend HTML response detected. Falling back to Gemini.");
        return await geminiFallback(url);
      }

      const data = await response.json();

      if (!response.ok) {
        // If YouTube blocked the server IP, use AI to fulfill the request
        if (data.error && (data.error.includes("sign in") || data.error.includes("bot"))) {
          console.info("Backend blocked by YouTube. Engaging AI metadata extraction...");
          return await geminiFallback(url);
        }
        throw new Error(data.error || `Server error: ${response.status}`);
      }

      return data;
    } catch (error: any) {
      console.error("apiService.extractMetadata primary attempt failed:", error);
      
      try {
        console.info("Attempting emergency AI fallback...");
        return await geminiFallback(url);
      } catch (fallbackError) {
        throw new Error("Unable to extract video details. The video might be private or deleted.");
      }
    }
  },

  /**
   * Generates a download URL for the unified backend download pipe
   */
  getDownloadUrl(videoId: string, resolution: string, type: 'mp3' | 'mp4'): string {
    return `/api/download?id=${videoId}&resolution=${encodeURIComponent(resolution)}&type=${type}`;
  }
};
