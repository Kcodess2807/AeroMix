'use client';

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

interface AudioState {
  volume: number;
  bass: number;
  tempo: number;
  pitch: number;
}

const GestureControls = () => {
  const [audioState, setAudioState] = useState<AudioState>({
    volume: 0.7,
    bass: 0.5,
    tempo: 1.0,
    pitch: 1.0
  });
  
  const [activeControl, setActiveControl] = useState<string | null>(null);
  
  const sendGesture = async (gesture: string) => {
    // Simulate API call
    console.log(`Sending gesture: ${gesture}`);
    
    // Update local state based on gesture
    setAudioState(prev => {
      const newState = { ...prev };
      
      switch (gesture) {
        case 'volume_up':
          newState.volume = Math.min(1, prev.volume + 0.1);
          break;
        case 'volume_down':
          newState.volume = Math.max(0, prev.volume - 0.1);
          break;
        case 'bass_up':
          newState.bass = Math.min(1, prev.bass + 0.1);
          break;
        case 'bass_down':
          newState.bass = Math.max(0, prev.bass - 0.1);
          break;
        case 'tempo_up':
          newState.tempo = Math.min(2, prev.tempo + 0.1);
          break;
        case 'tempo_down':
          newState.tempo = Math.max(0.5, prev.tempo - 0.1);
          break;
        case 'pitch_up':
          newState.pitch = Math.min(2, prev.pitch + 0.1);
          break;
        case 'pitch_down':
          newState.pitch = Math.max(0.5, prev.pitch - 0.1);
          break;
      }
      
      return newState;
    });
    
    // Visual feedback
    setActiveControl(gesture.split('_')[0]);
    setTimeout(() => setActiveControl(null), 500);
  };
  
  return (
    <div className="w-full h-full">
      <div className="grid grid-cols-2 gap-4">
        {/* Volume Controls */}
        <motion.div 
          className={`bg-black/30 p-4 rounded-lg border ${activeControl === 'volume' ? 'border-green-500' : 'border-indigo-900/50'}`}
          animate={{ scale: activeControl === 'volume' ? 1.03 : 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
        >
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-xl font-semibold">Volume</h3>
            <div className="text-xl font-mono">{Math.round(audioState.volume * 100)}%</div>
          </div>
          
          <div className="h-4 bg-black/50 rounded-full mb-4 overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-green-800 to-green-500"
              initial={{ width: `${audioState.volume * 100}%` }}
              animate={{ width: `${audioState.volume * 100}%` }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            />
          </div>
          
          <div className="flex gap-2">
            <motion.button 
              onClick={() => sendGesture('volume_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Volume Up
            </motion.button>
            <motion.button 
              onClick={() => sendGesture('volume_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Volume Down
            </motion.button>
          </div>
        </motion.div>
        
        {/* Bass Controls */}
        <motion.div 
          className={`bg-black/30 p-4 rounded-lg border ${activeControl === 'bass' ? 'border-blue-500' : 'border-indigo-900/50'}`}
          animate={{ scale: activeControl === 'bass' ? 1.03 : 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
        >
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-xl font-semibold">Bass</h3>
            <div className="text-xl font-mono">{Math.round(audioState.bass * 100)}%</div>
          </div>
          
          <div className="h-4 bg-black/50 rounded-full mb-4 overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-blue-800 to-blue-500"
              initial={{ width: `${audioState.bass * 100}%` }}
              animate={{ width: `${audioState.bass * 100}%` }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            />
          </div>
          
          <div className="flex gap-2">
            <motion.button 
              onClick={() => sendGesture('bass_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Bass Up
            </motion.button>
            <motion.button 
              onClick={() => sendGesture('bass_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Bass Down
            </motion.button>
          </div>
        </motion.div>
        
        {/* Tempo Controls */}
        <motion.div 
          className={`bg-black/30 p-4 rounded-lg border ${activeControl === 'tempo' ? 'border-orange-500' : 'border-indigo-900/50'}`}
          animate={{ scale: activeControl === 'tempo' ? 1.03 : 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
        >
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-xl font-semibold">Tempo</h3>
            <div className="text-xl font-mono">{audioState.tempo.toFixed(2)}x</div>
          </div>
          
          <div className="h-4 bg-black/50 rounded-full mb-4 overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-orange-800 to-orange-500"
              initial={{ width: `${(audioState.tempo - 0.5) / 1.5 * 100}%` }}
              animate={{ width: `${(audioState.tempo - 0.5) / 1.5 * 100}%` }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            />
          </div>
          
          <div className="flex gap-2">
            <motion.button 
              onClick={() => sendGesture('tempo_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Tempo Up
            </motion.button>
            <motion.button 
              onClick={() => sendGesture('tempo_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Tempo Down
            </motion.button>
          </div>
        </motion.div>
        
        {/* Pitch Controls */}
        <motion.div 
          className={`bg-black/30 p-4 rounded-lg border ${activeControl === 'pitch' ? 'border-purple-500' : 'border-indigo-900/50'}`}
          animate={{ scale: activeControl === 'pitch' ? 1.03 : 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
        >
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-xl font-semibold">Pitch</h3>
            <div className="text-xl font-mono">{audioState.pitch.toFixed(2)}x</div>
          </div>
          
          <div className="h-4 bg-black/50 rounded-full mb-4 overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-purple-800 to-purple-500"
              initial={{ width: `${(audioState.pitch - 0.5) / 1.5 * 100}%` }}
              animate={{ width: `${(audioState.pitch - 0.5) / 1.5 * 100}%` }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            />
          </div>
          
          <div className="flex gap-2">
            <motion.button 
              onClick={() => sendGesture('pitch_up')}
              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Pitch Up
            </motion.button>
            <motion.button 
              onClick={() => sendGesture('pitch_down')}
              className="flex-1 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md hover:opacity-90 transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Pitch Down
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default GestureControls;
