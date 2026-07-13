import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Sparkles, Plus, Filter } from "lucide-react";

function ResearchInput() {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const suggestedQueries = [
    "Latest developments in AI safety",
    "Climate change mitigation strategies",
    "Quantum computing breakthroughs",
    "Sustainable energy solutions",
  ];

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
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
      <div>
        <h2 className="text-2xl sm:text-3xl font-bold text-white">
          Research Workspace
        </h2>
        <p className="mt-2 text-slate-400">
          Enter your research query and let our AI agents analyze and verify information across multiple sources.
        </p>
      </div>

      {/* Research Input Card */}
      <motion.div
        whileHover={{ y: -2 }}
        className="group relative rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900/60 via-slate-900/40 to-slate-950/60 backdrop-blur-2xl overflow-hidden shadow-lg hover:shadow-xl hover:shadow-cyan-500/10 transition-all duration-300"
      >
        {/* Gradient Border Effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/0 to-blue-500/0 group-hover:from-cyan-500/10 group-hover:via-cyan-500/5 group-hover:to-blue-500/10 pointer-events-none transition-all duration-500" />

        <div className="relative p-8">
          {/* Input Section */}
          <div className="space-y-4">
            <motion.div
              animate={{ scale: isFocused ? 1.02 : 1 }}
              className="relative"
            >
              <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
                <Search
                  size={20}
                  className={`transition-colors duration-300 ${
                    isFocused ? "text-cyan-400" : "text-slate-500"
                  }`}
                />
              </div>

              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Ask anything... What do you want to research?"
                className="w-full bg-white/5 border border-white/10 rounded-xl pl-12 pr-20 py-4 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 focus:ring-2 focus:ring-cyan-500/20 transition-all duration-300"
              />

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 p-2.5 text-white hover:shadow-lg hover:shadow-cyan-500/20 transition-all"
              >
                <Sparkles size={18} />
              </motion.button>
            </motion.div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 backdrop-blur-sm px-4 py-2.5 text-sm font-medium text-slate-300 hover:text-white transition-all"
              >
                <Plus size={16} />
                Add Sources
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 backdrop-blur-sm px-4 py-2.5 text-sm font-medium text-slate-300 hover:text-white transition-all"
              >
                <Filter size={16} />
                Filters
              </motion.button>
            </div>
          </div>

          {/* Divider */}
          <div className="my-6 border-t border-white/5" />

          {/* Suggested Queries */}
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
              Suggested Queries
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {suggestedQueries.map((suggestion, idx) => (
                <motion.button
                  key={idx}
                  whileHover={{ scale: 1.02, x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setQuery(suggestion)}
                  className="group text-left rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 hover:border-white/10 backdrop-blur-sm p-3 transition-all"
                >
                  <p className="text-sm text-slate-300 group-hover:text-white transition">
                    {suggestion}
                  </p>
                </motion.button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </motion.section>
  );
}

export default ResearchInput;
