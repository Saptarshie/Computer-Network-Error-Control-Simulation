# utils.py  -- use this exact file (sender_port is 2 bytes / 16 bits)

from error_handler import calculate_crc, verify_crc

# --- Field widths (bits) ---
SENDER_IP_LEN = 32
SENDER_PORT_LEN = 16   # <-- changed to 16 bits (2 bytes)
RECEIVER_IP_LEN = 32
RECEIVER_PORT_LEN = 16
DATA_LEN_LEN = 16
ISLAST_LEN = 1
REDUNDANT_CODE_LEN = 7

# Offsets computed from the widths above (auto-updated)
OFF_SENDER_IP = 0
OFF_SENDER_PORT = OFF_SENDER_IP + SENDER_IP_LEN
OFF_RECEIVER_IP = OFF_SENDER_PORT + SENDER_PORT_LEN
OFF_RECEIVER_PORT = OFF_RECEIVER_IP + RECEIVER_IP_LEN
OFF_DATA_LEN = OFF_RECEIVER_PORT + RECEIVER_PORT_LEN
OFF_ISLAST = OFF_DATA_LEN + DATA_LEN_LEN
OFF_RED_CODE = OFF_ISLAST + ISLAST_LEN
OFF_DATA = OFF_RED_CODE + REDUNDANT_CODE_LEN

# --- Redundancy definitions (CRC polynomials and bit lengths are in BITS) ---
REDUNDANT_BIT_TYPE = {0: "checksum", 1: "crc-8", 2: "crc-10", 3: "crc-16", 4: "crc-32"}
REDUNDANT_BIT_CODE = {
    "checksum": "0000000",
    "crc-8": "0000001",
    "crc-10": "0000010",
    "crc-16": "0000011",
    "crc-32": "0000100",
}
CRC_POLY = {
    "crc-8": "111010101",
    "crc-10": "11000110011",
    "crc-16": "11000000000000101",
    "crc-32": "100000100110000010001110110110111",
}
# NOTE: these are CRC lengths in BITS (not bytes)
REDUNDANT_BITS_CNT = {
    "crc-8": 8,
    "crc-10": 10,
    "crc-16": 16,
    "crc-32": 32,
    "checksum": 16,
}


class DataFrame:
    def __init__(
        self,
        data=None,
        sender_ip=None,
        sender_port=None,
        receiver_ip=None,
        receiver_port=None,
        redundant_bit_type="crc-16",
        padding=0,
        isLast=False,
    ):
        # If constructor called with only one param, treat it as a serialized frame
        if sender_ip is None:
            self.data = data
        else:
            # Build a frame from components
            lastFrame = "1" if isLast else "0"
            # data length encoded as binary bit-field of DATA_LEN_LEN bits
            data_len_field = format(len(data), "0{}b".format(DATA_LEN_LEN))
            self.data = (
                sender_ip
                + sender_port
                + receiver_ip
                + receiver_port
                + data_len_field
                + lastFrame
                + REDUNDANT_BIT_CODE[redundant_bit_type]
                + data
                + "0" * padding
            )
            # append CRC computed over the entire frame so far
            self.data += calculate_crc(self.data, CRC_POLY[redundant_bit_type])

    def getSenderAddr(self):
        # return (sender-ip, sender-port) as bit-strings
        return (self.data[OFF_SENDER_IP:OFF_SENDER_PORT], self.data[OFF_SENDER_PORT:OFF_RECEIVER_IP])

    def getReceiverAddr(self):
        # return (receiver-ip, receiver-port) as bit-strings
        return (self.data[OFF_RECEIVER_IP:OFF_RECEIVER_PORT], self.data[OFF_RECEIVER_PORT:OFF_DATA_LEN])

    def getDatawordLen(self):
        # read DATA_LEN_LEN bits as a binary integer
        return int(self.data[OFF_DATA_LEN:OFF_ISLAST], 2)

    def getRedundantBitType(self):
        code_str = self.data[OFF_RED_CODE:OFF_DATA]
        reverse_code_map = {v: k for k, v in REDUNDANT_BIT_CODE.items()}
        return reverse_code_map.get(code_str, "unknown")

    def isLast(self):
        return self.data[OFF_ISLAST] == "1"

    def serialize(self):
        return self.data

    def getData(self):
        start = OFF_DATA
        end = start + self.getDatawordLen()
        return self.data[start:end]

    def validate(self):
        redundant_bit_type = self.getRedundantBitType()
        if redundant_bit_type == "checksum":
            # TODO: checksum handling if you want it
            return False
        else:
            # Handle unknown redundancy types safely
            if redundant_bit_type not in CRC_POLY:
                print(f"Warning: Unknown redundancy type '{redundant_bit_type}'. Validation failed.")
                return False
            polynomial = CRC_POLY[redundant_bit_type]
            return verify_crc(self.data, polynomial)

    @classmethod
    def createFrames(
        cls, data2send, sender_addr, receiver_addr, redundant_bits_type="crc-16", frame_size=64
    ):
        """
        Create frames respecting bit-field header widths.
        frame_size is in BYTES (typical 64). All internal arithmetic is in BITS.
        """
        # compute header size in BITS explicitly
        header_bits = (
            SENDER_IP_LEN
            + SENDER_PORT_LEN
            + RECEIVER_IP_LEN
            + RECEIVER_PORT_LEN
            + DATA_LEN_LEN
            + ISLAST_LEN
            + REDUNDANT_CODE_LEN
        )

        # CRC bits for chosen redundancy
        crc_bits = REDUNDANT_BITS_CNT[redundant_bits_type]

        # available payload bits per frame
        chunk_size = frame_size * 8 - header_bits - crc_bits
        if chunk_size <= 0:
            raise ValueError("Frame size too small for header + CRC")

        sender_ip, sender_port = sender_addr
        receiver_ip, receiver_port = receiver_addr
        frames = []
        for i in range(0, len(data2send), chunk_size):
            chunk = data2send[i : i + chunk_size]
            padding = "0" * (chunk_size - len(chunk))
            isLast = "0" if i + chunk_size < len(data2send) else "1"
            print("isLast : ", isLast)
            print(
                "sender_ip_len : ",
                len(sender_ip),
                "receiver_ip_len : ",
                len(receiver_ip),
                "sender_port_len : ",
                len(sender_port),
                "receiver_port_len : ",
                len(receiver_port),
                "data_len : ",
                len(chunk),
                "padding_len : ",
                len(padding),
            )
            # encode length in binary with DATA_LEN_LEN bits
            data_len_field = format(len(chunk), "0{}b".format(DATA_LEN_LEN))
            data = (
                sender_ip
                + sender_port
                + receiver_ip
                + receiver_port
                + data_len_field
                + isLast
                + REDUNDANT_BIT_CODE[redundant_bits_type]
                + chunk
                + padding
            )
            data += calculate_crc(data, CRC_POLY[redundant_bits_type])
            print("length : ", len(data))  # printed length is in bits
            frames.append(cls(data))
        return frames


