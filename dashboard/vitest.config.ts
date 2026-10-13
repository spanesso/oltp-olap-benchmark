import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

const root = import.meta.dirname;

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    globals: true,
  },
  resolve: {
    alias: {
      "@domain": resolve(root, "src/domain"),
      "@infra": resolve(root, "src/infrastructure"),
      "@presentation": resolve(root, "src/presentation"),
    },
  },
});
