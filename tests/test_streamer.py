import unittest
from unittest.mock import MagicMock, patch
import asyncio
from src.streamer import Streamer
import numpy as np


class TestStreamer(unittest.IsolatedAsyncioTestCase):
    @patch("cv2.VideoCapture")
    async def test_streamer_reads_frames(self, mock_video_capture):
        # Mock the behavior of cv2.VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),  # Mock frame 1
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),  # Mock frame 2
            (False, None),  # End of video
        ]
        mock_video_capture.return_value = mock_cap

        # Use a real asyncio.Queue
        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        # Initialize and start the Streamer
        streamer = Streamer("fake_path.mp4", queue, loop)
        await streamer.start()

        # Verify frames are pushed to the queue
        self.assertEqual(queue.qsize(), 3)  # 2 frames + 1 sentinel value
        self.assertIsNotNone(await queue.get())  # Frame 1
        self.assertIsNotNone(await queue.get())  # Frame 2
        self.assertIsNone(await queue.get())  # Sentinel value

    @patch("cv2.VideoCapture")
    async def test_streamer_handles_invalid_file(self, mock_video_capture):
        # Mock the behavior of cv2.VideoCapture for an invalid file
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False  # Simulate failure to open the file
        mock_video_capture.return_value = mock_cap

        # Use a real asyncio.Queue
        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        # Initialize and start the Streamer
        streamer = Streamer("invalid_path.mp4", queue, loop)
        with self.assertLogs("src.streamer", level="ERROR") as log:
            await streamer.start()

        # Verify the error message in the logs
        self.assertTrue(any("Unable to open video file: invalid_path.mp4" in message for message in log.output))


if __name__ == "__main__":
    unittest.main()
