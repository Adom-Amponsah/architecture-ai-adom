import React, { Suspense, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage, Grid } from '@react-three/drei';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

interface ModelViewerProps {
  glbBase64: string;
}

function Model({ glbBase64 }: { glbBase64: string }) {
  const gltf = useMemo(() => {
    // Decode base64 to blob
    const byteCharacters = atob(glbBase64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'model/gltf-binary' });
    const url = URL.createObjectURL(blob);
    
    // We can't use useGLTF hook directly with a dynamic URL created inside render loop easily
    // But since we want to trigger reload when prop changes, let's use a loader manually 
    // or rely on the fact that we are passing this url to a component.
    
    return url;
  }, [glbBase64]);

  // useGLTF expects a url string.
  // Note: useGLTF caches based on URL.
  const { scene } = useGLTF(gltf);

  return <primitive object={scene} />;
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
