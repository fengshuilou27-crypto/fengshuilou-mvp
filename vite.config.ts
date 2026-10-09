import devServer from "@hono/vite-dev-server"
import path from "path"
const __dirname = import.meta.dirname
import react from "@vitejs/plugin-react"
import { defineConfig, type Plugin } from "vite"
import { inspectAttr } from 'kimi-plugin-inspect-react'
import { LOGIN_HTML, cookieAuthed, gateEnabled } from "./api/gate-core"

// dev 預覽門禁：@hono/vite-dev-server 只把 /api/* 交給 hono，頁面與 /data/* 由 vite 直serve——
// 必須在 connect 層最前面加這道中間件，否則未登入訪客可繞過 hono 直接看到頁面和數據文件
function gatePlugin(): Plugin {
  return {
    name: "etf-access-gate",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (!gateEnabled) return next();
        const url = (req.url ?? "/").split("?")[0];
        if (url.startsWith("/api/auth/")) return next();
        if (cookieAuthed(req.headers.cookie)) return next();
        const isApi = url.startsWith("/api/");
        const isPage = (!isApi && !url.includes(".")) || url === "/index.html";
        if (isPage && req.method === "GET") {
          res.statusCode = 200;
          res.setHeader("Content-Type", "text/html; charset=utf-8");
          res.end(LOGIN_HTML);
          return;
        }
        res.statusCode = 401;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ error: "access required" }));
      });
    },
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    gatePlugin(),
    devServer({ entry: "api/boot.ts", exclude: [/^\/(?!api\/).*$/] }),
    inspectAttr(), react()],
  server: {
    port: 3000,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@contracts": path.resolve(__dirname, "./contracts"),
      "@db": path.resolve(__dirname, "./db"),
      "db": path.resolve(__dirname, "./db"),
    },
  },
  envDir: path.resolve(__dirname),
  build: {
    outDir: path.resolve(__dirname, "dist/public"),
    emptyOutDir: true,
  },
});
