'use client';

import { useState, useEffect } from "react";

interface AudioState {
  volume: number;
  bass: number;
  tempo: number;
  pitch: number;
}

export default function GestureControls() {
  const [audioState, setAudioState] = useState<AudioState>({
    volume: 0.5,
    bass: 0.5,
    tempo: 1.0,
    pitch: 1.0
  });
  
  const [error, setError] = useState<string | null>(null);
  
  // Fetch current state from backend
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
  
  // Send gesture to backend
  const sendGesture = async (gesture: string) => {
    try {
      const response = await fetch('/api/gesture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gesture }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      // Update state after gesture
      fetchState();
      setError(null);
    } catch (error: any) {
      console.error("Error sending gesture:", error);
      setError(`Connection error: ${error.message}`);
    }
  };
  
  useEffect(() => {
    // Fetch initial state
    fetchState();
    
    // Poll for updates every second
    const interval = setInterval(fetchState, 1000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="w-full h-full">
      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-500 rounded-md text-red-300">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-2 gap-4">
        {/* Volume Controls */}
        <div className="bg-black/30 p-4 rounded-lg border border-indigo-900/50">
          <h3 className="text-xl font-semibold mb-2">Volume: {Math.round(audioState.volume * 100)}%</h3>
          <div className="flex gap-2">
            <button 
              onClick={() => sendGesture('volume_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
            >
              Volume Up
            </button>
            <button 
              onClick={() => sendGesture('volume_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
            >
              Volume Down
            </button>
          </div>
        </div>
        
        {/* Bass Controls */}
        <div className="bg-black/30 p-4 rounded-lg border border-indigo-900/50">
          <h3 className="text-xl font-semibold mb-2">Bass: {Math.round(audioState.bass * 100)}%</h3>
          <div className="flex gap-2">
            <button 
              onClick={() => sendGesture('bass_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
            >
              Bass Up
            </button>
            <button 
              onClick={() => sendGesture('bass_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
            >
              Bass Down
            </button>
          </div>
        </div>
        
        {/* Tempo Controls */}
        <div className="bg-black/30 p-4 rounded-lg border border-indigo-900/50">
          <h3 className="text-xl font-semibold mb-2">Tempo: {audioState.tempo.toFixed(2)}x</h3>
          <div className="flex gap-2">
            <button 
              onClick={() => sendGesture('tempo_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
            >
              Tempo Up
            </button>
            <button 
              onClick={() => sendGesture('tempo_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
            >
              Tempo Down
            </button>
          </div>
        </div>
        
        {/* Pitch Controls */}
        <div className="bg-black/30 p-4 rounded-lg border border-indigo-900/50">
          <h3 className="text-xl font-semibold mb-2">Pitch: {audioState.pitch.toFixed(2)}x</h3>
          <div className="flex gap-2">
            <button 
              onClick={() => sendGesture('pitch_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
            >
              Pitch Up
            </button>
            <button 
              onClick={() => sendGesture('pitch_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
            >
              Pitch Down
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
