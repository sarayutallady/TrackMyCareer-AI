import { useEffect, useRef } from "react";
import NET from "vanta/dist/vanta.net.min";
import * as THREE from "three";

export default function Background3D() {
  const vantaRef = useRef(null);
  const vantaEffect = useRef(null);

  useEffect(() => {
    let resizeObserver;

    const initVanta = () => {
      if (vantaEffect.current) return;

      vantaEffect.current = NET({
        el: vantaRef.current,
        THREE,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,

         
        minHeight: document.body.scrollHeight,
        minWidth: window.innerWidth,

        scale: 1.0,
        scaleMobile: 1.0,
        color: 0xff009d,
        backgroundColor: 0x0b0e1a,
        points: 12.0,
        maxDistance: 22.0,
        spacing: 18.0,
      });
    };

    const timer = setTimeout(initVanta, 50);

    // 🔥 Recalculate height dynamically when page grows
    resizeObserver = new ResizeObserver(() => {
      if (vantaRef.current) {
        vantaRef.current.style.height = document.body.scrollHeight + "px";
      }
    });

    resizeObserver.observe(document.body);

    return () => {
      clearTimeout(timer);
      if (vantaEffect.current) vantaEffect.current.destroy();
      if (resizeObserver) resizeObserver.disconnect();
    };
  }, []);

  return (
    <div
      ref={vantaRef}
      className="fixed inset-0 w-full -z-10"
      style={{
        height: "100%",             
        minHeight: "100vh",
        position: "fixed",          
      }}
    />
  );
}
