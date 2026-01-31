import { cn } from '@/lib/utils';

interface ViewportProps {
  children?: React.ReactNode;
  title?: string;
  className?: string;
  tools?: React.ReactNode;
}

export function Viewport({ children, title = "VIEWPORT", className, tools }: ViewportProps) {
  return (
    <div className={cn("flex flex-col h-full border border-border bg-card overflow-hidden rounded-md", className)}>
      {/* Viewport Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-muted/30">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary/20"></span>
          <span className="text-xs font-mono font-medium text-muted-foreground tracking-widest">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {tools}
        </div>
      </div>

      {/* Canvas Area */}
      <div className="relative flex-1 bg-background overflow-hidden group">
        {/* Grid Background Pattern */}
        <div className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none" 
             style={{ 
               backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)',
               backgroundSize: '40px 40px'
             }} 
        />
        
        {/* Content */}
        <div className="relative z-10 w-full h-full">
          {children}
        </div>

        {/* Corner Indicators */}
        <div className="absolute top-4 left-4 w-4 h-4 border-l border-t border-primary/20 pointer-events-none" />
        <div className="absolute top-4 right-4 w-4 h-4 border-r border-t border-primary/20 pointer-events-none" />
        <div className="absolute bottom-4 left-4 w-4 h-4 border-l border-b border-primary/20 pointer-events-none" />
        <div className="absolute bottom-4 right-4 w-4 h-4 border-r border-b border-primary/20 pointer-events-none" />
      </div>
    </div>
  );
}
