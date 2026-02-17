
import React, { useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { DownloaderCard } from './components/DownloaderCard';
import { DownloadHistory } from './components/DownloadHistory';
import { FAQ } from './components/FAQ';
import { Footer } from './components/Footer';
import { useLocalStorage } from './hooks/useLocalStorage';
import { Theme, HistoryItem } from './types';
import { ArrowUp } from 'lucide-react';

const App: React.FC = () => {
  const [theme, setTheme] = useLocalStorage<Theme>('theme', Theme.DARK);
  const [history, setHistory] = useLocalStorage<HistoryItem[]>('download-history', []);

  useEffect(() => {
    if (theme === Theme.DARK) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('bg-slate-950', 'text-slate-100');
      document.body.classList.remove('bg-slate-50', 'text-slate-900');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.add('bg-slate-50', 'text-slate-900');
      document.body.classList.remove('bg-slate-950', 'text-slate-100');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === Theme.LIGHT ? Theme.DARK : Theme.LIGHT);
  };

  const handleDownloadSuccess = (item: HistoryItem) => {
    setHistory([item, ...history].slice(0, 10)); // Keep last 10
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const deleteHistoryItem = (id: string) => {
    setHistory(history.filter(i => i.id !== id));
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen selection:bg-red-500 selection:text-white">
      <Navbar theme={theme} onThemeToggle={toggleTheme} />
      
      <main>
        <Hero />
        
        <DownloaderCard onSuccess={handleDownloadSuccess} />
        
        <section id="features" className="py-20 px-6 max-w-6xl mx-auto space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-4xl md:text-5xl font-black">Power-Packed Features</h2>
            <p className="text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">
              We've engineered the fastest extraction engine to give you unparalleled media quality.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              title="Crystal Clear 4K"
              desc="Download videos in their original maximum resolution without losing a single pixel."
              color="text-blue-500"
            />
            <FeatureCard 
              title="Studio-Grade Audio"
              desc="Extract high-fidelity 320kbps MP3s perfect for offline listening on any device."
              color="text-purple-500"
            />
            <FeatureCard 
              title="Private & Anonymous"
              desc="We don't track your downloads or save your URLs. Your activity stays yours."
              color="text-emerald-500"
            />
          </div>
        </section>

        <DownloadHistory 
          items={history} 
          onClear={clearHistory} 
          onDelete={deleteHistoryItem} 
        />

        <FAQ />
      </main>

      <Footer />

      <button 
        onClick={scrollToTop}
        className="fixed bottom-8 right-8 p-4 bg-red-600 text-white rounded-2xl shadow-2xl shadow-red-500/40 hover:bg-red-700 transition-all hover:-translate-y-2 z-40 active:scale-90"
      >
        <ArrowUp className="w-6 h-6" />
      </button>
    </div>
  );
};

const FeatureCard: React.FC<{ title: string, desc: string, color: string }> = ({ title, desc, color }) => (
  <div className="glass p-8 rounded-3xl space-y-4 shadow-sm hover:shadow-xl transition-all border-b-4 border-transparent hover:border-red-500/50">
    <h3 className={`text-2xl font-bold ${color}`}>{title}</h3>
    <p className="text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
      {desc}
    </p>
  </div>
);

export default App;
