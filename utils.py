from error_handler import calculate_crc,verify_crc 

REDUNDANT_BIT_TYPE = { 0: "checksum" , 1: "crc-8" , 2: "crc-10" , 3: "crc-16" , 4: "crc-32" }
REDUNDANT_BIT_CODE = {"checksum": "0000000" , "crc-8": "0000001" , "crc-10": "0000010" , "crc-16": "0000011" , "crc-32": "0000100" }
CRC_POLY =  {
    "crc-8": "111010101",
    "crc-10": "11000110011",
    "crc-16": "11000000000000101",
    "crc-32": "100000100110000010001110110110111"
}
REDUNDANT_BITS_CNT= {
    "crc-8": 8,
    "crc-10": 10,
    "crc-16": 16,
    "crc-32": 32,
    "checksum": 2
}
class DataFrame:
    def __init__(self, data=None, sender_ip=None, sender_port=None, receiver_ip=None, 
             receiver_port=None, redundant_bit_type="crc-16", padding=0, isLast=False):
        if sender_ip is None:
            # Single parameter case
            self.data = data
        else:
            # Multiple parameters case
            lastFrame = "1" if isLast else "0"
            self.data = (sender_ip + sender_port + receiver_ip + receiver_port + 
                        str(len(data)).zfill(8) + lastFrame + 
                        REDUNDANT_BIT_CODE[redundant_bit_type] + data + 
                        "0" * padding)
            self.data += calculate_crc(self.data, CRC_POLY[redundant_bit_type])

    def getSenderAddr(self):
        return (self.data[:32],self.data[32:48]) #return (sender-ip,port)
    def getReceiverAddr(self):
        return (self.data[48:80],self.data[80:96]) #return (receiver-ip,port)
    def getDatawordLen(self):
        return int(self.data[96:104],2) #return dataword-len
    def getRedundantBitType(self):
        return REDUNDANT_BIT_TYPE[int(self.data[105:106],2)] #return redundant-bit-type
    def isLast(self):
        return self.data[104:105] == "1"
    def serialize(self):
        return self.data
    def getData(self):
        return self.data[106:106+self.getDatawordLen()]
    def validate(self):
        redundant_bit_type = self.getRedundantBitType()
        if redundant_bit_type == "checksum":
            pass #com in data1==data2 (for validation)
        else:
            polynomial = CRC_POLY[redundant_bit_type]
            if verify_crc(self.data,polynomial):
                return True
            else:
                return False
        
    @classmethod
    def createFrames(cls, data2send, sender_addr, receiver_addr, redundant_bits_type="crc-16",frame_size=64):

        chunk_size = 8*(frame_size-14-REDUNDANT_BITS_CNT[redundant_bits_type])
        sender_ip,sender_port = sender_addr
        receiver_ip,receiver_port = receiver_addr
        frames = []
        for i in range(0,len(data2send),chunk_size):
            chunk = data2send[i:i+chunk_size]
            padding = "0"*(chunk_size-len(chunk))
            isLast = "0" if i+chunk_size<len(data2send) else "1"
            print("isLast : ",isLast)
            print("sender_ip_len : ",len(sender_ip),"receiver_ip_len : ",len(receiver_ip),"sender_port_len : ",len(sender_port),"receiver_port_len : ",len(receiver_port),"data_len : ",len(chunk),"padding_len : ",len(padding))
            data = sender_ip+sender_port+receiver_ip+receiver_port+str(len(chunk)).zfill(8)+isLast+REDUNDANT_BIT_CODE[redundant_bits_type]+chunk+padding
            data+=calculate_crc(data,CRC_POLY[redundant_bits_type])
            print("length : ",len(data))
            frames.append(cls(data))
        return frames
        
    

def compare(data1,data2):
    pass #com in data1==data2 (for validation)

def ascii_to_bin(s: str) -> str:
    """Convert an ASCII string to its binary representation (8 bits per char)."""
    return ''.join(format(ord(ch), '08b') for ch in s)

def bin_to_ascii(b: str) -> str:
    """Convert a continuous binary string (8 bits per char) to ASCII text."""
    # Ensure length is a multiple of 8
    if len(b) % 8 != 0:
        raise ValueError("Binary string length must be a multiple of 8")
    
    if isinstance(b, bytes):
        return ''.join(format(byte, '08b') for byte in b)
    else:
        return ''.join(format(ord(ch), '08b') for ch in b)


def hex_to_bin(s: str) -> str:
    """
    Convert a hex string to a continuous binary string (zero-padded, 4 bits per hex digit).

    Accepts:
      - Optional '0x' prefix
      - Whitespace/underscores
      - Common separators (':' or '-') e.g., MAC addresses

    Examples:
      hex_to_bin("0x1A3")        -> "000110100011"
      hex_to_bin("1a3")          -> "000110100011"
      hex_to_bin("DE:AD:BE:EF")  -> "11011110101011011011111011101111"
      hex_to_bin("de-ad_be ef")  -> same as above
    """
    if s is None:
        raise ValueError("Input cannot be None")

    # Normalize input
    s = s.strip().lower().replace("_", "").replace(" ", "")
    for sep in (":", "-"):
        s = s.replace(sep, "")
    if s.startswith("0x"):
        s = s[2:]

    if s == "":
        return ""

    # Validate and convert
    try:
        n = int(s, 16)
    except ValueError:
        raise ValueError("Invalid hex string") from None

    # Preserve leading zeros present in the hex by padding to 4*len(s) bits
    width = 4 * len(s)
    return format(n, f"0{width}b")


def bin_to_hex(b: str) -> str:
    """
    Convert a binary string to a hex string (uppercase, zero-padded to full nibbles).

    Accepts:
      - Optional '0b' prefix
      - Whitespace/underscores
      - Grouped bits with spaces or separators

    Examples:
      bin_to_hex("0b000110100011") -> "1A3"
      bin_to_hex("1101111010101101") -> "DEAD"
      bin_to_hex("1101 1110 1010 1101") -> "DEAD"
    """
    if b is None:
        raise ValueError("Input cannot be None")

    # Normalize input
    b = b.strip().replace("_", "").replace(" ", "")
    if b.startswith("0b"):
        b = b[2:]

    if b == "":
        return ""

    # Validate binary
    if not all(ch in "01" for ch in b):
        raise ValueError("Invalid binary string")

    # Pad to multiple of 4 bits for clean hex conversion
    pad_len = (4 - len(b) % 4) % 4
    b = "0" * pad_len + b

    # Convert to hex (uppercase, no '0x')
    n = int(b, 2)
    width = len(b) // 4
    return format(n, f"0{width}X")