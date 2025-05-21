/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*', // <-- The * is required to match all subpaths!
        destination: 'http://127.0.0.1:5000/api/:path*', // Flask backend
      },
    ];
  },
};

export default nextConfig;
