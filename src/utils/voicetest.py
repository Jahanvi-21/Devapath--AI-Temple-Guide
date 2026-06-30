import edge_tts
import asyncio

TEXT = """
Namaste! Welcome to DevaPath.
I am your AI Temple Guide.
Today I will explain the selected temple in a friendly and respectful way.
"""

async def main():
    communicate = edge_tts.Communicate(
        TEXT,
        "en-IN-NeerjaNeural"   # Indian Female Voice
    )
    await communicate.save("guide.mp3")

asyncio.run(main())

print("Voice Generated Successfully!")









