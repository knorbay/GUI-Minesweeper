import tkinter as tk
import random
import subprocess
import os
from PIL import Image, ImageTk
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def play_sound(relative_path, volume=0.3):
    sound_path = os.path.join(BASE_DIR, relative_path)
    if os.path.exists(sound_path):
        subprocess.Popen(["afplay", "-v", str(volume), sound_path])
    else:
        print(f"Sound dosent exits: {sound_path}")
size = 8
NUMBER_COLORS = [
    "",
    "blue",
    "green",
    "red",
    "purple",
    "maroon",
    "cyan",
    "black",
    "gray"
]
CELL_SIZE = 48
GRID_SIZE = 0
OFFSET_X = 0
OFFSET_Y = 0
game_active = True
total_mines = 0
opened_count = 0
def get_difficulty_name():
    if size == 8:
        return "Easy"
    elif size == 12:
        return "Meduim"
    else:
        return "Hard"
def set_difficulty(new_size):
    global size
    size = new_size 
    restart_game()
def calculate_board_geometry():
    global CELL_SIZE, GRID_SIZE, OFFSET_X, OFFSET_Y

    CELL_SIZE = min(560 // size, 48)

    GRID_SIZE = CELL_SIZE * size

    OFFSET_X = (600 - GRID_SIZE) // 2
    OFFSET_Y = (600 - GRID_SIZE) // 2
def draw_board():
    global tiles
    canvas.delete("all")
    tiles = []
    for row in range(size):
        tile_row = []
        for col in range(size):
            x = OFFSET_X + col * CELL_SIZE
            y = OFFSET_Y + row * CELL_SIZE
            tile = canvas.create_rectangle(x,y,x + CELL_SIZE,y + CELL_SIZE,fill="#bdbdbd",outline="#8a8a8a",width=2)
            tile_row.append(tile)
        tiles.append(tile_row)
def restart_game():
    calculate_board_geometry()
    load_images()
    global board, opened, minesplaced
    global game_active, opened_count,flags
    game_active = True
    opened_count = 0
    board, opened, minesplaced, flags = create_board()
    draw_board()
    place_mines(minesplaced, board)
    update_info()
def click(event):
    if not game_active:
        return
    col = (event.x - OFFSET_X) // CELL_SIZE
    row = (event.y - OFFSET_Y) // CELL_SIZE
    if 0 <= col < size and 0 <= row < size:
        if not opened[row][col] and not flags[row][col]:
            if board[row][col] != -1:
                play_sound("assets/sounds/opencell_sound.mp3", volume=0.4)
        opencell(col, row)
def opencell(col, row):
    global opened_count, game_active
    if not (0 <= col < size and 0 <= row < size) or opened[row][col]:
        return
    if flags[row][col]:
        return
    opened[row][col] = True  
    opened_count += 1
    draw_cell(row, col)
    value = board[row][col]
    if value == -1:
        game_active = False
        show_explosion(row, col)
        reveal_all_mines()
        return
    if value == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                opencell(col + dc, row + dr)
    if game_active:
        check_win()
def create_board():
    board = [[0] * size for _ in range(size)]
    opened = [[False] * size for _ in range(size)]
    minesplaced = [[False] * size for _ in range(size)]
    flags=[[False] * size for _ in range(size)]
    return board, opened, minesplaced , flags
def check_win():
    global game_active
    safe_cells = (size * size) - total_mines
    if opened_count == safe_cells:
        game_active = False
        reveal_all_mines()
        canvas.create_text(
        GRID_SIZE//2,
        GRID_SIZE//2,
        text="KAZANDIN!",
        fill="green",
        font=("Arial",20,"bold")

)
def draw_flag(row, col):
    x = OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
    y = OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

    canvas.delete(f"flag_{row}_{col}")

    if flags[row][col]:
        play_sound("assets/sounds/flag_sound.mp3",volume=0.2)
        canvas.create_image(
            x,
            y,
            image=flag_image,
            tags=f"flag_{row}_{col}"
        )
def draw_cell(row, col):
    canvas.delete(f"flag_{row}_{col}")
    value = board[row][col]
    canvas.itemconfig(tiles[row][col], fill="white")
    x = OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
    y = OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
    if value == -1:
        canvas.create_image(
        x,
        y,
        image=bomb_image
    )
    elif value > 0:
        color = NUMBER_COLORS[value] if value <= 8 else "black"
        canvas.create_text(x, y, text=str(value), fill=color, font=("Arial", 12, "bold"))
def reveal_all_mines():

    mines = []

    for r in range(size):
        for c in range(size):

            if board[r][c] == -1 and not opened[r][c]:
                mines.append((r, c))
    if mines:
        window.after(250, lambda: reveal_next_mine(mines, 0))
    reveal_next_mine(mines, 0)
def reveal_next_mine(mines, index):

    if index >= len(mines):
        return
    r, c = mines[index]
    opened[r][c] = True
    draw_cell(r, c)
    show_explosion(r, c)
    if index % 2 == 0:
        play_sound("assets/sounds/explosion.mp3", volume=0.4)
    window.after(
        120,
        lambda: reveal_next_mine(mines, index + 1)
    )
def place_mines(minesplaced, board):
    global total_mines
    if size == 8:
        total_mines = random.randint(size+2,size+4)
    elif size == 12:
        total_mines = random.randint(size+10,size+16)
    else:
        total_mines = random.randint(size+20,size+24)
    placed = 0
    while placed < total_mines:
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        if not minesplaced[r][c]:
            minesplaced[r][c] = True
            board[r][c] = -1  
            placed += 1
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] != -1:
                        board[nr][nc] += 1
