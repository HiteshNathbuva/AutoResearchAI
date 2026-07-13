import { useState } from "react";

function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: "Workspace", href: "#" },
    { name: "Agents", href: "#" },
    { name: "Reports", href: "#" },
    { name: "History", href: "#" },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 sm:px-8 lg:px-10">
        {/* Logo */}
        <div className="flex items-center gap-3 cursor-pointer">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 font-bold text-white shadow-lg shadow-cyan-500/20">
            AI
          </div>

          <div>
            <h1 className="text-lg font-bold tracking-tight">
              AutoResearchAI
            </h1>

            <p className="text-xs text-slate-400">
              Multi-Agent Research Platform
            </p>
          </div>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-8 md:flex">
          {navLinks.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="text-sm font-medium text-slate-300 transition hover:text-white"
            >
              {item.name}
            </a>
          ))}
        </nav>

        {/* Desktop Button */}
        <div className="hidden md:block">
          <button className="rounded-xl bg-cyan-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-cyan-400 hover:shadow-lg hover:shadow-cyan-500/30">
            New Research
          </button>
        </div>

        {/* Mobile Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="rounded-lg border border-white/10 p-2 md:hidden"
        >
          ☰
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="border-t border-white/10 bg-slate-950 md:hidden">
          <div className="space-y-2 px-6 py-5">
            {navLinks.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="block rounded-lg px-3 py-2 text-slate-300 transition hover:bg-white/5 hover:text-white"
              >
                {item.name}
              </a>
            ))}

            <button className="mt-3 w-full rounded-xl bg-cyan-500 py-3 font-semibold text-white transition hover:bg-cyan-400">
              New Research
            </button>
          </div>
        </div>
      )}
    </header>
  );
}

export default Navbar;