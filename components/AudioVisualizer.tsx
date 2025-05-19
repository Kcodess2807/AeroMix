'use client';

import { useRef, useEffect, useState } from 'react';

interface AudioState {
  volume: number;
  bass: number;
  tempo: number;
  pitch: number;
}

export default function AudioVisualizer() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [audioState, setAudioState] = useState<AudioState>({
    volume: 0.5,
    bass: 0.5,
    tempo: 1.0,
    pitch: 1.0
  });
  
  const [error, setError] = useState<string | null>(null);
  
  // Fetch current state from backend
  useEffect(() => {
    const fetchState = async () => {
      try {
        const response = await fetch('/api/state');
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        setAudioState(data);
        setError(null);
      } catch (error: any) {
        console.error("Error fetching state:", error);
        setError(`Connection error: ${error.message}`);
      }
    };
    
    fetchState();
    const interval = setInterval(fetchState, 100); // Update more frequently for smooth animation
    return () => clearInterval(interval);
  }, []);
  
  // Draw visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Helper functions
    const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
    
    // Fill background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);
    
    // Calculate positions
    const centerY = height / 2;
    const spacing = width / 5;
    
    // Draw volume circle
    const volX = spacing;
    const volRadius = lerp(30, 100, audioState.volume);
    const volColor = `rgb(0, ${lerp(100, 255, audioState.volume)}, 0)`;
    
    // Draw filled circle
    ctx.beginPath();
    ctx.arc(volX, centerY, volRadius, 0, Math.PI * 2);
    ctx.fillStyle = volColor;
    ctx.fill();
    // Add black outline
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    // Add highlight effect
    ctx.beginPath();
    ctx.arc(volX, centerY - volRadius * 0.3, volRadius * 0.7, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.fill();
    
    // Draw bass circle
    const bassX = spacing * 2;
    const bassRadius = lerp(30, 100, audioState.bass);
    const bassColor = `rgb(0, 0, ${lerp(100, 255, audioState.bass)})`;
    
    // Draw filled circle
    ctx.beginPath();
    ctx.arc(bassX, centerY, bassRadius, 0, Math.PI * 2);
    ctx.fillStyle = bassColor;
    ctx.fill();
    // Add black outline
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    // Add highlight effect
    ctx.beginPath();
    ctx.arc(bassX, centerY - bassRadius * 0.3, bassRadius * 0.7, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.fill();
    
    // Draw tempo circle with pulse
    const tempoX = spacing * 3;
    const tempoVal = (audioState.tempo - 0.5) / 1.5; // Normalize to 0-1
    const tempoRadius = lerp(30, 100, tempoVal);
    const tempoColor = `rgb(${lerp(100, 0, tempoVal)}, ${lerp(100, 165, tempoVal)}, ${lerp(0, 255, tempoVal)})`;
    const pulse = 5 + 10 * Math.sin(Date.now() * audioState.tempo * 0.01);
    
    // Draw pulse effect
    ctx.beginPath();
    ctx.arc(tempoX, centerY, tempoRadius + pulse, 0, Math.PI * 2);
    ctx.lineWidth = 3;
    ctx.strokeStyle = tempoColor;
    ctx.stroke();
    
    // Draw filled circle
    ctx.beginPath();
    ctx.arc(tempoX, centerY, tempoRadius, 0, Math.PI * 2);
    ctx.fillStyle = tempoColor;
    ctx.fill();
    // Add black outline
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    // Add highlight effect
    ctx.beginPath();
    ctx.arc(tempoX, centerY - tempoRadius * 0.3, tempoRadius * 0.7, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.fill();
    
    // Draw pitch circle
    const pitchX = spacing * 4;
    const pitchVal = (audioState.pitch - 0.5) / 1.5; // Normalize to 0-1
    const pitchRadius = lerp(30, 100, pitchVal);
    
    // HSV to RGB conversion for pitch
    const hue = lerp(240, 300, pitchVal); // Blue to magenta
    const pitchColor = `hsl(${hue}, 100%, 50%)`;
    
    // Draw filled circle
    ctx.beginPath();
    ctx.arc(pitchX, centerY, pitchRadius, 0, Math.PI * 2);
    ctx.fillStyle = pitchColor;
    ctx.fill();
    // Add black outline
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    // Add highlight effect
    ctx.beginPath();
    ctx.arc(pitchX, centerY - pitchRadius * 0.3, pitchRadius * 0.7, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.fill();
    
    // Add labels
    ctx.font = '20px Arial';
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    
    ctx.fillText(`Volume: ${Math.round(audioState.volume * 100)}%`, volX, centerY + 150);
    ctx.fillText(`Bass: ${Math.round(audioState.bass * 100)}%`, bassX, centerY + 150);
    ctx.fillText(`Tempo: ${audioState.tempo.toFixed(2)}x`, tempoX, centerY + 150);
    ctx.fillText(`Pitch: ${audioState.pitch.toFixed(2)}x`, pitchX, centerY + 150);
    
    // Request animation frame
    requestAnimationFrame(() => {});
  }, [audioState]);
  
  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-500 rounded-md text-red-300">
          {error}
        </div>
      )}
      
      <canvas 
        ref={canvasRef} 
        width={1000} 
        height={500} 
        className="w-full h-full bg-black/20 rounded-lg"
      />
    </div>
  );
}
