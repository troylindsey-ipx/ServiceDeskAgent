from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)
from livekit.agents import voice
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_TICKET_MESSAGE
from token_tracker import token_tracker
import os
import asyncio

load_dotenv()

async def entrypoint(ctx: JobContext):
    print(f"AGENT: Entrypoint called for room: {ctx.room.name if ctx.room else 'No room yet'}")
    
    # Azure OpenAI Configuration
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([azure_api_key, azure_endpoint, azure_deployment]):
        raise ValueError("Missing required Azure OpenAI environment variables. Please check your .env file.")
    
    print("AGENT: Creating Azure OpenAI model...")
    print(f"AGENT: Using endpoint: {azure_endpoint}")
    print(f"AGENT: Using deployment: {azure_deployment}")
    print(f"AGENT: Using API version: {azure_api_version}")
    
    # Create Azure OpenAI realtime model (without transcription - handled by separate transcriber)
    model = openai.realtime.RealtimeModel.with_azure(
        azure_deployment=azure_deployment,
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=azure_api_version,
        voice="shimmer",
        temperature=0.8
    )
    
    
    print("AGENT: Connecting to room...")
    
    # Connect to the room and wait for participants
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    
    print(f"AGENT: Connected to room: {ctx.room.name}")
    print("AGENT: Waiting for participants...")
    
    # Wait for participants to join
    participant = await ctx.wait_for_participant()
    
    print(f"AGENT: Participant joined! Starting voice session in room: {ctx.room.name}")
    print(f"AGENT: Participant name: {participant.name}, identity: {participant.identity}")
    
    # Get participant name for function tools
    participant_name = participant.name or participant.identity or ""
    
    # Initialize token tracking
    print("AGENT: Initializing token tracking...")
    
    # Clean up any stale sessions first
    cleaned_count = token_tracker.cleanup_stale_sessions()
    if cleaned_count > 0:
        print(f"AGENT: Cleaned up {cleaned_count} stale sessions")
    
    tracking_session_id = token_tracker.start_session(
        room_name=ctx.room.name,
        user_name=participant_name,
        participant_identity=participant.identity
    )
    
    # Register agent service for token tracking
    token_tracker.register_service(tracking_session_id, "agent", "gpt-4o-realtime")
    
    print("AGENT: Creating function tools...")
    
    # Create function context with tools (now with participant name)
    assistant_fnc = AssistantFnc(participant_name)
    tools = [
        assistant_fnc.lookup_ticket,
        assistant_fnc.search_tickets_by_name,
        assistant_fnc.get_ticket_details,
        assistant_fnc.create_ticket
    ]
    
    print("AGENT: Creating voice agent...")
    
    # Create voice agent
    assistant = voice.Agent(
        instructions=INSTRUCTIONS,
        llm=model,
        tools=tools
    )

    # Create voice session using AgentSession (STT handled by separate transcriber service)
    session = voice.AgentSession(
        llm=model
    )
    
    # Add token tracking callback to session
    @session.on("agent_speech")
    def on_agent_speech(event):
        """Track tokens when agent generates speech"""
        try:
            # Extract token usage from the event if available
            # Note: This may need adjustment based on actual LiveKit event structure
            if hasattr(event, 'usage') and event.usage:
                input_tokens = getattr(event.usage, 'input_tokens', 0)
                output_tokens = getattr(event.usage, 'output_tokens', 0)
                
                if input_tokens > 0 or output_tokens > 0:
                    token_tracker.track_tokens(tracking_session_id, "agent", input_tokens, output_tokens)
                    print(f"AGENT: Tracked tokens - Input: {input_tokens}, Output: {output_tokens}")
        except Exception as e:
            print(f"AGENT: Error tracking tokens: {e}")
    
    print("AGENT: Voice session created, starting...")
    
    # Start the session with the room and agent
    await session.start(
        room=ctx.room,
        agent=assistant
    )
    
    print("AGENT: Voice session started successfully!")
    
    # Get participant name for personalized greeting
    participant_name = participant.name or participant.identity or "there"
    
    # Check if we can find existing tickets for this user
    print(f"AGENT: Checking for existing tickets for user: {participant_name}")
    
    # Immediately greet the user with personalized welcome message
    print("AGENT: Greeting the user...")
    personalized_greeting = f"Hello {participant_name}! {WELCOME_MESSAGE.strip()}"
    session.generate_reply(
        user_input="Please greet the user with a personalized IT help desk welcome message.",
        instructions=f"Say exactly: {personalized_greeting}"
    )
    
    # Keep the session running
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("AGENT: Voice session cancelled")
    finally:
        # End token tracking and get summary
        print("AGENT: Ending token tracking session...")
        usage_summary = token_tracker.end_session(tracking_session_id, "agent")
        
        if usage_summary:
            print("AGENT: Token Usage Summary:")
            print(f"  User: {usage_summary.get('user_name', 'Unknown')}")
            print(f"  Room: {usage_summary.get('room_name', 'Unknown')}")
            print(f"  Total Tokens: {usage_summary.get('totals', {}).get('total_tokens', 0)}")
            
            for service_type, service_data in usage_summary.get('services', {}).items():
                print(f"  {service_type.title()} Service ({service_data.get('model_name', 'Unknown')}):")
                print(f"    Input Tokens: {service_data.get('input_tokens', 0)}")
                print(f"    Output Tokens: {service_data.get('output_tokens', 0)}")
                print(f"    Total Tokens: {service_data.get('total_tokens', 0)}")
        
        await session.aclose()
        print("AGENT: Voice session closed")
    
if __name__ == "__main__":
    print("AGENT: Starting LiveKit agent worker...")
    print("AGENT: Worker will dispatch to new rooms automatically")
    
    # Configure worker options with more explicit settings
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint
    )
    
    try:
        cli.run_app(worker_options)
    except Exception as e:
        print(f"AGENT: Error starting worker: {e}")
        raise
