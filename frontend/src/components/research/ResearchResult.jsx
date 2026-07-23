import { motion } from "framer-motion";
import {
  TrendingUp,
  CheckCircle2,
  ExternalLink,
  Download,
  Share2,
  Book,
  Link2,
} from "lucide-react";

function ResearchResult() {
  const mockReport = {
    title: "AI Safety and Development Trends",
    confidence: 94,
    sources: 47,
    verifiedFacts: 23,
    summary:
      "This comprehensive analysis examines the latest developments in AI safety, governance frameworks, and responsible AI deployment strategies across leading organizations.",
    sections: [
      {
        id: 1,
        title: "Executive Summary",
        content:
          "AI development continues to accelerate, with increased focus on safety mechanisms and ethical considerations.",
      },
      {
        id: 2,
        title: "Key Findings",
        content:
          "Major technology companies have committed to AI safety research, with investments exceeding $2 billion annually.",
      },
      {
        id: 3,
        title: "Market Impact",
        content:
          "The AI safety market is projected to grow at 31% CAGR through 2030, creating new opportunities.",
      },
    ],
    topSources: [
      { id: 1, name: "OpenAI Research Papers", confidence: 98 },
      { id: 2, name: "MIT Technology Review", confidence: 95 },
      { id: 3, name: "DeepMind Blog", confidence: 94 },
      { id: 4, name: "Anthropic Safety Papers", confidence: 96 },
    ],
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] },
    },
  };

  return (
    <motion.section
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-100px" }}
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="space-y-2">
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Research Report
        </h2>
        <p className="text-slate-400 leading-relaxed">
          Your comprehensive research findings, verified and compiled.
        </p>
      </motion.div>

      {/* Report Preview Card */}
      <motion.div
        variants={itemVariants}
        whileHover={{ y: -4 }}
        transition={{ duration: 0.3 }}
        className="relative rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900/70 via-slate-900/50 to-slate-950/70 backdrop-blur-xl overflow-hidden shadow-xl hover:shadow-2xl hover:shadow-cyan-500/10 transition-all duration-300"
      >
        {/* Header Section */}
        <div className="relative border-b border-white/10 bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-indigo-500/10 p-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div className="flex-1">
              <h3 className="text-xl sm:text-2xl font-bold text-white">
                {mockReport.title}
              </h3>
              <p className="mt-2 text-slate-400 max-w-2xl leading-relaxed">
                {mockReport.summary}
              </p>
            </div>

            <motion.div
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.2 }}
              className="flex-shrink-0"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-cyan-500/15 to-blue-500/15 shadow-lg shadow-cyan-500/20">
                <div className="relative text-center">
                  <p className="text-2xl font-bold text-cyan-400">
                    {mockReport.confidence}%
                  </p>
                  <p className="text-[10px] text-cyan-300 font-semibold uppercase tracking-wider">
                    Confidence
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Metrics Row */}
        <div className="grid grid-cols-3 gap-4 border-b border-white/10 p-8">
          {[
            { icon: CheckCircle2, label: "Verified Facts", value: mockReport.verifiedFacts },
            { icon: Link2, label: "Sources", value: mockReport.sources },
            { icon: TrendingUp, label: "Sections", value: mockReport.sections.length },
          ].map((metric, idx) => {
            const Icon = metric.icon;
            return (
              <motion.div
                key={idx}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                transition={{ duration: 0.2 }}
                className="flex items-center gap-3"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/15 border border-cyan-500/30 shadow-sm">
                  <Icon size={20} className="text-cyan-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">{metric.label}</p>
                  <p className="text-lg font-semibold text-white">
                    {metric.value}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Content Sections */}
        <div className="p-8 space-y-4">
          {mockReport.sections.map((section) => (
            <motion.div
              key={section.id}
              variants={itemVariants}
              whileHover={{ x: 4, scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              transition={{ duration: 0.2 }}
              className="rounded-lg border border-white/5 bg-white/5 p-4 hover:bg-white/10 hover:border-white/10 transition-all duration-300 cursor-pointer"
            >
              <h4 className="flex items-center gap-2 text-base font-semibold text-white">
                <Book size={18} className="text-blue-400" />
                {section.title}
              </h4>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                {section.content}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Footer Actions */}
        <div className="border-t border-white/10 bg-slate-950/40 p-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-slate-300">
              Ready to share your findings?
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <motion.button
              whileHover={{ scale: 1.03, y: -1 }}
              whileTap={{ scale: 0.97 }}
              transition={{ duration: 0.15 }}
              className="flex items-center justify-center gap-2 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200"
            >
              <Download size={18} />
              Export PDF
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.03, y: -1 }}
              whileTap={{ scale: 0.97 }}
              transition={{ duration: 0.15 }}
              className="flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 transition-all duration-300"
            >
              <Share2 size={18} />
              Share Report
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Top Sources */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-white">Top Verified Sources</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {mockReport.topSources.map((source) => (
            <motion.a
              key={source.id}
              whileHover={{ x: 4, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
              href="#"
              className="group relative rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20 backdrop-blur-sm p-4 transition-all duration-300 flex items-center justify-between"
            >
              <div>
                <p className="font-medium text-white group-hover:text-cyan-400 transition-colors duration-200">
                  {source.name}
                </p>
                <p className="mt-1 text-sm text-slate-400">
                  {source.confidence}% confidence
                </p>
              </div>
              <motion.div
                whileHover={{ x: 2 }}
                transition={{ duration: 0.2 }}
              >
                <ExternalLink
                  size={18}
                  className="text-slate-500 group-hover:text-cyan-400 transition-colors duration-200 flex-shrink-0"
                />
              </motion.div>
            </motion.a>
          ))}
        </div>
      </motion.div>
    </motion.section>
  );
}

export default ResearchResult;
