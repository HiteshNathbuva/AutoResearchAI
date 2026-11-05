import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// Local dev: the Vite server proxies /api to the FastAPI backend so the
// frontend can use same-origin "/api" URLs (no CORS issues).
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = (env.VITE_API_URL || "http://127.0.0.1:8000/api").replace(/\/api\/?$/, "");
  return {
    plugins: [react()],
    build: { outDir: "dist" },
    server: {
      proxy: {
        "/api": { target, changeOrigin: true },
      },
    },
  };
});
