
import { VideoMetadata } from "../types";
import { extractMetadata as geminiFallback } from "./geminiService";

export const apiService = {
  /**
   * Hybrid Extractor:
   * 1. Tries the Python backend (real-time data)
   * 2. If blocked by YouTube (bot detection), falls back to Gemini AI
   */
  async extractMetadata(url: string): Promise<VideoMetadata> {
    try {
      const response = await fetch('/api/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const contentType = response.headers.get("content-type");
      
      // Handle serverless HTML error pages (404/500)
      if (contentType && contentType.includes("text/html")) {
        console.warn("Backend HTML response detected. Falling back to Gemini.");
        return await geminiFallback(url);
      }

      const data = await response.json();

      if (!response.ok) {
        // If YouTube blocked the server IP, use AI to fulfill the request
        if (data.error === "bot_blocked" || response.status === 403) {
          console.info("Backend blocked by YouTube. Engaging AI metadata extraction...");
          return await geminiFallback(url);
        }
        throw new Error(data.error || `Server error: ${response.status}`);
      }

      return data;
    } catch (error: any) {
      console.error("apiService.extractMetadata primary attempt failed:", error);
      
      // Final attempt: Gemini AI. This ensures the app always works.
      try {
        console.info("Attempting emergency AI fallback...");
        return await geminiFallback(url);
      } catch (fallbackError) {
        throw new Error("Unable to extract video details. The video might be private or deleted.");
      }
    }
  },

  /**
   * Generates a conceptual download URL for the backend
   */
  getDownloadUrl(videoId: string, format: string): string {
    return `/api/download?id=${videoId}&format=${encodeURIComponent(format)}`;
  }
};
