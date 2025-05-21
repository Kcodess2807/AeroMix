'use client';

import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface AudioState {
  volume: number;
  bass: number;
  tempo: number;
  pitch: number;
}

const AudioVisualizer = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [audioState, setAudioState] = useState<AudioState>({
    volume: 0.7,
    bass: 0.5,
    tempo: 1.0,
    pitch: 1.0
  });
  
  // Simulate API fetch with random values
  useEffect(() => {
    const interval = setInterval(() => {
      setAudioState(prev => ({
        volume: Math.max(0.1, Math.min(1, prev.volume + (Math.random() - 0.5) * 0.1)),
        bass: Math.max(0.1, Math.min(1, prev.bass + (Math.random() - 0.5) * 0.1)),
        tempo: Math.max(0.5, Math.min(2, prev.tempo + (Math.random() - 0.5) * 0.05)),
        pitch: Math.max(0.5, Math.min(2, prev.pitch + (Math.random() - 0.5) * 0.05))
      }));
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Canvas visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    
    // Animation function
    const draw = () => {
      // Clear canvas with gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, 'rgba(15, 23, 42, 0.9)');
      gradient.addColorStop(1, 'rgba(15, 23, 42, 0.7)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);
      
      // Draw grid lines
      ctx.strokeStyle = 'rgba(99, 102, 241, 0.1)';
      ctx.lineWidth = 1;
      
      // Horizontal lines
      for (let i = 0; i < height; i += 20) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(width, i);
        ctx.stroke();
      }
      
      // Vertical lines
      for (let i = 0; i < width; i += 20) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, height);
        ctx.stroke();
      }
      
      // Generate waveform data
      const waveformPoints = 100;
      const waveData = Array(waveformPoints).fill(0).map((_, i) => {
        const x = (i / waveformPoints) * width;
        
        // Create a complex waveform based on audio parameters
        const volumeFactor = audioState.volume * 50;
        const bassFactor = Math.sin(i * 0.01 * audioState.bass) * 20;
        const tempoFactor = Math.sin(i * 0.1 * audioState.tempo + Date.now() * 0.001) * 15;
        const pitchFactor = Math.sin(i * 0.2 * audioState.pitch + Date.now() * 0.002) * 10;
        
        const y = height / 2 + volumeFactor * Math.sin(i * 0.05 + Date.now() * 0.001) + bassFactor + tempoFactor + pitchFactor;
        
        return { x, y };
      });
      
      // Draw waveform
      ctx.beginPath();
      ctx.moveTo(waveData[0].x, waveData[0].y);
      for (let i = 1; i < waveData.length; i++) {
        ctx.lineTo(waveData[i].x, waveData[i].y);
      }
      ctx.strokeStyle = 'rgba(139, 92, 246, 0.8)';
      ctx.lineWidth = 3;
      ctx.stroke();
      
      // Draw a duplicate waveform with glow effect
      ctx.beginPath();
      ctx.moveTo(waveData[0].x, waveData[0].y);
      for (let i = 1; i < waveData.length; i++) {
        ctx.lineTo(waveData[i].x, waveData[i].y);
      }
      ctx.strokeStyle = 'rgba(167, 139, 250, 0.3)';
      ctx.lineWidth = 8;
      ctx.stroke();
      
      // Draw parameter indicators
      const indicatorRadius = 8;
      const indicatorY = height - 30;
      
      // Volume indicator
      const volX = width * 0.2;
      ctx.beginPath();
      ctx.arc(volX, indicatorY, indicatorRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, ${Math.floor(audioState.volume * 255)}, 0, 0.8)`;
      ctx.fill();
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = 'white';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(`Vol: ${Math.floor(audioState.volume * 100)}%`, volX, indicatorY + 20);
      
      // Bass indicator
      const bassX = width * 0.4;
      ctx.beginPath();
      ctx.arc(bassX, indicatorY, indicatorRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 0, ${Math.floor(audioState.bass * 255)}, 0.8)`;
      ctx.fill();
      ctx.stroke();
      ctx.fillText(`Bass: ${Math.floor(audioState.bass * 100)}%`, bassX, indicatorY + 20);
      
      // Tempo indicator
      const tempoX = width * 0.6;
      ctx.beginPath();
      ctx.arc(tempoX, indicatorY, indicatorRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${Math.floor(audioState.tempo * 100)}, 165, 255, 0.8)`;
      ctx.fill();
      ctx.stroke();
      ctx.fillText(`Tempo: ${audioState.tempo.toFixed(2)}x`, tempoX, indicatorY + 20);
      
      // Pitch indicator
      const pitchX = width * 0.8;
      ctx.beginPath();
      ctx.arc(pitchX, indicatorY, indicatorRadius, 0, Math.PI * 2);
      ctx.fillStyle = `hsl(${240 + audioState.pitch * 60}, 100%, 50%, 0.8)`;
      ctx.fill();
      ctx.stroke();
      ctx.fillText(`Pitch: ${audioState.pitch.toFixed(2)}x`, pitchX, indicatorY + 20);
      
      requestAnimationFrame(draw);
    };
    
    const animationId = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animationId);
  }, [audioState]);

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <canvas 
        ref={canvasRef} 
        width={500} 
        height={300} 
        className="w-full h-full bg-black/20 rounded-lg"
      />
      
      <div className="mt-4 grid grid-cols-4 gap-2 w-full">
        {Object.entries(audioState).map(([key, value]) => (
          <motion.div 
            key={key}
            className="bg-black/30 p-2 rounded-lg text-center"
            animate={{ scale: [1, 1.03, 1] }}
            transition={{ 
              repeat: Infinity, 
              duration: 2, 
              delay: ['volume', 'bass', 'tempo', 'pitch'].indexOf(key) * 0.5 
            }}
          >
            <div className="text-xs uppercase tracking-wider text-gray-400">{key}</div>
            <div className="font-mono">
              {key === 'volume' || key === 'bass' 
                ? `${Math.floor(value * 100)}%` 
                : `${value.toFixed(2)}x`}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default AudioVisualizer;
