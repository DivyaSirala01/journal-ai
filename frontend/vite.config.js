import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/notes": "http://127.0.0.1:8000",
      "/query": "http://127.0.0.1:8000",
    },
  },
});
