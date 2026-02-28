# RAT-Project: Silent Snake Edition

**Students:** Islam Essa 322521758   Raya Wattad 324883388

## Project Description

This tool simulates a Remote Access Trojan (RAT) disguised as a classic Snake game. It demonstrates how an attacker can use a legitimate-looking application as a "dropper" for a background process that provides full remote command-line access to a victim's machine.

## Required Files
- `snake_rat.py` (The Client/Victim app)
- `server.py` (The Attacker's Control Center)

## Technical Enhancements

In this version, significant improvements were made to ensure stability and cross-platform compatibility:

- **Raw Byte Transmission:** The client captures command output as raw bytes using `subprocess.check_output`, preventing local encoding crashes.
- **CP437 Decoding:** The server uses the cp437 codec (standard for Windows CMD) with a replacement fallback to correctly display symbols (like those in `dir`) without triggering `UnicodeDecodeError`.
- **Persistent Multi-threading:** The game and the RAT connection run on separate threads, ensuring the game remains playable even if the connection fluctuates.

## How to Execute

1. **Start the Server**
   - Run the `server.py` script on the attacker's machine:
     ```bash
     python server.py
     ```
   - The terminal will display: `[*] Server listening on port 9999.`

2. **Configure and Build the Client**
   - **Set the IP:** Open `snake_rat.py` and update the `server_ip` variable with your machine's IPv4 address.
   - **Install PyInstaller:**
     ```bash
     pip install pyinstaller
     ```
   - **Create the Executable:**
     ```bash
     python -m PyInstaller --onefile --noconsole snake_rat.py
     ```

3. **Deployment**
   - Transfer the `snake_rat.exe` from the `dist` folder to the victim's machine.
   - Once executed, the victim sees a functional Snake game with a Restart button.
   - The attacker's server will immediately receive a connection and can begin issuing system commands.

## Code Documentation

### `server.py`
- `xor_crypt(data, key)`: Secures communication using a symmetric XOR cipher.
- `handle_client(client_socket)`: Manages the command loop and handles the specialized CP437 decoding logic to fix character map errors.

### `snake_rat.py`
- `connect_to_server()`: Silently maintains the background socket connection and executes received commands via the system shell.
- `SnakeGame` (class): A complete implementation of the Snake game using `tkinter`, featuring score tracking and a reset mechanism.

## Strengths & Weaknesses

- **Strength – Evasion:** The use of `--noconsole` and threading makes the RAT invisible to the average user while they are playing the game.
- **Strength – Robust Output:** Handles specialized Windows characters (byte 0x8C, etc.) that typically crash basic Python RATs.
- **Weakness – Local Network:** Currently limited to the same LAN unless port forwarding or a VPS is utilized.

## Limitations & Deployment Obstacles

Building a Remote Access Trojan (RAT) disguised as a game involves overcoming several technical and environmental barriers. Below are the primary challenges and constraints encountered during the development of the *Silent Snake Edition* project:

- **Local Network Dependency:** The current architecture is restricted to Local Area Networks (LAN) because home and office routers utilize Network Address Translation (NAT). Without advanced configurations like port forwarding or a Virtual Private Server (VPS), the client cannot reach the Command and Control (C2) server across different external networks.

- **Signature-Based Detection:** Even with the `--noconsole` flag, antivirus software frequently flags PyInstaller executables. These "Generic Trojan" detections occur because the binary bundles a Python interpreter and network socket code, which mimics the behavior of known malware.

- **Operating System Security Layers:** Modern OS features, such as Windows Defender Real-Time Protection, monitor process activity. Even if the file is allowed to run, the antivirus may abruptly kill the process when it detects the background thread attempting to execute system-level commands like `dir` or `ipconfig`.

- **Static IP Requirements:** The client script hardcodes the `server_ip`. If the attacker's machine is assigned a new IP address via DHCP, the "victim" application will fail to establish a connection, requiring a rebuild of the executable or the use of Dynamic DNS (DDNS).
