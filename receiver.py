from communication_handler import receiveFrame
from utils import DataFrame,bin_to_ascii,hex_to_bin,bits_to_bytes
import os
from dotenv import load_dotenv

load_dotenv()

SENDER_IP = hex_to_bin(str(os.getenv('SENDER_IP')))
SENDER_PORT = hex_to_bin(str(os.getenv('SENDER_PORT')))
RECEIVER_IP = hex_to_bin(str(os.getenv('RECEIVER_IP')))
RECEIVER_PORT = hex_to_bin(str(os.getenv('RECEIVER_PORT')))

def receiver():
    receiver_data = ""
    while True:
        res = receiveFrame()
        if res is not None:
            frame = DataFrame(res)
            if frame.validate():
                print("Valid frame received : ",frame.getData())
                receiver_data += frame.getData()
            else:
                print("Error: Invalid frame received : ",frame.getData())
                # receiver_data+= frame.getData()
            print("isLast : ",frame.isLast())
            if frame.isLast():
                print("Last frame received")
                break
    print("Received data : ",receiver_data)
    print("Data length : ",len(receiver_data))
    # convert and write raw bytes
    data_bytes = bits_to_bytes(receiver_data)
    # raw bytes
    with open("receiver.bin", "wb") as fbin:
        fbin.write(data_bytes)

    # readable text (utf-8, replacing invalid sequences)
    with open("receiver.txt", "w", encoding="utf-8") as ftxt:
        ftxt.write(data_bytes.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    receiver()

