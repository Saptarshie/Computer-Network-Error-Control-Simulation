# test-receiver.py
# test-sender.py
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication_handler import receiveFrame

def test_receiver():
    print("Starting receiver test...")
    print("Waiting for frames...")
    
    # We'll try to receive 4 frames (matching the sender test)
    for i in range(4):
        print(f"\nWaiting for frame {i+1}...")
        frame = receiveFrame()
        
        if frame is not None:
            print(f"Received frame {i+1}: '{frame}'")
        else:
            print(f"Failed to receive frame {i+1}")
    
    print("\nReceiver test completed!")

if __name__ == "__main__":
    test_receiver()
