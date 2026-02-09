import cv2
import threading


class Presenter(threading.Thread):
    def __init__(self, output_queue, window_name="Video Presenter"):
        """
        Initializes the Presenter.
        :param output_queue: queue.Queue to receive (frame, detections) from the Detector.
        :param window_name: Name of the OpenCV window.
        """
        super().__init__()
        self.output_queue = output_queue
        self.window_name = window_name
        self.stop_event = threading.Event()

    def run(self):
        """
        Starts the Presenter thread to display frames with overlays.
        """
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        try:
            while not self.stop_event.is_set():
                # Get the next (frame, detections) from the output queue
                frame, detections = self.output_queue.get()

                if frame is None:  # Sentinel value to signal end of stream
                    break

                # Draw overlays on the frame
                self.draw_detections(frame, detections)

                # Display the frame
                cv2.imshow(self.window_name, frame)

                # Exit if the user presses 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    break

        finally:
            cv2.destroyAllWindows()

    def draw_detections(self, frame, detections):
        """
        Draws detection overlays on the frame.
        :param frame: The video frame.
        :param detections: The detection metadata.
        """
        for detection in detections:
            if detection["type"] == "edge_map":
                # Example: Overlay the edge map on the frame
                edges = detection["data"]
                frame[edges > 0] = [0, 255, 0]  # Highlight edges in green

    def stop(self):
        """
        Signals the thread to stop processing.
        """
        self.stop_event.set()