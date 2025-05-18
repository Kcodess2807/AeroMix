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


  async rewrites(){
    return[
      {
        source: '/api/:path', 
        destination: 'https://127.0.0.1: 5000/api/:path*', //route on which python api is running
      },
    ];
  },

}

export default nextConfig
