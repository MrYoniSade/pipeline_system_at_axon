import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from src.streamer import Streamer


class TestStreamer(unittest.IsolatedAsyncioTestCase):
    @patch("cv2.VideoCapture")
    async def test_streamer_reads_frames(self, mock_video_capture):
        # Mock the behavior of cv2.VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [(True, "frame1"), (True, "frame2"), (False, None)]  # Simulate 2 frames and EOF
        mock_video_capture.return_value = mock_cap

        # Mock asyncio.Queue
        mock_queue = AsyncMock()
        loop = asyncio.get_event_loop()

        # Initialize and start the Streamer
        streamer = Streamer("fake_path.mp4", mock_queue, loop)
        await streamer.start()

        # Verify frames are pushed to the queue
        mock_queue.put.assert_any_call("frame1")
        mock_queue.put.assert_any_call("frame2")
        mock_queue.put.assert_called_with(None)  # Sentinel value at the end

        # Verify VideoCapture methods were called
        mock_cap.isOpened.assert_called_once()
        mock_cap.read.assert_called()

    @patch("cv2.VideoCapture")
    @patch("builtins.print")
    async def test_streamer_handles_invalid_file(self, mock_print, mock_video_capture):
        # Mock the behavior of cv2.VideoCapture for an invalid file
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False  # Simulate failure to open the file
        mock_video_capture.return_value = mock_cap

        # Mock asyncio.Queue
        mock_queue = AsyncMock()
        loop = asyncio.get_event_loop()

        # Initialize and start the Streamer
        streamer = Streamer("invalid_path.mp4", mock_queue, loop)
        await streamer.start()

        # Verify the error message was printed
        mock_print.assert_called_with("Error in Streamer: Unable to open video file: invalid_path.mp4")

        # Verify VideoCapture methods were called
        mock_cap.isOpened.assert_called_once()


if __name__ == "__main__":
    unittest.main()
