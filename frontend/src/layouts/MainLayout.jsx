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
            y: [0, 40, 0],
            x: [0, 25, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-[-120px] left-[-120px] h-80 w-80 rounded-full bg-gradient-to-br from-cyan-500/25 via-blue-500/20 to-indigo-500/25 blur-3xl pointer-events-none"
        />

        {/* Secondary gradient orbs */}
        <motion.div
          animate={{
            y: [0, -50, 0],
            x: [0, -35, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
          className="absolute bottom-[-160px] right-[-160px] h-96 w-96 rounded-full bg-gradient-to-tl from-indigo-600/25 via-purple-500/20 to-blue-600/15 blur-3xl pointer-events-none"
        />

        {/* Tertiary accent orbs */}
        <motion.div
          animate={{
            y: [0, 60, 0],
            x: [0, -40, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 14,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
          className="absolute top-1/3 left-1/2 -translate-x-1/2 h-64 w-64 rounded-full bg-gradient-to-br from-blue-500/20 via-cyan-500/15 to-transparent blur-3xl pointer-events-none"
        />

        {/* Floating particles */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            animate={{
              y: [0, -30, 0],
              opacity: [0, 0.4, 0],
            }}
            transition={{
              duration: 4 + Math.random() * 3,
              repeat: Infinity,
              delay: Math.random() * 3,
              ease: "easeInOut",
            }}
            className="absolute rounded-full bg-cyan-400/15"
            style={{
              width: Math.random() * 3 + 2,
              height: Math.random() * 3 + 2,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}

        {/* Radial gradient background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(6,182,212,0.12),_transparent_50%)] pointer-events-none" />

        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.04] pointer-events-none" />
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
      <footer className="relative border-t border-white/5 bg-gradient-to-b from-slate-950 via-slate-950/95 to-slate-900/50 backdrop-blur-xl">
        {/* Subtle gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 via-transparent to-blue-500/5 pointer-events-none" />
        
        <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-10 py-16 relative">
          {/* Main Footer Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-12 mb-16">
            {/* Brand Section */}
            <div className="lg:col-span-2 space-y-5">
              <div className="flex items-center gap-3">
                <motion.div
                  whileHover={{ scale: 1.05, rotate: 3 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/25 transition-all duration-300"
                >
                  <span className="text-base font-bold tracking-wider text-white">AR</span>
                </motion.div>
                <div>
                  <h3 className="text-lg font-bold tracking-tight text-white">AutoResearchAI</h3>
                  <p className="text-[10px] text-cyan-400 font-semibold uppercase tracking-widest">Beta</p>
                </div>
              </div>
              <p className="text-sm leading-relaxed text-slate-400 max-w-sm">
                Multi-agent intelligence for professional research. Automate planning, analysis, verification, and reporting with advanced AI workflows.
              </p>
              
              {/* Social Links */}
              <div className="flex items-center gap-3 pt-2">
                {[
                  { name: 'GitHub', icon: 'github' },
                  { name: 'Twitter', icon: 'twitter' },
                  { name: 'Discord', icon: 'discord' },
                ].map((social) => (
                  <motion.a
                    key={social.name}
                    href="#"
                    whileHover={{ scale: 1.1, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-slate-400 transition-all duration-200 hover:border-cyan-500/30 hover:bg-cyan-500/10 hover:text-cyan-400"
                  >
                    <span className="text-xs font-semibold">{social.name[0]}</span>
                  </motion.a>
                ))}
              </div>
            </div>

            {/* Quick Links */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white">Quick Links</h4>
              <ul className="space-y-3">
                {['Research', 'Reports', 'History', 'Knowledge Hub'].map((link) => (
                  <li key={link}>
                    <motion.a
                      href="#"
                      whileHover={{ x: 4 }}
                      className="text-sm text-slate-400 hover:text-cyan-400 transition-all duration-200 inline-block"
                    >
                      {link}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white">Resources</h4>
              <ul className="space-y-3">
                {['Documentation', 'API Reference', 'GitHub', 'Status'].map((link) => (
                  <li key={link}>
                    <motion.a
                      href="#"
                      whileHover={{ x: 4 }}
                      className="text-sm text-slate-400 hover:text-cyan-400 transition-all duration-200 inline-block"
                    >
                      {link}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white">Legal</h4>
              <ul className="space-y-3">
                {['Privacy', 'Terms', 'Cookies', 'Contact'].map((link) => (
                  <li key={link}>
                    <motion.a
                      href="#"
                      whileHover={{ x: 4 }}
                      className="text-sm text-slate-400 hover:text-cyan-400 transition-all duration-200 inline-block"
                    >
                      {link}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Divider with gradient accent */}
          <div className="relative py-8">
            <div className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          </div>

          {/* Bottom Footer */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-slate-500">
              © {new Date().getFullYear()} AutoResearchAI. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <div className="inline-flex items-center gap-1.5 rounded-full bg-white/5 border border-white/10 px-3 py-1.5">
                <span className="text-[10px] text-slate-400 font-medium">Version</span>
                <span className="text-xs font-semibold text-slate-300">1.0</span>
                <span className="text-[10px] text-cyan-400 font-semibold">BETA</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span>Made with</span>
                <span className="text-red-500">❤</span>
                <span>for AI Research</span>
              </div>
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
