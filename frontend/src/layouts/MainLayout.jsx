import Navbar from "../components/common/Navbar";

function MainLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Background Decoration */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-[-120px] left-[-120px] h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="absolute bottom-[-160px] right-[-160px] h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl" />

        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.08),transparent_45%)]" />
      </div>

      {/* Navigation */}
      <Navbar />

      {/* Main Content */}
      <main className="mx-auto w-full max-w-7xl px-6 pt-28 pb-16 sm:px-8 lg:px-10">
        {children}
      </main>

      {/* Footer (Coming Soon) */}
      <footer className="border-t border-white/10 py-6 text-center text-sm text-slate-500">
        © {new Date().getFullYear()} AutoResearchAI • Production Grade Multi-Agent Research Platform
      </footer>
    </div>
  );
}

export default MainLayout;