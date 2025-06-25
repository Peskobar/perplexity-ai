import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { useTheme } from '@/context/ThemeContext'; // Hook do motywu

// Komponent animowanej sfery
const DistortedSphere = ({ kolor }) => {
  const ref = useRef();
  useFrame((state) => {
    // Prosta animacja obrotu sfery
    if (ref.current) {
       // ref.current.rotation.y += 0.001;
       // ref.current.rotation.x += 0.0005;
    }
  });

  return (
    <Sphere args={[1, 64, 64]} scale={2}> {/* args: [radius, widthSegments, heightSegments], scale dostosowuje rozmiar */}
      <MeshDistortMaterial
        color={kolor} // Kolor sfery
        attach="material"
        distort={0.5} // Siła zniekształcenia
        speed={2}    // Prędkość animacji zniekształcenia
        roughness={0.5} // Chropowatość materiału
      />
    </Sphere>
  );
};


const Tlo3D: React.FC = () => {
  const { theme } = useTheme(); // Pobierz aktualny motyw
  const [kolorSfery, setKolorSfery] = useState<string>('#5c6bc0'); // Domyślny kolor (odcień primary)

  // Zmieniaj kolor sfery w zależności od motywu
  useEffect(() => {
    // Możesz pobrać kolory z CSS variables lub zdefiniować je tutaj
    if (theme === 'ciemny') {
      setKolorSfery('#7b8ec8'); // Odcień primary w trybie ciemnym
    } else {
      setKolorSfery('#5c6bc0'); // Odcień primary w trybie jasnym
    }
     // Użyj opóźnienia lub animacji koloru dla płynniejszego przejścia
  }, [theme]);

  return (
    // Kontener Canvas z react-three-fiber
    // Kamerę można dostosować, dodać oświetlenie itp.
    <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
      {/* Proste oświetlenie */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />

      {/* Komponent animowanej sfery */}
      <DistortedSphere kolor={kolorSfery} />

      {/* OrbitControls pozwala na interakcję myszą (dla debugowania/efektu) */}
      {/* <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} /> */}
      {/* Usunąłem OrbitControls, żeby tło było statyczne, chyba że potrzebujesz interakcji */}
    </Canvas>
  );
};

export default Tlo3D;