def update_info():
    info_label.config(
        text=f"Difficulty: {get_difficulty_name()}   Mines: {total_mines}"
    )
def right_click(event):
    if not game_active:
        return
    col = (event.x - OFFSET_X) // CELL_SIZE
    row = (event.y - OFFSET_Y) // CELL_SIZE
    if not (0 <= row < size and 0 <= col < size):
        return
    if opened[row][col]:
        return
    flags[row][col] = not flags[row][col]

    draw_flag(row, col)
def load_images():
    global bomb_image, flag_image, explosion_image

    bomb = Image.open("assets/bomb.png")
    bomb = bomb.resize((CELL_SIZE - 8, CELL_SIZE - 8))
    bomb_image = ImageTk.PhotoImage(bomb)

    flag = Image.open("assets/flag.png")
    flag = flag.resize((CELL_SIZE - 8, CELL_SIZE - 8))
    flag_image = ImageTk.PhotoImage(flag)

    explosion = Image.open("assets/explosion.png")
    explosion = explosion.resize((CELL_SIZE , CELL_SIZE )) 
    explosion_image = ImageTk.PhotoImage(explosion)
def show_explosion(row, col):
    x = OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
    y = OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
    explosion = canvas.create_image(
        x,
        y,
        image=explosion_image
    )
    window.after(
        300,
        lambda: canvas.delete(explosion)
    )
window = tk.Tk()
window.title("MineSweeper")
window.geometry("900x670")
window.resizable(False, False)
top_frame = tk.Frame(window, bg="lightgray", pady=10)
top_frame.pack(fill=tk.X)
btn_restart = tk.Button(top_frame, text="Restart", command=restart_game, bg="white")
btn_restart.pack(side=tk.LEFT, padx=20)
btn_hard = tk.Button(top_frame, text="Hard (16x16)", command=lambda: set_difficulty(16))
btn_hard.pack(side=tk.RIGHT, padx=5)
btn_medium = tk.Button(top_frame, text="Medium (12x12)", command=lambda: set_difficulty(12))
btn_medium.pack(side=tk.RIGHT, padx=5)
btn_easy = tk.Button(top_frame, text="Easy (8x8)", command=lambda: set_difficulty(8))
btn_easy.pack(side=tk.RIGHT, padx=20)
info_label = tk.Label(
    top_frame,
    text="",
    bg="lightgray",
    font=("Arial", 11, "bold")
)
game_frame = tk.Frame(window)
game_frame.pack(expand=True)
canvas = tk.Canvas(game_frame, width=600, height=600)
canvas.pack()
info_label.pack(side=tk.LEFT, padx=20)
canvas.bind("<Button-1>", click)
canvas.bind("<Button-3>",right_click)
restart_game()
window.mainloop()
