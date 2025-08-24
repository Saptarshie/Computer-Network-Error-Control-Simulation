"""
Streamlit Dashboard for Error Detection Assignment

Place this file in the same folder as your provided project files
(error_handler.py, utils.py, sender.py, receiver.py, communication_handler.py).

Run:
    streamlit run streamlit_dashboard.py

Features:
- Accept input as raw bits string, uploaded file (text or binary) or typed text
- Choose one or more error-detection protocols (checksum, crc-8/10/16/32)
- Choose one or more error types (single-bit, two isolated, odd (3), burst)
- Provide custom bit positions (comma-separated) to flip
- Run tests and view results per-frame and aggregated
- Download corrupted frames or view binary/ASCII

Note: the dashboard uses your project's functions (DataFrame.createFrames,
calculate_crc/verify_crc, calculate_checksum/verify_checksum, inject_error).
If your local environment has different function names, adapt imports accordingly.
"""

import streamlit as st
import io
import os
import textwrap
from typing import List, Tuple, Dict, Any

# Import user's modules (these must be in the same directory)
from utils import DataFrame, ascii_to_bin, bytes_to_bits, bits_to_bytes, bin_to_ascii
from error_handler import inject_error, verify_crc, verify_checksum
import utils

# ---------------------------------------------------------------------------
# Utility helpers inside the dashboard (keeps user's code unchanged)
# ---------------------------------------------------------------------------

def flip_bits(bitstring: str, positions: List[int]) -> str:
    """Flip bits at given integer positions in a binary string.
    Positions are 0-based from the leftmost bit (index 0).
    If a position is out-of-range it is ignored.
    """
    if not bitstring:
        return bitstring
    bits = list(bitstring)
    L = len(bits)
    for pos in positions:
        if 0 <= pos < L:
            bits[pos] = "1" if bits[pos] == "0" else "0"
    return "".join(bits)


def parse_positions(text: str) -> List[int]:
    """Parse comma/space separated numbers into list of ints."""
    if not text:
        return []
    cleaned = text.replace(";", ",").replace(" ", ",")
    parts = [p.strip() for p in cleaned.split(",") if p.strip() != ""]
    out = []
    for p in parts:
        try:
            out.append(int(p))
        except Exception:
            continue
    return sorted(set(out))


def read_uploaded_file(uploaded_file) -> Tuple[str, bool]:
    """Return (bits_string, binary_flag). If file is text we encode utf-8 else treat as bytes."""
    raw = uploaded_file.read()
    # Try decode as utf-8 text
    try:
        s = raw.decode("utf-8")
        return (ascii_to_bin(s), False)
    except Exception:
        # treat as binary
        return (bytes_to_bits(raw), True)


# Map UI label -> inject_error type
ERROR_TYPE_MAP = {
    "Single-bit error": "single",
    "Two isolated single-bit errors": "two_isolated",
    "Odd number of errors (3 bits)": "odd",
    "Burst error": "burst",
}

# Friendly names for redundant bit types (use keys from utils)
AVAILABLE_PROTOCOLS = list(utils.REDUNDANT_BITS_CNT.keys())  # e.g. checksum, crc-8, ...

# Default addresses (32-bit IP, 16-bit port) used when creating frames
DEFAULT_SENDER_IP = "0" * utils.SENDER_IP_LEN
DEFAULT_SENDER_PORT = "0" * utils.SENDER_PORT_LEN
DEFAULT_RECEIVER_IP = "0" * utils.RECEIVER_IP_LEN
DEFAULT_RECEIVER_PORT = "0" * utils.RECEIVER_PORT_LEN


# ---------------------------------------------------------------------------
# Core processing: create frames, inject errors, validate
# ---------------------------------------------------------------------------

