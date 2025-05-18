// components/WebcamGestureDetector.jsx
'use client';

import { useRef, useEffect, useState } from 'react';
import styles from './WebcamGestureDetector.module.css';

export default function WebcamGestureDetector() {
    const videoRef = useRef(null);
    const [isStreaming, setIsStreaming] = useState(false);
    
    const startWebcam = async () => {
        try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        if (videoRef.current) {
            videoRef.current.srcObject = stream;
            setIsStreaming(true);
        }
        } catch (err) {
        console.error("Error accessing webcam:", err);
        }
    };
    
    const stopWebcam = () => {
        if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        videoRef.current.srcObject = null;
        setIsStreaming(false);
        }
    };
    
    return (
        <div className={styles.container}>
        <h2>Webcam Gesture Detection</h2>
        <div className={styles.webcamContainer}>
            <video 
            ref={videoRef} 
            autoPlay 
            className={styles.webcam}
            />
        </div>
        <div className={styles.controls}>
            {!isStreaming ? (
            <button onClick={startWebcam} className={styles.startButton}>
                Start Webcam
            </button>
            ) : (
            <button onClick={stopWebcam} className={styles.stopButton}>
                Stop Webcam
            </button>
            )}
        </div>
        </div>
    );
    }
