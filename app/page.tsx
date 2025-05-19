import { Suspense } from "react"
import HeroSection from "@/components/hero-section"
import FeaturesSection from "@/components/features-section"
import InteractiveDemo from "@/components/interactive-demo"
import TechnologySection from "@/components/technology-section"
import AboutSection from "@/components/about-section"
import Footer from "@/components/footer"
// Fix the extensions to match your actual files (.jsx)
import GestureControls from "@/components/GestureControls.tsx"
import AudioVisualizer from "@/components/AudioVisualizer.tsx"
import WebcamGestureDetector from "@/components/WebcamGestureDetector.tsx"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-black via-indigo-950 to-black text-white overflow-hidden">
      <HeroSection />
      <FeaturesSection />
      <Suspense fallback={<div className="h-screen flex items-center justify-center">Loading interactive demo...</div>}>
        <InteractiveDemo />
        <GestureControls />
        <AudioVisualizer />
        <WebcamGestureDetector />
      </Suspense>
      <TechnologySection />
      <AboutSection />
      <Footer />
    </main>
  )
}
