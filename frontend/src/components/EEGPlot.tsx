import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

interface EEGPlotProps {
  data: number[][]; // [n_channels, n_samples]
}

const EEGPlot: React.FC<EEGPlotProps> = ({ data }) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef(new THREE.Scene());
  const cameraRef = useRef(new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000));
  const rendererRef = useRef(new THREE.WebGLRenderer());
  const frameIdRef = useRef<number>(); // To hold our requestAnimationFrame id

  useEffect(() => {
    // Renderer setup
    const renderer = rendererRef.current;
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current?.appendChild(renderer.domElement);

    // Camera setup
    const camera = cameraRef.current;
    camera.position.set(500, 0, 10); // Set a good initial position to see all channels
    camera.lookAt(new THREE.Vector3(500, 0, 0)); // Look towards the center of the data

    // Start the animation loop
    const animate = () => {
      frameIdRef.current = requestAnimationFrame(animate);
      renderer.render(sceneRef.current, camera);
    };

    animate();

    // Clean up on component unmount
    return () => {
      if (frameIdRef.current) {
        cancelAnimationFrame(frameIdRef.current);
      }
      mountRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  useEffect(() => {
    const scene = sceneRef.current;
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#00ffff', '#ff00ff', '#ff8800', '#88ff00', '#0088ff', '#8800ff', '#ff0088', '#00ff88', '#880088', '#888800', '#008888', '#888888'];

    // Create a line for each channel and update its geometry
    data.forEach((channelData, channelIndex) => {
      const line = scene.children[channelIndex] as THREE.Line;

      if (line) {
        // Update existing geometry
        (line.geometry as THREE.BufferGeometry).setFromPoints(
          channelData.map((value, index) => new THREE.Vector3(index, value * 10000, channelIndex))
        );
      } else {
        // Create new line geometry
        const material = new THREE.LineBasicMaterial({ color: new THREE.Color(colors[channelIndex % colors.length]) });
        const geometry = new THREE.BufferGeometry().setFromPoints(
          channelData.map((value, index) => new THREE.Vector3(index, value * 10000, channelIndex))
        );
        scene.add(new THREE.Line(geometry, material));
      }
    });

  }, [data]);

  return <div ref={mountRef} style={{ width: '100%', height: '100%' }} />;
};

export default EEGPlot;
