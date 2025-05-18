"use client"

import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Slider } from "@/components/ui/slider"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Volume2, Music, Clock, Mic2, Play, Pause, RefreshCw, Video } from "lucide-react"
import { cn } from "@/lib/utils"
import { Toaster } from "@/components/ui/toaster"

export default function InteractiveDemo() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState([75])
  const [bass, setBass] = useState([50])
  const [tempo, setTempo] = useState([100])
  const [pitch, setPitch] = useState([0])
  const [activeTab, setActiveTab] = useState("sliders")
  const [isWebcamActive, setIsWebcamActive] = useState(false)
  const [recognizedGesture, setRecognizedGesture] = useState<string | null>(null)

  const audioContextRef = useRef<AudioContext | null>(null)
  const audioSourceRef = useRef<AudioBufferSourceNode | null>(null)
  const gainNodeRef = useRef<GainNode | null>(null)
  const bassFilterRef = useRef<BiquadFilterNode | null>(null)
  const webcamRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const audioBufferRef = useRef<AudioBuffer | null>(null)
  let gestureInterval: NodeJS.Timeout | null = null // Declare gestureInterval here

  // Initialize audio context
  useEffect(() => {
    const initAudio = async () => {
      try {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()

        // Create gain node for volume control
        gainNodeRef.current = audioContextRef.current.createGain()

        // Create filter for bass control
        bassFilterRef.current = audioContextRef.current.createBiquadFilter()
        bassFilterRef.current.type = "lowshelf"
        bassFilterRef.current.frequency.value = 200

        // Connect nodes
        bassFilterRef.current.connect(gainNodeRef.current)
        gainNodeRef.current.connect(audioContextRef.current.destination)

        // Load sample audio
        const response = await fetch("/sounds/loop.mp3")
        const arrayBuffer = await response.arrayBuffer()
        audioBufferRef.current = await audioContextRef.current.decodeAudioData(arrayBuffer)
      } catch (error) {
        console.error("Error initializing audio:", error)
      }
    }

    initAudio()

    return () => {
      if (audioContextRef.current && audioContextRef.current.state !== "closed") {
        audioContextRef.current.close()
      }
    }
  }, [])

  // Update audio parameters when sliders change
  useEffect(() => {
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.value = volume[0] / 100
    }

    if (bassFilterRef.current) {
      // Map 0-100 to -40 to 40 dB
      bassFilterRef.current.gain.value = ((bass[0] - 50) / 50) * 40
    }

    if (audioSourceRef.current && audioContextRef.current) {
      // Map 50-150 to 0.5-1.5 playback rate
      const playbackRate = tempo[0] / 100
      audioSourceRef.current.playbackRate.value = playbackRate

      // Pitch is handled through detune (cents)
      // Map -12 to 12 to -1200 to 1200 cents (1 semitone = 100 cents)
      audioSourceRef.current.detune.value = pitch[0] * 100
    }
  }, [volume, bass, tempo, pitch])

  // Play/pause audio
  const togglePlayback = () => {
    if (!audioContextRef.current || !audioBufferRef.current) return

    if (isPlaying) {
      if (audioSourceRef.current) {
        audioSourceRef.current.stop()
        audioSourceRef.current = null
      }
    } else {
      // Resume audio context if suspended
      if (audioContextRef.current.state === "suspended") {
        audioContextRef.current.resume()
      }

      // Create new source node
      audioSourceRef.current = audioContextRef.current.createBufferSource()
      audioSourceRef.current.buffer = audioBufferRef.current
      audioSourceRef.current.loop = true

      // Set initial parameters
      audioSourceRef.current.playbackRate.value = tempo[0] / 100
      audioSourceRef.current.detune.value = pitch[0] * 100

      // Connect and play
      audioSourceRef.current.connect(bassFilterRef.current!)
      audioSourceRef.current.start()

      // Handle when audio finishes (though it's looping)
      audioSourceRef.current.onended = () => {
        setIsPlaying(false)
      }
    }

    setIsPlaying(!isPlaying)
  }

  // Reset all parameters
  const resetParameters = () => {
    setVolume([75])
    setBass([50])
    setTempo([100])
    setPitch([0])
  }

  // Simulate gesture recognition
  const toggleWebcam = () => {
    if (isWebcamActive) {
      setIsWebcamActive(false)
      if (gestureInterval) {
        clearInterval(gestureInterval)
        gestureInterval = null
      }
      return
    }

    setIsWebcamActive(true)

    // Simulate gesture recognition with random gestures
    const gestures = ["Volume Up", "Volume Down", "Bass Boost", "Increase Tempo", "Lower Pitch"]

    gestureInterval = setInterval(() => {
      const randomGesture = gestures[Math.floor(Math.random() * gestures.length)]
      setRecognizedGesture(randomGesture)

      // Apply the "recognized" gesture effect
      switch (randomGesture) {
        case "Volume Up":
          setVolume((prev) => [Math.min(prev[0] + 5, 100)])
          break
        case "Volume Down":
          setVolume((prev) => [Math.max(prev[0] - 5, 0)])
          break
        case "Bass Boost":
          setBass((prev) => [Math.min(prev[0] + 10, 100)])
          break
        case "Increase Tempo":
          setTempo((prev) => [Math.min(prev[0] + 5, 150)])
          break
        case "Lower Pitch":
          setPitch((prev) => [Math.max(prev[0] - 1, -12)])
          break
      }

      // Clear the gesture after a short delay
      setTimeout(() => {
        setRecognizedGesture(null)
      }, 2000)
    }, 3000)

    return () => {
      if (gestureInterval) {
        clearInterval(gestureInterval)
        gestureInterval = null
      }
    }
  }

  // Visualizer animation
  useEffect(() => {
    if (!isPlaying || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    canvas.width = canvas.clientWidth
    canvas.height = canvas.clientHeight

    let animationId: number

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw waveform visualization
      const barCount = 64
      const barWidth = canvas.width / barCount
      const barMaxHeight = canvas.height * 0.8

      for (let i = 0; i < barCount; i++) {
        // Create a dynamic waveform based on current parameters
        const volumeFactor = volume[0] / 100
        const bassFactor = bass[0] / 50 - 1 // -1 to 1
        const tempoFactor = tempo[0] / 100
        const pitchFactor = (pitch[0] + 12) / 24 // 0 to 1

        // Calculate bar height with some randomness and parameter influence
        const time = Date.now() * 0.001 * tempoFactor
        const x = i / barCount
        const wave1 = Math.sin(time * 2 + x * Math.PI * 6) * 0.5 + 0.5
        const wave2 = Math.sin(time * 3 + x * Math.PI * 8) * 0.5 + 0.5
        const combinedWave = (wave1 * 0.6 + wave2 * 0.4) * volumeFactor

        // Add bass influence (more height in lower frequencies)
        const bassInfluence = Math.max(0, 1 - (i / barCount) * 2) * bassFactor * 0.5

        // Add pitch influence (shift the wave pattern)
        const pitchShift = Math.sin(x * Math.PI * 2 + pitchFactor * Math.PI * 2) * 0.2

        const barHeight = (combinedWave + bassInfluence + pitchShift) * barMaxHeight

        // Gradient based on parameters
        const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height)
        gradient.addColorStop(0, `rgba(${103 + pitch[0] * 5}, ${232 - bass[0]}, ${249 - tempo[0] / 2}, 0.8)`)
        gradient.addColorStop(1, `rgba(${192 - pitch[0] * 5}, ${132 + bass[0] / 2}, ${252 - tempo[0] / 3}, 0.4)`)

        ctx.fillStyle = gradient
        ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 1, barHeight)
      }

      animationId = requestAnimationFrame(draw)
    }

    draw()

    return () => {
      cancelAnimationFrame(animationId)
    }
  }, [isPlaying, volume, bass, tempo, pitch])

  return (
    <section id="demo" className="py-20 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-indigo-950/30 to-black/50 z-0"></div>

      <div className="container relative z-10 px-4 md:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-cyan-500">
            Try AeroMix Live
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            Experience the power of AeroMix with this interactive demo. Adjust controls manually or activate gesture
            recognition.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <Card className="col-span-1 lg:col-span-2 bg-black/40 border-purple-900/50 backdrop-blur-sm">
            <CardContent className="p-6">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="w-full mb-6 bg-black/30">
                  <TabsTrigger value="sliders" className="flex-1 data-[state=active]:bg-purple-900/30">
                    Manual Controls
                  </TabsTrigger>
                  <TabsTrigger value="gesture" className="flex-1 data-[state=active]:bg-purple-900/30">
                    Gesture Recognition
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="sliders" className="mt-0">
                  <div className="space-y-8">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Volume2 className="h-5 w-5 text-purple-400" />
                          <span className="text-white/90">Volume</span>
                        </div>
                        <span className="text-white/70">{volume[0]}%</span>
                      </div>
                      <Slider
                        value={volume}
                        onValueChange={setVolume}
                        max={100}
                        step={1}
                        className="[&_[role=slider]]:h-5 [&_[role=slider]]:w-5 [&_[role=slider]]:bg-gradient-to-r [&_[role=slider]]:from-purple-500 [&_[role=slider]]:to-cyan-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Music className="h-5 w-5 text-purple-400" />
                          <span className="text-white/90">Bass</span>
                        </div>
                        <span className="text-white/70">
                          {bass[0] > 50 ? `+${bass[0] - 50}%` : bass[0] < 50 ? `-${50 - bass[0]}%` : "0%"}
                        </span>
                      </div>
                      <Slider
                        value={bass}
                        onValueChange={setBass}
                        max={100}
                        step={1}
                        className="[&_[role=slider]]:h-5 [&_[role=slider]]:w-5 [&_[role=slider]]:bg-gradient-to-r [&_[role=slider]]:from-purple-500 [&_[role=slider]]:to-cyan-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Clock className="h-5 w-5 text-purple-400" />
                          <span className="text-white/90">Tempo</span>
                        </div>
                        <span className="text-white/70">{tempo[0]}%</span>
                      </div>
                      <Slider
                        value={tempo}
                        onValueChange={setTempo}
                        min={50}
                        max={150}
                        step={1}
                        className="[&_[role=slider]]:h-5 [&_[role=slider]]:w-5 [&_[role=slider]]:bg-gradient-to-r [&_[role=slider]]:from-purple-500 [&_[role=slider]]:to-cyan-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Mic2 className="h-5 w-5 text-purple-400" />
                          <span className="text-white/90">Pitch</span>
                        </div>
                        <span className="text-white/70">{pitch[0] > 0 ? `+${pitch[0]}` : pitch[0]}</span>
                      </div>
                      <Slider
                        value={pitch}
                        onValueChange={setPitch}
                        min={-12}
                        max={12}
                        step={1}
                        className="[&_[role=slider]]:h-5 [&_[role=slider]]:w-5 [&_[role=slider]]:bg-gradient-to-r [&_[role=slider]]:from-purple-500 [&_[role=slider]]:to-cyan-500"
                      />
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="gesture" className="mt-0">
                  <div className="aspect-video bg-black/50 rounded-lg overflow-hidden relative mb-6">
                    {isWebcamActive ? (
                      <>
                        <video ref={webcamRef} className="w-full h-full object-cover" autoPlay playsInline muted />
                        {recognizedGesture && (
                          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-purple-600/80 text-white px-4 py-2 rounded-full backdrop-blur-sm">
                            Gesture: {recognizedGesture}
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="w-full h-full flex flex-col items-center justify-center text-white/70">
                        <Video className="h-16 w-16 mb-4 text-purple-500/50" />
                        <p>Activate webcam to simulate gesture recognition</p>
                        <p className="text-sm text-white/50 mt-2">No actual video will be recorded or sent</p>
                      </div>
                    )}
                  </div>

                  <Button
                    onClick={toggleWebcam}
                    className={cn(
                      "w-full mb-4",
                      isWebcamActive
                        ? "bg-red-600 hover:bg-red-700"
                        : "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700",
                    )}
                  >
                    {isWebcamActive ? "Deactivate Simulation" : "Activate Gesture Simulation"}
                  </Button>

                  <p className="text-white/60 text-sm text-center">
                    This is a simulation of how gesture recognition would work. In the real AeroMix system, your actual
                    gestures would control the audio parameters.
                  </p>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-purple-900/50 backdrop-blur-sm flex flex-col">
            <CardContent className="p-6 flex-grow flex flex-col">
              <div className="mb-6 flex justify-between items-center">
                <h3 className="text-xl font-semibold text-white">Audio Visualizer</h3>
                <div className="flex gap-2">
                  <Button
                    size="icon"
                    variant="outline"
                    className="h-8 w-8 border-purple-900/50 hover:bg-purple-900/30"
                    onClick={resetParameters}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant={isPlaying ? "destructive" : "default"}
                    className={cn(
                      "h-8 w-8",
                      !isPlaying &&
                        "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700",
                    )}
                    onClick={togglePlayback}
                  >
                    {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div className="flex-grow relative bg-black/30 rounded-lg overflow-hidden">
                <canvas ref={canvasRef} className="w-full h-full" />

                {!isPlaying && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Button
                      size="lg"
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                      onClick={togglePlayback}
                    >
                      <Play className="mr-2 h-5 w-5" />
                      Play Audio Loop
                    </Button>
                  </div>
                )}
              </div>

              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-400">{volume[0]}</div>
                  <div className="text-xs text-white/60">VOLUME</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-cyan-400">
                    {bass[0] > 50 ? `+${bass[0] - 50}` : bass[0] < 50 ? `-${50 - bass[0]}` : "0"}
                  </div>
                  <div className="text-xs text-white/60">BASS</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-400">{tempo[0]}</div>
                  <div className="text-xs text-white/60">TEMPO</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-cyan-400">{pitch[0] > 0 ? `+${pitch[0]}` : pitch[0]}</div>
                  <div className="text-xs text-white/60">PITCH</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      <Toaster />
    </section>
  )
}
