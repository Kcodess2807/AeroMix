'use client';

import { useRef, useState } from 'react';

export default function WebcamGestureDetector() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
        };
        setIsStreaming(true);
        setError(null);
        console.log("[DEBUG] Webcam started, beginning to send frames...");
        sendFramesToBackend();
      }
    } catch (err: any) {
      setError(`Webcam error: ${err.message}`);
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

  // Send frames to backend for gesture prediction
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
        await fetch('/api/gesture-frame', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ frame: dataUrl }),
        });
        console.log("[DEBUG] Frame sent to backend");
      } catch (e) {
        console.error("[ERROR] Error sending frame to backend:", e);
      }
      requestAnimationFrame(sendFrame);
    };
    sendFrame();
  };

  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      {error && <div className="text-red-500 mb-4">{error}</div>}
      <div className="relative w-full aspect-video bg-black/30 rounded-lg overflow-hidden flex items-center justify-center">
        {isStreaming ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ background: "black" }}
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
