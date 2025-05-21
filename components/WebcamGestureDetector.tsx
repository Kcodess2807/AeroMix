'use client';

import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function WebcamGestureDetector() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detectedGesture, setDetectedGesture] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    return () => {
      stopWebcam();
    };
  }, []);

  useEffect(() => {
    if (isStreaming) {
      console.log("[DEBUG] isStreaming changed to true, starting frame sending...");
      sendFramesToBackend();
    }
  }, [isStreaming]);

  const startWebcam = async () => {
    if (!isMounted) {
      console.log("[DEBUG] Component not yet mounted, delaying webcam start...");
      return;
    }
    if (!videoRef.current) {
      console.error("[ERROR] Video ref is still not available after mount");
      setError("Video element not found");
      return;
    }
    try {
      console.log("[DEBUG] Requesting webcam access...");
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      console.log("[DEBUG] Webcam stream obtained:", stream);
      videoRef.current.srcObject = stream;
      console.log("[DEBUG] Stream attached to video element:", videoRef.current.srcObject);
      videoRef.current.onloadedmetadata = () => {
        console.log("[DEBUG] Video metadata loaded, attempting to play...");
        videoRef.current?.play()
          .then(() => {
            console.log("[DEBUG] Video playback started successfully");
            setIsStreaming(true);
            setError(null);
            console.log("[DEBUG] Webcam started...");
          })
          .catch((e) => {
            console.error("[ERROR] Failed to play video:", e);
            setError("Failed to play video");
          });
      };
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
      console.log("[DEBUG] Webcam stopped, isStreaming set to false");
    }
  };

  const sendFramesToBackend = () => {
    if (!videoRef.current) {
      console.error("[ERROR] Video ref is not available for frame sending");
      return;
    }
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error("[ERROR] Failed to get canvas context");
      return;
    }
    canvas.width = 224;
    canvas.height = 224;

    const sendFrame = async () => {
      console.log("[DEBUG] Checking streaming conditions...");
      console.log("[DEBUG] isStreaming:", isStreaming);
      console.log("[DEBUG] videoRef.current:", !!videoRef.current);
      console.log("[DEBUG] ctx:", !!ctx);
      if (!isStreaming) {
        console.log("[DEBUG] Stopping frame sending: isStreaming is false");
        return;
      }
      if (!videoRef.current) {
        console.log("[DEBUG] Stopping frame sending: videoRef.current is null");
        return;
      }
      if (!ctx) {
        console.log("[DEBUG] Stopping frame sending: ctx is null");
        return;
      }
      console.log("[DEBUG] Capturing frame...");
      ctx.save();
      ctx.scale(-1, 1);
      ctx.drawImage(videoRef.current, -canvas.width, 0, canvas.width, canvas.height);
      ctx.restore();
      const dataUrl = canvas.toDataURL('image/jpeg');
      console.log("[DEBUG] Frame captured, sending to backend...");
      try {
        const response = await fetch('http://127.0.0.1:5000/api/gesture-frame', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ frame: dataUrl }),
        });
        const result = await response.json();
        console.log("[DEBUG] Backend response:", result);
        console.log("[DEBUG] Result gestures:", result.gestures);
        if (result.status === "success" && result.gestures && result.gestures.length > 0) {
          const gesture = result.gestures[0];
          console.log("[DEBUG] Setting detected gesture:", gesture);
          setDetectedGesture(gesture);
          setTimeout(() => {
            console.log("[DEBUG] Clearing detected gesture");
            setDetectedGesture(null);
          }, 2000);
        } else {
          console.log("[DEBUG] No gestures detected in response");
        }
      } catch (e) {
        console.error("[ERROR] Error sending frame to backend:", e);
      }
      requestAnimationFrame(sendFrame);
    };
    console.log("[DEBUG] Starting frame sending loop...");
    sendFrame();
  };

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
      <div
        className="relative w-full bg-black/30 rounded-lg overflow-hidden flex items-center justify-center"
        style={{ height: '500px', maxWidth: '800px' }}
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
          style={{ background: 'black', width: '100%', height: '100%', display: 'block', transform: 'scaleX(-1)' }}
        />
        {!isStreaming && (
          <div className="absolute flex flex-col items-center justify-center w-full h-full">
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