def compare(data1, data2):
    pass  # comparator placeholder


def ascii_to_bin(s: str) -> str:
    """
    Convert a Python string to a continuous binary string using UTF-8 bytes.
    This guarantees each *byte* becomes 8 bits; multi-byte UTF-8 characters expand correctly.
    """
    if s is None or s == "":
        return ""
    b = s.encode("utf-8")
    return "".join(format(byte, "08b") for byte in b)


# convert continuous bitstring -> bytes (pads RIGHT to full bytes)
def bits_to_bytes(bits: str) -> bytes:
    bits = bits.strip().replace(" ", "").replace("\n", "")
    # pad RIGHT to full bytes (sender should avoid this, but be safe)
    pad_len = (-len(bits)) % 8
    if pad_len:
        bits = bits + ("0" * pad_len)
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


# convert bytes -> continuous bitstring "010101..."
def bytes_to_bits(b: bytes) -> str:
    return "".join(format(byte, "08b") for byte in b)

def bin_to_ascii(b: str) -> str:
    """
    Convert continuous binary string to a UTF-8-decoded Python string.
    Undecodable sequences are replaced so this never crashes.
    """
    if b is None or b == "":
        return ""
    data_bytes = bits_to_bytes(b)
    return data_bytes.decode("utf-8", errors="replace")


def hex_to_bin(s: str) -> str:
    """
    Convert a hex string to a continuous binary string (zero-padded, 4 bits per hex digit).
    """
    if s is None:
        raise ValueError("Input cannot be None")

    s = s.strip().lower().replace("_", "").replace(" ", "")
    for sep in (":", "-"):
        s = s.replace(sep, "")
    if s.startswith("0x"):
        s = s[2:]

    if s == "":
        return ""

    try:
        n = int(s, 16)
    except ValueError:
        raise ValueError("Invalid hex string") from None

    width = 4 * len(s)
    return format(n, f"0{width}b")


def bin_to_hex(b: str) -> str:
    """
    Convert a binary string to a hex string (uppercase, zero-padded to full nibbles).
    """
    if b is None:
        raise ValueError("Input cannot be None")

    b = b.strip().replace("_", "").replace(" ", "")
    if b.startswith("0b"):
        b = b[2:]

    if b == "":
        return ""

    if not all(ch in "01" for ch in b):
        raise ValueError("Invalid binary string")

    pad_len = (4 - len(b) % 4) % 4
    b = "0" * pad_len + b

    n = int(b, 2)
    width = len(b) // 4
    return format(n, f"0{width}X")

