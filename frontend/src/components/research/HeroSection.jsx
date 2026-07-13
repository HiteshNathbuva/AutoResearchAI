function HeroSection() {
  return (
    <section className="py-16">
      <div className="text-center">

        <div className="inline-flex items-center rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-300">
          🚀 AI Powered Research Platform
        </div>

        <h1 className="mt-8 text-5xl font-bold leading-tight text-white md:text-7xl">
          Research Faster
          <br />
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            With Multiple AI Agents
          </span>
        </h1>

        <p className="mx-auto mt-8 max-w-3xl text-lg leading-8 text-slate-400">
          AutoResearchAI automates planning, research, verification,
          report generation and source validation through an intelligent
          multi-agent workflow.
        </p>
      </div>
    </section>
  );
}

export default HeroSection;