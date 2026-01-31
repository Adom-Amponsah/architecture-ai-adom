import { LayoutTemplate, Box, Settings2, Sliders } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ControlPanelProps {
  generationMode: 'baseline' | 'diffusion';
  setGenerationMode: (mode: 'baseline' | 'diffusion') => void;
  viewMode: '2d' | '3d';
  setViewMode: (mode: '2d' | '3d') => void;
  className?: string;
}

export function ControlPanel({ 
  generationMode, 
  setGenerationMode, 
  viewMode, 
  setViewMode,
  className 
}: ControlPanelProps) {
  return (
    <div className={cn("flex flex-col gap-4 p-4 border border-border rounded-lg shadow-sm bg-card", className)}>
      
      {/* Section: View Mode */}
      <div className="space-y-2">
        <label className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground flex items-center gap-2">
          <Settings2 size={12} />
          View Mode
        </label>
        <div className="flex bg-muted p-1 rounded-md">
          <button
            onClick={() => setViewMode('2d')}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-1.5 text-xs font-medium rounded-sm transition-all",
              viewMode === '2d' 
                ? "bg-background text-foreground shadow-sm" 
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <LayoutTemplate size={14} />
            2D Plan
          </button>
          <button
            onClick={() => setViewMode('3d')}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-1.5 text-xs font-medium rounded-sm transition-all",
              viewMode === '3d' 
                ? "bg-background text-foreground shadow-sm" 
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Box size={14} />
            3D Model
          </button>
        </div>
      </div>

      <div className="h-px bg-border/50" />

      {/* Section: Generation Engine */}
      <div className="space-y-2">
        <label className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground flex items-center gap-2">
          <Sliders size={12} />
          Generation Engine
        </label>
        
        <div className="grid gap-2">
          <button
            onClick={() => setGenerationMode('baseline')}
            className={cn(
              "text-left px-3 py-2 rounded-md border text-xs transition-all",
              generationMode === 'baseline'
                ? "bg-primary/5 border-primary/20 text-primary"
                : "bg-transparent border-transparent hover:bg-muted text-muted-foreground"
            )}
          >
            <div className="font-medium mb-0.5">Template Match</div>
            <div className="text-[10px] opacity-70">Deterministic pattern matching from database</div>
          </button>

          <button
            onClick={() => setGenerationMode('diffusion')}
            className={cn(
              "text-left px-3 py-2 rounded-md border text-xs transition-all",
              generationMode === 'diffusion'
                ? "bg-primary/5 border-primary/20 text-primary"
                : "bg-transparent border-transparent hover:bg-muted text-muted-foreground"
            )}
          >
            <div className="font-medium mb-0.5">AI Diffusion</div>
            <div className="text-[10px] opacity-70">Generative graph diffusion for novel layouts</div>
          </button>
        </div>
      </div>

    </div>
  );
}
