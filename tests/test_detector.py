import queue
import unittest
from unittest.mock import AsyncMock
import asyncio
from src.detector import Detector
import numpy as np


class TestDetector(unittest.IsolatedAsyncioTestCase):
    async def test_detector_processes_frames_and_calls_callback(self):
        # Create asyncio.Queue for input and queue.Queue for output
        input_queue = asyncio.Queue()
        output_queue = asyncio.Queue()  # Use asyncio.Queue for compatibility

        # Mock the detection callback as an async function
        async_mock_callback = AsyncMock()

        # Create a Detector instance
        loop = asyncio.get_event_loop()
        detector = Detector(input_queue, output_queue, detection_callback=async_mock_callback, loop=loop)

        # Create dummy frames as NumPy arrays
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)  # Black image
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White image
        await input_queue.put(frame1)
        await input_queue.put(frame2)
        await input_queue.put(None)  # Sentinel value to signal end of stream

        # Start the detector
        await detector.start()

        # Wait for the detector to process frames
        for _ in range(10):  # Retry for up to 1 second (10 * 0.1s)
            if output_queue.qsize() == 3:  # Two frames + sentinel
                break
            await asyncio.sleep(0.1)

        # Stop the detector
        detector.stop()

        # Verify the output queue contains the processed frames and detections
        self.assertEqual(output_queue.qsize(), 3)  # Two frames + sentinel


if __name__ == "__main__":
    unittest.main()