"""Connect4 game graphics module."""

from typing import Tuple, Dict, Optional
import random
import sys
import os

import numpy as np
import pygame

from connect4_mcts import GameBoard


# Color RGB values
BLUE = (0, 123, 255)
LIGHT_BLUE = (215, 252, 250)
DARK_BLUE = (0, 73, 151)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
YELLOW = (238, 219, 4)
DARK_YELLOW = (138, 119, 0)
WHITE = (255, 255, 255)
BLACK = (50, 50, 50)

# Screen resolution
WIN_SIZE = (W_WIDTH, W_HEIGHT) = (800, 600)

# Frame rate
FPS = 30


class GameGraphics:
    """Connect4 game graphics class."""

    def __init__(
        self, win_size: Tuple[int, int], surface: pygame.Surface
    ) -> None:
        self.win_size = win_size
        self.surface = surface
        self.clouds: Dict[int, Tuple[int, int]] = {}
        self.n_cloud = 4
        self.create_clouds()

    def update_clouds(self, speed: float) -> None:
        """Update cloud animation.

        Args:
            speed (float): cloud speed.
        """
        for cloud_id, pos in self.clouds.items():
            self.clouds[cloud_id] = (pos[0] - int(speed / FPS), pos[1])
        self.remove_clouds()
        self.create_clouds()

    def create_clouds(self) -> None:
        """Create clouds sprites."""
        while len(self.clouds) < self.n_cloud:
            posx = random.randint(self.win_size[0], 2 * self.win_size[0])
            posy = random.randint(0, 2 * self.win_size[1])
            dist = 150
            cloud_id = 0
            spaced = True
            for pos in self.clouds.values():
                if abs(pos[1] - posy) < dist:
                    spaced = False
            if spaced:
                while cloud_id in self.clouds:
                    cloud_id += 1
                self.clouds[cloud_id] = (posx, posy)

    def remove_clouds(self) -> None:
        """Remove clouds sprites."""
        remove = []
        toll = 200
        for key, val in self.clouds.items():
            if val[0] < 0 - toll:
                remove.append(key)
        for i in remove:
            del self.clouds[i]

    def draw_cloud(self, pos: Tuple[int, int]) -> None:
        """Draw single cloud.

        Args:
            pos (Tuple[int, int]): X, Y screen coordinate.
        """
        r = 30
        p = (round(pos[0]), round(pos[1]))
        pygame.draw.circle(self.surface, BLACK, p, r)
        pygame.draw.circle(self.surface, BLACK, (p[0] + 30, p[1] + 10), r - 10)
        pygame.draw.circle(self.surface, BLACK, (p[0] + 60, p[1]), r)
        pygame.draw.circle(self.surface, BLACK, (p[0] + 110, p[1]), r)
        pygame.draw.circle(self.surface, BLACK, (p[0] + 30, p[1] - 30), r)
        pygame.draw.circle(self.surface, BLACK, (p[0] + 30, p[1] + 20), r + 10)
        pygame.draw.circle(self.surface, BLACK, (p[0] + 70, p[1] - 20), r + 10)
        pygame.draw.circle(self.surface, BLACK, (p[0] + 80, p[1] + 30), r)
        pygame.draw.circle(self.surface, WHITE, p, r)
        pygame.draw.circle(self.surface, WHITE, (p[0] + 30, p[1] + 10), r - 10)
        pygame.draw.circle(self.surface, WHITE, (p[0] + 60, p[1]), r)
        pygame.draw.circle(self.surface, WHITE, (p[0] + 110, p[1]), r)
        pygame.draw.circle(self.surface, WHITE, (p[0] + 30, p[1] - 30), r)
        pygame.draw.circle(self.surface, WHITE, (p[0] + 30, p[1] + 20), r + 10)
        pygame.draw.circle(self.surface, WHITE, (p[0] + 70, p[1] - 20), r + 10)
        pygame.draw.circle(self.surface, WHITE, (p[0] + 80, p[1] + 30), r)

    def draw_background(self, speed: float) -> None:
        """Draw background elements.

        Args:
            speed (float): Animation speed.
        """
        self.surface.fill(LIGHT_BLUE)
        self.update_clouds(speed=speed)
        for pos in self.clouds.values():
            self.draw_cloud(pos)

    def draw_board(self, board: np.ndarray) -> None:
        """Draw game board and players' pieces.

        Args:
            board (np.ndarray): Game matrix.
        """
        radius = 30
        w_space = 41
        h_space = 13
        shift = 7
        # Draw frame shadow
        frame = pygame.Surface((752, 451))
        frame.fill(BLACK)
        frame.set_colorkey(WHITE)
        for i in range(7):
            for j in range(6):
                pos = (
                    w_space + radius + i * (w_space + 2 * radius),
                    h_space + radius + j * (h_space + 2 * radius),
                )
                pygame.draw.circle(frame, WHITE, pos, radius)
        self.surface.blit(frame, (w_space / 2 + shift, 125 - shift))
        outline = pygame.Surface(self.win_size)
        outline.fill(WHITE)
        outline.set_colorkey(WHITE)
        points1 = ((0, shift), (shift, 0), (752 + shift, 0), (752, shift))
        points2 = (
            (752 + shift, 0),
            (752 + shift, 451),
            (752, 451 + shift),
            (752, shift),
        )
        pygame.draw.polygon(outline, BLACK, points1)
        pygame.draw.polygon(outline, DARK_BLUE, points2)
        self.surface.blit(outline, (20, 117))
        # Draw frame
        frame = pygame.Surface((752, 451))
        frame.fill(BLUE)
        frame.set_colorkey(WHITE)
        for i in range(7):
            for j in range(6):
                pos = (
                    w_space + radius + i * (w_space + 2 * radius),
                    h_space + radius + j * (h_space + 2 * radius),
                )
                pygame.draw.circle(frame, WHITE, pos, radius)
        # Draw pieces
        for row in range(6):
            for col in range(7):
                if board[5 - row, col] == 1:
                    pos = (
                        w_space + radius + col * (w_space + 2 * radius),
                        h_space + radius + row * (h_space + 2 * radius),
                    )
                    pygame.draw.circle(frame, RED, pos, radius)
                elif board[5 - row, col] == 2:
                    pos = (
                        w_space + radius + col * (w_space + 2 * radius),
                        h_space + radius + row * (h_space + 2 * radius),
                    )
                    pygame.draw.circle(frame, YELLOW, pos, radius)
        # Blit surface to screen
        self.surface.blit(frame, (w_space / 2, 125))

    def draw_select(self, column: int, turn: int) -> None:
        """Draw move selection.

        Args:
            column (int): Column index.
            turn (int): Player turn.
        """
        radius = 30
        w_space = 41
        h_space = 13
        shift = 3
        # Draw colored piece based on player turn
        if turn == 1:
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (
                w_space + radius + (column - 1) * (w_space + 2 * radius),
                h_space + radius,
            )
            pygame.draw.circle(surf, DARK_RED, pos, radius)
            self.surface.blit(surf, (w_space / 2 + shift, 18 - shift))
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (
                w_space + radius + (column - 1) * (w_space + 2 * radius),
                h_space + radius,
            )
            pygame.draw.circle(surf, RED, pos, radius)
            self.surface.blit(surf, (w_space / 2, 18))
        elif turn == 2:
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (
                w_space + radius + (column - 1) * (w_space + 2 * radius),
                h_space + radius,
            )
            pygame.draw.circle(surf, DARK_YELLOW, pos, radius)
            self.surface.blit(surf, (w_space / 2 + shift, 18 - shift))
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (
                w_space + radius + (column - 1) * (w_space + 2 * radius),
                h_space + radius,
            )
            pygame.draw.circle(surf, YELLOW, pos, radius)
            self.surface.blit(surf, (w_space / 2, 18))

    def gameover_screen(self, winner: Optional[int], select: int) -> None:
        """Draw gameover screen.

        Args:
            winner (int | None): Winner id or None.
            select (int): Button selection.
        """
        shift = 3
        surf = pygame.Surface(self.win_size)
        font = pygame.font.SysFont("Futura", 50)
        surf.fill(WHITE)
        surf.set_colorkey(WHITE)
        # Draw menu window
        pygame.draw.rect(surf, BLUE, (100, 150, 600, 300))
        pygame.draw.rect(surf, YELLOW, (200, 380, 120, 40))
        pygame.draw.rect(surf, RED, (480, 380, 120, 40))
        # Draw window shadow
        pygame.draw.polygon(surf, BLACK, (
            (100, 150), (100 + shift, 150 - shift), (700 + shift, 150 - shift),
            (700 + shift, 450 - shift), (700, 450), (700, 150)
        ))
        pygame.draw.polygon(surf, BLACK, (
            (200, 380), (200 + shift, 380 - shift), (320 + shift, 380 - shift),
            (320 + shift, 420 - shift), (320, 420), (320, 380)
        ))
        pygame.draw.polygon(surf, BLACK, (
            (480, 380), (480 + shift, 380 - shift), (600 + shift, 380 - shift),
            (600 + shift, 420 - shift), (600, 420), (600, 380)
        ))
        # Draw answear selector
        if select == 1:
            pygame.draw.rect(surf, WHITE, (200, 380, 120, 40), 3)
        elif select == 2:
            pygame.draw.rect(surf, WHITE, (480, 380, 120, 40), 3)
        # Draw separator line
        pygame.draw.rect(surf, WHITE, (150, 260, 500, 5))
        self.surface.blit(surf, (0, 0))
        # Draw text
        if winner == 1:
            champion = font.render("Red player is the winner!", True, WHITE)
            self.surface.blit(champion, (180, 182))
        elif winner == 2:
            champion = font.render("Yellow player is the winner!", True, WHITE)
            self.surface.blit(champion, (125, 182))
        else:
            champion = font.render("Game ended in a tie!", True, WHITE)
            self.surface.blit(champion, (185, 182))
        rematch = font.render("Rematch?", True, WHITE)
        yes = font.render("YES", True, WHITE)
        no = font.render("NO", True, WHITE)
        yes_s = font.render("YES", True, BLACK)
        no_s = font.render("NO", True, BLACK)
        self.surface.blit(rematch, (320, 310))
        self.surface.blit(yes_s, (225, 383))
        self.surface.blit(no_s, (517, 383))
        self.surface.blit(yes, (223, 385))
        self.surface.blit(no, (515, 385))


if __name__ == "__main__":

    # Initialize stuff
    os.system("cls")
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption("Connect 4 Montecarlo")
    window = pygame.display.set_mode(WIN_SIZE)
    clock = pygame.time.Clock()
    graphics = GameGraphics(win_size=WIN_SIZE, surface=window)

    # Begin new game
    while True:

        gameboard = GameBoard(cpu=1)
        game_over = False
        winner_id = None
        select_move = 1

        # Game loop
        while True:

            # Check for game over
            game_over, winner_id = gameboard.check_win()
            if game_over is True:
                pygame.time.wait(1000)
                break

            # Game controls
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

            # Draw game graphics
            graphics.draw_background(speed=100)
            graphics.draw_board(gameboard.board)
            graphics.draw_select(select_move, gameboard.turn)

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
