// src/setupProxy.js
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // This ensures Unity WebGL files are served correctly
  app.use(
    '/Web_text',
    createProxyMiddleware({
      target: 'http://localhost:3000',
      changeOrigin: true,
      onProxyReq: (proxyReq, req, res) => {
        // Remove any headers that might cause 403
        proxyReq.removeHeader('origin');
      }
    })
  );
};