import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

function HeroSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.12,
        delayChildren: 0.15,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] },
    },
  };

  return (
    <section className="relative min-h-[calc(100vh-5rem)] flex items-center justify-center py-12 sm:py-16 lg:py-20">
      {/* Premium Animated Background */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        {/* Animated gradient orbs */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-[10%] left-[5%] h-96 w-96 rounded-full bg-gradient-to-br from-cyan-500/25 via-blue-500/20 to-indigo-500/25 blur-3xl"
        />
        
        <motion.div
          animate={{
            scale: [1, 1.15, 1],
            opacity: [0.25, 0.4, 0.25],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
          className="absolute bottom-[10%] right-[5%] h-[28rem] w-[28rem] rounded-full bg-gradient-to-tl from-indigo-500/25 via-purple-500/20 to-blue-500/25 blur-3xl"
        />
        
        <motion.div
          animate={{
            x: [0, 50, 0],
            y: [0, -30, 0],
            opacity: [0.2, 0.35, 0.2],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[24rem] w-[24rem] rounded-full bg-gradient-to-br from-blue-500/20 via-cyan-500/15 to-transparent blur-3xl"
        />

        {/* Radial gradient overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(6,182,212,0.1),_transparent_50%)]" />
        
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.03]" />
        
        {/* Floating particles */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            animate={{
              y: [0, -20, 0],
              opacity: [0, 0.5, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut",
            }}
            className="absolute rounded-full bg-cyan-400/20"
            style={{
              width: Math.random() * 4 + 2,
              height: Math.random() * 4 + 2,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 space-y-8 text-center"
      >
        {/* Badge */}
        <motion.div variants={itemVariants}>
          <motion.div
            whileHover={{ scale: 1.03, y: -1 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center rounded-full border border-cyan-500/30 bg-cyan-500/10 backdrop-blur-sm px-5 py-2.5 text-sm font-medium text-cyan-300 hover:border-cyan-500/50 hover:bg-cyan-500/15 transition-all duration-300 shadow-lg shadow-cyan-500/10"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles size={16} className="mr-2.5" />
            </motion.div>
            AI-Powered Multi-Agent Research Platform
          </motion.div>
        </motion.div>

        {/* Main Headline */}
        <motion.div variants={itemVariants} className="space-y-4">
          <h1 className="mx-auto max-w-5xl text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] sm:leading-[1.15] text-white">
            Research Faster
            <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
              With Intelligent Agents
            </span>
          </h1>
        </motion.div>

        {/* Subheading */}
        <motion.p
          variants={itemVariants}
          className="mx-auto max-w-2xl text-base sm:text-lg leading-relaxed text-slate-400 px-4"
        >
          Automate planning, research, verification, report generation and source validation through our advanced multi-agent workflow ecosystem.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4"
        >
          <motion.button
            whileHover={{ scale: 1.03, y: -2 }}
            whileTap={{ scale: 0.97 }}
            transition={{ duration: 0.2 }}
            className="group flex items-center gap-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 px-8 py-4 font-semibold text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
          >
            Start Research
            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-200" />
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.03, y: -2 }}
            whileTap={{ scale: 0.97 }}
            transition={{ duration: 0.2 }}
            className="rounded-xl border border-white/20 bg-white/5 hover:bg-white/10 backdrop-blur-sm px-8 py-4 font-semibold text-white transition-all duration-300 hover:border-white/30"
          >
            View Demo
          </motion.button>
        </motion.div>

        {/* Feature Pills */}
        <motion.div
          variants={itemVariants}
          className="flex flex-wrap justify-center gap-2.5 pt-6"
        >
          {["Planning", "Research", "Verification", "Reports"].map((feature, index) => (
            <motion.span
              key={feature}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.98 }}
              className="rounded-full border border-white/10 bg-white/5 backdrop-blur-sm px-4 py-2 text-sm font-medium text-slate-300 hover:border-white/20 hover:bg-white/10 hover:text-white transition-all duration-200 cursor-pointer"
            >
              {feature}
            </motion.span>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}

export default HeroSection;
