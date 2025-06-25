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
