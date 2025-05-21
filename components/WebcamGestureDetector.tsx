'use client';

import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const WebcamGestureDetector = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [handPosition, setHandPosition] = useState({ x: 0, y: 0 });
  
  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
        };
        setIsStreaming(true);
        setError(null);
        
        // Simulate hand tracking with mouse movement
        document.addEventListener('mousemove', handleMouseMove);
      }
    } catch (err: any) {
      console.error("Error accessing webcam:", err);
      setError(`Webcam error: ${err.message}`);
    }
  };
  
  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsStreaming(false);
      document.removeEventListener('mousemove', handleMouseMove);
    }
  };
  
  const handleMouseMove = (e: MouseEvent) => {
    if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      setHandPosition({ x, y });
    }
  };
  
  useEffect(() => {
    return () => {
      stopWebcam();
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);
  
  useEffect(() => {
    if (isStreaming && canvasRef.current && videoRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      const drawFrame = () => {
        if (ctx && videoRef.current) {
          // Draw video frame
          ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
          
          // Draw hand tracking simulation
          if (isStreaming) {
            ctx.beginPath();
            ctx.arc(handPosition.x, handPosition.y, 20, 0, 2 * Math.PI);
            ctx.strokeStyle = '#4F46E5';
            ctx.lineWidth = 3;
            ctx.stroke();
            
            ctx.beginPath();
            ctx.arc(handPosition.x, handPosition.y, 5, 0, 2 * Math.PI);
            ctx.fillStyle = '#818CF8';
            ctx.fill();
            
            // Draw tracking points for fingers
            for (let i = 0; i < 5; i++) {
              const angle = (i / 5) * Math.PI;
              const distance = 40;
              const x = handPosition.x + Math.cos(angle) * distance;
              const y = handPosition.y + Math.sin(angle) * distance;
              
              ctx.beginPath();
              ctx.arc(x, y, 3, 0, 2 * Math.PI);
              ctx.fillStyle = '#A78BFA';
              ctx.fill();
              
              ctx.beginPath();
              ctx.moveTo(handPosition.x, handPosition.y);
              ctx.lineTo(x, y);
              ctx.strokeStyle = '#A78BFA';
              ctx.lineWidth = 1;
              ctx.stroke();
            }
          }
        }
        requestAnimationFrame(drawFrame);
      };
      
      const animationId = requestAnimationFrame(drawFrame);
      return () => cancelAnimationFrame(animationId);
    }
  }, [isStreaming, handPosition]);

  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      {error && (
        <div className="text-red-500 mb-4 p-3 bg-red-500/20 rounded-lg">
          {error}
        </div>
      )}
      
      <div className="relative w-full aspect-video bg-black/30 rounded-lg overflow-hidden">
        {isStreaming ? (
          <>
            <video 
              ref={videoRef} 
              className="absolute inset-0 w-full h-full object-cover opacity-0"
              autoPlay 
              playsInline
            />
            <canvas 
              ref={canvasRef} 
              width={640} 
              height={480}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-4 right-4 flex space-x-2">
              <motion.div 
                className="w-3 h-3 rounded-full bg-green-500"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
              <span className="text-xs text-white/80">Tracking Active</span>
            </div>
          </>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center flex-col gap-4">
            <motion.div 
              className="text-purple-300 text-6xl"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
            >
              📹
            </motion.div>
            <p className="text-gray-400">Webcam inactive</p>
          </div>
        )}
      </div>
      
      <motion.button
        onClick={isStreaming ? stopWebcam : startWebcam}
        className="mt-6 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-500 text-white rounded-full font-medium"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {isStreaming ? "Stop Webcam" : "Activate Gesture Simulation"}
      </motion.button>
      
      <p className="mt-2 text-sm text-gray-400">
        No actual video will be recorded or sent
      </p>
    </div>
  );
};

export default WebcamGestureDetector;