def process_frame_case(frame_bits: str, protocol: str, error_type_key: str, custom_positions: List[int]) -> Dict[str, Any]:
    """Given a serialized frame bits string (already with CRC/checksum appended by createFrames),
    apply the requested error (either built-in or custom) and validate it.

    Returns a dictionary with original, corrupted, detected (bool), remainder (for CRC),
    flipped positions, redundant bit type and the **received** data interpretation (bits, raw bytes, attempted UTF-8 text).
    """
    original = frame_bits

    # Create corrupted version
    if error_type_key == "Custom positions":
        corrupted = flip_bits(original, custom_positions)
        flipped_positions = custom_positions
    else:
        # map label -> inject_error mode (error_handler.inject_error expects 'single','two_isolated','odd','burst')
        inject_mode = ERROR_TYPE_MAP.get(error_type_key)
        if inject_mode is None:
            # fallback: treat as single
            inject_mode = "single"
        corrupted = inject_error(original, error_type=inject_mode)
        # inject_error prints flipped positions but does not return them. We will detect them by comparing strings.
        flipped_positions = [i for i in range(len(original)) if original[i] != corrupted[i]]

    # Validate using utils.DataFrame.validate()
    try:
        original_df = DataFrame(original)
        corrupted_df = DataFrame(corrupted)
        # The DataFrame.validate() returns True when frame is considered valid (i.e., no error detected)
        original_valid = original_df.validate()
        corrupted_valid = corrupted_df.validate()
    except Exception as e:
        return {
            "original": original,
            "corrupted": corrupted,
            "detected": True,
            "error": f"Exception during validation: {e}",
            "flipped_positions": flipped_positions,
            "received": {"bits": corrupted, "bytes": None, "text": None},
        }

    detected = not corrupted_valid  # if corrupted frame is invalid -> error detected

    # Try to compute CRC remainder if protocol is CRC
    remainder = None
    note = ""
    red_type = corrupted_df.getRedundantBitType()
    if red_type.startswith("crc"):
        try:
            # verify_crc prints remainder inside error_handler, but we'll also compute it here by calling verify_crc
            # verify_crc expects codeword and polynomial; utils.CRC_POLY contains polynomial strings
            polynomial = utils.CRC_POLY.get(red_type)
            if polynomial:
                crc_ok = verify_crc(corrupted, polynomial)
                remainder = "OK" if crc_ok else "NONZERO_REMAINDER"
        except Exception:
            remainder = None

    # For checksum we can show if verify_checksum passes
    if red_type == "checksum":
        try:
            checksum_ok = verify_checksum(corrupted)
            remainder = "OK" if checksum_ok else "NONZERO_CHECKSUM"
        except Exception:
            remainder = None

    # Build received-data: try to produce bytes and attempt UTF-8 decode for user-friendly display
    try:
        received_bytes = bits_to_bytes(corrupted)
        try:
            received_text = received_bytes.decode('utf-8')
        except Exception:
            # not valid UTF-8
            received_text = None
        received = {
            "bits": corrupted,
            "bytes": received_bytes,
            "text": received_text,
        }
    except Exception:
        received = {"bits": corrupted, "bytes": None, "text": None}

    return {
        "original": original,
        "corrupted": corrupted,
        "detected": detected,
        "remainder": remainder,
        "flipped_positions": flipped_positions,
        "red_type": red_type,
        "received": received,
    }


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Error Detection Playground", layout="wide")
st.title("📡 Error Detection — Checksum & CRC Playground")
st.markdown(
    "Use this interactive dashboard to test how checksum and different CRC polynomials detect various error types. Upload data or paste text/bits, choose protocols and error types, and run simulations per-frame."
)

# Input area
with st.sidebar:
    st.header("Input data")
    input_mode = st.radio("Choose how to provide input:", ["Text / Bits", "Upload file"], index=0)

    data_bits = ""
    binary_file = False
    if input_mode == "Text / Bits":
        raw_text = st.text_area("Type text (will be UTF-8 encoded) or paste a bit-string (010101...).", height=160)
        bits_radio = st.radio("Interpreting input as:", ["Text (UTF-8)", "Bit-string (0/1)"])
        if raw_text:
            if bits_radio.startswith("Text"):
                data_bits = ascii_to_bin(raw_text)
            else:
                # sanitize bit-string
                data_bits = "".join(ch for ch in raw_text if ch in "01")
    else:
        uploaded = st.file_uploader("Upload a file (text or binary).", type=None)
        if uploaded is not None:
            data_bits, binary_file = read_uploaded_file(uploaded)
            st.success(f"Loaded {uploaded.name} — inferred {'binary' if binary_file else 'text'} file")

    st.markdown("---")
    st.header("Frame & Address settings")
    frame_size = st.number_input("Frame size (bytes)", min_value=32, max_value=1500, value=64)
    st.text("(Header uses project's field widths; frame payload will be split accordingly.)")

    # Let user optionally set IP/Port fields (bitstrings or defaults)
    use_custom_addr = st.checkbox("Use custom sender/receiver addresses (provide as hex) ", value=False)
    if use_custom_addr:
        sender_ip_hex = st.text_input("Sender IP (hex, e.g. 0A0B0C0D)", value="0")
        sender_port_hex = st.text_input("Sender port (hex, 2 bytes)", value="0")
        receiver_ip_hex = st.text_input("Receiver IP (hex)", value="0")
        receiver_port_hex = st.text_input("Receiver port (hex)", value="0")
        try:
            sender_addr = (utils.hex_to_bin(sender_ip_hex).zfill(utils.SENDER_IP_LEN), utils.hex_to_bin(sender_port_hex).zfill(utils.SENDER_PORT_LEN))
            receiver_addr = (utils.hex_to_bin(receiver_ip_hex).zfill(utils.RECEIVER_IP_LEN), utils.hex_to_bin(receiver_port_hex).zfill(utils.RECEIVER_PORT_LEN))
        except Exception:
            st.error("Invalid hex for address fields — falling back to defaults.")
            sender_addr = (DEFAULT_SENDER_IP, DEFAULT_SENDER_PORT)
            receiver_addr = (DEFAULT_RECEIVER_IP, DEFAULT_RECEIVER_PORT)
    else:
        sender_addr = (DEFAULT_SENDER_IP, DEFAULT_SENDER_PORT)
        receiver_addr = (DEFAULT_RECEIVER_IP, DEFAULT_RECEIVER_PORT)

    st.markdown("---")
    st.header("Protocol & Error choices")
    protocols = st.multiselect("Error detection protocols (choose one or more):", AVAILABLE_PROTOCOLS, default=["crc-16"])

    error_choices = list(ERROR_TYPE_MAP.keys())
    error_choices.append("Custom positions")
    error_types_selected = st.multiselect("Error types to inject (choose one or more):", error_choices, default=["Single-bit error"]) 

    custom_positions_text = st.text_input("If using Custom positions — enter comma-separated bit indices (0-based):", value="")
    custom_positions = parse_positions(custom_positions_text)

    run_button = st.button("Run simulation")

