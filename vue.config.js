module.exports = {
  assetsDir: "static",
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:4776', // 接口的域名
        changeOrigin: true,
        secure: false
      }
    }
  }
};