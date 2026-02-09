import asyncio
import logging
from src.streamer import Streamer
from src.detector import Detector
from src.presenter import Presenter

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler("pipeline.log")  # Log to a file named 'pipeline.log'
    ]
)

logger = logging.getLogger(__name__)  # Create a logger for this module


def detection_callback(frame, detections):
    # Implement your detection callback logic here
    print(f"Frame: {frame}, Detections: {detections}")


async def main(video_path):
    # Create the queues
    input_queue = asyncio.Queue(maxsize=10)  # For Streamer → Detector
    output_queue = asyncio.Queue(maxsize=10)  # For Detector → Presenter

    # Initialize the Streamer
    streamer = Streamer(video_path, input_queue, asyncio.get_event_loop())

    # Initialize the Detector
    detector = Detector(input_queue, output_queue, detection_callback=detection_callback, loop=asyncio.get_event_loop())

    # Initialize the Presenter
    presenter = Presenter(output_queue)

    # Start the Presenter in a separate thread
    logger.info("Starting Presenter thread.")
    presenter_task = asyncio.create_task(presenter.async_run())

    # Start the Streamer and Detector as asyncio tasks
    logger.info("Starting Streamer and Detector.")
    streamer_task = asyncio.create_task(streamer.start())
    detector_task = asyncio.create_task(detector.start())

    # Run the Presenter thread and wait for all tasks to complete
    await asyncio.gather(streamer_task, detector_task, presenter_task)

    # Stop the Presenter after processing is complete
    presenter.stop()
    logger.info("Pipeline completed.")

if __name__ == "__main__":
    video_file_path = "C:/YonisSpace/YonisCode/pipeline_system_at_axon/data/People - 6387.mp4"
    logger.info("Starting the video processing pipeline.")
    asyncio.run(main(video_file_path))
