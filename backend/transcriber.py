import logging
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    MetricsCollectedEvent,
    RoomOutputOptions,
    StopResponse,
    WorkerOptions,
    cli,
    llm,
    metrics,
)
from livekit.plugins import openai
from token_tracker import token_tracker
import os

load_dotenv()

logger = logging.getLogger("transcriber")

# This transcriber will handle speech-to-text and publish transcripts to the room
class ServiceDeskTranscriber(Agent):
    def __init__(self, tracking_session_id: str = None):
        # Azure OpenAI Configuration
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Store tracking session ID
        self.tracking_session_id = tracking_session_id
        
        # Create Azure OpenAI STT
        stt = openai.STT.with_azure(
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=azure_api_version,
            model="gpt-4o-transcribe",
            language="en"
        )
        
        super().__init__(
            instructions="Transcribe audio for service desk support",
            stt=stt,
        )

    async def on_user_turn_completed(self, chat_ctx: llm.ChatContext, new_message: llm.ChatMessage):
        user_transcript = new_message.text_content
        logger.info(f"Transcribed: {user_transcript}")
        
        # Track token usage for transcription
        if self.tracking_session_id:
            try:
                # Estimate token usage for transcription
                # Note: This is an approximation since actual token usage may not be directly available
                estimated_input_tokens = len(user_transcript.split()) * 1.3  # Rough estimate
                estimated_output_tokens = len(user_transcript.split())  # Output is the transcript
                
                token_tracker.track_tokens(
                    self.tracking_session_id, 
                    "transcriber", 
                    int(estimated_input_tokens), 
                    int(estimated_output_tokens)
                )
                logger.debug(f"Tracked transcription tokens - Input: {int(estimated_input_tokens)}, Output: {int(estimated_output_tokens)}")
            except Exception as e:
                logger.error(f"Error tracking transcription tokens: {e}")
        
        # Stop processing after transcription to avoid generating responses
        raise StopResponse()

async def entrypoint(ctx: JobContext):
    logger.info(f"Starting Service Desk Transcriber, room: {ctx.room.name}")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Wait for participants to get user information
    participant = await ctx.wait_for_participant()
    participant_name = participant.name or participant.identity or ""
    
    logger.info(f"Transcriber: Participant joined - {participant_name}")
    
    # Clean up any stale sessions first
    cleaned_count = token_tracker.cleanup_stale_sessions()
    if cleaned_count > 0:
        logger.info(f"Transcriber: Cleaned up {cleaned_count} stale sessions")
    
    # Find or create token tracking session
    tracking_session_id = token_tracker.find_session_by_room_and_user(
        ctx.room.name, 
        participant.identity
    )
    
    if not tracking_session_id:
        # Create new session if agent hasn't started yet
        tracking_session_id = token_tracker.start_session(
            room_name=ctx.room.name,
            user_name=participant_name,
            participant_identity=participant.identity
        )
        logger.info(f"Transcriber: Created new token tracking session: {tracking_session_id}")
    else:
        logger.info(f"Transcriber: Using existing token tracking session: {tracking_session_id}")
    
    # Register transcriber service for token tracking
    token_tracker.register_service(tracking_session_id, "transcriber", "whisper")
    
    session = AgentSession(
        # Using session without VAD - will use default audio processing
    )
    
    @session.on("metrics_collected")
    def on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
    
    try:
        await session.start(
            agent=ServiceDeskTranscriber(tracking_session_id),
            room=ctx.room,
            room_output_options=RoomOutputOptions(
                transcription_enabled=True,
                # disable audio output since this is transcription only
                audio_enabled=False,
            ),
        )
    finally:
        # End transcriber token tracking when session ends
        logger.info("Transcriber: Ending token tracking session...")
        usage_summary = token_tracker.end_session(tracking_session_id, "transcriber")
        
        if usage_summary:
            logger.info("Transcriber: Token Usage Summary:")
            logger.info(f"  User: {usage_summary.get('user_name', 'Unknown')}")
            logger.info(f"  Room: {usage_summary.get('room_name', 'Unknown')}")
            
            for service_type, service_data in usage_summary.get('services', {}).items():
                logger.info(f"  {service_type.title()} Service ({service_data.get('model_name', 'Unknown')}):")
                logger.info(f"    Input Tokens: {service_data.get('input_tokens', 0)}")
                logger.info(f"    Output Tokens: {service_data.get('output_tokens', 0)}")
                logger.info(f"    Total Tokens: {service_data.get('total_tokens', 0)}")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
