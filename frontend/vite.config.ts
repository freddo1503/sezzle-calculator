import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react(), tailwindcss()],

  resolve: {
    alias: { "@": path.resolve(import.meta.dirname, "./src") },
  },

  server: {
    // The interface always calls a same-origin relative path, so no absolute
    // backend address is ever compiled into the bundle and the backend needs no
    // cross-origin configuration. The static file server in the assembled stack
    // proxies the same prefix. See docs/architecture.md section 8.5.
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },

  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      // Generated from the contract: covering it would measure the generator.
      exclude: ["src/api/**", "src/main.tsx", "**/*.config.*"],
    },
  },
});
