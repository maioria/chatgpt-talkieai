import { defineConfig } from "vite";
import uni from "@dcloudio/vite-plugin-uni";
const target = "https://crm.shoxfashion.com/api/cms-dashboard/";
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [uni()],
  server: {
    host: "0.0.0.0",
    proxy: {
      "/api/cms-dashboard": {
        target,
        rewrite: (path) => {
          console.log(path);
          return path.replace("/api/cms-dashboard", "/");
        },
        changeOrigin: true,
        secure: false,
        xfwd: false,
      },
    },
  },
});
