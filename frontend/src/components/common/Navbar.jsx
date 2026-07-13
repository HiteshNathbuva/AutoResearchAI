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
      transition={{ duration: 0.45 }}
      className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-2xl shadow-lg shadow-cyan-500/5"
    >
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-10">

        {/* Logo */}

        <div className="flex cursor-pointer items-center gap-4">

          <motion.div
            whileHover={{
              scale: 1.08,
              rotate: 3,
            }}
            className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/20"
          >
            <span className="text-lg font-bold tracking-wider text-white">
              AR
            </span>
          </motion.div>

          <div>

            <div className="flex items-center gap-2">

              <h1 className="text-lg font-bold tracking-tight text-white">
                AutoResearchAI
              </h1>

              <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-cyan-300">
                Beta
              </span>

            </div>

            <p className="text-xs text-slate-400">
              AI Research Operating System
            </p>

          </div>

        </div>

        {/* Desktop Navigation */}

        <nav className="hidden items-center gap-2 lg:flex">

          {navLinks.map((item) => {

            const Icon = item.icon;

            return (
              <motion.a
                whileHover={{ y: -2 }}
                key={item.name}
                href={item.href}
                className="group relative flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-slate-300 transition hover:text-white"
              >

                <Icon size={17} />

                {item.name}

                <span className="absolute bottom-0 left-4 h-[2px] w-0 rounded-full bg-cyan-400 transition-all duration-300 group-hover:w-[60%]" />

              </motion.a>
            );

          })}

        </nav>

        {/* Desktop CTA */}

        <div className="hidden lg:block">

          <motion.button
            whileHover={{
              scale: 1.03,
            }}
            whileTap={{
              scale: 0.97,
            }}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 transition"
          >

            <Plus size={18} />

            New Research

          </motion.button>

        </div>

        {/* Mobile Menu Button */}

        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="rounded-xl border border-white/10 p-2 text-white lg:hidden"
        >

          {mobileMenuOpen ? (
            <X size={22} />
          ) : (
            <Menu size={22} />
          )}

        </button>

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
            className="overflow-hidden border-t border-white/10 bg-slate-950 lg:hidden"
          >

            <div className="space-y-2 px-6 py-5">

              {navLinks.map((item) => {

                const Icon = item.icon;

                return (

                  <a
                    key={item.name}
                    href={item.href}
                    className="flex items-center gap-3 rounded-xl px-3 py-3 text-slate-300 transition hover:bg-white/5 hover:text-white"
                  >

                    <Icon size={18} />

                    {item.name}

                  </a>

                );

              })}

              <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3 font-semibold text-white">

                <Plus size={18} />

                New Research

              </button>

            </div>

          </motion.div>

        )}

      </AnimatePresence>

    </motion.header>
  );
}

export default Navbar;
