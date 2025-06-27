# Service Desk Agent - Transcriber Service

This document explains how to use the separate transcriber service for speech-to-text functionality.

## Architecture

The Service Desk Agent now uses a **separation of concerns** approach:

1. **transcriber.py** - Handles speech-to-text transcription
2. **agent.py** - Handles voice responses and function tools (create tickets, lookup tickets, etc.)

## Why Separate Services?

The original implementation had issues with:
- AsyncIO task creation errors
- STT streaming compatibility problems
- Complex realtime API configuration conflicts

The new approach provides:
- ✅ Clean separation of transcription and response generation
- ✅ Better error handling and debugging
- ✅ More reliable STT using proven LiveKit patterns
- ✅ Easier maintenance and updates

## Running the Services

### Option 1: Use the Helper Script
```bash
cd backend
python run_services.py
```

### Option 2: Run Services Manually

**Terminal 1 - Transcriber Service:**
```bash
cd backend
python transcriber.py start
```

**Terminal 2 - Agent Service:**
```bash
cd backend
python agent.py start
```

## Environment Variables

Make sure your `.env` file contains:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-10-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

## How It Works

1. **Transcriber Service** (`transcriber.py`):
   - Connects to LiveKit room with audio-only subscription
   - Uses Azure OpenAI Whisper for speech-to-text
   - Uses default LiveKit audio processing (Silero VAD removed for Windows compatibility)
   - Publishes transcriptions to the room
   - Does NOT generate voice responses

2. **Agent Service** (`agent.py`):
   - Uses Azure OpenAI realtime model for voice generation
   - Handles function tools (create_ticket, lookup_ticket, etc.)
   - Responds to transcribed text from the transcriber service
   - Generates voice responses using the realtime API

## Troubleshooting

### Transcriber Issues
- Check Azure OpenAI credentials
- Ensure Whisper model is available in your deployment
- Verify Silero VAD dependencies are installed

### Agent Issues
- Check realtime model deployment
- Verify function tools are working (test database connection)
- Check LiveKit room connectivity

### Both Services
- Ensure both services connect to the same LiveKit room
- Check that environment variables are loaded correctly
- Verify network connectivity to Azure OpenAI and LiveKit

## Testing

1. Start both services in separate terminals
2. Connect to the LiveKit room using the frontend or LiveKit Playground
3. Speak into your microphone
4. Verify transcriptions appear in the transcriber logs
5. Verify the agent responds with voice output
6. Test function tools by asking to create or lookup tickets

## Logs

Both services provide detailed logging:
- Transcriber logs show transcription results
- Agent logs show function tool execution and responses
- Both show LiveKit connection status and room events
