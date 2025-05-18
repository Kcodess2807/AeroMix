import { Github } from "lucide-react"

export default function Footer() {
  return (
    <footer className="py-12 bg-black/80 border-t border-purple-900/30">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-6 md:mb-0">
            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
              AeroMix
            </h2>
            <p className="text-white/60 mt-1">Shape Sound With Your Movements</p>
          </div>

          <div className="flex flex-col items-center md:items-end">
            <div className="flex gap-4 mb-4">
              <a href="#" className="text-white/60 hover:text-purple-400 transition-colors">
                <Github className="h-5 w-5" />
              </a>
            </div>
            <p className="text-white/40 text-sm">Powered by Python, Pyo, and shadcn/ui</p>
            <p className="text-white/40 text-sm mt-1">© {new Date().getFullYear()} AeroMix. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
