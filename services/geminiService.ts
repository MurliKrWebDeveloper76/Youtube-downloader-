
import { GoogleGenAI, Type } from "@google/genai";
import { VideoMetadata } from "../types";

/**
 * Extracts the YouTube Video ID from various URL formats including Shorts, Embeds, and mobile links.
 */
const extractVideoId = (url: string): string => {
  try {
    const cleanUrl = url.trim();
    // Handles standard watch?v=, shorts/, and embed/ URLs
    const regExp = /^.*(?:(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/|shorts\/)|(?:(?:watch)?\?v(?:i)?=))([^#&?]*).*/;
    const match = cleanUrl.match(regExp);
    
    if (match && match[1] && match[1].length === 11) {
      return match[1];
    }
    
    // Fallback for direct ID input or messy links
    const idMatch = cleanUrl.match(/[a-zA-Z0-9_-]{11}/);
    return idMatch ? idMatch[0] : 'dQw4w9WgXcQ';
  } catch (e) {
    return 'dQw4w9WgXcQ';
  }
};

/**
 * Cleans potential markdown formatting from Gemini's JSON response
 */
const cleanJsonResponse = (text: string): string => {
  return text.replace(/```json\n?/, '').replace(/\n?```/, '').trim();
};

export const extractMetadata = async (url: string): Promise<VideoMetadata> => {
  const videoId = extractVideoId(url);
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `You are a professional YouTube Metadata simulation engine. 
      Generate realistic, high-quality metadata for the video ID: ${videoId}. 
      Return the data in strict JSON format.`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            title: { 
              type: Type.STRING,
              description: "A professional, catchy YouTube video title."
            },
            channel: { 
              type: Type.STRING,
              description: "A realistic YouTube channel name."
            },
            duration: { 
              type: Type.STRING,
              description: "The video duration in MM:SS format."
            },
            views: { 
              type: Type.STRING,
              description: "Realistic view count (e.g. 1.2M, 500K)."
            },
          },
          required: ["title", "channel", "duration", "views"]
        },
      },
    });

    const rawText = response.text || '{}';
    const cleanedText = cleanJsonResponse(rawText);
    const data = JSON.parse(cleanedText);

    return {
      id: videoId,
      title: data.title || 'Incredible Tech Showcase',
      channel: data.channel || 'UltraTech HQ',
      duration: data.duration || '12:45',
      views: data.views || '1.2M',
      thumbnailUrl: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
      url: url
    };
  } catch (error) {
    console.error('Metadata simulation failed:', error);
    // Return a convincing fallback if the API call fails
    return {
      id: videoId,
      title: 'Trending Content Item',
      channel: 'Global Media Hub',
      duration: '08:15',
      views: '2.5M',
      thumbnailUrl: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
      url: url
    };
  }
};
