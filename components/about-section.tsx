"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Github, Linkedin, Mail, ExternalLink } from "lucide-react"

export default function AboutSection() {
  return (
    <section id="about" className="py-20 relative">
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
            About & Contact
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            Learn more about the creator behind AeroMix and get in touch
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <Card className="bg-black/40 border-purple-900/50 backdrop-blur-sm overflow-hidden">
            <CardContent className="p-0">
              <div className="grid grid-cols-1 md:grid-cols-3">
                <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 p-8 flex flex-col items-center justify-center">
                  <Avatar className="h-32 w-32 border-4 border-purple-500/30">
                    <AvatarImage src="/placeholder.svg?height=128&width=128" alt="Creator" />
                    <AvatarFallback className="bg-purple-900 text-white text-2xl">AM</AvatarFallback>
                  </Avatar>

                  <h3 className="text-xl font-semibold text-white mt-4">AeroMix Creator</h3>
                  <p className="text-white/70 text-sm mt-1">Audio Technology Innovator</p>

                  <div className="flex gap-3 mt-6">
                    <Button
                      size="icon"
                      variant="outline"
                      className="rounded-full h-10 w-10 bg-white/5 border-white/10 hover:bg-white/10"
                    >
                      <Github className="h-5 w-5 text-white" />
                    </Button>
                    <Button
                      size="icon"
                      variant="outline"
                      className="rounded-full h-10 w-10 bg-white/5 border-white/10 hover:bg-white/10"
                    >
                      <Linkedin className="h-5 w-5 text-white" />
                    </Button>
                    <Button
                      size="icon"
                      variant="outline"
                      className="rounded-full h-10 w-10 bg-white/5 border-white/10 hover:bg-white/10"
                    >
                      <Mail className="h-5 w-5 text-white" />
                    </Button>
                  </div>
                </div>

                <div className="md:col-span-2 p-8">
                  <h3 className="text-2xl font-semibold text-white mb-4">About the Project</h3>

                  <p className="text-white/80 mb-4">
                    AeroMix was born from a passion for creating more intuitive ways to interact with music and audio.
                    Inspired by the natural connection between movement and sound, this project aims to break down the
                    barriers between physical expression and digital audio manipulation.
                  </p>

                  <p className="text-white/80 mb-6">
                    The system combines computer vision, machine learning, and digital signal processing to create a
                    seamless experience that feels natural and responsive. Whether you're a professional musician, a
                    live performer, or just someone who loves to experiment with sound, AeroMix offers a new dimension
                    of creative control.
                  </p>

                  <div className="flex flex-col sm:flex-row gap-4 mt-8">
                    <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                      <Github className="mr-2 h-4 w-4" />
                      Get the Code on GitHub
                    </Button>
                    <Button variant="outline" className="border-purple-500 text-purple-400 hover:bg-purple-950/30">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      View Research Paper
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
            className="mt-12 text-center"
          >
            <h3 className="text-2xl font-semibold text-white mb-4">Get Involved</h3>
            <p className="text-white/70 max-w-2xl mx-auto mb-8">
              AeroMix is an open-source project and welcomes contributions from developers, musicians, and audio
              enthusiasts. Whether you want to improve the code, suggest features, or share your creative uses, we'd
              love to hear from you.
            </p>

            <Button
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              <Mail className="mr-2 h-5 w-5" />
              Contact Us
            </Button>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
