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
import os

load_dotenv()

logger = logging.getLogger("transcriber")

# This transcriber will handle speech-to-text and publish transcripts to the room
class ServiceDeskTranscriber(Agent):
    def __init__(self):
        # Azure OpenAI Configuration
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
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
        # Stop processing after transcription to avoid generating responses
        raise StopResponse()

async def entrypoint(ctx: JobContext):
    logger.info(f"Starting Service Desk Transcriber, room: {ctx.room.name}")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    session = AgentSession(
        # Using session without VAD - will use default audio processing
    )
    
    @session.on("metrics_collected")
    def on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
    
    await session.start(
        agent=ServiceDeskTranscriber(),
        room=ctx.room,
        room_output_options=RoomOutputOptions(
            transcription_enabled=True,
            # disable audio output since this is transcription only
            audio_enabled=False,
        ),
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
