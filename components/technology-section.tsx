'use client';

import { useRef } from "react";
import { motion, useScroll, useVelocity, useTransform } from "framer-motion";

const techs = [
  { name: "Python", description: "Core programming language for the AeroMix system." },
  { name: "Pyo", description: "Python module for digital signal processing." },
  { name: "OpenCV", description: "Computer vision library for image processing." },
  { name: "MediaPipe", description: "Framework for building multimodal ML pipelines." },
  { name: "OSC", description: "Open Sound Control protocol for networking." },
];

export default function TechnologySection() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollY } = useScroll({ container: ref });
  const velocity = useVelocity(scrollY);
  const scale = useTransform(velocity, [0, 2000], [1, 1.08]);

  return (
    <section className="py-20 bg-black/60" ref={ref}>
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-blue-300 mb-4">How Does It Work?</h2>
        <p className="text-center text-gray-300 mb-12 max-w-3xl mx-auto">
          AeroMix combines cutting-edge technologies to create a seamless bridge between physical movement and audio manipulation.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-2xl font-semibold mb-4">The Process</h3>
            <ol className="list-decimal list-inside text-lg text-gray-200 space-y-2">
              <li>Gesture Capture</li>
              <li>Computer Vision Processing</li>
              <li>Gesture Classification</li>
              <li>Parameter Mapping</li>
              <li>Audio Manipulation</li>
            </ol>
          </div>
          <div>
            <h3 className="text-2xl font-semibold mb-4">Technologies Used</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {techs.map((tech, idx) => (
                <motion.div
                  key={tech.name}
                  className="bg-indigo-950/60 p-6 rounded-lg shadow-lg border border-indigo-900"
                  style={{ scale }}
                  whileHover={{ scale: 1.07 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="text-purple-300 text-xl font-bold mb-2">{tech.name}</div>
                  <div className="text-gray-300">{tech.description}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-12 bg-black/30 rounded-lg p-6 border border-indigo-900/50">
          <h4 className="text-lg font-semibold mb-2 text-purple-300">Technical Specifications</h4>
          <div className="flex flex-wrap gap-2 text-sm text-indigo-200">
            <span className="bg-indigo-900 px-3 py-1 rounded-full">Python 3.9+</span>
            <span className="bg-indigo-900 px-3 py-1 rounded-full">MediaPipe Hands</span>
            <span className="bg-indigo-900 px-3 py-1 rounded-full">Pyo 1.0.4</span>
            <span className="bg-indigo-900 px-3 py-1 rounded-full">OpenCV 4.5+</span>
            <span className="bg-indigo-900 px-3 py-1 rounded-full">TensorFlow Lite</span>
          </div>
          <p className="mt-4 text-gray-400">
            AeroMix runs on standard hardware with a webcam, requiring minimal CPU resources for real-time performance.
          </p>
        </div>
        <div className="mt-8 bg-indigo-900/40 rounded-lg p-6 text-indigo-100">
          <h4 className="text-lg font-semibold mb-2">Future Developments</h4>
          <p>
            The AeroMix system is continuously evolving. Upcoming features include multi-user collaboration, expanded gesture vocabulary, integration with popular DAWs (Digital Audio Workstations), and enhanced machine learning models for more precise gesture recognition.
          </p>
        </div>
      </div>
    </section>
  );
}
