'use client';

import { useState, useEffect } from "react";
import styles from '/GestureControls.module.css';

export default function GestureControls(){
    const [ audioState, setAudioState ]= useState({
        volume: 0.5, 
        bass: 0.5, 
        tempo: 1.0, 
        pitch: 1.0
    });


    //fetching the current state of the audio from the backend
    const fetchState=async()=>{
        try{ 
            const response=await fetch('/api/state');
            const data=await response.json();
            setAudioState(data);
        } catch(error){
            console.error("error fetching the curreent state: ", error)
        }
    };

    //now sending the gesture recieved, to the backend
    const sendGesture = async ( gesture ) => {
        try{
            await fetch('/api/gesture', {
                method: 'POST', 
                headers:{
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({gesture}),
            });

            //responding accoridng to the gesture, updating state
            fetchState();
        }catch(error){
            console.error("error sending gesture: ", error);
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
            <div className={styles.container}>
            <h2>AeroMix Controls</h2>
            
            <div className={styles.controlsGrid}>
                {/* Volume Controls */}
                <div className={styles.controlCard}>
                <h3>Volume: {Math.round(audioState.volume * 100)}%</h3>
                <div className={styles.buttonGroup}>
                    <button onClick={() => sendGesture('volume_up')}>Volume Up</button>
                    <button onClick={() => sendGesture('volume_down')}>Volume Down</button>
                </div>
                </div>
                
                {/* Bass Controls */}
                <div className={styles.controlCard}>
                <h3>Bass: {Math.round(audioState.bass * 100)}%</h3>
                <div className={styles.buttonGroup}>
                    <button onClick={() => sendGesture('bass_up')}>Bass Up</button>
                    <button onClick={() => sendGesture('bass_down')}>Bass Down</button>
                </div>
                </div>
                
                {/* Tempo Controls */}
                <div className={styles.controlCard}>
                <h3>Tempo: {audioState.tempo.toFixed(2)}x</h3>
                <div className={styles.buttonGroup}>
                    <button onClick={() => sendGesture('tempo_up')}>Tempo Up</button>
                    <button onClick={() => sendGesture('tempo_down')}>Tempo Down</button>
                </div>
                </div>
                
                {/* Pitch Controls */}
                <div className={styles.controlCard}>
                <h3>Pitch: {audioState.pitch.toFixed(2)}x</h3>
                <div className={styles.buttonGroup}>
                    <button onClick={() => sendGesture('pitch_up')}>Pitch Up</button>
                    <button onClick={() => sendGesture('pitch_down')}>Pitch Down</button>
                </div>
                </div>
            </div>
            </div>
        );
    }