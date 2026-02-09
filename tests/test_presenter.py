import unittest
from unittest.mock import MagicMock, patch
import queue
from src.presenter import Presenter


class TestPresenter(unittest.TestCase):
    @patch("cv2.imshow")
    @patch("cv2.waitKey", side_effect=[-1, ord('q')])  # Simulate 'q' key press
    @patch("cv2.destroyAllWindows")
    def test_presenter_displays_frames(self, mock_destroy, mock_wait_key, mock_imshow):
        # Create a mock output queue
        mock_queue = queue.Queue()
        mock_queue.put(("frame1", [{"type": "edge_map", "data": "mock_edge_data"}]))
        mock_queue.put((None, None))  # Sentinel value to stop the Presenter

        # Initialize the Presenter
        presenter = Presenter(mock_queue)

        # Mock the draw_detections method to avoid actual drawing logic
        presenter.draw_detections = MagicMock()

        # Start the Presenter in the main thread for testing
        presenter.run()

        # Verify that frames were displayed
        mock_imshow.assert_called_with("Video Presenter", "frame1")

        # Verify that the 'q' key press stopped the Presenter
        mock_wait_key.assert_called()

        # Verify that the OpenCV window was destroyed
        mock_destroy.assert_called_once()

    @patch("cv2.destroyAllWindows")
    def test_presenter_handles_empty_queue(self, mock_destroy):
        # Create a mock output queue with a sentinel value
        mock_queue = queue.Queue()
        mock_queue.put((None, None))  # Sentinel value to stop the Presenter

        # Initialize the Presenter
        presenter = Presenter(mock_queue)

        # Start the Presenter in the main thread for testing
        presenter.run()

        # Verify that the OpenCV window was destroyed
        mock_destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()