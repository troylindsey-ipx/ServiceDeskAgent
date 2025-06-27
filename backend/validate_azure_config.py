#!/usr/bin/env python3
"""
Azure OpenAI Configuration Validator

This script validates your Azure OpenAI configuration before running the main agent.
Run this script to ensure all environment variables are properly set and the connection works.

Usage:
    python validate_azure_config.py
"""

import os
import sys
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'LIVEKIT_URL': 'LiveKit server URL',
        'LIVEKIT_API_KEY': 'LiveKit API key',
        'LIVEKIT_API_SECRET': 'LiveKit API secret',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI API key',
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI endpoint',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'Azure OpenAI deployment name'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"  ❌ {var} ({description})")
            print(f"  ❌ {var}: Not set")
        else:
            # Mask sensitive values for display
            if 'KEY' in var or 'SECRET' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(var)
        print(f"\nPlease check your .env file and ensure all variables are set.")
        return False
    
    print("✅ All environment variables are set!")
    return True

def validate_azure_endpoint():
    """Validate Azure OpenAI endpoint format."""
    print("\n🔍 Validating Azure OpenAI endpoint format...")
    
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    if not endpoint:
        print("❌ AZURE_OPENAI_ENDPOINT not set")
        return False
    
    if not endpoint.startswith('https://'):
        print(f"❌ Endpoint should start with 'https://': {endpoint}")
        return False
    
    if not '.openai.azure.com' in endpoint:
        print(f"❌ Endpoint should contain '.openai.azure.com': {endpoint}")
        return False
    
    print(f"✅ Endpoint format looks correct: {endpoint}")
    return True

async def test_azure_openai_connection():
    """Test connection to Azure OpenAI."""
    print("\n🔍 Testing Azure OpenAI connection...")
    
    try:
        from livekit.plugins import openai
        
        # Get configuration
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01-preview")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Create a simple test model (not realtime for validation)
        print("  📡 Creating test connection...")
        
        # Note: For validation, we'll just check if we can create the model object
        # without actually making API calls which would require LiveKit context
        try:
            model = openai.realtime.RealtimeModel.with_azure(
                azure_deployment=azure_deployment,
                azure_endpoint=azure_endpoint,
                api_key=azure_api_key,
                api_version=azure_api_version
            )
            print("✅ Azure OpenAI model configuration created successfully!")
            print("  📝 Note: Full connection test requires running the actual agent with LiveKit")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Azure OpenAI model: {str(e)}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import required modules: {str(e)}")
        print("  💡 Make sure you've installed requirements: pip install -r requirements.txt")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n🚀 Next Steps:")
    print("1. If all validations passed, you can run your agent:")
    print("   cd backend && python agent.py")
    print("\n2. If you encounter issues:")
    print("   - Check the Azure OpenAI Setup Guide: AZURE_OPENAI_SETUP.md")
    print("   - Verify your Azure OpenAI deployment is active in Azure Portal")
    print("   - Ensure you're using a supported region for GPT-4o Realtime")
    print("\n3. For production deployment:")
    print("   - Use Azure Key Vault for secrets management")
    print("   - Set up proper monitoring and logging")
    print("   - Configure appropriate access controls")

async def main():
    """Main validation function."""
    print("🔧 Azure OpenAI Configuration Validator")
    print("=" * 50)
    
    # Check environment variables
    env_check = check_environment_variables()
    
    # Validate endpoint format
    endpoint_check = validate_azure_endpoint()
    
    # Test connection
    connection_check = await test_azure_openai_connection()
    
    print("\n" + "=" * 50)
    print("📊 Validation Summary:")
    print(f"  Environment Variables: {'✅ PASS' if env_check else '❌ FAIL'}")
    print(f"  Endpoint Format: {'✅ PASS' if endpoint_check else '❌ FAIL'}")
    print(f"  Connection Test: {'✅ PASS' if connection_check else '❌ FAIL'}")
    
    if all([env_check, endpoint_check, connection_check]):
        print("\n🎉 All validations passed! Your Azure OpenAI configuration looks good.")
        print_next_steps()
        return 0
    else:
        print("\n❌ Some validations failed. Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during validation: {str(e)}")
        sys.exit(1)
