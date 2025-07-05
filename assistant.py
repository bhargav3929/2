import os
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import silero
from dotenv import load_dotenv

# Additional plugin imports
from livekit.plugins import deepgram, elevenlabs, openai

# Load environment variables
if os.path.exists(".env.local"):
    load_dotenv(dotenv_path=".env.local")
elif os.path.exists(".env"):
    load_dotenv(dotenv_path=".env")
print("✅ Environment variables loaded!")

@function_tool
async def lookup_weather(context: RunContext, location: str):
    """Used to look up weather information for a specific location."""
    weather_data = {
        "location": location,
        "weather": "sunny", 
        "temperature": 70,
        "humidity": "45%",
        "wind": "5 mph"
    }
    return weather_data

async def entrypoint(ctx: JobContext):
    print("🚀 Starting LiveKit Assistant...")

    # Check required keys
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "DEEPGRAM_API_KEY", "ELEVENLABS_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return

    await ctx.connect()
    print("✅ Connected to LiveKit room successfully!")

    # Agent personality and tool
    agent = Agent(
        instructions="""
            You are a friendly and helpful voice assistant built by LiveKit.
            - Warm, conversational, and approachable
            - Clear and concise in your responses
            - Helpful and eager to assist
            - Always start with a friendly greeting
            - Ask how you can help the user
            - Use the weather tool only when asked
            """,
        tools=[lookup_weather],
    )

    # Configure your chosen providers
    stt_engine = deepgram.STT()
    tts_engine = elevenlabs.TTS()
    llm_engine = openai.LLM(model="gpt-3.5-turbo")  # You can change to "gpt-4" if needed

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=stt_engine,
        llm=llm_engine,
        tts=tts_engine,
    )

    print("🎤 Agent session starting...")
    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help them today."
    )
    print("✅ Assistant is ready!")

if __name__ == "__main__":
    print("🤖 LiveKit Voice Assistant")
    print("=" * 40)
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
