from communication_handler import sendFrame
from utils import DataFrame,ascii_to_bin
import os
from dotenv import load_dotenv

load_dotenv()

SENDER_IP = str(os.getenv('SENDER_IP'))
SENDER_PORT = str(os.getenv('SENDER_PORT'))
RECEIVER_IP = str(os.getenv('RECEIVER_IP'))
RECEIVER_PORT = str(os.getenv('RECEIVER_PORT'))


sender_addr = (SENDER_IP, SENDER_PORT)
receiver_addr = (RECEIVER_IP, RECEIVER_PORT)
redundant_bit_type = "crc-16"
# Send a file to the receiver
def sendFile(filename):
    with open(filename, 'r') as f:
        data = ascii_to_bin(f.read())
        frames = DataFrame.createFrames(data,sender_addr,receiver_addr,redundant_bit_type)
        number_of_frames = len(frames)
        print(f"Sending {number_of_frames} frames")
        for frame in frames:
            sendFrame(frame.serialize())

if __name__ == "__main__":
    sendFile("input.txt")
