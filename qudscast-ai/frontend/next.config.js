/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3001/api/:path*',
      },
      {
        source: '/storage/:path*',
        destination: 'http://localhost:3001/storage/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
