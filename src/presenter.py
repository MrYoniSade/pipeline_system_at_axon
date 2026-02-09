import asyncio
import logging

logger = logging.getLogger(__name__)


class Presenter:
    def __init__(self, output_queue):
        self.output_queue = output_queue
        self.stop_event = False
        logger.info("Presenter initialized.")

    async def async_run(self):
        logger.info("Presenter started.")
        try:
            while not self.stop_event:
                logger.debug("Waiting for the next item from the output queue.")
                # Await the next item from the output queue
                frame, detections = await self.output_queue.get()
                logger.debug("Item retrieved from the output queue.")

                if frame is None:  # Sentinel value
                    logger.info("Received sentinel value. Stopping Presenter.")
                    break

                logger.debug("Processing frame and detections in Presenter.")
                # Process the frame and detections (implement your logic here)
                logger.debug(f"Frame: {frame}, Detections: {detections}")
        except Exception as e:
            logger.error(f"Error in Presenter: {e}", exc_info=True)
        finally:
            logger.info("Presenter stopped.")

    def run(self):
        logger.info("Running Presenter in the current event loop.")
        asyncio.run(self.async_run())

    def stop(self):
        logger.info("Stop signal received for Presenter.")
        self.stop_event = True
