# maze_game.py

import os
# Optional: suppress the Tk deprecation warning on macOS
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import json
import random
import time
import PySimpleGUI as sg
import keyboard

# Turn off PySimpleGUI's built-in icon entirely
sg.set_global_icon(None)

# Pick a theme
sg.theme('DarkBlue3')

# ───────────── CONFIGURATION ─────────────
CELL_SIZE         = 20     # Pixels per cell
MAX_FAILS_PER_MAP = 10     # Max failed attempts per maze
NUM_MAPS          = 5      # Total number of mazes
MAZE_WIDTH        = 41     # Maze width (must be odd)
MAZE_HEIGHT       = 31     # Maze height (must be odd)
HEIGHT            = MAZE_HEIGHT
WIDTH             = MAZE_WIDTH
start_pos         = (1, 1)
exit_pos          = (HEIGHT - 2, WIDTH - 2)

# ─────────── MAZE GENERATOR ────────────
def generate_maze(w, h):
    grid = [[1] * w for _ in range(h)]

    def carve(r, c):
        grid[r][c] = 0
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 < nr < h - 1 and 0 < nc < w - 1 and grid[nr][nc] == 1:
                grid[r + dr // 2][c + dc // 2] = 0
                carve(nr, nc)

    carve(1, 1)
    grid[h - 2][w - 2] = 0  # ensure exit is open
    return grid

# pre-generate all mazes
mazes = [generate_maze(WIDTH, HEIGHT) for _ in range(NUM_MAPS)]

# ─────────── HELPER FUNCTIONS ────────────
def grid_to_pixel(r, c):
    x = c * CELL_SIZE + CELL_SIZE / 2
    y = (HEIGHT - 1 - r) * CELL_SIZE + CELL_SIZE / 2
    return x, y

def animate_move(graph, fig, old_xy, new_xy, steps=8, delay=0.02):
    dx = (new_xy[0] - old_xy[0]) / steps
    dy = (new_xy[1] - old_xy[1]) / steps
    for _ in range(steps):
        graph.MoveFigure(fig, dx, dy)
        window.refresh()
        time.sleep(delay)

def draw_map(graph, map_idx, failed_paths):
    graph.Erase()
    maze = mazes[map_idx]

    # draw walls
    for r in range(HEIGHT):
        for c in range(WIDTH):
            if maze[r][c] == 1:
                x1, y1 = c * CELL_SIZE, (HEIGHT - 1 - r) * CELL_SIZE
                graph.DrawRectangle(
                    (x1, y1),
                    (x1 + CELL_SIZE, y1 + CELL_SIZE),
                    fill_color='black',
                    line_color='black'
                )

    # draw failed paths
    for path in failed_paths[map_idx]:
        pts = [grid_to_pixel(r, c) for r, c in path]
        for i in range(len(pts) - 1):
            graph.DrawLine(pts[i], pts[i + 1], color='red', width=2)

    # draw exit flag
    ex, ey = grid_to_pixel(*exit_pos)
    graph.DrawText('🏁', (ex, ey), font=('Any', int(CELL_SIZE * 0.7)))

    # draw player start
    pr, pc = start_pos
    px, py = grid_to_pixel(pr, pc)
    player_fig = graph.DrawCircle((px, py), CELL_SIZE * 0.3, fill_color='blue')

    return pr, pc, player_fig

# ─────────── SETUP WINDOW ────────────
username = sg.popup_get_text('Enter your username:', 'Maze Game') or 'Anonymous'

graph = sg.Graph(
    canvas_size=(WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE),
    graph_bottom_left=(0, 0),
    graph_top_right=(WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE),
    key='-G-',
    enable_events=False
)
status = sg.Text('', key='-STATUS-')

layout = [
    [status],
    [graph]
]

# One and only one Window call, with icon=None
window = sg.Window(
    'Maze Game',
    layout,
    return_keyboard_events=True,
    finalize=True,
    icon=None
)

# ─────────── INITIALIZE GAME STATE ────────────
map_index      = 0
fail_counts    = [0] * NUM_MAPS
failed_paths   = [[] for _ in range(NUM_MAPS)]
total_attempts = 0

player_row, player_col, player_fig = draw_map(graph, map_index, failed_paths)
current_path = [start_pos]

# ─────────── MAIN GAME LOOP ────────────
while True:
    window['-STATUS-'].update(
        f'Map {map_index+1}/{NUM_MAPS}   '
        f'Fails {fail_counts[map_index]}/{MAX_FAILS_PER_MAP}   '
        f'Total Attempts {total_attempts}'
    )

    event, _ = window.read(timeout=100)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    sprint = keyboard.is_pressed('shift')

    dr = dc = 0
    if keyboard.is_pressed('w'):      dr = -1
    elif keyboard.is_pressed('s'):    dr = +1
    elif keyboard.is_pressed('a'):    dc = -1
    elif keyboard.is_pressed('d'):    dc = +1

    if dr or dc:
        new_r, new_c = player_row + dr, player_col + dc
        maze = mazes[map_index]

        # don’t revisit
        if (new_r, new_c) in current_path:
            time.sleep(0.01 if sprint else 0.05)
            continue

        # valid move?
        if (0 <= new_r < HEIGHT and 0 <= new_c < WIDTH
                and maze[new_r][new_c] == 0):
            old_xy = grid_to_pixel(player_row, player_col)
            player_row, player_col = new_r, new_c
            new_xy = grid_to_pixel(player_row, player_col)

            animate_move(
                graph, player_fig, old_xy, new_xy,
                steps=4 if sprint else 8,
                delay=0.005 if sprint else 0.02
            )

            current_path.append((player_row, player_col))

            # dead-end check
            neighbors = [
                (player_row-1, player_col),
                (player_row+1, player_col),
                (player_row, player_col-1),
                (player_row, player_col+1),
            ]
            free = [
                (r, c) for r, c in neighbors
                if 0 <= r < HEIGHT and 0 <= c < WIDTH and maze[r][c] == 0
            ]
            if len(free) <= 1 and (player_row, player_col) != exit_pos:
                sg.popup('You hit a dead end and were eaten by trolls!', title='Dead End')
                fail_counts[map_index] += 1
                total_attempts += 1
                failed_paths[map_index].append(current_path[:])

                if fail_counts[map_index] >= MAX_FAILS_PER_MAP:
                    sg.popup('Game over, restarting!')
                    map_index = 0
                    fail_counts = [0] * NUM_MAPS
                    total_attempts = 0
                    failed_paths = [[] for _ in range(NUM_MAPS)]

                player_row, player_col, player_fig = draw_map(graph, map_index, failed_paths)
                current_path = [start_pos]

window.close()

