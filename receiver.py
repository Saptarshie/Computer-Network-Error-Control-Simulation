from communication_handler import receiveFrame
from utils import DataFrame,bin_to_ascii
import os
from dotenv import load_dotenv

load_dotenv()

SENDER_IP = str(os.getenv('SENDER_IP'))
SENDER_PORT = str(os.getenv('SENDER_PORT'))
RECEIVER_IP = str(os.getenv('RECEIVER_IP'))
RECEIVER_PORT = str(os.getenv('RECEIVER_PORT'))

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
                receiver_data+= frame.getData()
            if frame.isLast():
                print("Last frame received")
                break
    print("Received data : ",receiver_data)

    receiver_file_name = "receiver.txt"
    with open(receiver_file_name,"w") as f:
        f.write(bin_to_ascii(receiver_data))

if __name__ == "__main__":
    receiver()

