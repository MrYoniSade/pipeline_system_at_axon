import cv2


class Streamer:
    def __init__(self, video_path, queue, loop):
        """
        Initializes the Streamer.
        :param video_path: Path to the video file.
        :param queue: asyncio.Queue to push frames into.
        :param loop: asyncio event loop.
        """
        self.video_path = video_path
        self.queue = queue
        self.loop = loop
        self.cap = None

    async def start(self):
        """
        Starts reading frames asynchronously and pushes them into the queue.
        """
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                raise ValueError(f"Unable to open video file: {self.video_path}")

            while True:
                # Offload blocking I/O to a thread pool
                ret, frame = await self.loop.run_in_executor(None, self.cap.read)
                if not ret:
                    break  # End of video

                # Push the frame into the queue
                await self.queue.put(frame)

            # Push sentinel value to signal end of stream
            await self.queue.put(None)

        except Exception as e:
            print(f"Error in Streamer: {e}")

        finally:
            if self.cap:
                self.cap.release()
