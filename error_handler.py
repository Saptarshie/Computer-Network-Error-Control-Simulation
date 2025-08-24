import socket
import sys
import random

def calculate_crc(dataword, polynomial):
    """
    Calculates the CRC for a given dataword and polynomial.
    """
    # Convert strings to lists for mutable operations
    n = len(polynomial)
    padded_data = list(dataword + '0' * (n-1))
    
    # Perform polynomial division
    for i in range(len(dataword)):
        if padded_data[i] == '1':
            for j in range(n):
                padded_data[i+j] = str(int(padded_data[i+j]) ^ int(polynomial[j]))
    
    # Return the CRC remainder
    return ''.join(padded_data)[-n+1:]


def calculate_checksum(data):
    if len(data) % 16 != 0:
        padding_needed = 16 - (len(data) % 16)
        data = '0' * padding_needed + data
        
    words = [data[i:i+16] for i in range(0, len(data), 16)]
    
    total_sum = '0' * 16
    for word in words:
        sum_val = int(total_sum, 2) + int(word, 2)
        if sum_val > 0xFFFF: # Handle carry
            sum_val = (sum_val & 0xFFFF) + 1
        total_sum = format(sum_val, '016b')

    checksum = ''.join('1' if bit == '0' else '0' for bit in total_sum)
    return checksum

def inject_error(codeword,error_type='single'):
    codeword_list = list(codeword)
    length = len(codeword_list)
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
    for i in range(len(codeword) - n + 1):
        if codeword_list[i] == '1':
            for j in range(n):
                codeword_list[i + j] = str(int(codeword_list[i + j]) ^ int(polynomial[j]))

    # The remainder is the last n-1 bits of the result
    remainder = "".join(codeword_list)[-(n-1):]
    print(f"Receiver's CRC Calculation (Remainder): {remainder}")

    # If the remainder contains any '1's, an error is present
    return '1' not in remainder

def verify_checksum(data_with_checksum,redundant_bits_cnt=16):
    data = data_with_checksum[:-redundant_bits_cnt]
    checksum = data_with_checksum[-redundant_bits_cnt:]
    calculated_checksum = calculate_checksum(data)
    return calculated_checksum == checksum