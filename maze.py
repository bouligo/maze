import numpy
import random
import time
from PIL import Image

# Careful with stack overflows
import sys
import resource
sys.setrecursionlimit(5000000)  # Because I suck at coding 
resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import argparse


class Maze:
    number = 0
    def __init__(self, game):
        self.game = game

    def generate(self):
        Maze.number += 1

        self.prepare_next("right", 0, random.randrange(1, Game.h - 1, 2))

        # create exit
        while True:
            exit_height = random.randint(1, len(self.game.maze_numpy[0]) - 2)
            if numpy.count_nonzero(self.game.maze_numpy[len(self.game.maze_numpy) - 2][exit_height]):
                self.game.maze_numpy[len(self.game.maze_numpy) - 1][exit_height] = self.game.color
                break

        for i in range(len(self.game.maze_numpy[0])):
            if numpy.count_nonzero(self.game.maze_numpy[0][i]):
                self.game.maze_numpy[0][i] = self.game.color
                break

        self.game.draw(True)

    def prepare_next(self, direction: str, x: int, y: int):
        # On keypress, exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                sys.exit()

        if not numpy.count_nonzero(self.game.maze_numpy[x][y]):
            self.game.maze_numpy[x][y] = self.game.color
            self.game.draw()

        directions_possible = self.go_next(direction, x, y)
        if len(directions_possible) == 0:
            return
        else:
            random.shuffle(directions_possible)
            next_direction = directions_possible.pop()

            if next_direction == 'right': self.prepare_next(next_direction, x + 1, y)
            if next_direction == 'left': self.prepare_next(next_direction, x - 1, y)
            if next_direction == 'up': self.prepare_next(next_direction, x, y - 1)
            if next_direction == 'down': self.prepare_next(next_direction, x, y + 1)

        self.prepare_next(direction, x, y)

    def go_next(self, direction: str, x: int, y: int) -> list:
        choices = ['left', 'right', 'up', 'down']
        if direction == "left": choices.remove('right')
        if direction == "right": choices.remove('left')
        if direction == "up": choices.remove('down')
        if direction == "down": choices.remove('up')

        # Removing if target is white already
        if y - 1 > 0 and numpy.count_nonzero(self.game.maze_numpy[x][y - 1]):
            if choices.count('up'): choices.remove('up')
        if y + 1 < len(self.game.maze_numpy[0]) - 1 and numpy.count_nonzero(self.game.maze_numpy[x][y + 1]):
            if choices.count('down'): choices.remove('down')
        if x + 1 < len(self.game.maze_numpy) - 1 and numpy.count_nonzero(self.game.maze_numpy[x + 1][y]):
            if choices.count('right'): choices.remove('right')
        if x - 1 > 0 and numpy.count_nonzero(self.game.maze_numpy[x - 1][y]):
            if choices.count('left'): choices.remove('left')

        # Being GREEDY
        if not x % 2:
            if choices.count('up'): choices.remove('up')
            if choices.count('down'): choices.remove('down')
        if not y % 2:
            if choices.count('right'): choices.remove('right')
            if choices.count('left'): choices.remove('left')

        if (x - 2 < 0
                or y + 1 > len(self.game.maze_numpy[0]) - 1
                or y - 1 < 0
                or numpy.count_nonzero(self.game.maze_numpy[x - 2][y])
                or numpy.count_nonzero(self.game.maze_numpy[x - 2][y + 1])
                or numpy.count_nonzero(self.game.maze_numpy[x - 2][y - 1])
                or numpy.count_nonzero(self.game.maze_numpy[x - 1][y + 1])
                or numpy.count_nonzero(self.game.maze_numpy[x - 1][y - 1])):
            if choices.count('left'): choices.remove('left')
        if (x + 2 > len(self.game.maze_numpy) - 1
                or y + 1 > len(self.game.maze_numpy[0]) - 1
                or y - 1 < 0
                or numpy.count_nonzero(self.game.maze_numpy[x + 2][y])
                or numpy.count_nonzero(self.game.maze_numpy[x + 2][y + 1])
                or numpy.count_nonzero(self.game.maze_numpy[x + 2][y - 1])
                or numpy.count_nonzero(self.game.maze_numpy[x + 1][y + 1])
                or numpy.count_nonzero(self.game.maze_numpy[x + 1][y - 1])):
            if choices.count('right'): choices.remove('right')
        if (y - 2 < 0
                or x + 1 > len(self.game.maze_numpy) - 1
                or x - 1 < 0
                or numpy.count_nonzero(self.game.maze_numpy[x][y - 2])
                or numpy.count_nonzero(self.game.maze_numpy[x + 1][y - 2])
                or numpy.count_nonzero(self.game.maze_numpy[x - 1][y - 2])
                or numpy.count_nonzero(self.game.maze_numpy[x + 1][y - 1])
                or numpy.count_nonzero(self.game.maze_numpy[x - 1][y - 1])):
            if choices.count('up'): choices.remove('up')
        if (y + 2 > len(self.game.maze_numpy[0]) - 1
                or x + 1 > len(self.game.maze_numpy) - 1
                or x - 1 < 0
                or numpy.count_nonzero(self.game.maze_numpy[x][y + 2])
                or numpy.count_nonzero(self.game.maze_numpy[x + 1][y + 2])
                or numpy.count_nonzero(self.game.maze_numpy[x - 1][y + 2])
                or numpy.count_nonzero(self.game.maze_numpy[x + 1][y + 1])
                or numpy.count_nonzero(self.game.maze_numpy[x - 1][y + 1])):
            if choices.count('down'): choices.remove('down')

        return choices

    def save_to_image(self, folder_destination):
        img = Image.fromarray(self.game.maze_numpy, 'RGB')
        img.save(f'{folder_destination}/maze_{Maze.number}.png')


