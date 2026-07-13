import { motion } from "framer-motion";
import {
  CheckCircle2,
  Circle,
  Clock,
  Brain,
  Search,
  Shield,
  PenTool,
} from "lucide-react";

function WorkflowProgress() {
  const agents = [
    {
      id: 1,
      name: "Planner",
      description: "Breaks down research into actionable tasks",
      icon: Brain,
      status: "completed",
    },
    {
      id: 2,
      name: "Research Agent",
      description: "Searches and aggregates relevant information",
      icon: Search,
      status: "active",
    },
    {
      id: 3,
      name: "Verifier",
      description: "Validates sources and cross-references data",
      icon: Shield,
      status: "pending",
    },
    {
      id: 4,
      name: "Writer",
      description: "Compiles findings into comprehensive reports",
      icon: PenTool,
      status: "pending",
    },
  ];

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
      transition: { duration: 0.4 },
    },
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
        return "text-cyan-400";
      case "active":
        return "text-blue-400";
      case "pending":
        return "text-slate-500";
      default:
        return "text-slate-500";
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case "completed":
        return "bg-cyan-500/10 border-cyan-500/30";
      case "active":
        return "bg-blue-500/10 border-blue-500/30";
      case "pending":
        return "bg-white/5 border-white/10";
      default:
        return "bg-white/5 border-white/10";
    }
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
          Workflow Progress
        </h2>
        <p className="mt-2 text-slate-400">
          Watch as our intelligent agents work through each stage of the research process.
        </p>
      </div>

      {/* Agent Workflow */}
      <div className="space-y-4">
        {agents.map((agent, index) => {
          const Icon = agent.icon;
          const isLast = index === agents.length - 1;
          const statusColor = getStatusColor(agent.status);
          const statusBg = getStatusBg(agent.status);

          return (
            <motion.div key={agent.id} variants={itemVariants}>
              <div className="relative">
                {/* Connecting Line */}
                {!isLast && (
                  <div
                    className={`absolute left-8 top-24 h-12 w-0.5 ${
                      agent.status === "completed"
                        ? "bg-gradient-to-b from-cyan-500 to-cyan-500/30"
                        : agent.status === "active"
                          ? "bg-gradient-to-b from-cyan-500 to-slate-500/30"
                          : "bg-slate-500/20"
                    }`}
                  />
                )}

                {/* Agent Card */}
                <motion.div
                  whileHover={{ x: 4 }}
                  className={`relative rounded-2xl border ${statusBg} bg-gradient-to-br from-slate-900/60 to-slate-950/60 backdrop-blur-xl p-6 transition-all hover:shadow-lg hover:shadow-blue-500/10`}
                >
                  {/* Status Badge */}
                  <div className="absolute top-4 right-4">
                    {agent.status === "completed" ? (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", delay: 0.2 }}
                      >
                        <CheckCircle2 size={24} className="text-cyan-400" />
                      </motion.div>
                    ) : agent.status === "active" ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      >
                        <Clock size={24} className="text-blue-400" />
                      </motion.div>
                    ) : (
                      <Circle size={24} className="text-slate-500" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex items-start gap-4 pr-12">
                    <motion.div
                      whileHover={{ rotate: 10, scale: 1.1 }}
                      className={`flex h-12 w-12 items-center justify-center rounded-xl border ${
                        agent.status === "completed"
                          ? "border-cyan-500/40 bg-cyan-500/15"
                          : agent.status === "active"
                            ? "border-blue-500/40 bg-blue-500/15"
                            : "border-white/10 bg-white/5"
                      } flex-shrink-0`}
                    >
                      <Icon
                        size={24}
                        className={statusColor}
                      />
                    </motion.div>

                    <div className="flex-1">
                      <h3 className="flex items-center gap-2 text-lg font-semibold text-white">
                        {agent.name}
                        {agent.status === "active" && (
                          <span className="inline-flex h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
                        )}
                      </h3>
                      <p className="mt-1 text-sm text-slate-400">
                        {agent.description}
                      </p>

                      {/* Progress Bar */}
                      {agent.status !== "pending" && (
                        <motion.div
                          className="mt-3 h-1.5 w-full rounded-full overflow-hidden bg-white/5"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                        >
                          <motion.div
                            className={`h-full rounded-full ${
                              agent.status === "completed"
                                ? "bg-gradient-to-r from-cyan-500 to-cyan-400"
                                : "bg-gradient-to-r from-blue-500 to-blue-400"
                            }`}
                            initial={{ width: 0 }}
                            animate={{
                              width: agent.status === "completed" ? "100%" : "60%",
                            }}
                            transition={{ duration: 0.8, ease: "easeOut" }}
                          />
                        </motion.div>
                      )}
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4"
      >
        {[
          { label: "Completed", value: "1", color: "cyan" },
          { label: "In Progress", value: "1", color: "blue" },
          { label: "Pending", value: "2", color: "slate" },
        ].map((stat) => (
          <motion.div
            key={stat.label}
            whileHover={{ scale: 1.02 }}
            className={`rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm p-4 text-center transition-all hover:bg-white/10`}
          >
            <p className={`text-2xl font-bold text-${stat.color}-400`}>
              {stat.value}
            </p>
            <p className="mt-1 text-sm text-slate-400">{stat.label}</p>
          </motion.div>
        ))}
      </motion.div>
    </motion.section>
  );
}

export default WorkflowProgress;
