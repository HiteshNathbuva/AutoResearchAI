import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowUp } from "lucide-react";
import Navbar from "../components/common/Navbar";

function MainLayout({ children }) {
  const [showBackToTop, setShowBackToTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 400);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

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

      {/* Premium Footer */}
      <footer className="relative border-t border-white/10 bg-gradient-to-b from-slate-950 via-slate-950/95 to-slate-900/50 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-10 py-16">
          {/* Main Footer Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-12 mb-16">
            {/* Brand Section */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/20">
                  <span className="text-sm font-bold text-white">AR</span>
                </div>
                <div>
                  <h3 className="text-base font-bold tracking-tight text-white">AutoResearchAI</h3>
                  <p className="text-[10px] text-cyan-400 font-semibold uppercase tracking-widest">Beta</p>
                </div>
              </div>
              <p className="text-sm leading-relaxed text-slate-400 max-w-sm">
                Multi-agent intelligence for professional research. Automate planning, analysis, verification, and reporting with advanced AI workflows.
              </p>
              <p className="text-xs text-slate-500 flex items-center gap-2">
                <span>Made with</span>
                <span className="text-red-500">❤</span>
                <span>for AI Research</span>
              </p>
            </div>

            {/* Quick Links */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white">Quick Links</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Research</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Reports</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">History</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Knowledge Hub</a></li>
              </ul>
            </div>

            {/* Resources */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white">Resources</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Documentation</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">API Reference</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">GitHub</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Status</a></li>
              </ul>
            </div>

            {/* Legal */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white">Legal</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Privacy</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Terms</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Cookies</a></li>
                <li><a href="#" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-150">Contact</a></li>
              </ul>
            </div>
          </div>

          {/* Divider with gradient accent */}
          <div className="relative py-8">
            <div className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          </div>

          {/* Bottom Footer */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
            <p>© {new Date().getFullYear()} AutoResearchAI. All rights reserved.</p>
            <div className="inline-flex items-center gap-1 rounded-full bg-white/5 border border-white/10 px-3 py-1">
              <span className="text-[10px] text-slate-400">Version</span>
              <span className="font-semibold text-slate-300">1.0</span>
              <span className="text-[10px] text-cyan-400 font-semibold">BETA</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Back To Top Button */}
      <AnimatePresence>
        {showBackToTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.2 }}
            onClick={scrollToTop}
            className="fixed bottom-8 right-8 z-40 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 p-3 text-white shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-all hover:scale-110"
          >
            <ArrowUp size={20} />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}

export default MainLayout;
