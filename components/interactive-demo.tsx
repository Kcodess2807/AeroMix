'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import WebcamGestureDetector from "@/components/WebcamGestureDetector";
import AudioVisualizer from "@/components/AudioVisualizer";
import GestureControls from "@/components/GestureControls";

export default function InteractiveDemo() {
  const [activeTab, setActiveTab] = useState("manual");

  return (
    <section className="py-20 bg-black/50 backdrop-blur-sm" id="try-it">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-blue-300 mb-4">Try AeroMix Live</h2>
        <p className="text-center text-gray-300 mb-12 max-w-3xl mx-auto">
          Experience the power of AeroMix with this interactive demo. Adjust controls
          manually or activate gesture recognition.
        </p>
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          <div className="lg:col-span-3 bg-black/40 rounded-xl p-6 border border-indigo-900/50">
            <Tabs defaultValue="manual" value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="w-full mb-6">
                <TabsTrigger value="manual" className="flex-1">Manual Controls</TabsTrigger>
                <TabsTrigger value="gesture" className="flex-1">Gesture Recognition</TabsTrigger>
              </TabsList>

              <TabsContent value="manual" className="h-[400px]">
                <GestureControls />
              </TabsContent>

              <TabsContent value="gesture" className="h-[400px] flex flex-col items-center justify-center">
                <WebcamGestureDetector />
                <p className="text-center text-sm text-gray-400 mt-4">
                  This is a simulation of how gesture recognition would work. In the real AeroMix system,
                  your actual gestures would control the audio parameters.
                </p>
              </TabsContent>
            </Tabs>
          </div>

          <div className="lg:col-span-2 bg-black/40 rounded-xl p-6 border border-indigo-900/50">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">Audio Visualizer</h3>
              <div className="flex gap-2">
                <button className="p-2 rounded-full bg-black/30">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M9 21H3v-6"/><path d="M14 10 3 21"/></svg>
                </button>
                <button className="p-2 rounded-full bg-purple-600">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                </button>
              </div>
            </div>
            <AudioVisualizer />
            <button className="w-full mt-6 py-3 bg-gradient-to-r from-purple-600 to-blue-500 rounded-lg flex items-center justify-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Play Audio Loop
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
