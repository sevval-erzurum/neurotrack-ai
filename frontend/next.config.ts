import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // cacheComponents kapalı: veri tamamen istemcide çekiliyor, sunucu önbelleği kazanç sağlamıyor;
  // açıkken 16.4.2'de statik sayfaların ilk ziyarette hydrate olmadığı görüldü.
  output: "standalone",
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  // /api/v1/* isteklerini src/app/api/v1/[...path]/route.ts backend'e iletir (aynı origin).
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },
};

export default nextConfig;
