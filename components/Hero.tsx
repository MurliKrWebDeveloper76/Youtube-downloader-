
import React from 'react';
import { Zap, Shield, Rocket, Sparkles } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <div className="relative pt-32 pb-12 px-6 text-center space-y-8 overflow-hidden">
      {/* Background Blobs */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-red-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob" />
      <div className="absolute top-0 -right-4 w-72 h-72 bg-rose-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000" />
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000" />

      <div className="relative inline-flex items-center gap-2 px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full text-sm font-bold animate-bounce">
        <Sparkles className="w-4 h-4" />
        Most Advanced YouTube Downloader
      </div>

      <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-tight">
        Download Without <br />
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-red-500 via-rose-500 to-rose-600">
          Limits. Fast. Secure.
        </span>
      </h1>

      <p className="max-w-2xl mx-auto text-lg md:text-xl text-slate-500 dark:text-slate-400 font-medium">
        Experience the next generation of media downloading. Instant extraction, 
        premium qualities up to 4K, and seamless MP3 conversion.
      </p>

      <div className="flex flex-wrap justify-center gap-6 mt-12">
        <FeatureBadge icon={<Zap className="w-4 h-4" />} text="Instant Processing" />
        <FeatureBadge icon={<Shield className="w-4 h-4" />} text="Virus Free" />
        <FeatureBadge icon={<Rocket className="w-4 h-4" />} text="High Speed" />
      </div>
    </div>
  );
};

const FeatureBadge: React.FC<{ icon: React.ReactNode, text: string }> = ({ icon, text }) => (
  <div className="flex items-center gap-2 px-4 py-2 glass rounded-2xl text-sm font-bold shadow-sm">
    <span className="text-red-500">{icon}</span>
    {text}
  </div>
);
