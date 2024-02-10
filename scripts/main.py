"""Connect4 Monte Carlo main."""

from typing import List
from threading import Thread
from queue import Queue
import sys
import os

import pygame

from game_graphics import GameGraphics
from connect4_mcts import GameBoard, MCTS, Node

# Screen resolution
WIN_SIZE = (W_WIDTH, W_HEIGHT) = (800, 600)

# MCTS move computation time
PROCESS_TIME = 5

# Frame rate
FPS = 30


if __name__ == "__main__":

    # Initialize stuff
    os.system("cls")
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption("Connect 4 Montecarlo")
    window = pygame.display.set_mode(WIN_SIZE)
    clock = pygame.time.Clock()
    move_queue: "Queue[int]" = Queue()
    graphics = GameGraphics(win_size=WIN_SIZE, surface=window)

    # Begin new game
    while True:

        gameboard = GameBoard(cpu=1)
        montecarlo = MCTS(symbol=1, t=PROCESS_TIME)
        game_over = False
        winner_id = None
        select_move = 1
        threads: List[Thread] = []

        # Game loop
        while True:

            # Check for game over
            game_over, winner_id = gameboard.check_win()
            if game_over is True:
                pygame.time.wait(1000)
                break

            # Human turn
            if gameboard.turn != gameboard.cpu:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            sys.exit()
                        elif event.key == pygame.K_RIGHT:
                            if select_move < 7:
                                select_move += 1
                        elif event.key == pygame.K_LEFT:
                            if select_move > 1:
                                select_move -= 1
                        elif event.key == pygame.K_RETURN:
                            if gameboard.board[5, select_move - 1] == 0:
                                gameboard.apply_move(select_move)

            # Monte Carlo turn
            else:

                # Start thinking
                if len(threads) == 0:
                    root = Node(
                        parent=None,
                        board=gameboard.board,
                        turn=montecarlo.symbol,
                    )
                    t = Thread(
                        target=lambda q, x: q.put(montecarlo.compute_move(x)),
                        args=(move_queue, root),
                    )
                    t.start()
                    threads.append(t)

                # Ready to play
                if move_queue.empty() is False:
                    threads.pop()
                    move = move_queue.get()
                    gameboard.board[move] = montecarlo.symbol
                    gameboard.switch_turn()

            # Draw game graphics
            graphics.draw_background(speed=100)
            graphics.draw_board(board=gameboard.board)
            if gameboard.turn != gameboard.cpu:
                graphics.draw_select(column=select_move, turn=gameboard.turn)

            # Update stuff
            clock.tick(FPS)
            pygame.event.pump()
            pygame.display.flip()

        # Game over / continue
        select_option = 1
        new_game = False
        while new_game is False:

            # Menu controls
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    elif event.key == pygame.K_RIGHT:
                        if select_option < 2:
                            select_option += 1
                    elif event.key == pygame.K_LEFT:
                        if select_option > 1:
                            select_option -= 1
                    elif event.key == pygame.K_RETURN:
                        if select_option == 1:
                            new_game = True
                        elif select_option == 2:
                            sys.exit()

            # Draw game over screen
            graphics.draw_background(speed=100)
            graphics.gameover_screen(winner_id, select_option)

            # Update stuff
            clock.tick(FPS)
            pygame.event.pump()
            pygame.display.flip()
