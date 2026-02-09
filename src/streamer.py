import cv2
import logging

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(self, video_path, queue, loop):
        """
        Initializes the Streamer.
        :param video_path: Path to the video file.
        :param queue: asyncio.Queue to push frames into.
        :param loop: asyncio event loop.
        """
        self.video_path = video_path
        self.queue = queue
        self.loop = loop
        self.cap = None
        logger.info(f"Streamer initialized with video path: {self.video_path}")

    async def start(self):
        """
        Starts reading frames asynchronously and pushes them into the queue.
        """
        try:
            logger.info("Opening video file.")
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                raise ValueError(f"Unable to open video file: {self.video_path}")
            logger.info("Video file opened successfully.")

            while True:
                # Offload blocking I/O to a thread pool
                ret, frame = await self.loop.run_in_executor(None, self.cap.read)
                if not ret:
                    logger.info("End of video reached.")
                    break  # End of video

                # Log frame dimensions for debugging
                logger.debug(f"Read a frame with dimensions: {frame.shape if frame is not None else 'None'}")

                # Push the frame into the queue
                await self.queue.put(frame)
                logger.debug("Frame pushed to the queue.")

            # Push sentinel value to signal end of stream
            await self.queue.put(None)
            logger.info("Sentinel value pushed to the queue. Streamer finished.")

        except Exception as e:
            logger.error(f"Error in Streamer: {e}", exc_info=True)

        finally:
            if self.cap:
                self.cap.release()
                logger.info("VideoCapture released.")
                logger.info("queue size after releasing VideoCapture: %d", self.queue.qsize())
