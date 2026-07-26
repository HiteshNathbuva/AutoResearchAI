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
      <footer className="relative border-t border-white/[0.06] bg-slate-950/80 backdrop-blur-2xl">
        {/* Subtle gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/30 to-slate-950/60 pointer-events-none" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_rgba(6,182,212,0.03),_transparent_70%)] pointer-events-none" />
        
        <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-10 py-20 relative">
          {/* Main Footer Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-16 gap-y-12 mb-16">
            {/* Brand Section */}
            <div className="lg:col-span-1 space-y-5">
              <div className="flex items-center gap-3">
                <motion.div
                  whileHover={{ scale: 1.08 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/15 transition-all duration-300"
                >
                  <span className="text-xs font-bold tracking-wider text-white">AR</span>
                </motion.div>
                <div>
                  <h3 className="text-sm font-semibold tracking-tight text-white">AutoResearchAI</h3>
                  <motion.span 
                    initial={{ opacity: 0.7 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
                    className="text-[9px] text-cyan-400 font-semibold uppercase tracking-widest"
                  >
                    Beta
                  </motion.span>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-slate-400 max-w-[240px]">
                Multi-agent intelligence for professional research. Automate planning, analysis, verification, and reporting with advanced AI workflows.
              </p>
              
              {/* Social Links */}
              <div className="flex items-center gap-2 pt-1">
                {[
                  { name: 'GitHub', icon: 'github' },
                  { name: 'Twitter', icon: 'twitter' },
                  { name: 'Discord', icon: 'discord' },
                ].map((social) => (
                  <motion.a
                    key={social.name}
                    href="#"
                    whileHover={{ y: -3, scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex h-7 w-7 items-center justify-center rounded-md border border-white/8 bg-white/[0.03] text-slate-500 transition-all duration-300 hover:border-cyan-500/30 hover:bg-cyan-500/10 hover:text-cyan-400"
                  >
                    <span className="text-[10px] font-semibold">{social.name[0]}</span>
                  </motion.a>
                ))}
              </div>
            </div>

            {/* Product Links */}
            <div className="space-y-4">
              <motion.h4 
                className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-300"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
              >
                Product
              </motion.h4>
              <ul className="space-y-2.5">
                {['Research', 'Reports', 'History', 'Knowledge Hub'].map((link, idx) => (
                  <li key={link}>
                    <motion.a
                      href="#"
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: idx * 0.05 }}
                      whileHover={{ x: 4 }}
                      className="text-xs text-slate-400 hover:text-white transition-colors duration-200 inline-flex items-center gap-1.5 group"
                    >
                      <span className="w-0 group-hover:w-1.5 h-[1px] bg-cyan-400 transition-all duration-300" />
                      {link}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources Links */}
            <div className="space-y-4">
              <motion.h4 
                className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-300"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 }}
              >
                Resources
              </motion.h4>
              <ul className="space-y-2.5">
                {['Documentation', 'API Reference', 'GitHub', 'Status'].map((link, idx) => (
                  <li key={link}>
                    <motion.a
                      href="#"
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 0.15 + idx * 0.05 }}
                      whileHover={{ x: 4 }}
                      className="text-xs text-slate-400 hover:text-white transition-colors duration-200 inline-flex items-center gap-1.5 group"
                    >
                      <span className="w-0 group-hover:w-1.5 h-[1px] bg-cyan-400 transition-all duration-300" />
                      {link}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company Links */}
            <div className="space-y-4">
              <motion.h4 
                className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-300"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
              >
                Company
              </motion.h4>
              <ul className="space-y-2.5">
                {['Privacy', 'Terms', 'Cookies', 'Contact'].map((link, idx) => (
                  <li key={link}>
                    <motion.a
                      href="#"
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 0.25 + idx * 0.05 }}
                      whileHover={{ x: 4 }}
                      className="text-xs text-slate-400 hover:text-white transition-colors duration-200 inline-flex items-center gap-1.5 group"
                    >
                      <span className="w-0 group-hover:w-1.5 h-[1px] bg-cyan-400 transition-all duration-300" />
                      {link}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Premium Divider with glow */}
          <div className="relative mb-8">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent h-[1px]" />
            <div className="border-t border-white/[0.04]" />
          </div>

          {/* Bottom Footer */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-[11px] text-slate-500 font-medium">
              © {new Date().getFullYear()} AutoResearchAI. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              {/* Version Badge */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="inline-flex items-center gap-2 rounded-full bg-white/[0.02] border border-white/[0.06] px-3 py-1.5 backdrop-blur-sm"
              >
                <span className="text-[9px] text-slate-500 font-semibold uppercase tracking-wider">Version</span>
                <span className="text-[11px] font-medium text-slate-400">1.0</span>
                <span className="text-[9px] text-cyan-400 font-semibold uppercase tracking-wider">Beta</span>
              </motion.div>
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
