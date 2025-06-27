# Azure OpenAI Setup Guide

This guide will help you set up Azure OpenAI for your ServiceDeskAgent project.

## Prerequisites

- Azure subscription with access to Azure OpenAI Service
- Azure CLI installed (optional, for command-line setup)

## Step 1: Create Azure OpenAI Resource

### Via Azure Portal:
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure OpenAI"
4. Click "Create" and fill in:
   - **Subscription**: Improvix Primary Subscription
   - **Resource Group**: OpenAI-Testing
   - **Region**: East US2
   - **Name**: ipx-OpenAI-Testing
   - **Pricing Tier**: Standard S0

### Via Azure CLI:
```bash
# Create resource group (if needed)
az group create --name myResourceGroup --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name servicedesk-openai \
  --resource-group myResourceGroup \
  --location eastus \
  --kind OpenAI \
  --sku s0
```

## Step 2: Deploy GPT-4o Realtime Model

1. Navigate to your Azure OpenAI resource
2. Go to "Model deployments" or "Azure OpenAI Studio"
3. Click "Create new deployment"
4. Select:
   - **Model**: `gpt-4o-realtime-preview`
   - **Deployment name**: `gpt-4o-realtime` (remember this name)
   - **Version**: Latest available
   - **Deployment type**: Standard
5. Click "Create"

## Step 3: Get Your Configuration Values

### API Key:
1. Go to your Azure OpenAI resource
2. Navigate to "Keys and Endpoint"
3. Copy "KEY 1" or "KEY 2"

### Endpoint:
1. In the same "Keys and Endpoint" section
2. Copy the "Endpoint" URL (e.g., `https://your-resource.openai.azure.com/`)

### API Version:
- Use `2024-10-01-preview` (already set in sample.env)

### Deployment Name:
- Use the deployment name you created in Step 2 (e.g., `gpt-4o-realtime`)

## Step 4: Configure Environment Variables

1. Copy `backend/sample.env` to `backend/.env`
2. Fill in your Azure OpenAI values:

```env
LIVEKIT_URL="your_livekit_url"
LIVEKIT_API_SECRET="your_livekit_secret"
LIVEKIT_API_KEY="your_livekit_key"

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY="your_azure_openai_key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_VERSION="2024-10-01-preview"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-realtime"
```

## Step 5: Test Your Setup

Run your ServiceDeskAgent to verify the Azure OpenAI integration:

```bash
cd backend
python agent.py
```

If configured correctly, you should see the agent start without errors.

## Troubleshooting

### Common Issues:

1. **"Missing required Azure OpenAI environment variables"**
   - Ensure all four Azure OpenAI variables are set in your `.env` file

2. **"Deployment not found"**
   - Verify your deployment name matches exactly
   - Ensure the deployment is in "Succeeded" state

3. **"Rate limit exceeded"**
   - Check your Azure OpenAI quota and usage
   - Consider upgrading your pricing tier if needed

4. **"Region not supported"**
   - GPT-4o Realtime is only available in certain regions
   - Try East US, West Europe, or other supported regions

### Supported Regions for GPT-4o Realtime:
- East US
- West Europe
- Sweden Central
- (Check Azure documentation for latest list)

## Cost Considerations

- Azure OpenAI pricing is based on tokens processed
- Realtime API has different pricing than standard text API
- Monitor usage in Azure Portal under "Cost Management"
- Set up billing alerts to avoid unexpected charges

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use Azure Key Vault** for production environments
3. **Implement proper access controls** on your Azure OpenAI resource
4. **Monitor API usage** regularly
5. **Rotate API keys** periodically

## Next Steps

Once your Azure OpenAI setup is working:
1. Test all voice interaction features
2. Monitor performance and latency
3. Set up proper logging and monitoring
4. Consider implementing fallback mechanisms
5. Plan for production deployment with proper security
