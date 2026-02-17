
import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export const FAQ: React.FC = () => {
  const faqs = [
    { q: "Is YT Ultra free to use?", a: "Yes, our tool is 100% free with no hidden charges or subscriptions required for basic usage." },
    { q: "What formats are supported?", a: "We support high-quality MP4 video (up to 4K) and MP3 audio (up to 320kbps)." },
    { q: "Is there a limit on download size?", a: "No, you can download videos of any length, though larger files will take longer to process." },
    { q: "Do I need to install any software?", a: "No, YT Ultra is a web-based tool that works directly in your browser on desktop and mobile." },
  ];

  return (
    <section id="faq" className="py-20 px-6 max-w-3xl mx-auto space-y-12">
      <div className="text-center">
        <h2 className="text-4xl font-black mb-4">Common Questions</h2>
        <p className="text-slate-500">Everything you need to know about our service.</p>
      </div>

      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <AccordionItem key={i} question={faq.q} answer={faq.a} />
        ))}
      </div>
    </section>
  );
};

const AccordionItem: React.FC<{ question: string, answer: string }> = ({ question, answer }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="glass rounded-2xl overflow-hidden shadow-sm transition-all hover:shadow-md">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 text-left flex items-center justify-between font-bold text-lg"
      >
        {question}
        {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </button>
      <div className={`px-6 overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? 'max-h-40 pb-6 opacity-100' : 'max-h-0 opacity-0'}`}>
        <p className="text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
          {answer}
        </p>
      </div>
    </div>
  );
};
