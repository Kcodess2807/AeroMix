'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

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
    pitch: 1.0,
  });
  const [activeControl, setActiveControl] = useState<string | null>(null);

  useEffect(() => {
    const fetchState = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/state');
        const data = await response.json();
        setAudioState(data);
        console.log('[DEBUG] Fetched audio state:', data);
      } catch (e) {
        console.error('[ERROR] Failed to fetch audio state:', e);
      }
    };
    fetchState();
    const interval = setInterval(fetchState, 1000); // Poll every second
    return () => clearInterval(interval);
  }, []);

  const sendGesture = async (gesture: string) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/gesture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gesture }),
      });
      const data = await response.json();
      console.log('[DEBUG] Gesture response:', data);
      setAudioState(data.state || audioState);
      setActiveControl(gesture.split('_')[0]);
      setTimeout(() => setActiveControl(null), 500);
    } catch (e) {
      console.error('[ERROR] Failed to send gesture:', e);
    }
  };

  return (
    <div className="w-full h-full">
      <div className="grid grid-cols-2 gap-4">
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
        {/* Repeat for Bass, Tempo, Pitch controls with similar structure */}
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