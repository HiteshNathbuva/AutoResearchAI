import { motion } from "framer-motion";
import Navbar from "../components/common/Navbar";

function MainLayout({ children }) {
  return (
    <div className="relative min-h-screen bg-slate-950 text-white overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        {/* Primary gradient orbs */}
        <motion.div
          animate={{
            y: [0, 30, 0],
            x: [0, 20, 0],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-[-120px] left-[-120px] h-80 w-80 rounded-full bg-gradient-to-br from-cyan-500/20 to-cyan-500/10 blur-3xl pointer-events-none"
        />

        {/* Secondary gradient orbs */}
        <motion.div
          animate={{
            y: [0, -40, 0],
            x: [0, -30, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute bottom-[-160px] right-[-160px] h-96 w-96 rounded-full bg-gradient-to-tl from-indigo-600/20 to-blue-600/10 blur-3xl pointer-events-none"
        />

        {/* Tertiary accent orbs */}
        <motion.div
          animate={{
            y: [0, 50, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
          className="absolute top-1/3 left-1/2 h-64 w-64 rounded-full bg-gradient-to-br from-blue-500/15 to-cyan-500/5 blur-3xl pointer-events-none"
        />

        {/* Radial gradient background */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.08),transparent_45%)] pointer-events-none" />

        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-grid-pattern opacity-5 pointer-events-none" />
      </div>

      {/* Navigation */}
      <Navbar />

      {/* Main Content */}
      <main className="relative mx-auto w-full max-w-7xl px-6 pt-28 pb-20 sm:px-8 lg:px-10">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-white/10 py-8 bg-gradient-to-r from-slate-950/50 via-slate-950/30 to-slate-950/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-10">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-400">
              © {new Date().getFullYear()} AutoResearchAI • Production Grade Multi-Agent Research Platform
            </p>
            <div className="flex gap-6">
              <a href="#" className="text-sm text-slate-400 hover:text-slate-300 transition">
                Documentation
              </a>
              <a href="#" className="text-sm text-slate-400 hover:text-slate-300 transition">
                API Reference
              </a>
              <a href="#" className="text-sm text-slate-400 hover:text-slate-300 transition">
                Status
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Scroll indicator */}
      <motion.div
        animate={{ y: [0, 6, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="fixed bottom-8 left-1/2 transform -translate-x-1/2 hidden lg:flex flex-col items-center gap-2 text-slate-500 pointer-events-none"
      >
        <p className="text-xs font-semibold uppercase tracking-widest">Scroll</p>
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </motion.div>
    </div>
  );
}

export default MainLayout;
