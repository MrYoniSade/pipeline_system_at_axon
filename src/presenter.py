import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class Presenter:
    def __init__(self, output_queue):
        self.output_queue = output_queue
        self.stop_event = False
        logger.info("Presenter initialized.")

    async def async_run(self):
        logger.info("Presenter started.")
        try:
            # Create a named window and move it to the upper-left corner
            window_name = "Video Stream"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.moveWindow(window_name, 0, 0)

            while not self.stop_event:
                logger.debug("Waiting for the next item from the output queue.")
                # Await the next item from the output queue
                frame, detections = await self.output_queue.get()
                logger.debug("Item retrieved from the output queue.")

                if frame is None:  # Sentinel value
                    logger.info("Received sentinel value. Stopping Presenter.")
                    break

                # Ensure the frame is a valid NumPy array
                if not isinstance(frame, np.ndarray):
                    raise ValueError("The provided frame is not a valid NumPy array.")

                # Draw rectangles for each detection
                for (x, y, w, h) in detections:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Optionally apply blur to the frame
                frame = self.apply_blur(frame)

                logger.debug("Processing frame and detections in Presenter.")
                # Display the frame in the upper-left corner
                cv2.imshow(window_name, frame)

                # Wait for a short period to allow real-time display
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Quit signal received. Stopping Presenter.")
                    break

        except Exception as e:
            logger.error(f"Error in Presenter: {e}", exc_info=True)
        finally:
            cv2.destroyAllWindows()
            logger.info("Presenter stopped.")

    @staticmethod
    def apply_blur(frame):
        # Apply Gaussian blur to the frame
        return cv2.GaussianBlur(frame, (5, 5), 0)

    def stop(self):
        logger.info("Stop signal received for Presenter.")
        self.stop_event = True