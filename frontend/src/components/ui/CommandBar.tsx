import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ArrowRight, Terminal, Loader2, CornerDownLeft } from 'lucide-react';

interface CommandBarProps {
  onSubmit: (prompt: string) => void;
  isProcessing?: boolean;
  className?: string;
}

export function CommandBar({ onSubmit, isProcessing, className }: CommandBarProps) {
  const [value, setValue] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Auto-focus on mount like a real command line
    inputRef.current?.focus();
    
    // Listen for '/' key to focus
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !isProcessing) {
      onSubmit(value);
      // Optional: keep text or clear it. Usually clearing is better for "commands" but for prompts maybe keeping is better? 
      // Let's clear for now as per previous behavior.
      // setValue(''); 
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={cn("w-full flex flex-col gap-2", className)}>
      <form 
        onSubmit={handleSubmit}
        className="relative flex flex-col group bg-background border border-border rounded-lg shadow-sm focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all"
      >
        <div className="absolute left-3 top-3 text-muted-foreground/50">
          <Terminal size={16} />
        </div>
        
        <textarea
          ref={inputRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your architectural vision...
(e.g. 'A modern 2-bedroom apartment with an open kitchen')"
          className="w-full min-h-[120px] p-3 pl-10 bg-transparent border-none resize-none 
                     font-mono text-sm focus:outline-none 
                     placeholder:text-muted-foreground/50"
          disabled={isProcessing}
        />

        <div className="flex items-center justify-between p-2 border-t border-border/50 bg-muted/20 rounded-b-lg">
           <span className="text-[10px] text-muted-foreground font-mono px-2">
            CMD: GENERATE_LAYOUT
          </span>

          {isProcessing ? (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 text-primary rounded text-xs font-medium">
                <Loader2 className="animate-spin" size={14} />
                <span>PROCESSING</span>
            </div>
          ) : (
            <button 
              type="submit"
              disabled={!value.trim()}
              className="flex items-center gap-2 px-3 py-1.5 bg-primary text-primary-foreground rounded text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              <span>EXECUTE</span>
              <CornerDownLeft size={14} />
            </button>
          )}
        </div>
      </form>
      <div className="flex justify-between px-1">
        <span className="text-[10px] text-muted-foreground font-mono">
          Shift + Enter for new line
        </span>
      </div>
    </div>
  );
}
