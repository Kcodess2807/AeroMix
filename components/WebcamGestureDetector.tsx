'use client';

import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function WebcamGestureDetector() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detectedGesture, setDetectedGesture] = useState<string | null>(null);

  const startWebcam = async () => {
    try {
      console.log("[DEBUG] Requesting webcam access...");
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          console.log("[DEBUG] Video metadata loaded, playing video...");
          videoRef.current?.play().catch((e) => console.error("[ERROR] Failed to play video:", e));
        };
        setIsStreaming(true);
        setError(null);
        console.log("[DEBUG] Webcam started, beginning to send frames...");
        sendFramesToBackend();
      }
    } catch (err: any) {
      const errorMessage = `Webcam error: ${err.message}`;
      setError(errorMessage);
      console.error("[ERROR] Webcam error:", err);
    }
  };

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsStreaming(false);
      console.log("[DEBUG] Webcam stopped");
    }
  };

  const sendFramesToBackend = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 224;
    canvas.height = 224;

    const sendFrame = async () => {
      if (!isStreaming || !videoRef.current || !ctx) return;
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/jpeg');
      try {
        const response = await fetch('http://127.0.0.1:5000/api/gesture-frame', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ frame: dataUrl }),
        });
        const result = await response.json();
        console.log("[DEBUG] Backend response:", result);
        if (result.gestures && result.gestures.length > 0) {
          setDetectedGesture(result.gestures[0]);
          setTimeout(() => setDetectedGesture(null), 2000);
        }
      } catch (e) {
        console.error("[ERROR] Error sending frame to backend:", e);
      }
      requestAnimationFrame(sendFrame);
    };
    sendFrame();
  };

  useEffect(() => {
    return () => stopWebcam(); // Cleanup on unmount
  }, []);

  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      {error && <div className="text-red-500 mb-4">{error}</div>}
      {detectedGesture && (
        <motion.div
          className="absolute top-4 text-green-500 text-xl font-bold"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          Gesture Detected: {detectedGesture}
        </motion.div>
      )}
      <div className="relative w-full aspect-video bg-black/30 rounded-lg overflow-hidden flex items-center justify-center">
        {isStreaming ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ background: 'black' }}
          />
        ) : (
          <div className="flex flex-col items-center justify-center w-full h-full">
            <span className="text-6xl text-purple-300">📹</span>
            <p className="text-gray-400">Webcam inactive</p>
          </div>
        )}
      </div>
      <button
        onClick={isStreaming ? stopWebcam : startWebcam}
        className="mt-6 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-500 text-white rounded-full font-medium hover:opacity-90 transition"
      >
        {isStreaming ? "Stop Webcam" : "Activate Gesture Simulation"}
      </button>
      <p className="mt-2 text-sm text-gray-400">
        No actual video will be recorded or sent
      </p>
    </div>
  );
}