class Game:
    zoom_scale = 1

    def __init__(self):
        self.frame_number = 0
        pygame.init()
        self.calculate_screen_resolution()

        self.color = Game.color or [random.randint(40, 255), random.randint(40, 255), random.randint(40, 255)]
        self.maze_numpy = numpy.zeros((Game.w, Game.h, 3), dtype=numpy.uint8)

        if Game.live_drawing:
            self.screen = pygame.display.set_mode((Game.w * Game.zoom_scale, Game.h * Game.zoom_scale), pygame.FULLSCREEN if Game.full_screen else pygame.RESIZABLE)
            self.surf = pygame.surfarray.make_surface(self.maze_numpy)
            pygame.display.set_caption("Maze generator")

        self.maze = Maze(self)

    def calculate_screen_resolution(self):
        info = pygame.display.Info()
        screen_w, screen_h = info.current_w - 1, info.current_h - 1
        if Game.full_screen:
            Game.zoom_scale = 8
            Game.w, Game.h = screen_w // Game.zoom_scale, screen_h // Game.zoom_scale
        else:
            Game.zoom_scale = max(1, min(screen_h // Game.h, screen_w // Game.w))

        if (Game.w % 2) == 0:
            Game.w -= 1
        if (Game.h % 2) == 0:
            Game.h -= 1

    def start(self):
        while True:
            start_time = time.process_time()
            self.maze.generate()
            if Game.verbose:
                print(f"Maze {Maze.number} generated in {int((time.process_time() - start_time) / 60)}m {(time.process_time() - start_time) % 60}s")
            time.sleep(2)
            if Game.save_to_folder:
                self.maze.save_to_image(Game.save_to_folder)
            if not Game.screensaver_mode:
                break

            self.color = Game.color or [random.randint(40, 255), random.randint(40, 255), random.randint(40, 255)]
            self.maze_numpy = numpy.zeros((Game.w, Game.h, 3), dtype=numpy.uint8)

    def draw(self, forced_draw=False):
        if not Game.live_drawing:
            return

        if self.frame_number % (Game.frames_skipped + 1) == 0 or forced_draw:
            surf = pygame.surfarray.make_surface(self.maze_numpy)
            if Game.zoom_scale == 1:
                self.screen.blit(surf, surf.get_rect())
            else:
                frame = pygame.transform.scale(surf, (Game.w * Game.zoom_scale, Game.h * Game.zoom_scale))
                self.screen.blit(frame, frame.get_rect())
            pygame.display.update()
        self.frame_number += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='maze.py',
        description='Generates mazes to display as screensaver / write them on disk',
        add_help=False)

    parser.add_argument('--help', help="Shows help for this program", action='store_true')

    parser.add_argument('-w', '--width', default=400, type=int, help="Width of generated mazes in windowed mode (Default: 400)")
    parser.add_argument('-h', '--height', default=220, type=int, help="Width of generated mazes in windowed mode (Default: 220)")
    parser.add_argument('-f', '--fullscreen', help="Enable fullscreen support", action='store_true')  # on/off flag

    parser.add_argument('-l', '--loop', help="Generates mazes continuously like a screensaver and exits on keypress (generally used with --fullscreen)", action='store_true')  # on/off flag
    parser.add_argument('-d', '--donotdisplay', help="Maze is generated without being displayed on screen (generally used with --output)", action='store_true')  # on/off flag
    parser.add_argument('-o', '--output', dest="folder", help="Write images of mazes to disk on specified output folder")

    parser.add_argument('-s', '--speed', default=0, type=int, help="Speed to draw mazes, 0 is slowest (Default: 0)")
    parser.add_argument('-c', '--color', nargs=3, type=int, help="Color of the maze, default is random (Syntax: red,green,blue values in a space-separated list)")
    parser.add_argument('-v', '--verbose', help="Shows time required to generate each maze", action='store_true')  # on/off flag
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        sys.exit(0)

    Game.verbose = args.verbose
    Game.screensaver_mode = args.loop
    Game.full_screen = args.fullscreen
    Game.live_drawing = not args.donotdisplay
    Game.h = args.height
    Game.w = args.width
    Game.color = args.color
    Game.frames_skipped = args.speed
    Game.save_to_folder = args.folder

    game = Game()
    game.start()
