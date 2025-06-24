# LiveKit AI Service Desk Agent

This is a real-time AI voice agent application built to assist users in creating IT Help Desk tickets and to perform simple troubleshooting. The application now uses **Azure OpenAI** for enterprise-grade AI capabilities with real-time voice interaction.

## Features

- **Real-time voice interaction** using Azure OpenAI's GPT-4o Realtime API
- **IT Help Desk ticket creation** and management
- **Simple troubleshooting assistance** for common IT issues
- **Enterprise security** with Azure OpenAI integration
- **LiveKit integration** for seamless voice communication

## Prerequisites

- Python 3.8+ and Node.js 16+
- Azure subscription with Azure OpenAI Service access
- LiveKit account and API credentials

## Setup Instructions

### 1. Install Dependencies
```bash
# Install all dependencies (frontend and backend)
npm run install-deps
```

### 2. Configure Azure OpenAI
Follow the detailed setup guide: **[AZURE_OPENAI_SETUP.md](./AZURE_OPENAI_SETUP.md)**

### 3. Environment Configuration
1. Copy `backend/sample.env` to `backend/.env`
2. Fill in your configuration values:
   - LiveKit credentials
   - Azure OpenAI credentials (see setup guide)

### 4. Validate Configuration (Optional)
```bash
# Test your Azure OpenAI setup
npm run validate
```

### 5. Run the Application
```bash
# Start both frontend and backend simultaneously
npm run dev
```

This will start:
- **Token Server**: LiveKit token server on http://localhost:5001
- **Voice Agent**: Python voice agent with Azure OpenAI
- **Frontend**: React development server on http://localhost:5173

## Configuration

The application requires the following environment variables:

### LiveKit Configuration
- `LIVEKIT_URL` - Your LiveKit server URL
- `LIVEKIT_API_KEY` - Your LiveKit API key
- `LIVEKIT_API_SECRET` - Your LiveKit API secret

### Azure OpenAI Configuration
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-10-01-preview)
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Your GPT-4o Realtime deployment name

## Troubleshooting

If you encounter issues:
1. **No voice agent connection**: See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions
2. **Azure OpenAI setup**: Check the [Azure OpenAI Setup Guide](./AZURE_OPENAI_SETUP.md)
3. **Configuration validation**: Run `npm run validate` to test your setup
4. **Detailed debugging**: Check both frontend and backend console output

### Quick Debugging Commands
```bash
# Test your configuration
npm run validate

# Run backend separately to see errors
cd backend && python agent.py dev

# Fix common Windows npm dependency issues
npm run fix-frontend

# Run with detailed logging
set LIVEKIT_LOG_LEVEL=debug && npm run dev
```

### Common Windows Issues
If you see rollup/native module errors:
```bash
# Quick fix for Windows dependency issues
npm run fix-frontend
```

For comprehensive troubleshooting, see **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**

## Architecture

- **Backend**: Python with LiveKit Agents framework
- **Frontend**: React with Vite
- **AI Provider**: Azure OpenAI (GPT-4o Realtime)
- **Voice Processing**: LiveKit real-time communication
