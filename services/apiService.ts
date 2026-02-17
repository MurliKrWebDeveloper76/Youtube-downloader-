
import { VideoMetadata } from "../types";

export const apiService = {
  /**
   * Calls the Python backend to extract real metadata using yt-dlp
   */
  async extractMetadata(url: string): Promise<VideoMetadata> {
    try {
      const response = await fetch('/api/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const contentType = response.headers.get("content-type");
      
      if (!response.ok) {
        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Server error: ${response.status}`);
        } else {
          const text = await response.text();
          console.error("Backend returned non-JSON error:", text);
          throw new Error(`Backend Error (${response.status}): The server returned an unexpected response. This usually means the API route is missing or the backend failed.`);
        }
      }

      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        console.error("Expected JSON but got:", text);
        throw new Error("Invalid response from server. Expected JSON metadata.");
      }

      return await response.json();
    } catch (error: any) {
      console.error("apiService.extractMetadata error:", error);
      throw error;
    }
  },

  /**
   * Generates a conceptual download URL for the backend
   */
  getDownloadUrl(videoId: string, format: string): string {
    return `/api/download?id=${videoId}&format=${encodeURIComponent(format)}`;
  }
};
