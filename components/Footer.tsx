
import React from 'react';
import { Youtube, Twitter, Github, Mail, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 pt-20 pb-10 px-6 mt-20">
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
        <div className="col-span-1 md:col-span-2 space-y-6">
          <div className="flex items-center gap-2">
            <Youtube className="w-8 h-8 text-red-500 fill-red-500" />
            <span className="text-2xl font-bold tracking-tight">YT Ultra</span>
          </div>
          <p className="text-slate-500 dark:text-slate-400 max-w-sm font-medium leading-relaxed">
            The world's premier YouTube media extractor. Built for speed, privacy, 
            and high-fidelity output. No ads, no tracking, just content.
          </p>
          <div className="flex gap-4">
            <SocialLink icon={<Twitter className="w-5 h-5" />} />
            <SocialLink icon={<Github className="w-5 h-5" />} />
            <SocialLink icon={<Mail className="w-5 h-5" />} />
          </div>
        </div>

        <div>
          <h4 className="font-bold text-lg mb-6">Product</h4>
          <ul className="space-y-4 text-slate-500 dark:text-slate-400 font-medium">
            <li><a href="#" className="hover:text-red-500 transition-colors">Video Downloader</a></li>
            <li><a href="#" className="hover:text-red-500 transition-colors">MP3 Converter</a></li>
            <li><a href="#" className="hover:text-red-500 transition-colors">HD Thumbnails</a></li>
            <li><a href="#" className="hover:text-red-500 transition-colors">Browser Extension</a></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-lg mb-6">Legal</h4>
          <ul className="space-y-4 text-slate-500 dark:text-slate-400 font-medium">
            <li><a href="#" className="hover:text-red-500 transition-colors">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-red-500 transition-colors">Terms of Service</a></li>
            <li><a href="#" className="hover:text-red-500 transition-colors">DMCA Notice</a></li>
            <li><a href="#" className="hover:text-red-500 transition-colors">Contact Support</a></li>
          </ul>
        </div>
      </div>

      <div className="max-w-6xl mx-auto mt-20 pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-col md:row items-center justify-between gap-4">
        <p className="text-slate-400 text-sm font-medium">
          © 2024 YT Ultra Downloader. All rights reserved.
        </p>
        <p className="text-slate-400 text-sm flex items-center gap-1 font-medium">
          Made with <Heart className="w-4 h-4 text-red-500 fill-red-500" /> by Ultra Engineering
        </p>
      </div>
    </footer>
  );
};

const SocialLink: React.FC<{ icon: React.ReactNode }> = ({ icon }) => (
  <a href="#" className="p-3 bg-slate-100 dark:bg-slate-800 rounded-xl text-slate-500 hover:text-red-500 transition-all hover:-translate-y-1">
    {icon}
  </a>
);
