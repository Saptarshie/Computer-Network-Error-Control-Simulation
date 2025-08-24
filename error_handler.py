import socket
import sys
import random

# Define 48-bit sender and receiver addresses
SENDER_ADDR = '110011001100110011001100110011001100110011001100'
RECEIVER_ADDR = '001100110011001100110011001100110011001100110011'

def hex_to_binary(hex_str):
    """Converts a hexadecimal string to a binary string."""
    try:
        return bin(int(hex_str, 16))[2:]
    except ValueError:
        return None

def calculate_crc(dataword, polynomial):
    """
    Calculates the CRC for a given dataword and polynomial.
    """
    # --- Step 1: Append n-1 zeros to the dataword ---
    # n is the length of the polynomial (number of bits)
    n = len(polynomial)
    padded_data = dataword + '0' * (n - 1)
    padded_data_list = list(padded_data)

    # --- Step 2: Perform polynomial division (XOR operations) ---
    for i in range(len(dataword)):
        # If the current bit is '1', perform XOR
        if padded_data_list[i] == '1':
            for j in range(n):
                # XOR the current data segment with the polynomial
                padded_data_list[i + j] = str(int(padded_data_list[i + j]) ^ int(polynomial[j]))

    # --- Step 3: The remainder is the CRC code ---
    crc_code = "".join(padded_data_list)[-n+1:]
    return crc_code

def inject_error(codeword):
    codeword_list = list(codeword)
    length = len(codeword_list)

    error_type = input("Select error type (single, two_isolated, odd, burst): ")
    print(f"\nInjecting a '{error_type}' error...")
    if error_type == 'single':
        pos = random.randint(0, length - 1)
        codeword_list[pos] = '1' if codeword_list[pos] == '0' else '0'
        print(f"Flipping bit at position {pos}")

    elif error_type == 'two_isolated':
        pos1 = random.randint(0, length - 1)
        pos2 = random.randint(0, length - 1)
        while pos1 == pos2: 
            pos2 = random.randint(0, length - 1)
        
        codeword_list[pos1] = '1' if codeword_list[pos1] == '0' else '0'
        codeword_list[pos2] = '1' if codeword_list[pos2] == '0' else '0'
        print(f"Flipping bits at positions {pos1} and {pos2}")

    elif error_type == 'odd':
        num_errors = 3
        positions = random.sample(range(length), num_errors)
        for pos in positions:
            codeword_list[pos] = '1' if codeword_list[pos] == '0' else '0'
        print(f"Flipping bits at positions {sorted(positions)}")

    elif error_type == 'burst':
        burst_length = random.randint(2, 6)
        start_pos = random.randint(0, length - burst_length)
        
        for i in range(start_pos, start_pos + burst_length):
            codeword_list[i] = '1' if codeword_list[i] == '0' else '0'
        print(f"Flipping a burst of {burst_length} bits from position {start_pos}")
    
    return "".join(codeword_list)

def verify_crc(codeword, polynomial):
    n = len(polynomial)
    codeword_list = list(codeword)
    for i in range(len(codeword) - (n - 1)):
        if codeword_list[i] == '1':
            for j in range(n):
                codeword_list[i + j] = str(int(codeword_list[i + j]) ^ int(polynomial[j]))

    # The remainder is the last n-1 bits of the result
    remainder = "".join(codeword_list)[-(n-1):]
    print(f"Receiver's CRC Calculation (Remainder): {remainder}")
    
    # If the remainder contains any '1's, an error is present
    return '1' not in remainder