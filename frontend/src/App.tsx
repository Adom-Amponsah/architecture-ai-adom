import { useState } from 'react'
import { LayoutDashboard, Box, Settings, Loader2 } from 'lucide-react'

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
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [layoutSvg, setLayoutSvg] = useState<string | null>(null)
  const [program, setProgram] = useState<ArchitecturalProgram | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsGenerating(true)
    setLayoutSvg(null)
    setError(null)
    setProgram(null)

    try {
      // 1. Parse Prompt
      const parseResponse = await fetch('/api/v1/parser/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: prompt }),
      })

      if (!parseResponse.ok) throw new Error('Failed to parse prompt')
      const parsedProgram = await parseResponse.json()
      setProgram(parsedProgram)

      // 2. Generate Baseline Layout
      const genResponse = await fetch('/api/v1/generation/baseline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedProgram),
      })

      if (!genResponse.ok) throw new Error('Failed to generate layout')
      const layoutData = await genResponse.json()
      setLayoutSvg(layoutData.svg_content)

    } catch (err) {
      console.error(err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="flex h-screen w-full bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            ARchitectureAI
          </h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <button className="flex items-center space-x-3 w-full p-3 rounded-lg bg-blue-50 text-blue-600">
            <LayoutDashboard size={20} />
            <span className="font-medium">Design Studio</span>
          </button>
          <button className="flex items-center space-x-3 w-full p-3 rounded-lg text-gray-600 hover:bg-gray-50">
            <Box size={20} />
            <span className="font-medium">Projects</span>
          </button>
          <button className="flex items-center space-x-3 w-full p-3 rounded-lg text-gray-600 hover:bg-gray-50">
            <Settings size={20} />
            <span className="font-medium">Settings</span>
          </button>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6 justify-between">
          <h2 className="text-lg font-semibold text-gray-800">New Design Project</h2>
        </header>

        {/* Workspace */}
        <div className="flex-1 flex overflow-hidden">
          {/* Prompt Panel */}
          <div className="w-96 bg-white border-r border-gray-200 p-6 overflow-y-auto flex flex-col gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Design Requirements
              </label>
              <textarea
                className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="Describe your architectural needs (e.g., 'A modern 2-bedroom apartment with an open kitchen and large balcony facing south...')"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>
            
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt}
              className={`w-full py-3 px-4 rounded-lg text-white font-medium flex items-center justify-center space-x-2
                ${isGenerating || !prompt 
                  ? 'bg-gray-300 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30'}`}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Processing...</span>
                </>
              ) : (
                <span>Generate Layout</span>
              )}
            </button>

            {error && (
              <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm border border-red-100">
                {error}
              </div>
            )}

            {/* Constraint Visualizer */}
            {program && (
              <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <h3 className="text-sm font-medium text-gray-500 mb-3">Detected Constraints</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>Rooms detected:</span>
                    <span className="font-medium">{program.rooms.length}</span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {program.rooms.map((room) => (
                      <span key={room.id} className="px-2 py-1 bg-white border border-gray-200 rounded text-xs text-gray-600">
                        {room.name}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Visualization Viewport */}
          <div className="flex-1 bg-gray-100 relative flex flex-col">
            
            {/* Toggle View (Placeholder) */}
            <div className="absolute top-4 right-4 z-10 bg-white rounded-lg shadow-sm border border-gray-200 p-1 flex">
              <button className="px-3 py-1 text-sm font-medium bg-gray-100 rounded text-gray-800">2D Plan</button>
              <button className="px-3 py-1 text-sm font-medium text-gray-500 hover:text-gray-800">3D Model</button>
            </div>

            {/* Content Area */}
            <div className="flex-1 flex items-center justify-center p-8">
              {layoutSvg ? (
                <div 
                  className="bg-white shadow-xl rounded-lg p-8 max-w-full max-h-full overflow-auto"
                  dangerouslySetInnerHTML={{ __html: layoutSvg }}
                />
              ) : (
                <div className="text-center text-gray-400">
                  <LayoutDashboard size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Enter a prompt to generate a floorplan</p>
                </div>
              )}
            </div>
            
            {/* 3D Canvas (Hidden for MVP 2D focus, or we can show it below) */}
            {/* 
            <div className="h-1/3 border-t border-gray-200 relative">
               <Canvas camera={{ position: [5, 5, 5], fov: 50 }}>
                  <ambientLight intensity={0.5} />
                  <pointLight position={[10, 10, 10]} />
                  <OrbitControls makeDefault />
                  <gridHelper args={[20, 20]} />
                  <mesh position={[0, 0.5, 0]}>
                    <boxGeometry />
                    <meshStandardMaterial color="orange" />
                  </mesh>
                </Canvas>
            </div>
            */}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
