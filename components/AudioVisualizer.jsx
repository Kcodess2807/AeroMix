// components/AudioVisualizer.jsx
'use client';

import { useRef, useEffect, useState } from 'react';
import styles from './AudioVisualizer.module.css';

export default function AudioVisualizer() {
  const canvasRef = useRef(null);
  const [audioState, setAudioState] = useState({
    volume: 0.5,
    bass: 0.5,
    tempo: 1.0,
    pitch: 1.0
  });
  
  // Fetch current state from backend
  useEffect(() => {
    const fetchState = async () => {
      try {
        const response = await fetch('/api/state');
        const data = await response.json();
        setAudioState(data);
      } catch (error) {
        console.error("Error fetching state:", error);
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
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Helper functions
    const lerp = (a, b, t) => a + (b - a) * t;
    
    // Calculate positions
    const centerY = height / 2;
    const spacing = width / 5;
    
    // Draw volume circle
    const volX = spacing;
    const volRadius = lerp(30, 100, audioState.volume);
    const volColor = `rgb(0, ${lerp(100, 255, audioState.volume)}, 0)`;
    
    ctx.beginPath();
    ctx.arc(volX, centerY, volRadius, 0, Math.PI * 2);
    ctx.fillStyle = volColor;
    ctx.fill();
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    
    // Draw bass circle
    const bassX = spacing * 2;
    const bassRadius = lerp(30, 100, audioState.bass);
    const bassColor = `rgb(0, 0, ${lerp(100, 255, audioState.bass)})`;
    
    ctx.beginPath();
    ctx.arc(bassX, centerY, bassRadius, 0, Math.PI * 2);
    ctx.fillStyle = bassColor;
    ctx.fill();
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    
    // Draw tempo circle with pulse
    const tempoX = spacing * 3;
    const tempoVal = (audioState.tempo - 0.5) / 1.5; // Normalize to 0-1
    const tempoRadius = lerp(30, 100, tempoVal);
    const tempoColor = `rgb(${lerp(100, 0, tempoVal)}, ${lerp(100, 165, tempoVal)}, ${lerp(0, 255, tempoVal)})`;
    const pulse = 5 + 10 * Math.sin(Date.now() * audioState.tempo * 0.01);
    
    ctx.beginPath();
    ctx.arc(tempoX, centerY, tempoRadius + pulse, 0, Math.PI * 2);
    ctx.lineWidth = 3;
    ctx.strokeStyle = tempoColor;
    ctx.stroke();
    
    ctx.beginPath();
    ctx.arc(tempoX, centerY, tempoRadius, 0, Math.PI * 2);
    ctx.fillStyle = tempoColor;
    ctx.fill();
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    
    // Draw pitch circle
    const pitchX = spacing * 4;
    const pitchVal = (audioState.pitch - 0.5) / 1.5; // Normalize to 0-1
    const pitchRadius = lerp(30, 100, pitchVal);
    const pitchColor = `rgb(${lerp(0, 255, pitchVal)}, 0, ${lerp(255, 0, pitchVal)})`;
    
    ctx.beginPath();
    ctx.arc(pitchX, centerY, pitchRadius, 0, Math.PI * 2);
    ctx.fillStyle = pitchColor;
    ctx.fill();
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#000';
    ctx.stroke();
    
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
    <div className={styles.container}>
      <h2>Audio Visualization</h2>
      <canvas 
        ref={canvasRef} 
        width={1000} 
        height={500} 
        className={styles.canvas}
      />
    </div>
  );
}
