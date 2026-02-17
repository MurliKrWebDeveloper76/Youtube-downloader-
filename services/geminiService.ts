
import { GoogleGenAI, Type } from "@google/genai";
import { VideoMetadata } from "../types";

/**
 * Extracts the YouTube Video ID from various URL formats.
 */
const extractVideoId = (url: string): string => {
  try {
    const cleanUrl = url.trim();
    const regExp = /^.*(?:(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/|shorts\/)|(?:(?:watch)?\?v(?:i)?=))([^#&?]*).*/;
    const match = cleanUrl.match(regExp);
    if (match && match[1] && match[1].length === 11) return match[1];
    const idMatch = cleanUrl.match(/[a-zA-Z0-9_-]{11}/);
    return idMatch ? idMatch[0] : 'dQw4w9WgXcQ';
  } catch (e) {
    return 'dQw4w9WgXcQ';
  }
};

/**
 * Robust JSON cleaner for Gemini outputs.
 */
const cleanJsonResponse = (text: string): string => {
  return text.replace(/```json\n?/, '').replace(/\n?```/, '').trim();
};

export const extractMetadata = async (url: string): Promise<VideoMetadata> => {
  const videoId = extractVideoId(url);
  
  // Use a hard fallback immediately if the key is missing or invalid
  if (!process.env.API_KEY || process.env.API_KEY === 'undefined') {
    console.warn("API_KEY missing, using local simulation mode.");
    return getFallbackMetadata(videoId, url);
  }

  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `Generate realistic YouTube metadata for ID: ${videoId}. 
      Return JSON with fields: title, channel, duration, views.`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            title: { type: Type.STRING },
            channel: { type: Type.STRING },
            duration: { type: Type.STRING },
            views: { type: Type.STRING },
          },
          required: ["title", "channel", "duration", "views"]
        },
      },
    });

    const data = JSON.parse(cleanJsonResponse(response.text || '{}'));

    return {
      id: videoId,
      title: data.title || 'Incredible Media Stream',
      channel: data.channel || 'Ultra Network',
      duration: data.duration || '05:20',
      views: data.views || '850K',
      thumbnailUrl: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
      url: url
    };
  } catch (error) {
    console.error('Gemini Extraction failed, using fallback:', error);
    return getFallbackMetadata(videoId, url);
  }
};

const getFallbackMetadata = (id: string, url: string): VideoMetadata => ({
  id,
  title: 'High Quality YouTube Video',
  channel: 'Content Creator',
  duration: '10:00',
  views: '1.5M',
  thumbnailUrl: `https://img.youtube.com/vi/${id}/hqdefault.jpg`,
  url
});
