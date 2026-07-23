import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import {
  BrainCircuit,
  BookOpen,
  FileText,
  History,
  Plus,
  Menu,
  X,
  FileText as FileIcon,
  ExternalLink,
  HelpCircle,
} from "lucide-react";

function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    {
      name: "Research",
      href: "#",
      icon: BrainCircuit,
    },
    {
      name: "Reports",
      href: "#",
      icon: FileText,
    },
    {
      name: "History",
      href: "#",
      icon: History,
    },
    {
      name: "Knowledge Hub",
      href: "#",
      icon: BookOpen,
    },
  ];

  return (
    <motion.header
      initial={{ y: -70, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.45, ease: [0.25, 0.1, 0.25, 1] }}
      className="fixed inset-x-0 top-0 z-50 border-b border-white/5 bg-slate-950/70 backdrop-blur-xl shadow-2xl shadow-black/20"
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 via-transparent to-blue-500/5 pointer-events-none" />
      
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-10 relative">

        {/* Logo */}
        <motion.div 
          className="flex cursor-pointer items-center gap-4 group"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div
            whileHover={{
              scale: 1.05,
              rotate: 2,
            }}
            whileTap={{ scale: 0.95 }}
            className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
          >
            {/* Inner glow effect */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/20 to-transparent" />
            <span className="relative text-lg font-bold tracking-wider text-white">
              AR
            </span>
          </motion.div>

          <div className="flex flex-col">
            <div className="flex items-center gap-2.5">
              <h1 className="text-lg font-bold tracking-tight text-white">
                AutoResearchAI
              </h1>
              <motion.span 
                whileHover={{ scale: 1.05 }}
                className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-cyan-300 shadow-sm shadow-cyan-500/10"
              >
                Beta
              </motion.span>
            </div>

            <motion.p
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-xs font-medium bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent tracking-wide"
            >
              AI Research Operating System
            </motion.p>
          </div>
        </motion.div>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-1 lg:flex">
          {navLinks.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.a
                key={item.name}
                href={item.href}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.95 }}
                className="group relative flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-400 transition-all duration-200 hover:text-white hover:bg-white/5"
              >
                <Icon size={17} className="transition-colors duration-200 group-hover:text-cyan-400" />
                {item.name}
                <motion.span 
                  className="absolute bottom-0 left-4 h-[2px] w-0 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 transition-all duration-300 group-hover:w-[calc(100%-32px)]" 
                />
              </motion.a>
            );
          })}
        </nav>

        {/* Desktop CTA */}
        <div className="hidden lg:flex items-center gap-3">
          <motion.a
            href="#"
            whileHover={{ scale: 1.05, y: -1 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-400 transition-all duration-200 hover:text-white hover:bg-white/5"
          >
            <BrainCircuit size={18} />
            <span className="hidden sm:inline">GitHub</span>
          </motion.a>
          
          <motion.button
            whileHover={{
              scale: 1.03,
              y: -1,
              boxShadow: "0 8px 25px -5px rgba(6, 182, 212, 0.4)",
            }}
            whileTap={{
              scale: 0.97,
            }}
            transition={{ duration: 0.15 }}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-cyan-500/25 transition-all duration-300"
          >
            <Plus size={18} />
            New Research
          </motion.button>
        </div>

        {/* Mobile Menu Button */}
        <motion.button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="rounded-xl border border-white/10 bg-white/5 p-2.5 text-white lg:hidden hover:bg-white/10 transition-colors duration-200"
        >
          <AnimatePresence mode="wait">
            {mobileMenuOpen ? (
              <motion.div
                key="close"
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <X size={22} />
              </motion.div>
            ) : (
              <motion.div
                key="menu"
                initial={{ rotate: 90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: -90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Menu size={22} />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{
              opacity: 0,
              height: 0,
            }}
            animate={{
              opacity: 1,
              height: "auto",
            }}
            exit={{
              opacity: 0,
              height: 0,
            }}
            transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
            className="overflow-hidden border-t border-white/5 bg-slate-950/95 backdrop-blur-xl lg:hidden"
          >
            <motion.div 
              className="space-y-1 px-6 py-6"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            >
              {navLinks.map((item, index) => {
                const Icon = item.icon;
                return (
                  <motion.a
                    key={item.name}
                    href={item.href}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    whileHover={{ x: 4 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex items-center gap-3 rounded-xl px-4 py-3.5 text-slate-400 transition-all duration-200 hover:bg-white/5 hover:text-white"
                  >
                    <Icon size={18} className="transition-colors duration-200" />
                    <span className="font-medium">{item.name}</span>
                  </motion.a>
                );
              })}

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.2 }}
                className="pt-4 space-y-2"
              >
                <motion.button
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 py-3.5 font-semibold text-white shadow-lg shadow-cyan-500/25 transition-all duration-300"
                >
                  <Plus size={18} />
                  New Research
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 py-3.5 font-medium text-slate-400 transition-all duration-200 hover:bg-white/10 hover:text-white"
                >
                  <BrainCircuit size={18} />
                  View on Github
                </motion.button>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}

export default Navbar;
