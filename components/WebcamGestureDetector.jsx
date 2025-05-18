'use client';

import { useRef, useState, useEffect } from 'react';
import styles from './WebcamGestureDetector.module.css';

export default function WebcamGestureDetector() {
  const videoRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  
  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsStreaming(true);
        setError(null);
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      setError(`Webcam error: ${err.message}`);
    }
  };
  
  // Auto-start webcam when component mounts
  useEffect(() => {
    startWebcam();
    
    // Cleanup function
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className={styles.container}>
      <h2>Webcam Gesture Detection</h2>
      {error && <div className={styles.error}>{error}</div>}
      <div className={styles.webcamContainer}>
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline
          className={styles.webcam}
          onCanPlay={() => console.log("Video can play")}
        />
      </div>
      <div className={styles.controls}>
        {!isStreaming ? (
          <button onClick={startWebcam} className={styles.startButton}>
            Start Webcam
          </button>
        ) : (
          <div className={styles.statusActive}>Webcam Active</div>
        )}
      </div>
    </div>
  );
}
