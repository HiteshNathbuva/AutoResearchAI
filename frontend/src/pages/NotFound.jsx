import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/70 p-10 text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-cyan-300">404</p>
      <h1 className="mt-2 text-3xl font-bold">Page not found</h1>
      <p className="mt-3 text-slate-400">
        The page you are looking for does not exist or was moved.
      </p>
      <Link
        to="/"
        className="mt-6 inline-block rounded-lg bg-cyan-500 px-5 py-2.5 font-semibold text-slate-950"
      >
        Back to research
      </Link>
    </section>
  );
}
