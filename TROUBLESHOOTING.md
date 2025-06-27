# ServiceDeskAgent Troubleshooting Guide

## Common Issues and Solutions

### 1. Frontend Starts but No Voice Agent Connection

**Symptoms:**
- Frontend loads at http://localhost:5173
- No voice agent appears or connection fails
- Backend may show errors

**Solutions:**

#### Check Backend Status
```bash
# Run backend separately to see detailed errors
cd backend
python agent.py
```

#### Verify Environment Configuration
```bash
# Validate your Azure OpenAI setup
npm run validate
```

#### Common Backend Issues:

**Missing Environment Variables:**
- Ensure `backend/.env` exists (copy from `backend/sample.env`)
- Verify all required variables are set:
  - `LIVEKIT_URL`
  - `LIVEKIT_API_KEY` 
  - `LIVEKIT_API_SECRET`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_DEPLOYMENT_NAME`

**Azure OpenAI Issues:**
- Check deployment is active in Azure Portal
- Verify you're using a supported region for GPT-4o Realtime
- Ensure API version is correct (2024-10-01-preview)

**LiveKit Connection Issues:**
- Verify LiveKit credentials are correct
- Check LiveKit server is accessible
- Ensure no firewall blocking connections

### 2. Python Dependencies Issues

**Error:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### 3. Node.js Dependencies Issues

**Error:** Package not found or npm errors

**Solution:**
```bash
cd frontend
npm install
```

### 4. Port Conflicts

**Error:** Port already in use

**Solutions:**
- Frontend (port 5173): Kill existing Vite processes
- Backend: Check if another Python agent is running

```bash
# Kill processes using specific ports
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5173 | xargs kill -9
```

### 5. Azure OpenAI Deployment Issues

**Common Problems:**
- Deployment not found
- Quota exceeded
- Region not supported
- WebSocket handshake errors (400 status)

**Solutions:**
1. Check Azure Portal for deployment status
2. Verify deployment name matches environment variable
3. Ensure sufficient quota allocation
4. Use supported regions (East US, Sweden Central, etc.)

**WebSocket 400 Error Fix:**
If you see `WSServerHandshakeError: 400, message='Invalid response status'`:

**CRITICAL: This error means your Azure OpenAI configuration needs adjustment.**

1. **Check Your Azure Portal:**
   - Go to Azure Portal → Your OpenAI Resource → Model Deployments
   - Verify you have a deployment with model `gpt-4o-realtime-preview`
   - Note the exact deployment name (case-sensitive)

2. **Update Your .env File:**
   ```bash
   # Example correct configuration:
   AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com"
   AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-realtime"  # Your actual deployment name
   AZURE_OPENAI_API_VERSION="2024-10-21"
   AZURE_OPENAI_API_KEY="your-api-key-here"
   ```

3. **Common Configuration Issues:**
   - **Wrong deployment name**: Must match exactly what's in Azure Portal
   - **Wrong endpoint format**: Should NOT have trailing slash
   - **Wrong API version**: Try `2024-08-01-preview` if current doesn't work
   - **Inactive deployment**: Check deployment status in Azure Portal
   - **Quota exceeded**: Check usage limits in Azure Portal

4. **Supported Regions for GPT-4o Realtime:**
   - East US
   - East US 2  
   - Sweden Central
   - West US 3
   
   If your resource is in an unsupported region, create a new one.

5. **Test Configuration:**
   ```bash
   # Validate your setup
   npm run validate
   
   # If validation passes but agent still fails, check:
   # - Deployment is not paused
   # - API key has correct permissions
   # - Resource has sufficient quota
   ```

6. **Alternative: Use Standard GPT-4o (Non-Realtime):**
   If realtime isn't available, temporarily use standard GPT-4o:
   ```bash
   # In your .env, change deployment to standard GPT-4o
   AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"  # Standard deployment
   ```
   Note: This will disable realtime voice features but allow text interaction.

### 6. Voice Connection Not Working

**Symptoms:**
- Frontend loads but microphone doesn't activate
- No audio input/output

**Solutions:**
1. **Browser Permissions:**
   - Allow microphone access in browser
   - Check browser console for permission errors

2. **HTTPS Requirement:**
   - LiveKit requires HTTPS for production
   - Use localhost for development (HTTP allowed)

3. **Audio Device Issues:**
   - Check system audio settings
   - Try different browser
   - Test with headphones

### 7. Debugging Steps

#### Enable Detailed Logging
```bash
# Set environment variable for more verbose output
export LIVEKIT_LOG_LEVEL=debug
npm run dev
```

#### Check Browser Console
1. Open browser developer tools (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab for failed requests

#### Test Components Separately
```bash
# Test backend only
cd backend
python agent.py

# Test frontend only
cd frontend
npm run dev

# Test Azure OpenAI connection
npm run validate
```

### 8. Getting Help

If issues persist:

1. **Check Logs:** Look at both frontend and backend console output
2. **Verify Configuration:** Double-check all environment variables
3. **Test Connectivity:** Ensure Azure OpenAI and LiveKit are accessible
4. **Browser Compatibility:** Try different browsers (Chrome recommended)
5. **Network Issues:** Check firewall and proxy settings

### 9. Quick Reset

If all else fails, try a complete reset:

```bash
# Clean install
rm -rf node_modules frontend/node_modules
npm run install-deps

# Reset environment
cp backend/sample.env backend/.env
# Edit backend/.env with your credentials

# Validate setup
npm run validate

# Start fresh
npm run dev
```

## Support Resources

- [Azure OpenAI Setup Guide](./AZURE_OPENAI_SETUP.md)
- [LiveKit Documentation](https://docs.livekit.io/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
