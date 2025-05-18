"use client"

import type React from "react"

import { useState, useRef } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Volume2, Music, Clock, Mic2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface FeatureCardProps {
  title: string
  description: string
  icon: React.ReactNode
  videoSrc: string
  index: number
}

function FeatureCard({ title, description, icon, videoSrc, index }: FeatureCardProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const handlePlaySound = () => {
    if (!audioRef.current) {
      audioRef.current = new Audio("/sounds/click.mp3")
      audioRef.current.volume = 0.3
    }

    audioRef.current.currentTime = 0
    audioRef.current.play().catch((e) => console.error("Audio play failed:", e))
  }

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play().catch((e) => console.error("Video play failed:", e))
      }
      setIsPlaying(!isPlaying)
    }
    handlePlaySound()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      viewport={{ once: true }}
      className="w-full"
    >
      <Card className="overflow-hidden bg-black/40 border-purple-900/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 h-full flex flex-col">
        <CardHeader className="pb-2">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center mb-2">
            {icon}
          </div>
          <CardTitle className="text-xl text-white">{title}</CardTitle>
          <CardDescription className="text-white/70">{description}</CardDescription>
        </CardHeader>
        <CardContent className="flex-grow p-0 relative group cursor-pointer" onClick={togglePlay}>
          <div className="aspect-video bg-black/50 overflow-hidden relative">
            <video
              ref={videoRef}
              src={videoSrc}
              className="w-full h-full object-cover"
              loop
              muted
              playsInline
              onEnded={() => setIsPlaying(false)}
            />
            <div
              className={cn(
                "absolute inset-0 flex items-center justify-center bg-black/40 transition-opacity",
                isPlaying ? "opacity-0" : "opacity-100",
              )}
            >
              <Button
                size="icon"
                variant="ghost"
                className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-sm text-white hover:bg-white/20 hover:scale-110 transition-all"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 5V19L19 12L8 5Z" fill="currentColor" />
                </svg>
              </Button>
            </div>
          </div>
        </CardContent>
        <CardFooter className="pt-2 pb-4">
          <Button
            variant="ghost"
            className="w-full text-purple-400 hover:text-purple-300 hover:bg-purple-950/30"
            onClick={togglePlay}
          >
            {isPlaying ? "Pause Demo" : "Play Demo"}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  )
}

export default function FeaturesSection() {
  const features = [
    {
      title: "Volume Control",
      description: "Control volume levels with intuitive hand movements",
      icon: <Volume2 className="h-6 w-6 text-white" />,
      videoSrc: "/videos/volume-demo.mp4",
    },
    {
      title: "Bass Control",
      description: "Adjust bass frequencies with dynamic gestures",
      icon: <Music className="h-6 w-6 text-white" />,
      videoSrc: "/videos/bass-demo.mp4",
    },
    {
      title: "Tempo Control",
      description: "Change tempo in real-time with rhythmic movements",
      icon: <Clock className="h-6 w-6 text-white" />,
      videoSrc: "/videos/tempo-demo.mp4",
    },
    {
      title: "Pitch Control",
      description: "Manipulate pitch with precise hand positioning",
      icon: <Mic2 className="h-6 w-6 text-white" />,
      videoSrc: "/videos/pitch-demo.mp4",
    },
  ]

  return (
    <section id="features" className="py-20 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-indigo-950/20 to-black/50 z-0"></div>

      <div className="container relative z-10 px-4 md:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
            See It In Action
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            Experience the power of gesture-based audio control with these four key features
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              videoSrc={feature.videoSrc}
              index={index}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
