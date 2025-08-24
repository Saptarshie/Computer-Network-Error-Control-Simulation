from communication_handler import sendFrame
from utils import DataFrame,ascii_to_bin,hex_to_bin,bytes_to_bits
import os
from dotenv import load_dotenv

load_dotenv()

SENDER_IP = hex_to_bin(str(os.getenv('SENDER_IP')))
SENDER_PORT = hex_to_bin(str(os.getenv('SENDER_PORT')))
RECEIVER_IP = hex_to_bin(str(os.getenv('RECEIVER_IP')))
RECEIVER_PORT = hex_to_bin(str(os.getenv('RECEIVER_PORT')))


sender_addr = (SENDER_IP, SENDER_PORT)
receiver_addr = (RECEIVER_IP, RECEIVER_PORT)
redundant_bit_type = "crc-16"
# Send a file to the receiver
def sendFile(filename,binary=None):
    """
    Send a file. If filename ends with .bin OR binary==True -> treat as raw bytes.
    Otherwise read as text and encode to UTF-8 bytes before converting to bits.
    """
    # decide binary vs text. explicit `binary` param overrides extension check.
    if binary is None:
        binary = filename.lower().endswith(".bin")

    if binary:
        # open raw bytes
        with open(filename, "rb") as f:
            file_bytes = f.read()
        data_bits = bytes_to_bits(file_bytes)
    else:
        # open text, encode to utf-8 bytes then convert to bits
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
        # Prefer the utf-8-aware ascii_to_bin from earlier:
        data_bits = ascii_to_bin(text)   # ascii_to_bin should encode via utf-8 internally
        file_bytes = text.encode("utf-8")          # <-- raw bytes to write into input.bin
       # Write a binary copy of the input text in UTF-8 
        with open("input.bin", "wb") as fbin:
            fbin.write(file_bytes)                # <-- write bytes, NOT the '0101...' string

    # Optional: debug print lengths
    print(f"Preparing to send file: {filename}  (binary={binary})")
    print("Total payload bits:", len(data_bits))

    frames = DataFrame.createFrames(data_bits, sender_addr, receiver_addr, redundant_bit_type)
    number_of_frames = len(frames)
    print(f"Sending {number_of_frames} frames")
    # print("data to sent : ", data_bits)
    for frame in frames:
        sendFrame(frame.serialize())

if __name__ == "__main__":
    sendFile("input.txt")
