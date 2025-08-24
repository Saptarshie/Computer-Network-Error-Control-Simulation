# test-sender.py
# test-sender.py
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from communication_handler import sendFrame

def test_sender():
    # Test frames to send
    test_frames = [
        "Hello, this is a test frame!",
        "1010101010101010",
        "This is a longer test frame to see if the socket communication works with larger amounts of data.",
        "Final test frame"
    ]
    
    # Give the receiver time to start
    print("Waiting for receiver to start...")
    time.sleep(3)
    
    # Send each test frame
    for i, frame in enumerate(test_frames):
        print(f"\nSending test frame {i+1}: '{frame}'")
        sendFrame(frame)
        # Wait a moment between sends
        time.sleep(1)
    
    print("\nAll test frames sent!")

if __name__ == "__main__":
    test_sender()
