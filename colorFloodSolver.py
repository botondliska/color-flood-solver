import cv2
import numpy as np

board = [[1,3,5,5,1,5,2,5,5,4],
         [5,1,4,4,5,4,3,5,4,1],
         [1,4,3,4,2,3,1,3,2,2],
         [2,5,4,4,1,3,4,5,1,1],
         [2,3,2,2,3,3,2,2,3,3],
         [3,1,3,1,4,4,2,1,4,1],
         [1,2,5,5,4,3,5,4,2,3],
         [3,2,1,3,1,3,1,4,5,5],
         [3,1,3,5,3,1,4,1,4,3],
         [5,1,2,5,5,2,1,4,5,1]]

visited = [[True, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False],
           [False, False, False, False, False, False, False, False, False, False]]

minSolvedDepth = 20

def analyze_color_flood(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from {image_path}")
        
    h, w, _ = img.shape
    rows, cols = 10, 10
    cell_h = h / rows
    cell_w = w / cols
    
    grid_array = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for r in range(rows):
        for c in range(cols):
            y1 = int(r * cell_h) + 5
            y2 = int((r + 1) * cell_h) - 5
            x1 = int(c * cell_w) + 5
            x2 = int((c + 1) * cell_w) - 5
            
            cell_img = img[y1:y2, x1:x2]
            pixels = cell_img.reshape(-1, 3)
            
            valid_pixels = []
            for p in pixels:
                b, g, r_val = p
                if (b > 30 or g > 30 or r_val > 30) and (b < 240 or g < 240 or r_val < 240):
                    valid_pixels.append([r_val, g_val, b])
            
            if len(valid_pixels) == 0:
                grid_array[r][c] = 0
                continue
                
            median_rgb = np.median(valid_pixels, axis=0)
            r_val, g_val, b_val = median_rgb[0], median_rgb[1], median_rgb[2]
            
            if abs(r_val - 74) < 30 and abs(g_val - 144) < 30 and abs(b_val - 226) < 30:
                color_num = 1
            elif abs(r_val - 255) < 30 and abs(g_val - 215) < 30 and abs(b_val - 0) < 30:
                color_num = 2
            elif abs(r_val - 139) < 30 and abs(g_val - 0) < 30 and abs(b_val - 255) < 30:
                color_num = 3
            elif abs(r_val - 255) < 30 and abs(g_val - 107) < 30 and abs(b_val - 107) < 30:
                color_num = 4
            elif abs(r_val - 0) < 30 and abs(g_val - 206) < 30 and abs(b_val - 209) < 30:
                color_num = 5
            else:
                raise ValueError(f"couldn't recognize a color ({x1}-{y1}, {x2}-{y2} )")
                
            grid_array[r][c] = color_num
            
    return grid_array

def get_remaining_colors(board, visited):
    colors = set()
    for i in range(len(board)):
        for j in range(len(board[0])):
            if not visited[i][j]:
                colors.add(board[i][j])
    return len(colors)

def checkAvailableColors(board, visited):
    availableColors = set()
    for i in range(len(board)):
        for j in range(len(board[0])):
            if visited[i][j]:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = i + dr, j + dc
                    if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and not visited[nr][nc]:
                        availableColors.add(board[nr][nc])
    return availableColors

def checkifSolved(visited):
    return all(all(val for val in row) for row in visited)

def apply_color_and_expand(board, visited, color):
    stack = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if visited[i][j]:
                board[i][j] = color
                stack.append((i, j))

    while stack:
        r, c = stack.pop()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                if not visited[nr][nc] and board[nr][nc] == color:
                    visited[nr][nc] = True
                    stack.append((nr, nc))

seen_states = {}

def solve(board, visited, color, steps):
    global minSolvedDepth
    if len(steps) >= minSolvedDepth:
        return

    apply_color_and_expand(board, visited, color)

    state_tuple = tuple(tuple(row) for row in visited)
    if state_tuple in seen_states and seen_states[state_tuple] <= len(steps):
        return
    seen_states[state_tuple] = len(steps)

    if checkifSolved(visited):
        if len(steps) < minSolvedDepth:
            minSolvedDepth = len(steps)
            print(steps, f"({len(steps)})")
            print()
        return
        
    if len(steps) + get_remaining_colors(board, visited) >= minSolvedDepth:
        return

    availableColors = checkAvailableColors(board, visited)
    for c in availableColors:
        next_board = [row[:] for row in board]
        next_visited = [row[:] for row in visited]
        solve(next_board, next_visited, c, steps + [c])

apply_color_and_expand(board, visited, board[0][0])
solve(board, visited, board[0][0], [])