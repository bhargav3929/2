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
from livekit.plugins import groq, silero

# Try to load from .env.local, fallback to .env, or use environment variables
try:
    from dotenv import load_dotenv
    # Try .env.local first, then .env
    if os.path.exists(".env.local"):
        load_dotenv(dotenv_path=".env.local")
    elif os.path.exists(".env"):
        load_dotenv(dotenv_path=".env")
    print("Environment variables loaded successfully!")
except ImportError:
    print("python-dotenv not found. Using system environment variables.")

@function_tool
async def lookup_weather(
    context: RunContext,
    location: str,
):
    """Used to look up weather information for a specific location."""
    # This is a simple mock weather function
    # In a real application, you would call a weather API
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
    
    # Check if required environment variables are set
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "GROQ_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with your credentials.")
        print("   See the README.md for instructions on getting these keys.")
        return
    
    await ctx.connect()
    print("✅ Connected to LiveKit room successfully!")

    agent = Agent(
        instructions="""
            You are a friendly and helpful voice assistant built by LiveKit.
            
            Your personality:
            - Warm, conversational, and approachable
            - Clear and concise in your responses
            - Helpful and eager to assist
            
            Guidelines:
            - Always start conversations with a friendly greeting
            - Ask how you can help the user
            - Only use the weather tool when users specifically ask about weather
            - If you don't know something, be honest about it
            - Keep responses natural and conversational
            
            Remember: You can have voice conversations with users in real-time!
            """,
        tools=[lookup_weather],
    )
    
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=groq.STT(),  
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=groq.TTS(model="playai-tts"), 
    )

    print("🎤 Agent session starting...")
    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help them today."
    )
    print("✅ Assistant is ready and waiting for user interaction!")

if __name__ == "__main__":
    print("🤖 LiveKit Voice Assistant")
    print("=" * 40)
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))