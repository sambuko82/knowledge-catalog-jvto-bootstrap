module.exports = {
  apps: [
    {
      name: "okf-api",
      script: "dist/server.js",
      cwd: __dirname,
      exec_mode: "fork",
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 2000,
      env: {
        NODE_ENV: "production",
        HOST: "127.0.0.1",
        PORT: "3300",
      },
    },
  ],
};
