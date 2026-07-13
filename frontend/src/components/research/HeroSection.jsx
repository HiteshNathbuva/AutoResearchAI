import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

function HeroSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" },
    },
  };

  return (
    <section className="relative py-20 sm:py-28">
      {/* Decorative Elements */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-1/4 left-1/3 h-64 w-64 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-500/20 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-80 w-80 rounded-full bg-gradient-to-r from-indigo-500/20 to-cyan-500/20 blur-3xl" />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-8 text-center"
      >
        {/* Badge */}
        <motion.div variants={itemVariants}>
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="inline-flex items-center rounded-full border border-cyan-500/30 bg-cyan-500/10 backdrop-blur-sm px-4 py-2 text-sm font-medium text-cyan-300 hover:border-cyan-500/50 hover:bg-cyan-500/15 transition"
          >
            <Sparkles size={16} className="mr-2" />
            AI-Powered Multi-Agent Research Platform
          </motion.div>
        </motion.div>

        {/* Main Headline */}
        <motion.div variants={itemVariants} className="space-y-6">
          <h1 className="mx-auto text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight leading-tight text-white">
            Research Faster
            <br />
            <span className="inline-block bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
              With Intelligent Agents
            </span>
          </h1>
        </motion.div>

        {/* Subheading */}
        <motion.p
          variants={itemVariants}
          className="mx-auto max-w-2xl text-lg sm:text-xl leading-relaxed text-slate-300"
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
            whileTap={{ scale: 0.98 }}
            className="group flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-3.5 font-semibold text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition"
          >
            Start Research
            <ArrowRight size={20} className="group-hover:translate-x-1 transition" />
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            className="rounded-xl border border-white/20 bg-white/5 hover:bg-white/10 backdrop-blur-sm px-8 py-3.5 font-semibold text-white transition"
          >
            View Demo
          </motion.button>
        </motion.div>

        {/* Feature Pills */}
        <motion.div
          variants={itemVariants}
          className="flex flex-wrap justify-center gap-2 pt-8"
        >
          {["Planning", "Research", "Verification", "Reports"].map((feature) => (
            <motion.span
              key={feature}
              whileHover={{ scale: 1.05 }}
              className="rounded-full border border-white/10 bg-white/5 backdrop-blur-sm px-3 py-1.5 text-sm font-medium text-slate-300 hover:border-white/20 hover:bg-white/10 transition"
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
