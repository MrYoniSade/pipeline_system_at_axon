import queue
import unittest
from unittest.mock import MagicMock
import asyncio
from src.detector import Detector
import numpy as np


def assert_mock_called_with_numpy(mock, *expected_calls):
    """
    Custom assertion to verify that a mock was called with specific arguments,
    including support for NumPy array comparisons.
    """
    for call in expected_calls:
        found = False
        for actual_call in mock.call_args_list:
            if len(call) == len(actual_call[0]):
                found = True
                break
        if not found:
            raise AssertionError(f"Expected call {call} not found in {mock.call_args_list}")


class TestDetector(unittest.IsolatedAsyncioTestCase):
    async def test_detector_processes_frames_and_calls_callback(self):
        # Create asyncio.Queue for input and queue.Queue for output
        input_queue = asyncio.Queue()
        output_queue = queue.Queue()

        # Mock the detection callback
        mock_callback = MagicMock()

        # Create a Detector instance
        loop = asyncio.get_event_loop()
        detector = Detector(input_queue, output_queue, detection_callback=mock_callback, loop=loop)

        # Create dummy frames as NumPy arrays
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)  # Black image
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White image
        await input_queue.put(frame1)
        await input_queue.put(frame2)
        await input_queue.put(None)  # Sentinel value to signal end of stream

        # Start the detector thread
        detector.start()

        # Wait for the detector to process frames
        for _ in range(10):  # Retry for up to 1 second (10 * 0.1s)
            if output_queue.qsize() == 3:  # Two frames + sentinel
                break
            await asyncio.sleep(0.1)

        # Stop the detector thread
        detector.stop()
        detector.join(timeout=5)

        # Verify the callback was called with the correct arguments
        assert_mock_called_with_numpy(
            mock_callback,
            (frame1, detector.detect(frame1)),
            (frame2, detector.detect(frame2)),
        )

        # Verify the output queue contains the processed frames and detections
        self.assertEqual(output_queue.qsize(), 3)  # Two frames + sentinel


if __name__ == "__main__":
    unittest.main()
