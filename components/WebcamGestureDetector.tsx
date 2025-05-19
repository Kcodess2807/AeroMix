'use client';

import { useRef, useState } from 'react';

export default function WebcamGestureDetector() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    }
  };

  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      {error && <div className="text-red-500 mb-4">{error}</div>}

      <div className="relative w-full aspect-video bg-black/30 rounded-lg overflow-hidden">
        {isStreaming ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center flex-col gap-4">
            <div className="text-purple-300 text-6xl">📹</div>
            <p className="text-gray-400">Webcam inactive</p>
          </div>
        )}
      </div>

      <button
        onClick={isStreaming ? stopWebcam : startWebcam}
        className="mt-6 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-500 text-white rounded-full font-medium"
      >
        {isStreaming ? "Stop Webcam" : "Activate Gesture Simulation"}
      </button>

      <p className="mt-2 text-sm text-gray-400">
        No actual video will be recorded or sent
      </p>
    </div>
  );
}
