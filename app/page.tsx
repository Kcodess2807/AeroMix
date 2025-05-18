import { Suspense } from "react"
import HeroSection from "@/components/hero-section"
import FeaturesSection from "@/components/features-section"
import InteractiveDemo from "@/components/interactive-demo"
import TechnologySection from "@/components/technology-section"
import AboutSection from "@/components/about-section"
import Footer from "@/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-black via-indigo-950 to-black text-white overflow-hidden">
      <HeroSection />
      <FeaturesSection />
      <Suspense fallback={<div className="h-screen flex items-center justify-center">Loading interactive demo...</div>}>
        <InteractiveDemo />
      </Suspense>
      <TechnologySection />
      <AboutSection />
      <Footer />
    </main>
  )
}
