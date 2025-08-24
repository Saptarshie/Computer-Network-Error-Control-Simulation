# For the sender
def sendFrame(frame):
    """
    Send a frame through socket connection.
    
    Args:
        frame (str): The frame to be sent
    """
    import socket
    
    # Create a socket
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Define receiver address and port
    receiver_address = ('localhost', 12345)
    
    try:
        # Connect to receiver
        sender_socket.connect(receiver_address)
        
        # Send the frame
        sender_socket.sendall(frame.encode())
        print("Frame sent successfully")
        
    except Exception as e:
        print(f"Error sending frame: {e}")
        
    finally:
        # Close the socket
        sender_socket.close()




# For the receiver
def receiveFrame():
    """
    Receive a frame through socket connection.
    
    Returns:
        str: The received frame or None if an error occurred
    """
    import socket
    
    # Create a socket
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Define server address and port
    server_address = ('localhost', 12345)
    
    try:
        # Bind the socket to the address and port
        receiver_socket.bind(server_address)
        
        # Listen for incoming connections
        receiver_socket.listen(1)
        print("Waiting for connection...")
        
        # Accept a connection
        connection, client_address = receiver_socket.accept()
        print("Connection established with", client_address)
        
        try:
            # Receive the frame
            frame = connection.recv(4096).decode()
            print("Frame received")
            return frame
            
        except Exception as e:
            print(f"Error receiving frame: {e}")
            return None
            
        finally:
            # Close the connection
            connection.close()
            
    except Exception as e:
        print(f"Error setting up receiver: {e}")
        return None
        
    finally:
        # Close the socket
        receiver_socket.close()
