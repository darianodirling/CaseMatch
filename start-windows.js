// Windows-compatible startup script for CaseMatch
const { spawn } = require('child_process');
const path = require('path');

// Set environment variables for Windows
process.env.NODE_ENV = 'development';
process.env.HOST = '0.0.0.0';
process.env.PORT = '3000';

console.log('Starting CaseMatch on Windows...');
console.log('Server will run on http://localhost:3000');

// Start the server
const server = spawn('npx', ['tsx', 'server/index.ts'], {
  stdio: 'inherit',
  shell: true,
  cwd: process.cwd()
});

server.on('error', (err) => {
  console.error('Failed to start server:', err);
});

server.on('close', (code) => {
  console.log(`Server process exited with code ${code}`);
});