import asyncio
import cv2
import threading
from concurrent.futures import ThreadPoolExecutor


class Detector(threading.Thread):
    def __init__(self, input_queue, output_queue, detection_callback=None, max_workers=4, loop=None):
        """
        Initializes the Detector.
        :param input_queue: asyncio.Queue to receive frames from the Streamer.
        :param output_queue: queue.Queue to send (frame, detections) to the Presenter.
        :param detection_callback: Optional callback function to process detections.
        :param max_workers: Maximum number of threads in the thread pool.
        :param loop: The asyncio event loop.
        """
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.detection_callback = detection_callback
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loop = loop

    def run(self):
        """
        Starts processing frames from the input queue and performs detection.
        """
        try:
            while not self.stop_event.is_set():
                # Get the next frame from the input queue (thread-safe)
                frame = asyncio.run_coroutine_threadsafe(self.input_queue.get(), self.loop).result()
                if frame is None:  # Sentinel value to signal end of stream
                    self.output_queue.put((None, None))  # Propagate sentinel
                    break

                # Submit detection to the thread pool
                self.executor.submit(self.process_frame, frame)

        except Exception as e:
            print(f"Error in Detector: {e}")

        finally:
            self.executor.shutdown(wait=True)

    def process_frame(self, frame):
        """
        Processes a single frame and pushes the result to the output queue.
        """
        detections = self.detect(frame)

        # Call the detection callback if provided
        if self.detection_callback:
            self.detection_callback(frame, detections)

        # Push the frame and detections to the output queue
        self.output_queue.put((frame, detections))

    def stop(self):
        """
        Signals the thread to stop processing.
        """
        self.stop_event.set()

    @staticmethod
    def detect(frame):
        """
        Performs object detection on a single frame.
        :param frame: The video frame to process.
        :return: A list of detections (e.g., bounding boxes, labels, etc.).
        """
        # Example: Convert the frame to grayscale and detect edges
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_frame, 100, 200)

        # Example detection result (replace with actual detection logic)
        detections = [{"type": "edge_map", "data": edges}]
        return detections
