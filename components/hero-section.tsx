'use client';

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface Particle {
  top: number;
  left: number;
  width: number;
  height: number;
  background: string;
  boxShadow: string;
  duration: number;
  delay: number;
  y: number;
  x: number;
}

interface HeroSectionProps {
  onTryDemo: () => void;
}

export default function HeroSection({ onTryDemo }: HeroSectionProps) {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    // Only run on client to avoid hydration mismatch
    const count = 30;
    const generated = Array.from({ length: count }).map(() => ({
      top: Math.random() * 100,
      left: Math.random() * 100,
      width: Math.random() * 6 + 2,
      height: Math.random() * 6 + 2,
      background: `rgba(${Math.floor(Math.random() * 100 + 100)}, ${Math.floor(Math.random() * 100)}, ${Math.floor(Math.random() * 255)}, 0.7)`,
      boxShadow: `0 0 ${Math.random() * 10 + 5}px rgba(139,92,246,0.5)`,
      duration: Math.random() * 10 + 10,
      delay: Math.random() * 5,
      y: Math.random() * 40 - 20,
      x: Math.random() * 40 - 20,
    }));
    setParticles(generated);
  }, []);

  return (
    <section className="relative h-screen flex flex-col items-center justify-center text-center p-4 overflow-hidden">
      {/* Animated background particles */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        {particles.map((p, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{
              top: `${p.top}%`,
              left: `${p.left}%`,
              width: `${p.width}px`,
              height: `${p.height}px`,
              background: p.background,
              boxShadow: p.boxShadow,
            }}
            animate={{
              y: [0, p.y, 0],
              x: [0, p.x, 0],
              opacity: [0.7, 1, 0.7]
            }}
            transition={{
              duration: p.duration,
              repeat: Infinity,
              repeatType: "loop",
              delay: p.delay
            }}
          />
        ))}
      </div>

      <motion.h1 
        className="text-6xl md:text-8xl font-bold text-purple-400 mb-4"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        AeroMix
      </motion.h1>
      <motion.p 
        className="text-xl md:text-2xl mb-8"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.2 }}
      >
        Shape Sound With Your Movements – Real-Time Gesture-Based Audio Control
      </motion.p>
      <motion.p 
        className="max-w-xl mx-auto mb-12 text-gray-300"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.4 }}
      >
        AeroMix revolutionizes music production and performance by translating physical gestures into precise audio control, creating an intuitive bridge between movement and sound.
      </motion.p>
      <motion.div 
        className="flex flex-col sm:flex-row justify-center gap-4"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.6 }}
      >
        <button className="bg-purple-600 hover:bg-purple-700 px-8 py-4 rounded-lg text-white font-semibold transition-all transform hover:scale-105">
          Explore Features
        </button>
        <button 
          onClick={onTryDemo}
          className="bg-indigo-800 hover:bg-indigo-700 px-8 py-4 rounded-lg text-white font-semibold transition-all transform hover:scale-105 relative overflow-hidden group"
        >
          <span className="relative z-10">Try Demo</span>
          <span className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
        </button>
      </motion.div>
    </section>
  );
}