# Main area: results
if "" == data_bits:
    st.info("No input data yet — paste text/bits or upload a file from the left sidebar.")
else:
    st.markdown("### Input summary")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"Input length: **{len(data_bits)} bits**")
        example_preview = data_bits[:256] + ("..." if len(data_bits) > 256 else "")
        st.text_area("Preview (first 256 bits):", value=example_preview, height=120)
    with col2:
        st.write("Frame size:", frame_size, "bytes")
        st.write("Selected protocols:", protocols)
    with col3:
        st.write("Selected error types:")
        for e in error_types_selected:
            st.write("-", e)

    if run_button:
        if not protocols:
            st.error("Please select at least one protocol.")
        elif not error_types_selected:
            st.error("Please select at least one error type.")
        else:
            st.success("Running simulation — this may take a moment depending on data length and frame count.")

            # Build results container
            results = []

            for protocol in protocols:
                # create frames for this protocol
                try:
                    frames = DataFrame.createFrames(data_bits, sender_addr, receiver_addr, redundant_bits_type=protocol, frame_size=frame_size)
                except Exception as e:
                    st.error(f"Failed to create frames for protocol {protocol}: {e}")
                    continue

                st.markdown(f"#### Protocol: `{protocol}` — {len(frames)} frame(s) created")

                # For each error type apply to each frame and record
                protocol_table_rows = []
                for err in error_types_selected:
                    for fi, frame_obj in enumerate(frames):
                        frame_bits = frame_obj.serialize()
                        # choose positions to flip (if custom) -- note these positions are relative to the whole serialized frame
                        positions_for_case = custom_positions if err == "Custom positions" else []

                        res = process_frame_case(frame_bits, protocol, err, positions_for_case)
                        # Add additional metadata
                        res_row = {
                            "protocol": protocol,
                            "frame_index": fi,
                            "error_type": err,
                            "detected": res.get("detected"),
                            "flipped_positions": res.get("flipped_positions"),
                            "remainder": res.get("remainder"),
                            "corrupted_length": len(res.get("corrupted", "")),
                        }
                        protocol_table_rows.append(res_row)

                        # Show a collapsible detail for the first few frames to avoid noise
                        if fi < 4:
                            with st.expander(f"Protocol={protocol} | Frame={fi} | Error={err} | Detected={res_row['detected']}"):
                                st.write("**Flipped positions**:", res_row["flipped_positions"]) 
                                st.write("**Remainder/Checksum status**:", res_row["remainder"]) 
                                st.write("Original (first 256 bits):")
                                st.code(res.get("original")[:256] + ("..." if len(res.get("original")) > 256 else ""))
                                st.write("Corrupted (first 256 bits):")
                                st.code(res.get("corrupted")[:256] + ("..." if len(res.get("corrupted")) > 256 else ""))
                                # Download links
                                b_io = io.BytesIO(bits_to_bytes(res.get("corrupted")))
                                st.download_button(label="Download corrupted frame as bytes", data=b_io.getvalue(), file_name=f"corrupted_{protocol}_frame{fi}_{err}.bin")

                # aggregated dataframe for protocol
                st.markdown(f"**Summary table for {protocol}**")
                import pandas as pd

                df = pd.DataFrame(protocol_table_rows)
                if not df.empty:
                    # aggregate counts
                    total_cases = len(df)
                    detected_cases = df["detected"].sum()
                    undetected_cases = total_cases - detected_cases
                    st.write(f"Total cases: {total_cases} — Detected: {detected_cases} — Undetected: {undetected_cases}")
                    st.dataframe(df)
                else:
                    st.write("No rows for this protocol (something went wrong).")

            st.success("Simulation complete.")

    else:
        st.info("Configure options in the sidebar and press **Run simulation**.")


st.markdown("---")
st.caption("Built for the CSE lab assignment. Let me know if you want extra features: visual bitmaps of frames, per-bit heatmap, or automatic case-finding where checksum detects but CRC doesn't (I can add that!).")
