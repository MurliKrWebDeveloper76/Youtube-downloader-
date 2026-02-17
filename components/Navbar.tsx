
import React from 'react';
import { Sun, Moon, Play, Download } from 'lucide-react';
import { Theme } from '../types';

interface NavbarProps {
  theme: Theme;
  onThemeToggle: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ theme, onThemeToggle }) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 glass">
      <div className="flex items-center gap-2 group cursor-pointer">
        <div className="relative">
          <Play className="w-8 h-8 text-red-500 fill-red-500 transition-transform group-hover:scale-110" />
          <Download className="absolute -bottom-1 -right-1 w-4 h-4 text-white bg-slate-900 rounded-full p-0.5 border border-white" />
        </div>
        <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-rose-600 dark:from-red-400 dark:to-rose-500">
          YT Ultra
        </span>
      </div>

      <div className="hidden md:flex items-center gap-8 text-sm font-medium dark:text-slate-300">
        <a href="#downloader" className="hover:text-red-500 transition-colors">Downloader</a>
        <a href="#features" className="hover:text-red-500 transition-colors">Features</a>
        <a href="#faq" className="hover:text-red-500 transition-colors">FAQ</a>
      </div>

      <button
        onClick={onThemeToggle}
        className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
      >
        {theme === Theme.LIGHT ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5 text-yellow-400" />}
      </button>
    </nav>
  );
};
