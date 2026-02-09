import cv2
import imutils
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class Detector:
    def __init__(self, input_queue, output_queue, detection_callback=None, max_workers=4, loop=None):
        """
        Initializes the Detector.
        :param input_queue: asyncio.Queue to receive frames from the Streamer.
        :param output_queue: asyncio.Queue to send (frame, detections) to the Presenter.
        :param detection_callback: Optional callback function to process detections.
        :param max_workers: Maximum number of threads in the thread pool.
        :param loop: The asyncio event loop associated with the queues.
        """
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.detection_callback = detection_callback
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.stop_event = asyncio.Event()
        self.loop = loop or asyncio.get_event_loop()  # Use the provided loop or get the current event loop
        self.prev_frame = None  # Store the previous frame for motion detection
        logger.info("Detector initialized.")

    async def start(self):
        """
        Starts the Detector to process frames from the input queue.
        """
        logger.info("Detector started.")
        try:
            while not self.stop_event.is_set():
                frame = await self.input_queue.get()
                if frame is None:  # Sentinel value to stop processing
                    logger.info("Received sentinel value. Stopping Detector.")
                    break
                await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.process_frame, frame
                )
        except Exception as e:
            logger.error(f"Error in Detector: {e}", exc_info=True)
        finally:
            # Ensure the sentinel value is added to the output queue in the correct loop
            asyncio.run_coroutine_threadsafe(
                self.output_queue.put((None, None)), self.loop
            )
            logger.info("Detector stopped.")

    def process_frame(self, frame):
        """
        Processes a single frame and sends the result to the output queue.
        :param frame: The frame to process.
        """
        try:
            # Perform detection logic
            detections = self.detect(frame)

            # Use asyncio.run_coroutine_threadsafe to put the result in the output queue
            asyncio.run_coroutine_threadsafe(
                self.output_queue.put((frame, detections)),
                self.loop  # Pass the event loop associated with the asyncio.Queue
            )
        except Exception as e:
            logger.error(f"Error processing frame: {e}", exc_info=True)

    def detect(self, frame):
        """
        Motion detection logic.
        :param frame: The frame to analyze.
        :return: Detections (bounding boxes of motion areas).
        """
        try:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detections = []

            if self.prev_frame is None:
                self.prev_frame = gray_frame
            else:
                # Compute the absolute difference between the current frame and the previous frame
                diff = cv2.absdiff(gray_frame, self.prev_frame)
                thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # Store bounding boxes of detected motion areas
                for contour in cnts:
                    if cv2.contourArea(contour) < 500:  # Ignore small areas
                        continue
                    x, y, w, h = cv2.boundingRect(contour)
                    detections.append((x, y, w, h))

                # Update the previous frame
                self.prev_frame = gray_frame

            return detections
        except Exception as e:
            logger.error(f"Error in detection logic: {e}", exc_info=True)
            return []

    def stop(self):
        """
        Stops the Detector by setting the stop event.
        """
        logger.info("Stop signal received for Detector.")
        self.stop_event.set()
