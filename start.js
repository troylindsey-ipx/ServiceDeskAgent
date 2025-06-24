#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting ServiceDeskAgent...\n');

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

function log(prefix, message, color = colors.reset) {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`${color}[${timestamp}] ${prefix}:${colors.reset} ${message}`);
}

// Check if .env file exists
const fs = require('fs');
const envPath = path.join(__dirname, 'backend', '.env');

if (!fs.existsSync(envPath)) {
    log('ERROR', 'Backend .env file not found!', colors.red);
    log('SETUP', 'Please copy backend/sample.env to backend/.env and configure your credentials', colors.yellow);
    process.exit(1);
}

// Check if frontend dependencies are installed
const frontendNodeModules = path.join(__dirname, 'frontend', 'node_modules');
const frontendPackageLock = path.join(__dirname, 'frontend', 'package-lock.json');

function cleanInstallFrontend() {
    log('SETUP', 'Cleaning and reinstalling frontend dependencies...', colors.yellow);
    const { execSync } = require('child_process');
    try {
        // Remove node_modules and package-lock.json
        if (fs.existsSync(frontendNodeModules)) {
            log('SETUP', 'Removing node_modules...', colors.yellow);
            fs.rmSync(frontendNodeModules, { recursive: true, force: true });
        }
        if (fs.existsSync(frontendPackageLock)) {
            log('SETUP', 'Removing package-lock.json...', colors.yellow);
            fs.unlinkSync(frontendPackageLock);
        }
        
        // Clean install
        log('SETUP', 'Installing fresh dependencies...', colors.yellow);
        execSync('npm install', { 
            cwd: path.join(__dirname, 'frontend'),
            stdio: 'inherit'
        });
        log('SETUP', 'Frontend dependencies installed successfully!', colors.green);
        return true;
    } catch (error) {
        log('ERROR', 'Failed to install frontend dependencies', colors.red);
        log('ERROR', 'Please manually run: cd frontend && rm -rf node_modules package-lock.json && npm install', colors.red);
        return false;
    }
}

if (!fs.existsSync(frontendNodeModules)) {
    if (!cleanInstallFrontend()) {
        process.exit(1);
    }
}

// Start token server
log('TOKEN SERVER', 'Starting LiveKit token server...', colors.magenta);
const tokenServer = spawn('python', ['token_server.py'], {
    cwd: path.join(__dirname, 'backend'),
    stdio: 'pipe'
});

// Start backend agent
log('AGENT', 'Starting Python agent...', colors.blue);
const backend = spawn('python', ['agent.py', 'dev'], {
    cwd: path.join(__dirname, 'backend'),
    stdio: 'pipe'
});

// Start frontend
log('FRONTEND', 'Starting React development server...', colors.green);
const frontend = spawn('npm', ['run', 'dev'], {
    cwd: path.join(__dirname, 'frontend'),
    stdio: 'pipe',
    shell: true
});

// Handle token server output
tokenServer.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        log('TOKEN SERVER', message, colors.magenta);
    }
});

tokenServer.stderr.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        log('TOKEN SERVER ERROR', message, colors.red);
    }
});

// Handle backend output
backend.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        log('AGENT', message, colors.blue);
    }
});

backend.stderr.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        log('AGENT ERROR', message, colors.red);
    }
});

// Handle frontend output
frontend.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        // Filter out some verbose vite messages
        if (!message.includes('watching for file changes') && 
            !message.includes('hmr update')) {
            log('FRONTEND', message, colors.green);
        }
    }
});

frontend.stderr.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        log('FRONTEND ERROR', message, colors.red);
    }
});

// Handle process exits
tokenServer.on('close', (code) => {
    if (code !== 0) {
        log('TOKEN SERVER', `Process exited with code ${code}`, colors.red);
    } else {
        log('TOKEN SERVER', 'Process stopped', colors.yellow);
    }
});

backend.on('close', (code) => {
    if (code !== 0) {
        log('AGENT', `Process exited with code ${code}`, colors.red);
    } else {
        log('AGENT', 'Process stopped', colors.yellow);
    }
});

frontend.on('close', (code) => {
    if (code !== 0) {
        log('FRONTEND', `Process exited with code ${code}`, colors.red);
    } else {
        log('FRONTEND', 'Process stopped', colors.yellow);
    }
});

// Handle Ctrl+C
process.on('SIGINT', () => {
    log('SYSTEM', 'Shutting down...', colors.yellow);
    tokenServer.kill('SIGINT');
    backend.kill('SIGINT');
    frontend.kill('SIGINT');
    process.exit(0);
});

// Success message
setTimeout(() => {
    console.log('\n' + colors.bright + colors.green + '✅ ServiceDeskAgent is starting up!' + colors.reset);
    console.log(colors.cyan + '📱 Frontend: http://localhost:5173' + colors.reset);
    console.log(colors.magenta + '🔑 Token Server: http://localhost:5001' + colors.reset);
    console.log(colors.blue + '🤖 Agent: Python voice agent running' + colors.reset);
    console.log(colors.yellow + '💡 Press Ctrl+C to stop all services' + colors.reset + '\n');
}, 2000);
