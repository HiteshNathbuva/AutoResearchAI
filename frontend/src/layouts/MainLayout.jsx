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

      {/* Footer */}
      <footer className="relative border-t border-white/10 mt-20 bg-gradient-to-b from-slate-950/50 to-slate-950/80 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-10 py-12">
          {/* Footer Content */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            {/* Branding */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold tracking-tight text-white">AutoResearchAI</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Multi-agent intelligence for professional research. Automate planning, analysis, verification, and reporting.
              </p>
            </div>

            {/* Quick Links */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-300">Quick Links</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Research</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Reports</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">History</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Knowledge Hub</a></li>
              </ul>
            </div>

            {/* Resources */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-300">Resources</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Documentation</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">API Reference</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">GitHub</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Status</a></li>
              </ul>
            </div>

            {/* Legal */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-300">Legal</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Privacy Policy</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Terms of Service</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Cookies</a></li>
                <li><a href="#" className="text-xs text-slate-400 hover:text-slate-300 transition">Contact</a></li>
              </ul>
            </div>
          </div>

          {/* Footer Divider */}
          <div className="border-t border-white/5 pt-6">
            <p className="text-xs text-slate-500 text-center">
              © {new Date().getFullYear()} AutoResearchAI. All rights reserved. Production Grade Multi-Agent Research Platform.
            </p>
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
