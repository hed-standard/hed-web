import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig(({ command }) => {
  const isProduction = command === "build";

  return {
    base: isProduction ? "/hed-web/" : "/",

    build: {
      outDir: "buildweb",
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, "index.html"),
          validate_dataset: path.resolve(__dirname, "validate_dataset.html"),
          validate_file: path.resolve(__dirname, "validate_file.html"),
        },
        output: {
          manualChunks(id) {
            if (id.includes("node_modules/lodash")) {
              return "lodash";
            }
          },
        },
      },
      manifest: true,
      sourcemap: true,
    },

    plugins: [react()],
  };
});
