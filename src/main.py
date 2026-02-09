import asyncio
import queue
from src.streamer import Streamer
from src.detector import Detector


def detection_callback(detections):
    """
    Callback function to handle detections.
    :param detections: The detection results.
    """
    print(f"Processed frame with detections: {detections}")


async def main(video_path):
    # Create the queues
    input_queue = asyncio.Queue(maxsize=10)  # For Streamer → Detector
    output_queue = queue.Queue(maxsize=10)  # For Detector → Presenter

    # Get the asyncio event loop
    loop = asyncio.get_event_loop()

    # Initialize the Streamer
    streamer = Streamer(video_path, input_queue, loop)

    # Initialize the Detector
    detector = Detector(input_queue, output_queue, detection_callback=detection_callback, loop=loop)

    # Start the Detector thread
    detector.start()

    # Start the Streamer
    await streamer.start()

    # Wait for the Detector to finish processing
    detector.join()

    print("Pipeline completed.")

if __name__ == "__main__":
    video_file_path = "C:/YonisSpace/YonisCode/pipeline_system_at_axon/data/People - 6387.mp4"
    asyncio.run(main(video_file_path))
