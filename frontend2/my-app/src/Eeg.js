import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { useEffect, useRef, useState } from "react";

// Three.js
let scene = new THREE.Scene();
scene.add(new THREE.AmbientLight(0xcccccc));
var camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.set(-20, 1.3, 0);
var renderer = new THREE.WebGLRenderer();
const _controls = new OrbitControls(camera, renderer.domElement);
const clock = new THREE.Clock();

const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
renderer.setClearColor(0xffffff, 0);
// Soft white light
scene.add(ambientLight);

// Directional Light
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(1, 1, 1); // Position the light
scene.add(directionalLight);
// End Three.js

// Constants
const maxDataPoints = 625; // 5 seconds of data at 125 points per second
const scaleFactor = 1000; // Adjust this factor based on your data's range
const animationDuration = 5; /// Maximum data points to display
var size = 50;
var divisions = 125;

function Eeg() {
  const refContainer = useRef(null); // div for Three.js
  const dataRef = useRef(Array.from({ length: 16 }, () => Array(1).fill(0))); // 16 channels of data global store
  const [isReadyForAnimation, setIsReadyForAnimation] = useState(false); // Flag to start animation
  const [data, setData] = useState(
    Array.from({ length: 16 }, () => Array(1).fill(0))
  ); // Data to be displayed in scene [channel][data
  const animationRequestRef = useRef(null); // Reference to animation request
  const lineMeshesRef = useRef([]); // Reference to line meshes displayed in scene
  const [tubes, setTubes] = useState([]); // Reference to line meshes displayed in scene
  const ws = useRef(null); // Reference to WebSocket

  // Setup WebSocket and Three.js
  useEffect(() => {
    if (!ws.current) {
      ws.current = new WebSocket("ws://localhost:8000/ws");
      ws.current.onopen = () => {
        console.log("WebSocket Connected");
      };

      ws.current.onmessage = (event) => {
        if (event.data) {
          let newData = JSON.parse(event.data);
          if (newData.length === 0) {
            return;
          }
          //console.log("New data",newData);
          //console.log("I setup the data");
          dataRef.current = dataRef.current.map((subArray, index) => {
            return [...subArray, ...(newData[index] || [])];
          });
          setData(newData);

          //console.log("I setup the data");

          // Check if we have enough data for animation
          if (
            !isReadyForAnimation &&
            dataRef.current[0].length >= maxDataPoints
          ) {
            console.log("I am ready for animation");
            setIsReadyForAnimation(true);
          }
        }
      };

      renderer.setSize(window.innerWidth, window.innerHeight);
      refContainer.current &&
        refContainer.current.appendChild(renderer.domElement);

      scene.add(new THREE.GridHelper(size, divisions));

      let animate = function () {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
      };
      animate();
    }
  }, []);

  // Animate
  useEffect(() => {
    console.log({ isReadyForAnimation });

    // sleep for 5 seconds
    setTimeout(() => {}, 5000);

    if (isReadyForAnimation) {
      console.log("I am animating");
      const nextChunk = dataRef.current.map((channel) =>
        channel.slice(0, maxDataPoints)
      );

      // Create Tube Geometries
      const tubeGeometries = createTubeGeometries(data);
      setTubes(tubeGeometries);
      console.log({ tubeGeometries });
      let elapsedTime = 0;

      const animate = () => {
        animationRequestRef.current = requestAnimationFrame(animate);

        elapsedTime += clock.getDelta();

        if (elapsedTime >= animationDuration) {
          removeLineMeshes();
          elapsedTime = 0;
          dataRef.current = dataRef.current.map((channel) =>
            channel.slice(maxDataPoints)
          );
          const hasEnoughDataForAnimation =
            dataRef.current[0].length >= maxDataPoints;
          setIsReadyForAnimation(true);
        }

        renderer.render(scene, camera);
      };
      animate();
    }
  }, [isReadyForAnimation]);

  const createTubeGeometries = (data) => {
    return data.map((channelData, index) => {
      const points = channelData.map(
        (value, i) =>
          new THREE.Vector3(0, value * scaleFactor + index, (i / 125) * 10 - 5)
      );
      const path = new THREE.CatmullRomCurve3(points);
      const tubeGeometry = new THREE.TubeGeometry(path, 64, 0.1, 8, true);
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(
          `hsl(${(index / data.length) * 360}, 100%, 50%)`
        ),
        specular: 0x555555,
        shininess: 30,
      });
      const tube = new THREE.Mesh(tubeGeometry, material);
      return tube;
    });
  };

  useEffect(() => {
    // Update the scene with new tubes
    if (isReadyForAnimation) {
      setTubes((prevTubes) => {
        // Remove old tubes from the scene
        prevTubes.forEach((tube) => {
          scene.remove(tube);
          tube.geometry.dispose();
          tube.material.dispose();
        });

        // Create and return new tubes
        const newTubes = createTubeGeometries(data);
        newTubes.forEach((tube) => scene.add(tube));
        return newTubes;
      });
    }
  }, [tubes]);

  const removeLineMeshes = () => {
    lineMeshesRef.current.forEach((mesh) => {
      scene.remove(mesh);
      mesh.geometry.dispose();
      mesh.material.dispose();
    });
    lineMeshesRef.current = [];
  };

  return <div ref={refContainer} />;
}

export default Eeg;
