import numpy
import random
import time
from PIL import Image

# Careful with stack overflows
import sys
import resource
sys.setrecursionlimit(500000)
resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))

h, w = 100, 100
zoom_scale = 10
live_drawing = True
frames_skipped=0


if (w % 2) == 0 :
    w -= 1
if (h % 2) == 0 :
    h -= 1

color = [random.randint(40, 255), random.randint(40, 255), random.randint(40, 255)]
maze_numpy = numpy.zeros((w, h, 3), dtype=numpy.uint8)

if live_drawing:
    import pygame
    pygame.init()
    if zoom_scale == 1:
        screen = pygame.display.set_mode((w, h))  # , pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((w * zoom_scale, h * zoom_scale))  # , pygame.RESIZABLE)
    surf = pygame.surfarray.make_surface(maze_numpy)
    pygame.display.set_caption("Maze generator")

def go_next(direction:str, x:int, y:int) -> str:
    choices = ['left', 'right', 'up', 'down']
    if direction == "left": choices.remove('right')
    if direction == "right": choices.remove('left')
    if direction == "up": choices.remove('down')
    if direction == "down": choices.remove('up')

    # Removing if target is white already
    if y-1 > 0 and numpy.count_nonzero(maze_numpy[x][y-1]):
        if choices.count('up'): choices.remove('up')
    if y+1 < len(maze_numpy[0])-1 and numpy.count_nonzero(maze_numpy[x][y+1]):
        if choices.count('down'): choices.remove('down')
    if x+1 < len(maze_numpy)-1 and numpy.count_nonzero(maze_numpy[x+1][y]):
        if choices.count('right'): choices.remove('right')
    if x-1 > 0 and numpy.count_nonzero(maze_numpy[x-1][y]):
        if choices.count('left'): choices.remove('left')

    # Being GRIDY
    if not x%2:
        if choices.count('up'): choices.remove('up')
        if choices.count('down'): choices.remove('down')
    if not y % 2:
        if choices.count('right'): choices.remove('right')
        if choices.count('left'): choices.remove('left')



    if (x-2 < 0
        or y+1 > len(maze_numpy[0])-1
        or y-1 < 0
        or numpy.count_nonzero(maze_numpy[x-2][y])
        or numpy.count_nonzero(maze_numpy[x-2][y+1])
        or numpy.count_nonzero(maze_numpy[x-2][y-1])
        or numpy.count_nonzero(maze_numpy[x-1][y+1])
        or numpy.count_nonzero(maze_numpy[x-1][y-1])):
        if choices.count('left'): choices.remove('left')
    if (x+2 > len(maze_numpy)-1
        or y+1 > len(maze_numpy[0])-1
        or y-1 < 0
        or numpy.count_nonzero(maze_numpy[x+2][y])
        or numpy.count_nonzero(maze_numpy[x+2][y+1])
        or numpy.count_nonzero(maze_numpy[x+2][y-1])
        or numpy.count_nonzero(maze_numpy[x+1][y+1])
        or numpy.count_nonzero(maze_numpy[x+1][y-1])):
        if choices.count('right'): choices.remove('right')
    if (y-2 < 0
        or x+1 > len(maze_numpy)-1
        or x-1 < 0
        or numpy.count_nonzero(maze_numpy[x][y-2])
        or numpy.count_nonzero(maze_numpy[x+1][y-2])
        or numpy.count_nonzero(maze_numpy[x-1][y-2])
        or numpy.count_nonzero(maze_numpy[x+1][y-1])
        or numpy.count_nonzero(maze_numpy[x-1][y-1])):
        if choices.count('up'): choices.remove('up')
    if (y+2 > len(maze_numpy[0])-1
        or x+1 > len(maze_numpy)-1
        or x-1 < 0
        or numpy.count_nonzero(maze_numpy[x][y+2])
        or numpy.count_nonzero(maze_numpy[x+1][y+2])
        or numpy.count_nonzero(maze_numpy[x-1][y+2])
        or numpy.count_nonzero(maze_numpy[x+1][y+1])
        or numpy.count_nonzero(maze_numpy[x-1][y+1])):
        if choices.count('down'): choices.remove('down')

    return choices

frame_number = 0
def draw(forced_draw=False):
    global frame_number
    if live_drawing and (frame_number % (frames_skipped+1) == 0 or forced_draw):
        surf = pygame.surfarray.make_surface(maze_numpy)
        if zoom_scale == 1:
            screen.blit(surf, surf.get_rect())
        else:
            frame = pygame.transform.scale(surf, (w * zoom_scale, h * zoom_scale))
            screen.blit(frame, frame.get_rect())
        pygame.display.update()
    frame_number += 1

def maze(direction: str, x: int, y: int):
    if not numpy.count_nonzero(maze_numpy[x][y]):
        maze_numpy[x][y] = color
        draw()

    directions_possible = go_next(direction, x, y)
    if len(directions_possible) == 0:
        return
    else:
        random.shuffle(directions_possible)
        next_direction = directions_possible.pop()

        if next_direction == 'right': maze(next_direction, x + 1, y)
        if next_direction == 'left': maze(next_direction, x - 1, y)
        if next_direction == 'up': maze(next_direction, x, y - 1)
        if next_direction == 'down': maze(next_direction, x, y + 1)

    maze(direction, x, y)


start_time = time.process_time()
maze("right", 0, random.randrange(1, h-1, 2))

# create exit
while True:
    exit_height = random.randint(1, len(maze_numpy[0])-2)
    if numpy.count_nonzero(maze_numpy[len(maze_numpy)-2][exit_height]):
        maze_numpy[len(maze_numpy)-1][exit_height] = color
        break

for i in range(len(maze_numpy[0])):
    if numpy.count_nonzero(maze_numpy[0][i]):
        maze_numpy[0][i] = color
        break

draw(True)

print(f"Maze generated in {int((time.process_time() - start_time)/60)}m {(time.process_time() - start_time)%60}s")
time.sleep(5)
img = Image.fromarray(maze_numpy, 'RGB')
img.save('/tmp/maze.png')