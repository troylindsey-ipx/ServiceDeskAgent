#!/usr/bin/env python3
"""
Script to run both the transcriber and agent services for the Service Desk Agent
"""
import subprocess
import sys
import os
from pathlib import Path

def run_service(script_name, service_name):
    """Run a service script"""
    script_path = Path(__file__).parent / script_name
    
    print(f"Starting {service_name}...")
    print(f"Command: python {script_path} start")
    
    try:
        # Run the service
        result = subprocess.run([
            sys.executable, str(script_path), "start"
        ], cwd=Path(__file__).parent)
        
        return result.returncode
    except KeyboardInterrupt:
        print(f"\n{service_name} interrupted by user")
        return 0
    except Exception as e:
        print(f"Error running {service_name}: {e}")
        return 1

def main():
    """Main function to run services"""
    print("Service Desk Agent - Starting Services")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment")
        return 1
    
    print("Environment variables check: ✓")
    print()
    
    # Ask user which service to run
    print("Select service to run:")
    print("1. Transcriber only (Speech-to-Text)")
    print("2. Agent only (Voice responses + Function tools)")
    print("3. Both services (Recommended)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        return run_service("transcriber.py", "Transcriber Service")
    elif choice == "2":
        return run_service("agent.py", "Agent Service")
    elif choice == "3":
        print("\nTo run both services, you'll need to run them in separate terminals:")
        print(f"Terminal 1: python {Path(__file__).parent / 'transcriber.py'} start")
        print(f"Terminal 2: python {Path(__file__).parent / 'agent.py'} start")
        print("\nFor now, starting the transcriber service...")
        return run_service("transcriber.py", "Transcriber Service")
    else:
        print("Invalid choice. Exiting.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
