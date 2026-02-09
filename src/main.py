import asyncio
from streamer import Streamer


async def main():
    video_path = "../data/People - 6387.mp4"  # Replace with the actual video path
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    streamer = Streamer(video_path, queue, loop)
    await streamer.start()

if __name__ == "__main__":
    asyncio.run(main())
