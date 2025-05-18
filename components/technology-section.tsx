"use client"

import { motion } from "framer-motion"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight } from "lucide-react"

export default function TechnologySection() {
  const technologies = [
    {
      name: "Python",
      description: "Core programming language for the AeroMix system",
      icon: "/icons/python.svg",
    },
    {
      name: "Pyo",
      description: "Python module for digital signal processing",
      icon: "/icons/audio.svg",
    },
    {
      name: "OpenCV",
      description: "Computer vision library for image processing",
      icon: "/icons/opencv.svg",
    },
    {
      name: "MediaPipe",
      description: "Framework for building multimodal ML pipelines",
      icon: "/icons/mediapipe.svg",
    },
    {
      name: "OSC",
      description: "Open Sound Control protocol for networking",
      icon: "/icons/osc.svg",
    },
  ]

  const steps = [
    {
      title: "Gesture Capture",
      description: "User moves hand/body in front of webcam, which captures the movement in real-time video frames.",
    },
    {
      title: "Computer Vision Processing",
      description:
        "MediaPipe and OpenCV analyze the video frames to detect and track hand landmarks and body positions.",
    },
    {
      title: "Gesture Classification",
      description: "Machine learning model classifies the detected gestures into predefined control categories.",
    },
    {
      title: "Parameter Mapping",
      description: "Classified gestures are mapped to specific audio parameters (volume, bass, tempo, pitch).",
    },
    {
      title: "Audio Manipulation",
      description: "Pyo audio engine applies the parameter changes to the audio stream in real-time.",
    },
  ]

  return (
    <section id="technology" className="py-20 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-indigo-950/30 to-black/50 z-0"></div>

      <div className="container relative z-10 px-4 md:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
            How Does It Work?
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            AeroMix combines cutting-edge technologies to create a seamless bridge between physical movement and audio
            manipulation.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h3 className="text-2xl font-semibold mb-6 text-white">The Process</h3>

            <Accordion type="single" collapsible className="w-full">
              {steps.map((step, index) => (
                <AccordionItem
                  key={index}
                  value={`step-${index}`}
                  className="border-b border-purple-900/30 last:border-0"
                >
                  <AccordionTrigger className="text-white hover:text-purple-400 hover:no-underline py-4">
                    <div className="flex items-center">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 mr-3 text-white text-sm font-medium">
                        {index + 1}
                      </div>
                      {step.title}
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="text-white/70 pl-11">{step.description}</AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h3 className="text-2xl font-semibold mb-6 text-white">Technologies Used</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {technologies.map((tech, index) => (
                <Card
                  key={index}
                  className="bg-black/40 border-purple-900/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300"
                >
                  <CardContent className="p-6 flex items-center">
                    <div className="w-12 h-12 rounded-full bg-purple-950/50 flex items-center justify-center mr-4 flex-shrink-0">
                      <img src={tech.icon || "/placeholder.svg"} alt={tech.name} className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-white mb-1">{tech.name}</h4>
                      <p className="text-sm text-white/70">{tech.description}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="mt-8 bg-gradient-to-r from-purple-900/20 to-blue-900/20 p-6 rounded-lg border border-purple-900/30">
              <h4 className="text-lg font-medium text-white mb-3">Technical Specifications</h4>
              <div className="flex flex-wrap gap-2 mb-4">
                <Badge variant="outline" className="bg-purple-950/30 text-purple-300 border-purple-700/50">
                  Python 3.9+
                </Badge>
                <Badge variant="outline" className="bg-purple-950/30 text-purple-300 border-purple-700/50">
                  MediaPipe Hands
                </Badge>
                <Badge variant="outline" className="bg-purple-950/30 text-purple-300 border-purple-700/50">
                  Pyo 1.0.4
                </Badge>
                <Badge variant="outline" className="bg-purple-950/30 text-purple-300 border-purple-700/50">
                  OpenCV 4.5+
                </Badge>
                <Badge variant="outline" className="bg-purple-950/30 text-purple-300 border-purple-700/50">
                  TensorFlow Lite
                </Badge>
              </div>
              <p className="text-sm text-white/70">
                AeroMix runs on standard hardware with a webcam, requiring minimal CPU resources for real-time
                performance.
              </p>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          viewport={{ once: true }}
          className="mt-16 bg-gradient-to-r from-purple-900/20 via-indigo-900/20 to-blue-900/20 p-8 rounded-lg border border-purple-900/30"
        >
          <div className="flex flex-col md:flex-row items-center">
            <div className="mb-6 md:mb-0 md:mr-8 flex-shrink-0">
              <div className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 flex items-center justify-center">
                <ArrowRight className="h-8 w-8 text-white" />
              </div>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Future Developments</h3>
              <p className="text-white/70">
                The AeroMix system is continuously evolving. Upcoming features include multi-user collaboration,
                expanded gesture vocabulary, integration with popular DAWs (Digital Audio Workstations), and enhanced
                machine learning models for more precise gesture recognition.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
