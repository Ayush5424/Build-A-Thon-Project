import asyncio
import websockets
import cv2
import numpy as np
import base64
import gesture_engine  # this imports your gesture_engine.py file

async def handle_connection(websocket):
    """
    Handles a single WebSocket connection.
    Receives video frames, processes them, and sends back gestures.
    """
    print("✅ Client connected.")
    try:
        async for message in websocket:
            # Each message is a base64 JPEG (data URL)
            if "," in message:
                _, encoded = message.split(",", 1)
            else:
                encoded = message

            # Decode frame
            img_bytes = base64.b64decode(encoded)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Detect gesture
            gesture_name = gesture_engine.get_gesture(frame)

            # If valid gesture detected
            if gesture_name:
                print(f"🤖 Detected Gesture: {gesture_name}")
                await websocket.send(gesture_name)

    except websockets.ConnectionClosed:
        print("❌ Client disconnected.")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        print("🔚 Connection handler finished.")


async def main():
    """
    Starts the WebSocket server using new websockets API (v15+)
    """
    host = "localhost"
    port = 8765
    print(f"🚀 WebSocket server running at ws://{host}:{port}")
    async with websockets.serve(handle_connection, host, port, max_size=1_000_000):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
