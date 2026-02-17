
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
          'Accept': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const contentType = response.headers.get("content-type");
      
      // If we receive HTML, the server likely returned a 404 or a 500 error page
      if (contentType && contentType.includes("text/html")) {
        console.error("Critical: Received HTML response. Check Vercel logs.");
        throw new Error("Backend unavailable. The server returned an error page instead of JSON. This may be due to a deployment issue or a 404 error.");
      }

      if (!response.ok) {
        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Error ${response.status}: Failed to process video.`);
        }
        throw new Error(`Server Error (${response.status}). Please try again later.`);
      }

      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Invalid response format received from the server.");
      }

      const data = await response.json();
      return data;
    } catch (error: any) {
      console.error("apiService.extractMetadata error details:", error);
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
