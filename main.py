import tkinter as tk
import random
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
        return "Medium"
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
            tile = canvas.create_rectangle(x,y,x + CELL_SIZE,y + CELL_SIZE,fill="gray")
            tile_row.append(tile)
        tiles.append(tile_row)
def restart_game():
    calculate_board_geometry()
    global board, opened, minesplaced
    global game_active, opened_count
    game_active = True
    opened_count = 0
    board, opened, minesplaced = create_board()
    draw_board()
    place_mines(minesplaced, board)
    update_info()
def click(event):
    if not game_active:
        return
    col = (event.x - OFFSET_X) // CELL_SIZE
    row = (event.y - OFFSET_Y) // CELL_SIZE
    if 0 <= col < size and 0 <= row < size:
        opencell(col, row)
def opencell(col, row):
    global opened_count, game_active
    if not (0 <= col < size and 0 <= row < size) or opened[row][col]:
        return
    opened[row][col] = True  
    opened_count += 1
    draw_cell(row, col)
    value = board[row][col]
    if value == -1:
        game_active = False
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
    return board, opened, minesplaced
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
def draw_cell(row, col):
    value = board[row][col]
    canvas.itemconfig(tiles[row][col], fill="white")
    x = OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
    y = OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
    if value == -1:
        canvas.create_text(x, y, text="X", fill="red")
    elif value > 0:
        color = NUMBER_COLORS[value] if value <= 8 else "black"
        canvas.create_text(x, y, text=str(value), fill=color, font=("Arial", 12, "bold"))
def reveal_all_mines():
    for r in range(size):
        for c in range(size):
            if board[r][c] == -1 and not opened[r][c]:
                opened[r][c] = True
                draw_cell(r, c)
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
restart_game()
window.mainloop()
