import { useState } from 'react'
import { Layers, Loader2, AlertCircle } from 'lucide-react'
import ModelViewer from './components/ModelViewer'
import { CommandBar } from './components/ui/CommandBar'
import { Viewport } from './components/ui/Viewport'
import { ControlPanel } from './components/ui/ControlPanel'

// Types based on backend schemas
interface Room {
  id: string;
  name: string;
  type: string;
}

interface ArchitecturalProgram {
  rooms: Room[];
  raw_prompt: string;
}

function App() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationMode, setGenerationMode] = useState<'baseline' | 'diffusion'>('diffusion')
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d')
  
  const [layoutSvg, setLayoutSvg] = useState<string | null>(null)
  const [glbContent, setGlbContent] = useState<string | null>(null)
  
  const [program, setProgram] = useState<ArchitecturalProgram | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async (promptText: string) => {
    setIsGenerating(true)
    setLayoutSvg(null)
    setGlbContent(null)
    setError(null)
    setProgram(null)

    try {
      // 1. Parse Prompt
      const parseResponse = await fetch('/api/v1/parser/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: promptText }),
      })

      if (!parseResponse.ok) throw new Error('Failed to parse prompt')
      const parsedProgram = await parseResponse.json()
      console.log('Parsed program:', parsedProgram)
      setProgram(parsedProgram)

      // 2. Generate Layout
      const endpoint = generationMode === 'diffusion' 
        ? '/api/v1/generation/diffusion' 
        : '/api/v1/generation/baseline'

      const genResponse = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedProgram),
      })

      if (!genResponse.ok) throw new Error('Failed to generate layout')
      const layoutData = await genResponse.json()
      console.log('Generation response:', layoutData)
      setLayoutSvg(layoutData.svg_content)
      
      if (layoutData.glb_content) {
        setGlbContent(layoutData.glb_content)
        setViewMode('3d') // Auto-switch to 3D if available
      } else {
        setViewMode('2d')
      }

    } catch (err) {
      console.error(err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      
      {/* Left Sidebar: Controls & Input */}
      <div className="w-[360px] flex flex-col border-r border-border bg-card/30 backdrop-blur-sm z-10 flex-shrink-0">
        {/* Header */}
        <div className="p-6 border-b border-border">
            <h1 className="font-mono font-bold tracking-tighter text-xl">
            ARchitecture<span className="font-light">AI</span>
            </h1>
            <p className="text-xs text-muted-foreground mt-1 font-mono">
            Generative Spatial Design Studio
            </p>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
            
            {/* Control Panel */}
            <ControlPanel 
                generationMode={generationMode}
                setGenerationMode={setGenerationMode}
                viewMode={viewMode}
                setViewMode={setViewMode}
                className="w-full"
            />

            {/* Command Input */}
            <div className="space-y-3">
                <label className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground pl-1">
                    Design Prompt
                </label>
                <CommandBar 
                    onSubmit={handleGenerate}
                    isProcessing={isGenerating}
                    className="w-full"
                />
            </div>
            
        </div>

        {/* Footer Info */}
        <div className="p-4 border-t border-border bg-muted/10">
            <div className="text-[10px] text-muted-foreground font-mono flex justify-between items-center">
                <span>v0.1.0-alpha</span>
                <span className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                    System Ready
                </span>
            </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 relative flex flex-col min-w-0 bg-muted/5">
        <Viewport 
          title="ACTIVE PROJECT"
          className="h-full w-full rounded-none border-none shadow-none"
          tools={
            program && (
              <div className="flex items-center gap-2 px-2 py-1 bg-background/50 rounded text-xs text-muted-foreground border border-border/50">
                <Layers size={12} />
                <span>{program.rooms.length} Units Detected</span>
              </div>
            )
          }
        >
          {/* Content Area */}
          <div className="w-full h-full flex items-center justify-center relative">
            {!layoutSvg && !glbContent ? (
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto border border-dashed border-border rounded-lg flex items-center justify-center bg-background/50">
                  <Layers className="text-muted-foreground/30" />
                </div>
                <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">No Layout Generated</p>
                    <p className="text-xs text-muted-foreground font-mono">
                    Enter a prompt in the sidebar to begin.
                    </p>
                </div>
              </div>
            ) : (
              <>
                {viewMode === '2d' && layoutSvg && (
                  <div 
                    className="bg-white shadow-lg border border-border/10 p-12 max-w-[90%] max-h-[90%] overflow-auto rounded-sm animate-in fade-in duration-500"
                    dangerouslySetInnerHTML={{ __html: layoutSvg }}
                  />
                )}
                {viewMode === '3d' && glbContent && (
                  <div className="w-full h-full animate-in fade-in duration-500">
                    <ModelViewer glbBase64={glbContent} />
                  </div>
                )}
              </>
            )}

            {/* Loading Overlay */}
            {isGenerating && (
              <div className="absolute inset-0 bg-background/50 backdrop-blur-sm z-50 flex flex-col items-center justify-center gap-4">
                <Loader2 className="animate-spin text-primary" size={32} />
                <div className="font-mono text-xs tracking-widest text-muted-foreground">PROCESSING ARCHITECTURE...</div>
              </div>
            )}

            {/* Error Overlay */}
            {error && (
              <div className="absolute bottom-8 right-8 bg-destructive/5 border border-destructive/20 text-destructive p-4 rounded-md shadow-lg max-w-md animate-in slide-in-from-bottom-4">
                <div className="flex items-start gap-3">
                  <AlertCircle size={18} className="mt-0.5" />
                  <div className="space-y-1">
                    <h4 className="font-medium text-sm">Generation Failed</h4>
                    <p className="text-xs opacity-90">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Viewport>
      </div>

    </div>
  )
}

export default App
