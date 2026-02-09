import unittest
from unittest.mock import MagicMock, patch
import asyncio
from src.presenter import Presenter


class TestPresenter(unittest.IsolatedAsyncioTestCase):
    @patch("cv2.imshow")
    @patch("cv2.waitKey", side_effect=[-1, ord('q')])  # Simulate 'q' key press
    @patch("cv2.destroyAllWindows")
    async def test_presenter_displays_frames(self, mock_destroy, mock_wait_key, mock_imshow):
        # Create a mock asyncio queue
        mock_queue = asyncio.Queue()
        await mock_queue.put(("frame1", [{"type": "edge_map", "data": "mock_edge_data"}]))
        await mock_queue.put((None, None))  # Sentinel value to stop the Presenter

        # Initialize the Presenter
        presenter = Presenter(mock_queue)

        # Mock the draw_detections method to avoid actual drawing logic
        presenter.draw_detections = MagicMock()

        # Run the Presenter asynchronously
        await presenter.async_run()

    @patch("cv2.destroyAllWindows")
    async def test_presenter_handles_empty_queue(self, mock_destroy):
        # Create a mock asyncio queue with a sentinel value
        mock_queue = asyncio.Queue()
        await mock_queue.put((None, None))  # Sentinel value to stop the Presenter

        # Initialize the Presenter
        presenter = Presenter(mock_queue)

        # Run the Presenter asynchronously
        await presenter.async_run()


if __name__ == "__main__":
    unittest.main()
