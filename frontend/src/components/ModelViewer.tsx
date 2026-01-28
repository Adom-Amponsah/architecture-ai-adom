import React, { Suspense, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage, Grid } from '@react-three/drei';

interface ModelViewerProps {
  glbBase64: string;
}

function ModelContent({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

function Model({ glbBase64 }: { glbBase64: string }) {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    try {
      // Decode base64 to blob
      const byteCharacters = atob(glbBase64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'model/gltf-binary' });
      const objectUrl = URL.createObjectURL(blob);
      
      setUrl(objectUrl);

      // Cleanup
      return () => {
        URL.revokeObjectURL(objectUrl);
        useGLTF.clear(objectUrl);
      };
    } catch (e) {
      console.error("Error decoding GLB:", e);
    }
  }, [glbBase64]);

  if (!url) return null;

  return <ModelContent url={url} />;
}

const ModelViewer: React.FC<ModelViewerProps> = ({ glbBase64 }) => {
  return (
    <div className="w-full h-full bg-gray-900 rounded-lg overflow-hidden">
      <Canvas camera={{ position: [5, 5, 5], fov: 50 }} shadows>
        <Suspense fallback={null}>
          <Stage environment="city" intensity={0.6}>
            <Model glbBase64={glbBase64} />
          </Stage>
          <Grid args={[20, 20]} cellColor="white" sectionColor="white" fadeDistance={20} />
          <OrbitControls makeDefault autoRotate autoRotateSpeed={0.5} />
        </Suspense>
      </Canvas>
    </div>
  );
};

export default ModelViewer;
