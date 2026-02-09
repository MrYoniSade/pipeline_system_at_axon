import unittest
from unittest.mock import patch
import asyncio
import numpy as np

from src.presenter import Presenter


class TestPresenter(unittest.IsolatedAsyncioTestCase):
    @patch("cv2.imshow")
    @patch("cv2.waitKey", side_effect=[-1, ord('q')])  # Simulate 'q' key press
    @patch("cv2.destroyAllWindows")
    async def test_presenter_displays_frames(self, _, __, ___):
        # Create a mock asyncio queue
        mock_queue = asyncio.Queue()
        # Provide a valid NumPy array as the frame and detections as a list of tuples
        frame = np.zeros((480, 640, 3), dtype=np.uint8)  # Example blank frame
        await mock_queue.put((frame, [(10, 20, 30, 40)]))  # Example detection
        await mock_queue.put((None, None))  # Sentinel value to stop the Presenter

        # Initialize the Presenter
        presenter = Presenter(mock_queue)

        # Run the Presenter asynchronously
        await presenter.async_run()

    @patch("cv2.destroyAllWindows")
    async def test_presenter_handles_empty_queue(self, _):
        # Create a mock asyncio queue with a sentinel value
        mock_queue = asyncio.Queue()
        await mock_queue.put((None, None))  # Sentinel value to stop the Presenter

        # Initialize the Presenter
        presenter = Presenter(mock_queue)

        # Run the Presenter asynchronously
        await presenter.async_run()

    async def test_apply_blur(self):
        # Create a mock frame with some variation (e.g., a gradient)
        mock_frame = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        # Apply the blur using the Presenter class
        blurred_frame = Presenter.apply_blur(mock_frame)

        # Ensure the blurred frame is not identical to the original frame
        self.assertFalse(np.array_equal(mock_frame, blurred_frame), "The frame was not blurred.")

        # Optionally, check if the blurred frame still has the same shape
        self.assertEqual(mock_frame.shape, blurred_frame.shape, "The blurred frame shape is incorrect.")


if __name__ == "__main__":
    unittest.main()
